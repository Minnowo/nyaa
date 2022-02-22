
import traceback
import discord

import sys 
import os 

from discord.ext import commands

from . import threaded_queue
from . import rss_handler
from . import regex
from . import util
from . import constants
from . import config 

class RSS(commands.Cog):
    """ cogs for handling RSS content sent from webhooks"""

    nyaa_cog = True

    config_path = None

    rss_channel_map = {

    }

    def __init__(self, bot) -> None:
        
        print(f"   Loading {constants.bcolors.WARNING}RSS{constants.bcolors.ENDC} ->", end="", flush=True)

        self.bot = bot

        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), constants.RSS_CONFIG)

        config.load(self.config_path, conf = self.rss_channel_map)
    
        util.replace_list_set(self.rss_channel_map)

        self.worker_queue  = threaded_queue.WorkerQueue(self.handle_discord_message)
        
        print(constants.bcolors.OKGREEN + " Done." + constants.bcolors.ENDC)


    def __del__(self):
        
        print("\nRSS Cog Closing:")

        self.worker_queue.cleanup()

        print("   Saving config... ->", end="", flush=True)

        config.save(self.config_path, conf = self.rss_channel_map)
        
        print(constants.bcolors.OKGREEN + " Done." + constants.bcolors.ENDC)


    async def cog_check(self, ctx):
        """A local check which applies to all commands in this cog."""
        
        if not ctx.guild:
            raise commands.NoPrivateMessage
        
        return True


    async def cog_command_error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('This command can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    
    def handle_discord_message(self, message : discord.message):

        if not message.guild:
            return

        i_server_id = message.guild.id
        s_server_id = str(message.guild.id)
        channel_id = message.channel.id

        if s_server_id not in self.rss_channel_map:
            return 

        if channel_id not in self.rss_channel_map[s_server_id]:
            return

        links = set()
        
        for i in regex.MATCH_RE_DISCORD_LINK.findall(message.content):
            links.add(i)

        for i in message.attachments:
            links.add(i.url)

        if links:
            with open("config\\links.txt", "a") as writer:
                
                for i in links:
                    print("adding " + i)    
                    writer.write(i.strip() + "\n")

        # print("message recieved for channel")


    @commands.command(name='subs', aliases=['subscribed'])
    async def listsubs_(self, ctx, *, _):
        
        embed = discord.Embed(color = constants.EMBED_COLOR)
        
        for server_id in rss_handler.RSSHandler.rss_channel_map:
            for channel_id in rss_handler.RSSHandler.rss_channel_map[server_id]:

                server = self.bot.get_guild(server_id)

                if not server:
                    continue

                channel = server.get_channel(channel_id)

                if not channel:
                    continue

                embed.add_field(name = str(channel_id), 
                                value = 'name: {0}\nserver: {1}'.format(channel.name, channel.guild.name), inline=False)

        await ctx.send(embed = embed)


    @commands.command(name='rss')
    async def subscribe_(self, ctx, channel : str = None):
        print("subscribing to channel")

        if not ctx.guild:
            return

        if not channel:
            if rss_handler.RSSHandler.instance.subscribe_channel(ctx.guild.id, ctx.channel.id):
                await ctx.send("successfully subscribed to the channel")
                return 

            await ctx.send("could not subscribe to the channel")
            return 

        if isinstance(channel, str):
        
            m = regex.PARSE_CHANNEL_MENTION.search(channel)
        
            if m:
                channel = util.parse_int(m.group(1))

            else:
                channel = util.parse_int(channel, None)

                if not channel:
                    await ctx.send("invalid channel")
                    return

        if isinstance(channel, int):
            id = channel

            channel = self.bot.get_channel(id)
            
            if not channel:
                await ctx.send(f"cannot find channel with given id: {id}")
                return 

            if rss_handler.RSSHandler.instance.subscribe_channel(ctx.guild.id, channel.id):
                await ctx.send("successfully subscribed to the channel")
                return 

        await ctx.send("could not subscribe to the channel")


    @commands.Cog.listener()
    async def on_message(self, message):
        """process messages from the rss feed"""
        
        self.worker_queue.enqueue(message)
