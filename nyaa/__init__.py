

import discord
import os.path

import os 
import asyncio

from discord.ext import commands
from discord.ext.commands import has_permissions

from . import constants
from . import config
from . import util
from . import threaded_queue
from . import cog_user_join_message
from . import cog_reaction_roles
from . import rss_handler
from . import file_handler

def get_cog_classes(name):
    """gets all cog classes"""

    module = __import__(name, globals(), None, (), 1)

    return [
        cls for cls in module.__dict__.values() 
        if (
            hasattr(cls, "nyaa_cog") and cls.__module__ == module.__name__
        )
    ]


def load_configs():
    config.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), constants.BOT_CONFIG), "bot", True)
    config.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), constants.CONFIG_FILE))
    # config.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "doujin_cache.json"), "doujin_cache")
    config.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), constants.RSS_CONFIG), conf = rss_handler.RSSHandler.rss_channel_map)
    config.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), constants.LEAVE_JOIN_CONFIG), conf = cog_user_join_message.LeaveJoinMessage.event_map)

    util.replace_list_set(rss_handler.RSSHandler.rss_channel_map)
    util.replace_list_set(cog_user_join_message.LeaveJoinMessage.event_map)

def save_configs():
    # config.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "conf.json"))
    # config.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "doujin_cache.json"), "doujin_cache")
    config.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), constants.RSS_CONFIG), conf = rss_handler.RSSHandler.rss_channel_map)
    config.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), constants.LEAVE_JOIN_CONFIG), conf = cog_user_join_message.LeaveJoinMessage.event_map)
    config.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), constants.REACTION_ROLES_CONFIG), conf = cog_reaction_roles.ReactionRoles.reaction_roles_data)
    config.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), constants.THIGH_CONFIG), conf = cog_reaction_roles.ReactionRoles.reaction_roles_data)

def main():
    
    print("\nstarting bot:")
    print("loading configs...")
    load_configs()

    bot = commands.Bot(command_prefix = config.get(("bot"), "prefix"), intents=discord.Intents.all())
    bot.remove_command('help')

    config.set(("bot"), "instance", bot)

    print("loading cogs...")
    print("====================================")
    
    for i in config.get(("bot"), "cogs"):
        print("loading cog:", i)

        for ii in get_cog_classes(i):

            instance = ii(bot)
            bot.add_cog(instance)

            config.set(("bot", "loaded_cogs"), i, instance)

    print("====================================")
    print("\nrunning event loop...\n")    

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(bot.start(config.get(("bot"), "token")))
    except KeyboardInterrupt:
        print("KeyboardInterrupt")

    for name, thread in threaded_queue.active_threads.items():
        print("ending thread:", name)
        thread.cleanup()

    print("saving configs")
    save_configs()

    print("closing file handles")
    file_handler.FileHandler.get_instance().deinit_file_handles()
