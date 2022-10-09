
import discord
import os 
import random 
import json 
import traceback
import sys

from discord.ext import commands

from .. import constants
from .. import util 

# constants used
CONFIG_FORMAT = "config\\sauce\\{0}\\{0}_lines.json"
LINKS_SFW_FORMAT = "config\\sauce\\{0}\\{0}_links_sfw.txt"
LINKS_NSFW_FORMAT = "config\\sauce\\{0}\\{0}_links_nsfw.txt"

LINK_FILE_END   = "--links-end--"

MODULES = ["appleworm", "bondage", "cutegirls", "feet", "femboy", "fubuki", "gura", "hutao", 
           "kemonomimi", "mori", "navel", "okayu", "panties", "pekora", "rushia", "suisei", 
           "thighs", "witch", "nyaa", "ranni", "laplus", "subaru", "baelz"]

SAUCE_MAP = { }

from .cog_base import BaseNyaaCog

# cog responsible for handling image commands 
class ImageCommands(BaseNyaaCog):

    IMAGE_COMMANDS_LOGGER = util.get_logger(*constants.IMAGE_COMMANDS_LOGGER)

    def __init__(self, bot):
        BaseNyaaCog.__init__(self, bot)
        self.logger = self.IMAGE_COMMANDS_LOGGER


    async def cog_command_error(self, ctx, error):
        
        if isinstance(error, commands.NoPrivateMessage):

            return await self.send_message_wrapped(ctx, 'This command can not be used in Private Messages.')

        self.logger.error('Ignoring exception in command {}:'.format(ctx.command))
        self.logger.error(error)



    # used to read a new url from the given file
    def get_url(self, handle, conf, config_key, retries = 5):
        """ 
            handle     : the open file handle
            conf       : config dict for the file (contains line number for each file)
            config_key : the key to be used in the config to access the correct file numbers
            retries    : the number of tries until assuming bad config 
        """
        tries = 0
        lines = 0

        try:

            while tries != retries:
                
                lines += 1
                tries += 1

                # read a line from the file
                line = handle.readline().strip()

                # is http url, return it
                if line.startswith("http"):
                    return line 

                # end of file, reset to line 1 and keep trying
                if line == LINK_FILE_END:
                    lines = 0
                    handle.seek(0)
                    conf["config"][config_key] = 0 

            return None 

        finally:
            # update the line number in the config
            conf["config"][config_key] += lines 


    # handles the nsfw link file and sending content from it 
    async def handle_nsfw(self, ctx, mod):
        """mod is the module dict stored in SAUCE_MAP"""

        # check file handle
        if mod["handles"]["nsfw"] is None:
            await ctx.send("Could not load config file.")
            return 

        # try and get a url
        url = self.get_url(mod["handles"]["nsfw"], mod, "nsfw")

        # could not read link from file
        if url is None:
            await ctx.send("There is no media for channel type NSFW.")
            return 
        
        # url found, send image
        await self.send_image_embed(ctx, url) 



    # handles the nsfw link file and sending content from it
    async def handle_sfw(self, ctx, mod):
        """mod is the module dict stored in SAUCE_MAP"""

        # check file handle
        if mod["handles"]["sfw"] is None:
            await ctx.send("Could not load config file.")
            return 

        # try and get a url
        url = self.get_url(mod["handles"]["sfw"], mod, "sfw")
        
        # could not read link from file
        if url is None:
            await ctx.send("There is no media for channel type SFW.")
            return 
        
        # url found, send image
        await self.send_image_embed(ctx, url)




    # handles sending content for sfw and nsfw channels
    async def image_embed(self, ctx, key, requested_type = None):
        """
        key is the module name
        requested_type is the content type prefered 
        """

        # get module from config 
        mod = SAUCE_MAP.get(key, None)
        isNSFW = ctx.channel.is_nsfw()

        # check for bad config 
        if mod is None:
            print(f"Could not find module with name of '{key}'")
            await ctx.send("There has been an unexpected error.")
            return  

        # if there is a requested content type, deal with it
        if requested_type is not None:
            
            # wants nsfw content 
            if requested_type == "nsfw":
                
                # if the channel is sfw, do not send anything
                if not isNSFW:
                    await ctx.send("NSFW channel is required for NSFW content.")
                    return 

                # wants nsfw content in nsfw channel, all good send it 
                await self.handle_nsfw(ctx, mod)
                return 

            # wants sfw content 
            elif requested_type == "sfw":

                # no need for checks sfw can go anywhere 
                await self.handle_sfw(ctx, mod)
                return 
                

        # no content requested, send nsfw content for nsfw channel
        if isNSFW:
            await self.handle_nsfw(ctx, mod)
            return 

        # sfw channel send sfw content 
        await self.handle_sfw(ctx, mod)
        

    # fun / informative commands with little content stored in constant_media.py
    # @commands.command(name = "loli", aliases=['isloli'])
    # async def _isloli(self, ctx):
    #     # send loli diagram
    #     await self.send_image_embed(ctx, constant_media.DIF_BETWEEN_LOLI_AND_SMOL)

    # @commands.command(name = "awoo", aliases=['awooo'])
    # async def _awooo(self, ctx):
    #     # send random awoo content
    #     await self.send_image_embed(ctx, random.choice(constant_media.AWOO_SET))

    # @commands.command(name = "bonk")
    # async def _bonk(self, ctx):
    #     # send bonk
    #     await self.send_image_embed(ctx, "https://cdn.discordapp.com/attachments/942174974754566204/942293277485445160/02018.jpg")

   

    

    # module commands go here,
    # since its not possible to register commands in a cog without using the decorator,
    # i'm just adding the command for each module myself instead of in a config somewhere else

    # currently just forcing 'sfw' or 'nsfw' content for each command cause i don't have time to sort through it all
    
    @commands.command(name = "baelz", aliases = ["hakos", "hakosbaelz", "bae"])
    async def _bae(self, ctx):
        await self.image_embed(ctx, 'baelz', 'nsfw')

    @commands.command(name = "subaru")
    async def _subaru(self, ctx):
        await self.image_embed(ctx, 'subaru', 'sfw')

    @commands.command(name = "laplus", aliases=["la+"])
    async def _laplus(self, ctx):
        await self.image_embed(ctx, 'laplus', 'nsfw')

    @commands.command(name = "ranni")
    async def _ranni(self, ctx):
        await self.image_embed(ctx, 'ranni', 'nsfw')

    @commands.command(name = "nyaa", aliases=["nyah", "nya", "nyaaa", "nyaaaa", "nyaaaaa", "nyaaaaaa"])
    async def _nyaa(self, ctx):
        await self.image_embed(ctx, 'nyaa', 'sfw')

    @commands.command(name='appleworm', aliases=['worm'])
    async def _appleworm(self, ctx):
        await self.image_embed(ctx, 'appleworm', 'sfw')
    
    @commands.command(name='bondage', aliases=['bdsm'])
    async def _bondage(self, ctx):
        await self.image_embed(ctx, 'bondage', 'nsfw')
    
    @commands.command(name='cutegirls', aliases=['girl'])
    async def _cutegirls(self, ctx):
        await self.image_embed(ctx, 'cutegirls', 'sfw')
    
    @commands.command(name='feet', aliases=[])
    async def _feet(self, ctx):
        await self.image_embed(ctx, 'feet', 'nsfw')
    
    @commands.command(name='femboy', aliases=['trap'])
    async def _femboy(self, ctx):
        await self.image_embed(ctx, 'femboy', 'nsfw')

    @commands.command(name='fubuki', aliases=[])
    async def _fubuki(self, ctx):
        await self.image_embed(ctx, 'fubuki', 'nsfw')

    @commands.command(name='gura', aliases=[])
    async def _gura(self, ctx):
        await self.image_embed(ctx, 'gura', 'sfw')

    @commands.command(name='hutao', aliases=[])
    async def _hutao(self, ctx):
        await self.image_embed(ctx, 'hutao', 'nsfw')

    @commands.command(name='kemonomimi', aliases=['kemo', 'neko'])
    async def _kemonomimi(self, ctx, sfw : str = None):
        if sfw is None:
            await self.image_embed(ctx, 'kemonomimi')
        
        else:
            if len(sfw) >= 1:
                if sfw[0].lower() == "n":
                    await self.image_embed(ctx, 'kemonomimi', "nsfw")
                elif sfw[0].lower() == "s":
                    await self.image_embed(ctx, 'kemonomimi', "sfw")

    @commands.command(name='mori', aliases=['cali'])
    async def _mori(self, ctx):
        await self.image_embed(ctx, 'mori', 'sfw')

    @commands.command(name='navel', aliases=['stomach'])
    async def _navel(self, ctx):
        await self.image_embed(ctx, 'navel', 'nsfw')

    @commands.command(name='okayu', aliases=[])
    async def _okayu(self, ctx):
        await self.image_embed(ctx, 'okayu', 'nsfw')

    @commands.command(name='panties', aliases=['pantsu'])
    async def _panties(self, ctx):
        await self.image_embed(ctx, 'panties', 'nsfw')

    @commands.command(name='pekora', aliases=['peko'])
    async def _pekora(self, ctx):
        await self.image_embed(ctx, 'pekora', 'nsfw')

    @commands.command(name='rushia', aliases=[])
    async def _rushia(self, ctx):
        await self.image_embed(ctx, 'rushia', 'nsfw')

    @commands.command(name='suisei', aliases=['sui'])
    async def _suisei(self, ctx):
        await self.image_embed(ctx, 'suisei', 'nsfw')

    @commands.command(name='thighs', aliases=['thigh'])
    async def _thighs(self, ctx):
        await self.image_embed(ctx, 'thighs', 'nsfw')

    @commands.command(name='witch', aliases=[])
    async def _witch(self, ctx):
        await self.image_embed(ctx, 'witch', 'nsfw')

