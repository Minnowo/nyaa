
import traceback
import sys
import discord
import datetime

from discord.ext import commands
from discord.ext.commands.context import Context

from . import util
from . import constants
from . import regex

class LeaveJoinMessage(commands.Cog):
    """ handles user leave / join message """

    event_map = {
        constants.MEMBER_LEAVE : {
            # serverid           : channels
            # 381952489655894016 : [],
        },
        constants.MEMBER_JOIN : {

        }
    }

    nyaa_cog = True

    def __init__(self, bot) -> None:
        self.bot = bot

    async def __error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('This command can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
  

    @commands.Cog.listener()
    async def on_member_join(self, member):

        guild = member.guild 

        for channel_id in self.event_map[constants.MEMBER_JOIN].get(guild.id, []):
            
            channel = guild.get_channel(channel_id)

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

        for channel_id in self.event_map[constants.MEMBER_LEAVE].get(guild.id, []):
            
            channel = guild.get_channel(channel_id)

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
        
        if not ctx.guild:
            return

        if not ctx.author.permissions_in(ctx.channel).manage_guild:
            await ctx.send("you required the ability to manage the guild to use this command >:3")
            return 

        if not event or event not in self.event_map:
            await ctx.send(f"must specify the event to subscribe -> {constants.MEMBER_LEAVE}, {constants.MEMBER_JOIN}")
            return 

        server_id = str(ctx.guild.id)

        if server_id not in self.event_map[event]:
            self.event_map[event][server_id] = set()

        if not channel:
            self.event_map[event][server_id].add(ctx.channel.id)
            await ctx.send("subscribed to the current channel")
            return

        # get the channel id from the mention string <#12345678>
        m = regex.PARSE_CHANNEL_MENTION.search(channel)
        
        if m:
            id = util.parse_int(m.group(1))

        else:
            id = util.parse_int(channel, None)

            if not channel:
                await ctx.send("invalid channel")
                return

        channel = ctx.guild.get_channel(id)
        
        if not channel:
            await ctx.send(f"cannot find channel with given id: {id}")
            return 

        self.event_map[event][server_id].add(channel.id)
        await ctx.send(f"subscribed to the channel with the id: {id}")

    