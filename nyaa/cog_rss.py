
import traceback
import discord

import sys 

from discord.ext import commands

from . import threaded_queue
from . import rss_handler
from . import regex
from . import util
from . import constants

class RSS(commands.Cog):
    """ cogs for handling RSS content sent from webhooks"""

    nyaa_cog = True

    def __init__(self, bot) -> None:
        
        self.bot = bot
        self.worker_queue  = threaded_queue.WorkerQueue(rss_handler.RSSHandler.get_instance().handle_discord_message)
        threaded_queue.active_threads["rss"] = self.worker_queue


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
