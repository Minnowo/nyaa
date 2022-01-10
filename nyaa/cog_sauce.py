
import itertools
from posixpath import abspath
import traceback
import discord
import asyncio
import sys 
import requests
import os 

from discord.ext import commands
from discord.ext.commands import has_permissions

class Sauce(commands.Cog):
    """ """

    nyaa_cog = True

    async def __error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('This command can not be used in Private Messages.')
            except discord.HTTPException:
                pass

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
