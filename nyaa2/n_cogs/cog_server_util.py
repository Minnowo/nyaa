
import traceback
import sys
import base64
import discord
import random
from discord.errors import HTTPException

from discord.ext import commands
from discord.ext.commands.context import Context 
import discord.ext.commands.errors

from .. import util
from .. import constants

from . import (
    BaseNyaaCog
)

class ServerUtil(BaseNyaaCog):
    """ server utility functions """

    COG_Server_Util_LOGGER = util.get_logger(*constants.COG_SERVER_UTIL_LOGGER)

    def __init__(self, bot) -> None:
        BaseNyaaCog.__init__(self, bot)
        self.logger = self.COG_Server_Util_LOGGER



    async def cog_command_error(self, ctx, error):
        
        if isinstance(error, commands.NoPrivateMessage):

            return await self.send_message_wrapped(ctx, 'This command can not be used in Private Messages.')
        
        self.logger.error('Ignoring exception in command {}:'.format(ctx.command))
        self.logger.error(error)

        # print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        # traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        


    @commands.command(name='help')
    async def help_(self, ctx, *, search: str = None):

        await self.send_message_wrapped(ctx, random.choice(constants.JOKE_HELP))



    @commands.command(name='invite', aliases=['getinvite'])
    async def invite_(self, ctx): 
        await ctx.send(f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot")



    @commands.command(name='random', aliases=["rand", "rnd"])
    async def random_(self, ctx, a : str, b : str): 
        
        a = util.parse_int(a, None)
        b = util.parse_int(b, None)

        if not a or not b:
            
            return await self.send_message_wrapped(ctx, "Please enter a min and max number")

        if a > b:

            return await self.send_message_wrapped(ctx, str(random.randint(b, a)))
            
        return await self.send_message_wrapped(ctx, str(random.randint(a, b)))



    @commands.command(name='clear', aliases=["delete", "purge"])
    async def clear_(self, ctx, amount = 5): 

        if not ctx.guild:
            
            return await self.send_message_wrapped(ctx, "can't purge dms, sorry </3")

        if ctx.author.permissions_in(ctx.channel).manage_messages:
            
            return await ctx.channel.purge(limit = amount + 1)

        return await self.send_message_wrapped(ctx, "I lack permission. ~~master pwease give me admin <3~~")



    @commands.command(name='getuser', aliases=["getmember", "fetchuser", "user", "member"])
    async def getuser_(self, ctx, *, id : str = None): 
        
        if id is None:
            return await self.send_message_wrapped(ctx, "Pwease specify a User or their ID <3")

        id = util.get_mention_id_from_string(id)

        if id is None:
            return await self.send_message_wrapped(ctx, "Invalid ID or @")

        try:
            
            member = await self.bot.fetch_user(id)

        except HTTPException as e:
            
            self.logger.error(e)
            
            return await self.send_message_wrapped(ctx, "There was an error making the request")

        except (discord.errors.NotFound, discord.ext.commands.errors.MemberNotFound):

            return await self.send_message_wrapped(ctx, "Could not find the user </3")

        embed = discord.Embed(color = constants.EMBED_COLOR)
        embed.set_author(name = f"{member.name}#{member.discriminator}", icon_url = member.avatar_url_as(size=128))
        embed.set_thumbnail(url=member.avatar_url_as(size=128))
        embed.add_field(name =f"**User:**", value = 'Mention: <@{}> \nName: {} \nId: {}'.format(member.id, member, member.id), inline=False)
        embed.add_field(name =f"**Account Created On:**", value = member.created_at, inline=False)

        await ctx.send(embed=embed)



    @commands.command(name='getserver', aliases=["server", "fetchserver", "guild", "getguild"])
    async def getguild_(self, ctx, *, id : discord.Guild = None): 
        
        if isinstance(id, str):
            id = util.parse_int(id)

        if id is None:
            guild = ctx.guild

        elif isinstance(id, discord.Guild):
            guild = id 
        
        else:
            
            try:
            
                guild = self.bot.get_guild(id)
            
            except HTTPException:
                
                return await self.send_message_wrapped(ctx, "There was an error making the request")
                
            except (discord.errors.NotFound, discord.ext.commands.errors.GuildNotFound):
                return await self.send_message_wrapped(ctx, "I'm not in this server </3")

        if not guild:

            return await self.send_message_wrapped(ctx, "I'm not in this server ;w;")

        embed = discord.Embed(color = constants.EMBED_COLOR)
        embed.set_author(name = f"{guild.name}", icon_url = guild.icon_url)
        embed.set_thumbnail(url=guild.icon_url)
        embed.add_field(name =f"**Server:**", value = 'Name: {} \nMember Count: {} \nChannel Count: {} \n Owner Id: {}\n Id: {}'.format(guild.name, guild.member_count,len(guild.channels),guild.owner_id, guild.id), inline=False)
        embed.add_field(name =f"**Created On:**", value = guild.created_at, inline=False)

        await ctx.send(embed=embed)

