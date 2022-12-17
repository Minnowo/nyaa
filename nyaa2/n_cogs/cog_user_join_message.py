import sys
import discord
import datetime
import os 

from discord.ext import commands

from .. import util
from .. import constants
from .. import n_database as db

from . import BaseNyaaCog

class LeaveJoinMessage(BaseNyaaCog):
    """ handles user leave / join message """

    event_map = {
    }

    nyaa_cog = True

    def __init__(self, bot) -> None:
        BaseNyaaCog.__init__(self, bot)

        self.DB_SESSION = db.DiscordEventDB.get_instance()

        self.MEMBER_JOIN_EVENT  = self.DB_SESSION.select_event_id_by_name(constants.MEMBER_JOIN)
        self.MEMBER_LEAVE_EVENT = self.DB_SESSION.select_event_id_by_name(constants.MEMBER_LEAVE)
        self.event_map[constants.MEMBER_JOIN]  = self.MEMBER_JOIN_EVENT
        self.event_map[constants.MEMBER_LEAVE] = self.MEMBER_LEAVE_EVENT


    async def cog_check(self, ctx):

        if not ctx.guild:
            raise commands.NoPrivateMessage

        perms = ctx.channel.permissions_for(ctx.author)

        if perms is None or not perms.manage_channels:
    
            raise commands.MissingPermissions(["manage_channels"])

        return True



    async def cog_command_error(self, ctx, error):

        if isinstance(error, commands.NoPrivateMessage):

            return await self.send_message_wrapped(ctx, 'This command can not be used in Private Messages ;w;')

        if isinstance(error, commands.MissingPermissions):

            return await self.send_message_wrapped(ctx, "You are missing permissions to use this command >:3")
        
        self.logger.error('Ignoring exception in command {}:'.format(ctx.command))
        self.logger.error(error)



    @commands.Cog.listener()
    async def on_member_join(self, member):

        guild = member.guild 

        for channel_id in self.DB_SESSION.select_channels_where_event(guild.id, self.MEMBER_JOIN_EVENT):
            
            channel = guild.get_channel(channel_id['channel_id'])

            if not channel:
                continue

            self.logger.info(f"User {member.id} has joined {guild.id}")

            date_time = member.joined_at or str(datetime.datetime.now().strftime("%x")) + " " + str(datetime.datetime.now().strftime("%X"))
            
            leave_join_embed = discord.Embed(color = constants.EMBED_USER_JOIN_COLOR)
            leave_join_embed.set_author(name = f"**{member.name} Joined The Server**", icon_url = member.avatar)
            leave_join_embed.set_footer(text = f"Joined at: {date_time}")
            leave_join_embed.add_field(name =f"**User:**", 
                                       value = f'Mention: <@{member.id}>\n' + \
                                               f'Name: {member} \n' + \
                                               f'Id: {member.id}', inline=False)
            leave_join_embed.add_field(name =f"**Account Created On:**", value = member.created_at, inline=False)

            await self.send_message_wrapped(channel, embed=leave_join_embed)


    @commands.Cog.listener()
    async def on_member_remove(self, member):

        guild = member.guild 

        for channel_id in self.DB_SESSION.select_channels_where_event(guild.id, self.MEMBER_LEAVE_EVENT):
            
            channel = guild.get_channel(channel_id['channel_id'])

            if not channel:
                continue

            self.logger.info(f"User {member.id} has joined {guild.id}")

            date_time = member.joined_at or str(datetime.datetime.now().strftime("%x")) + " " + str(datetime.datetime.now().strftime("%X"))
            
            leave_join_embed = discord.Embed(color = constants.EMBED_USER_LEFT_COLOR)
            leave_join_embed.set_author(name = f"**{member.name} Left The Server**", icon_url = member.avatar)
            leave_join_embed.set_footer(text = f"Joined at: {date_time}")                        
            leave_join_embed.add_field(name =f"**User:**", 
                                       value = f'Mention: <@{member.id}>\n' + \
                                               f'Name: {member} \n' + \
                                               f'Id: {member.id}', inline=False)
            leave_join_embed.add_field(name =f"**Account Created On:**", value = member.created_at, inline=False)

            await self.send_message_wrapped(channel, embed=leave_join_embed)


    @commands.command(name='leave_join_message', aliases=['ljm'])
    async def subscribe_(self, ctx, event : str = None, channel : str = None):
        
        if not event or event not in self.event_map:

            return await self.send_message_wrapped(ctx, f"Must specify the event to subscribe -> '{constants.MEMBER_LEAVE}' or '{constants.MEMBER_JOIN}'")

        self.DB_SESSION.add_server(ctx.guild.id, ctx.guild.name, ctx.guild.owner_id, ctx.guild.created_at)

        if not channel:

            self.DB_SESSION.add_channel(ctx.guild.id, ctx.channel.id, ctx.channel.name, 0)
            self.DB_SESSION.add_channel_event(ctx.channel.id, self.event_map[event.lower()])
            self.DB_SESSION.commit()
            
            return await self.send_message_wrapped(ctx, "Subscribed to the current channel")

        id = util.get_channel_id_from_string(channel)
        
        if not id:

            return await self.send_message_wrapped(ctx, "Invalid channel")


        channel = ctx.guild.get_channel(id)
        
        if not channel:
            
            return await self.send_message_wrapped(f"I cannot find channel with given id: {id}")

        self.logger.info(f"Subscribed to {ctx.guild.id}")

        self.DB_SESSION.add_channel(ctx.guild.id, channel.id, channel.name, 0)
        self.DB_SESSION.add_channel_event(channel.id, self.event_map[event.lower()])
        self.DB_SESSION.commit()
        
        await self.send_message_wrapped(ctx, f"Subscribed to the channel with the id: {id}")



    @commands.command(name='remove_leave_join_message', aliases=['rljm'])
    async def unsubscribe_(self, ctx, event : str = None, channel : str = None):
        
        if not event or event not in self.event_map:

            return await self.send_message_wrapped(ctx, f"Must specify the event to subscribe -> '{constants.MEMBER_LEAVE}' or '{constants.MEMBER_JOIN}'")

        if not channel:

            self.DB_SESSION.remove_channel_event_2(ctx.guild.id, ctx.channel.id, self.event_map[event.lower()])
            
            return await self.send_message_wrapped(ctx, "Unsubscribed from the current channel")

        id = util.get_channel_id_from_string(channel)
        
        if not id:

            return await self.send_message_wrapped(ctx, "Invalid channel")

        channel = ctx.guild.get_channel(id)
        
        if not channel:

            return await self.send_message_wrapped(ctx, f"I cannot find channel with given id: {id}")

        self.logger.info(f"Unsubscribed to {ctx.guild.id}")

        self.DB_SESSION.remove_channel_event_2(ctx.guild.id, channel.id, self.event_map[event.lower()])

        await self.send_message_wrapped(ctx, f"Unsubscribed from the channel with the id: {id}")

    