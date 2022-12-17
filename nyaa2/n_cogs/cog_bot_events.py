

from discord.ext import commands

from .. import constants
from .. import n_database as db 
from .. import util

from .cog_base import BaseNyaaCog

# cog used for debug and bot events 
class BotEvents(BaseNyaaCog):
    """ events for the bot """

    def __init__(self, bot) -> None:
        BaseNyaaCog.__init__(self, bot)


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

        with self.DISCORD_LOG_DB_INSTANCE:

            for i in self.bot.guilds:

                if not i.owner:
    
                    self.DISCORD_LOG_DB_INSTANCE.add_server(i.id, i.name, -1, i.created_at)

                    self.logger.warning(f"guild {i} has None type owner")

                else:
                    
                    self.DISCORD_LOG_DB_INSTANCE.add_server(i.id, i.name, i.owner.id, i.created_at)

                self.logger.info(f"[  {i.name}")

        self.logger.info("====================================")

        self.logger.info("Trusted Users:")
        self.logger.info("====================================")

        for trusted in self.MISC_DB_INSTANCE.get_all_trusted():

            self.logger.info(f"[{trusted['user_id']}] [  {trusted['username']}")

        self.logger.info("====================================")


    @commands.Cog.listener()
    async def on_guild_join(self, guild):

        self.logger.info(f"Bot has joined guild {guild.name}")

        self.DISCORD_LOG_DB_INSTANCE.add_server(guild.id, guild.name, guild.owner.id, guild.created_at)


    @commands.Cog.listener()
    async def on_message(self, message):
        
        if message.guild is None or \
           message.author.bot:
            return 

        # if message.guild.id == 381952489655894016 and message.channel.id == 942174974754566204:
            
        #     with open(constants.URL_SAVE + "url.txt", "a") as writer:

        #         for attachment in message.attachments:

        #             writer.write(attachment.url + "\n")

        #     with open(constants.URL_SAVE + "purl.txt", "a") as writer:

        #         for attachment in message.attachments:

        #             writer.write(attachment.proxy_url + "\n")

        self.DISCORD_LOG_DB_INSTANCE.add_channel_message_user(message)

        
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        
        if message.guild is None or \
           message.author.bot:
            return 

        self.DISCORD_LOG_DB_INSTANCE.set_message_deleted(message.id)
        