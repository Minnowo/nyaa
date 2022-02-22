

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
# from . import cog_user_join_message
# from . import cog_reaction_roles
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



def main():
    os.system("") # enable console color on windows 

    # print(f"HEADER    : {constants.bcolors.HEADER}test{constants.bcolors.ENDC}")
    # print(f"OKBLUE    : {constants.bcolors.OKBLUE}test{constants.bcolors.ENDC}")
    # print(f"OKCYAN    : {constants.bcolors.OKCYAN}test{constants.bcolors.ENDC}")
    # print(f"OKGREEN   : {constants.bcolors.OKGREEN}test{constants.bcolors.ENDC}")
    # print(f"WARNING   : {constants.bcolors.WARNING}test{constants.bcolors.ENDC}")
    # print(f"FAIL      : {constants.bcolors.FAIL}test{constants.bcolors.ENDC}")
    # print(f"BOLD      : {constants.bcolors.BOLD}test{constants.bcolors.ENDC}")
    # print(f"UNDERLINE : {constants.bcolors.UNDERLINE}test{constants.bcolors.ENDC}")
    # return 
    print("\nstarting bot:")
    print("loading bot config...", end="", flush=True)

    # load configs 
    config.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), constants.BOT_CONFIG), "bot", True)

    print(constants.bcolors.OKGREEN + " Done." + constants.bcolors.ENDC)

    # get bot instance 
    bot = commands.Bot(command_prefix = config.get(("bot"), "prefix"), intents=discord.Intents.all())
    bot.remove_command('help') # remove help command ;3c

    # make bot instance global through the config 
    config.set(("bot"), "instance", bot)

    print("loading cogs...")
    
    # read the list of cogs pre-defined in config.py
    for i in config.get(("bot"), "cogs"):

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
                print(constants.bcolors.FAIL + "ERROR loading cog:")
                print(f"   {e}" + constants.bcolors.ENDC)

    print("\nrunning event loop...\n")    

    try:
        # run main event loop 
        loop = asyncio.get_event_loop()
        loop.run_until_complete(bot.start(config.get(("bot"), "token")))
    except KeyboardInterrupt:
        print(constants.bcolors.FAIL + "KeyboardInterrupt" + constants.bcolors.ENDC)

    # dispose any threaded queue used by any cogs
    for name, thread in threaded_queue.active_threads.items():
        print("ending thread:", name, end="", flush=True)
        thread.cleanup()
        print(constants.bcolors.OKGREEN + " Done." + constants.bcolors.ENDC)

    # delete any cog instances 
    loaded = config.get(("bot",), "loaded_cogs")
    for i in loaded:
        
        # call deconstructor for each cog
        loaded[i].__del__()
