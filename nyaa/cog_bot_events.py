
import traceback
import sys
import discord
import random
from discord.ext import commands
from . import constants

class BotEvents(commands.Cog):
    """ events for the bot """

    nyaa_cog = True

    def __init__(self, bot) -> None:
        self.bot = bot

    async def __local_check(self, ctx):
        """A local check which applies to all commands in this cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def __error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('This command can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    # @commands.command(name='debug')
    # async def debug_(self, ctx, *, search: str = None):
    #     await ctx.send("~~test~~")
    
    @commands.command(name='help')
    async def help_(self, ctx, *, search: str = None):

        await ctx.send(random.choice(constants.JOKE_HELP))

    @commands.Cog.listener()
    async def on_ready(self):
        print("====================================")
        print(" \"{0.user.name}\"  has connected".format(self.bot))
        print("====================================")
        print("\nServers:")
        print("====================================\n")
        for i in self.bot.guilds:
            print(" [ {0.name}".format(i))
        print("\n====================================")
