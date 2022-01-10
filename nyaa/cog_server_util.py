
import traceback
import sys
import base64
import discord

from discord.ext import commands
from discord.ext.commands.context import Context 

from . import util
from . import constants

class ServerUtil(commands.Cog):
    """ server utility functions """

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
    

    @commands.command(name='invite', aliases=['getinvite'])
    async def invite_(self, ctx): 
        await ctx.send(f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot")


    @commands.command(name='clear', aliases=["delete", "purge"])
    async def clear_(self, ctx : Context, amount = 5): 

        if not ctx.guild:
            await ctx.send("can't purge dms, sorry </3")
            return 

        if ctx.author.permissions_in(ctx.channel).manage_messages:
            await ctx.channel.purge(limit = amount + 1)
            return 

        await ctx.send("no perms </3")


    @commands.command(name='getuser', aliases=["getmember", "fetchuser", "user", "member"])
    async def getuser_(self, ctx, *, id : discord.Member = None): 
        
        if not id:
            await ctx.send("please specify a user or id")
            return 

        if isinstance(id, str):
            id = util.parse_int(id, None)

            if id == None:
                await ctx.send("invalid id, requires int")
                return

        if isinstance(id, discord.Member):
            member = id 

        else:
            try:
                member = await self.bot.fetch_user(id)
            except discord.errors.NotFound:
                await ctx.send("user not found")
                return

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

        if not id:
            guild = ctx.guild

        elif isinstance(id, discord.Guild):
            guild = id 
        
        else:
            try:
                guild = self.bot.get_guild(id)
            except discord.errors.NotFound:
                await ctx.send("guild not found")
                return

        if not guild:
            await ctx.send("I'm not in this server ;w;")
            return

        embed = discord.Embed(color = constants.EMBED_COLOR)
        embed.set_author(name = f"{guild.name}", icon_url = guild.icon_url)
        embed.set_thumbnail(url=guild.icon_url)
        embed.add_field(name =f"**Server:**", value = 'Name: {} \nMember Count: {} \nChannel Count: {} \n Owner Id: {}\n Id: {}'.format(guild.name, guild.member_count,len(guild.channels),guild.owner_id, guild.id), inline=False)
        embed.add_field(name =f"**Created On:**", value = guild.created_at, inline=False)

        await ctx.send(embed=embed)


        
    @commands.command(name = "encode64", aliases=['eb64', 'e64', 'base64encode', 'base64e'])
    async def encode_base64_(ctx, *, string):
        string_bytes = string.encode("ascii")
        base64_bytes = base64.b64encode(string_bytes) 
        base64_string = base64_bytes.decode("ascii") 
        msg = f'Encoded: \n```{base64_string}```'

        if len(msg) < 2000:
            await ctx.send(msg)
        
        else:
            msg1 = msg[:(len(msg) // 2)] + "```"
            msg2 = "```" + msg[(len(msg) // 2) :]
            await ctx.send(msg1)
            await ctx.send(msg2)

    @commands.command(name = "decode64", aliases=['db64', 'd64','base64decode', 'base64d'])
    async def decode_base64_(ctx, *, string):
        string_bytes = string.encode("ascii")
        base64_bytes = base64.b64decode(string_bytes) 
        base64_string = base64_bytes.decode("ascii") 
        msg = f'Decoded: \n```{base64_string}```'

        if len(msg) < 2000:
            await ctx.send(msg)
        
        else:
            msg1 = msg[:(len(msg) // 2)] + "```"
            msg2 = "```" + msg[(len(msg) // 2) :]
            await ctx.send(msg1)
            await ctx.send(msg2)