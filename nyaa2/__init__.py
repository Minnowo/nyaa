

import discord
import os.path

import os 
import asyncio

from discord.ext import commands
# from discord.ext.commands import has_permissions

from . import n_cogs
from . import constants
from . import config
from . import util
# from . import threaded_queue
from . import n_database

NYAA2_LOGGER = util.get_logger(*constants.NYAA2_BASE_LOGGER)


def get_cog_classes(name):
    """gets all cog classes"""

    module = __import__(name, globals(), None, (), 1)

    return [cls for cls in module.__dict__.values() if hasattr(cls, "nyaa_cog") and cls is not n_cogs.cog_base.BaseNyaaCog]


def create_important_paths():

    for dir in constants.DIRECTORIES:

        if not os.path.isdir(dir):

            util.create_directory(dir)



def main():
    NYAA2_LOGGER.info("Nyaa2 starting...")

    os.system("")  # enable console color on windows 

    NYAA2_LOGGER.info(f"Loading {constants.BOT_CONFIG}")
    config.load(constants.BOT_CONFIG, "bot", True)


    # get bot instance 
    bot = commands.Bot(command_prefix=config.get(("bot"), "prefix"), intents=discord.Intents.all())
    bot.remove_command('help')  # remove help command ;3c

    loop = asyncio.get_event_loop()

    # make bot instance global through the config 
    config.set(("bot"), "instance", bot)


    NYAA2_LOGGER.info("Loading databases")

    db_instance = n_database.DiscordEventDB.get_instance()
    db_instance.connect()
    db_instance.create_tables()
    db_instance.add_event(constants.MEMBER_LEAVE)
    db_instance.add_event(constants.MEMBER_JOIN)

    db_instance = n_database.DiscordLogDB.get_instance()
    db_instance.connect()
    db_instance.create_tables()

    db_instance = n_database.MediaUrlDB.get_instance()
    db_instance.connect()
    db_instance.create_tables()

    db_instance = n_database.MiscDB.get_instance()
    db_instance.connect()
    db_instance.create_tables()
    db_instance.add_trusted_user("dev", config.get(("bot"), "dev_user_id"))

    cats = n_database.MediaUrlDB.get_instance().get_all_categories()

    for ls in cats:

        constants.IMAGE_CATEGORY_MAP[ls['category_name']] = int(ls['category_id'])

    NYAA2_LOGGER.info("Loading cogs")

    # read the list of cogs pre-defined in config.py
    for i in config.get(("bot"), "cogs"):

        # import all cog classes from the file
        for cog_class in get_cog_classes(i):

            try:

                NYAA2_LOGGER.info(f"Loading {cog_class}")

                # create instance of the cog 
                instance = cog_class(bot)

                # register instance with the bot
                asyncio.ensure_future(bot.add_cog(instance))

                # add to loaded cogs 
                config.set(("bot", "loaded_cogs"), i, instance)

            except Exception as e:

                NYAA2_LOGGER.error(e)


    NYAA2_LOGGER.info("Running event loop")

    try:
        # run main event loop 
        # await bot.start(config.get(("bot"), "token"))
        loop.run_until_complete(bot.start(config.get(("bot"), "token")))

    except KeyboardInterrupt:
        NYAA2_LOGGER.error("Keyboard Interrupt")
        asyncio.ensure_future(bot.close())

    NYAA2_LOGGER.info("Shutting down databases")

    n_database.DiscordEventDB.get_instance().close()
    n_database.DiscordLogDB.get_instance().close() 
    n_database.MediaUrlDB.get_instance().close()
    n_database.MiscDB.get_instance().close()
