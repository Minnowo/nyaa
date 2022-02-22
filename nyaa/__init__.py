

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

# reads the given file and searches for any class with the 'nyaa_cog' member and returns it
# this is used to import the cogs without using the builtin function because its bad 
def get_cog_classes(name):
    """gets all cog classes"""

    module = __import__(name, globals(), None, (), 1)

    return [
        cls for cls in module.__dict__.values() 
        if (
            hasattr(cls, "nyaa_cog") and cls.__module__ == module.__name__
        )
    ]


# loads the config files for the cogs and bot information
def load_configs():

    # config for bot information (prefix, token)
    config.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), constants.BOT_CONFIG), "bot", True)

    # config for rss channels (poorly names cause i kinda gave up on it so now its just a listener basically)
    config.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), constants.RSS_CONFIG), conf = rss_handler.RSSHandler.rss_channel_map)

    # config for user leave / join cog 
    config.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), constants.LEAVE_JOIN_CONFIG), conf = cog_user_join_message.LeaveJoinMessage.event_map)

    # these cogs use set() instead of list() so convert all list to set
    util.replace_list_set(rss_handler.RSSHandler.rss_channel_map)
    util.replace_list_set(cog_user_join_message.LeaveJoinMessage.event_map)

# save config files
def save_configs():

    config.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), constants.RSS_CONFIG), conf = rss_handler.RSSHandler.rss_channel_map)
    config.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), constants.LEAVE_JOIN_CONFIG), conf = cog_user_join_message.LeaveJoinMessage.event_map)
    config.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), constants.REACTION_ROLES_CONFIG), conf = cog_reaction_roles.ReactionRoles.reaction_roles_data)

def main():
    
    print("\nstarting bot:")
    print("loading configs...")

    # load configs 
    load_configs()

    # get bot instance 
    bot = commands.Bot(command_prefix = config.get(("bot"), "prefix"), intents=discord.Intents.all())
    bot.remove_command('help') # remove help command ;3c

    # make bot instance global through the config 
    config.set(("bot"), "instance", bot)

    print("loading cogs...")
    print("====================================")
    
    # read the list of cogs pre-defined in config.py
    for i in config.get(("bot"), "cogs"):
        print("loading cog:", i)

        # import all cog classes from the file
        for ii in get_cog_classes(i):
            try:
                # create instance of the cog 
                instance = ii(bot)

                # register instance with the bot
                bot.add_cog(instance)

                # add to loaded cogs 
                config.set(("bot", "loaded_cogs"), i, instance)
            except Exception as e:
                print(f"failed to load cog '{i}' -> {e}")

    print("====================================")
    print("\nrunning event loop...\n")    

    try:
        # run main event loop 
        loop = asyncio.get_event_loop()
        loop.run_until_complete(bot.start(config.get(("bot"), "token")))
    except KeyboardInterrupt:
        print("KeyboardInterrupt")

    # dispose any threaded queue used by any cogs
    for name, thread in threaded_queue.active_threads.items():
        print("ending thread:", name)
        thread.cleanup()

    print("saving configs")

    # save configs 
    save_configs()

    # delete any cog instances 
    loaded = config.get(("bot",), "loaded_cogs")
    for i in loaded:
        
        # call deconstructor for each cog
        loaded[i].__del__()
