
import discord
from discord.ext import commands

from .. import constants
from .. import util

class BaseNyaaCog(commands.Cog):
    """ Base Nyaa Cog Class, all cogs should inherit from this """

    COG_BASE_LOGGER = util.get_logger(*constants.COG_BASE_LOGGER)

    nyaa_cog = True
    
    def __init__(self, bot) -> None:
        self.bot = bot
        self.logger = self.COG_BASE_LOGGER

    def shutdown(self) -> None:
        """ Perform cleanup """
    
    async def cog_check(self, ctx):
        """A local check which applies to all commands in this cog."""

        return True

    async def cog_command_error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""

        self.logger.error(error)


    async def send_message_wrapped(self, ctx, *args, **kwargs):
        """ calls ctx.send wrapped with a try except block """
        try:
        
            return await ctx.send(*args, **kwargs)
        
        except discord.HTTPException as e:
            
            self.logger.error(e)


    async def send_image_embed(self, ctx, url):
        """sends a discord emebd with an image set to the given url"""

        embed = discord.Embed(color = constants.EMBED_COLOR)
        embed.set_image(url = url)

        try:
            
            await ctx.send(embed=embed)

        except discord.HTTPException as e:

            self.logger.error(e)