
import traceback
import sys
import discord
import datetime
import os 
from discord import permissions

from discord.ext import commands
from discord.ext.commands.context import Context

from . import util
from . import constants
from . import regex
from . import config 
from . import n_database as db


class LeaveJoinMessage(commands.Cog):
    """ handles user leave / join message """

    config_path = None
    event_map = {
    }

    nyaa_cog = True

    def __init__(self, bot) -> None:

        print(f"   Loading {constants.bcolors.WARNING}LeaveJoinMessage{constants.bcolors.ENDC} ->", end="", flush=True)

        self.DB_SESSION = db.DB.get_instance()
        self.DB_SESSION.add_event(constants.MEMBER_LEAVE)
        self.DB_SESSION.add_event(constants.MEMBER_JOIN)

        self.MEMBER_JOIN_EVENT  = self.DB_SESSION.select_event_id_by_name(constants.MEMBER_JOIN)
        self.MEMBER_LEAVE_EVENT = self.DB_SESSION.select_event_id_by_name(constants.MEMBER_LEAVE)
        self.event_map[constants.MEMBER_JOIN] = self.MEMBER_JOIN_EVENT
        self.event_map[constants.MEMBER_LEAVE] = self.MEMBER_LEAVE_EVENT

        self.bot = bot

        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), constants.LEAVE_JOIN_CONFIG)
        
        # config.load(self.config_path, conf = self.event_map)

        # util.replace_list_set(self.event_map)

        print(constants.bcolors.OKGREEN + " Done." + constants.bcolors.ENDC)


    def __del__(self):
        print("\nLeaveJoinMessage Cog Closing:")
        print("   Saving config... ->", end="", flush=True)
        # config.save(self.config_path, conf = self.event_map)
        print(constants.bcolors.OKGREEN + " Done" + constants.bcolors.ENDC)
        
    
    async def cog_check(self, ctx):
        """A local check which applies to all commands in this cog."""

        if not ctx.guild:
            raise commands.NoPrivateMessage

        if not ctx.author.permissions_in(ctx.channel).manage_channels:
            raise commands.MissingPermissions(["manage_channels"])
            
        return True

    async def cog_command_error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""

        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('This command can not be used in Private Messages ;w;')
            except discord.HTTPException:
                pass

        if isinstance(error, commands.MissingPermissions):
            try:
                return await ctx.send("You are missing permissions to use this command >:3")
            except discord.HTTPException:
                pass
        
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


    @commands.Cog.listener()
    async def on_member_join(self, member):

        guild = member.guild 

        # for channel_id in self.event_map[constants.MEMBER_JOIN].get(str(guild.id), []):
        for channel_id in self.DB_SESSION.select_channels_where_event(int(guild.id), self.MEMBER_JOIN_EVENT):
            
            channel = guild.get_channel(channel_id['channel_id'])
            # channel = guild.get_channel(channel_id)

            if not channel:
                continue

            date_time = member.joined_at or str(datetime.datetime.now().strftime("%x")) + " " + str(datetime.datetime.now().strftime("%X"))
            
            leave_join_embed = discord.Embed(color = constants.EMBED_USER_JOIN_COLOR)
            leave_join_embed.set_author(name = f"**{member.name} Joined The Server**", icon_url = member.avatar_url_as(size=128))
            leave_join_embed.set_footer(text = f"Joined at: {date_time}")
            leave_join_embed.add_field(name =f"**User:**", value = 'Mention: <@{}> \nName: {} \nId: {}'.format(member.id, member, member.id), inline=False)
            leave_join_embed.add_field(name =f"**Account Created On:**", value = member.created_at, inline=False)

            await channel.send(embed = leave_join_embed)


    @commands.Cog.listener()
    async def on_member_remove(self, member):

        guild = member.guild 

        for channel_id in self.DB_SESSION.select_channels_where_event(int(guild.id), self.MEMBER_LEAVE_EVENT):
        # for channel_id in self.event_map[constants.MEMBER_LEAVE].get(str(guild.id), []):
            
            channel = guild.get_channel(channel_id['channel_id'])
            # channel = guild.get_channel(channel_id)

            if not channel:
                continue

            date_time = member.joined_at or str(datetime.datetime.now().strftime("%x")) + " " + str(datetime.datetime.now().strftime("%X"))
            
            leave_join_embed = discord.Embed(color = constants.EMBED_USER_LEFT_COLOR)
            leave_join_embed.set_author(name = f"**{member.name} Left The Server**", icon_url = member.avatar_url_as(size=128))
            leave_join_embed.set_footer(text = f"Joined at: {date_time}")                        
            leave_join_embed.add_field(name =f"**User:**", value = 'Mention: <@{}> \nName: {} \nId: {}'.format(member.id, member, member.id), inline=False)
            leave_join_embed.add_field(name =f"**Account Created On:**", value = member.created_at, inline=False)

            await channel.send(embed = leave_join_embed)


    @commands.command(name='leave_join_message', aliases=['ljm'])
    async def subscribe_(self, ctx, event : str = None, channel : str = None):
        
        if not event or event not in self.event_map:
            await ctx.send(f"Must specify the event to subscribe -> '{constants.MEMBER_LEAVE}' or '{constants.MEMBER_JOIN}'")
            return 

        self.DB_SESSION.add_server(ctx.guild.id, ctx.guild.name, ctx.guild.owner_id, ctx.guild.created_at)

        if not channel:
            self.DB_SESSION.add_channel(ctx.guild.id, ctx.channel.id, ctx.channel.name, 0)
            self.DB_SESSION.add_channel_event(ctx.channel.id, self.event_map[event.lower()])
            self.DB_SESSION.commit()
            
            await ctx.send("Subscribed to the current channel uwu")
            return

        # get the channel id from the mention string <#12345678>
        m = regex.PARSE_CHANNEL_MENTION.search(channel)
        
        if m:
            id = util.parse_int(m.group(1))

        else:
            id = util.parse_int(channel, None)

            if not channel:
                await ctx.send("Invalid channel")
                return

        channel = ctx.guild.get_channel(id)
        
        if not channel:
            await ctx.send(f"I cannot find channel with given id: {id}")
            return 

        self.DB_SESSION.add_channel(ctx.guild.id, channel.id, channel.name, 0)
        self.DB_SESSION.add_channel_event(channel.id, self.event_map[event.lower()])
        self.DB_SESSION.commit()
        
        await ctx.send(f"Subscribed to the channel with the id: {id}")



    @commands.command(name='remove_leave_join_message', aliases=['rljm'])
    async def unsubscribe_(self, ctx, event : str = None, channel : str = None):
        
        if not event or event not in self.event_map:
            await ctx.send(f"Must specify the event to subscribe -> {constants.MEMBER_LEAVE}, {constants.MEMBER_JOIN}")
            return 

        if not channel:
            self.DB_SESSION.remove_channel_event_2(ctx.guild.id, ctx.channel.id, self.event_map[event.lower()])
            await ctx.send("Unsubscribed from the current channel uwo")
            return

        id = util.get_channel_id_from_string(channel)
        
        if not id:
            await ctx.send("Invalid channel")
            return

        channel = ctx.guild.get_channel(id)
        
        if not channel:
            await ctx.send(f"I cannot find channel with given id: {id}")
            return 

        self.DB_SESSION.remove_channel_event_2(ctx.guild.id, channel.id, self.event_map[event.lower()])
        await ctx.send(f"Unsubscribed from the channel with the id: {id}")

    