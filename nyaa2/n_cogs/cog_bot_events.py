
import discord
import random

from discord.ext import commands

from .. import constants
from .. import n_database as db 
from .. import util

from .cog_base import BaseNyaaCog

# cog used for debug and bot events 
class BotEvents(BaseNyaaCog):
    """ events for the bot """

    COG_BOT_EVENTS_LOGGER = util.get_logger(*constants.COG_BOT_EVENTS_LOGGER)
    
    def __init__(self, bot) -> None:
        BaseNyaaCog.__init__(self, bot)
        self.logger = self.COG_BOT_EVENTS_LOGGER


    async def cog_check(self, ctx):

        if not ctx.guild:

            self.logger.info(f"Private message from {ctx.author.id}. Ignoring.")

            raise commands.NoPrivateMessage

        return True


    async def cog_command_error(self, ctx, error):
        
        if isinstance(error, commands.NoPrivateMessage):

            return await self.send_message_wrapped(ctx, 'This command can not be used in Private Messages.')

        self.logger.error('Ignoring exception in command {}:'.format(ctx.command))
        self.logger.error(error)
    


    @commands.Cog.listener()
    async def on_ready(self):

        self.logger.info("====================================")
        self.logger.info(f"{self.bot.user.name} has connected")
        self.logger.info("====================================")
        self.logger.info("Servers:")
        self.logger.info("====================================")

        for i in self.bot.guilds:

            self.logger.info(f"[  {i.name}")

        self.logger.info("====================================")



