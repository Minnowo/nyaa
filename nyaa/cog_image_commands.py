
from ast import alias
import itertools
from posixpath import abspath
import traceback
import discord
import asyncio
import sys
from discord import embeds 
import requests
import os 
import hentai_dl
import random 
import json 

from discord.ext import commands
from discord.ext.commands import has_permissions
from requests.utils import requote_uri

from . import constants
from . import constant_media
from . import util 


CONFIG_FORMAT = "config\\sauce\\{0}\\{0}_lines.json"
LINKS_SFW_FORMAT = "config\\sauce\\{0}\\{0}_links_sfw.txt"
LINKS_NSFW_FORMAT = "config\\sauce\\{0}\\{0}_links_nsfw.txt"

LINK_FILE_END   = "--links-end--"

MODULES = ["appleworm", "bondage", "cutegirls", "feet", "femboy", "fubuki", "gura", "hutao", 
           "kemonomimi", "mori", "navel", "okayu", "panties", "pekora", "rushia", "suisei", "thighs", "witch"]

SAUCE_MAP = { }

class ImageCommands(commands.Cog):
    """ """

    nyaa_cog = True
    

    def __del__(self):
        
        for i in SAUCE_MAP:

            for ii in SAUCE_MAP[i]["handles"]:

                if SAUCE_MAP[i]["handles"][ii] is not None:
                    SAUCE_MAP[i]["handles"][ii].close()

            try:
                with open(SAUCE_MAP[i]["paths"]["config"], "w") as writer:
                    json.dump(SAUCE_MAP[i]["config"], writer, indent=5)

                print(f"Image config saved for '{i}'.")

            except Exception as e:
                print(f"Could not save config for '{i}' -> '{e}'")
    

    def __init__(self, bot):
        
        self.bot = bot 

        def write_file(filename, text):
            
            if isinstance(text, dict):
                with open(filename, "w") as w:
                    json.dump(text, w, indent=3)
                return 

            with open(filename, "w") as w:
                w.write(text)

        def load_config(path):
            try:
                with open(path, "r") as reader:
                    return json.load(reader)
            except:
                return {"nsfw" : 0, "sfw" : 0, "dnm" : False, "sfwo" : False}

        def load_link_file(path):
            try:
                return open(path, "r")
            except:
                return None 

        for i in MODULES:

            config_path     = CONFIG_FORMAT.format(i)
            links_sfw_path  = LINKS_SFW_FORMAT.format(i)
            links_nsfw_path = LINKS_NSFW_FORMAT.format(i)

            SAUCE_MAP[i] = {}
            SAUCE_MAP[i]["paths"] = {}
            SAUCE_MAP[i]["paths"]["config"]      = config_path
            SAUCE_MAP[i]["paths"]["links-sfw"]   = links_sfw_path
            SAUCE_MAP[i]["paths"]["links-nsfw"]  = links_nsfw_path

            SAUCE_MAP[i]["handles"] = {}           # file handles
            SAUCE_MAP[i]["handles"]["sfw"] = None  # sfw links
            SAUCE_MAP[i]["handles"]["nsfw"] = None # nsfw links

            SAUCE_MAP[i]["config"] = {"nsfw" : 0, "sfw" : 0 }

            if not os.path.isdir(os.path.dirname(config_path)):
                
                os.makedirs(os.path.dirname(config_path), exist_ok=True)

                write_file(config_path, SAUCE_MAP[i]["config"])
                write_file(links_sfw_path , "\n" + LINK_FILE_END)
                write_file(links_nsfw_path, "\n" + LINK_FILE_END)
                continue
            

            if not os.path.isfile(config_path):
                write_file(config_path, SAUCE_MAP[i]["config"])

            else:
                SAUCE_MAP[i]["config"] = load_config(config_path)


            if not os.path.isfile(links_sfw_path):
                write_file(links_sfw_path , "\n" + LINK_FILE_END)

            else:
                handle = load_link_file(links_sfw_path) 
                
                if handle is not None:

                    for ii in range(SAUCE_MAP[i]["config"]["sfw"]):
                        line = handle.readline().strip()
                        
                        if line == LINK_FILE_END:
                            SAUCE_MAP[i]["config"]["sfw"] = 0
                            handle.seek(0)
                            break 
                        
                    SAUCE_MAP[i]["handles"]["sfw"] = handle


            if not os.path.isfile(links_nsfw_path):
                write_file(links_nsfw_path , "\n" + LINK_FILE_END)

            else:
                
                handle = load_link_file(links_nsfw_path) 
                
                if handle is not None:

                    for ii in range(SAUCE_MAP[i]["config"]["nsfw"]):
                        line = handle.readline().strip()

                        if line == LINK_FILE_END:
                            SAUCE_MAP[i]["config"]["nsfw"] = 0
                            handle.seek(0)
                            break 
                        
                    SAUCE_MAP[i]["handles"]["nsfw"] = handle


    async def cog_command_error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('This command can not be used in Private Messages.')
            except discord.HTTPException:
                pass

    def get_url(self, handle, conf, config_key, retries = 5):

        tries = 0
        lines = 0

        try:

            while tries != retries:
                
                lines += 1
                tries += 1

                line = handle.readline().strip()

                if line.startswith("http"):
                    return line 

                if line == LINK_FILE_END:
                    lines = 0
                    handle.seek(0)
                    conf["config"][config_key] = 0 

            return None 

        finally:
            
            conf["config"][config_key] += lines 

    async def send_image_embed(self, ctx, url):
        embed = discord.Embed(color = constants.EMBED_COLOR)
        embed.set_image(url = url)
        await ctx.send(embed=embed)

    async def handle_nsfw(self, ctx, mod):

        if mod["handles"]["nsfw"] is None:
            await ctx.send("Could not load config file.")
            return 

        url = self.get_url(mod["handles"]["nsfw"], mod, "nsfw")

        if url is None:
            await ctx.send("There is no media for channel type NSFW.")
            return 
        
        await self.send_image_embed(ctx, url) 

    async def handle_sfw(self, ctx, mod):

        if mod["handles"]["sfw"] is None:
            await ctx.send("Could not load config file.")
            return 

        url = self.get_url(mod["handles"]["sfw"], mod, "sfw")
        
        if url is None:
            await ctx.send("There is no media for channel type SFW.")
            return 
        
        await self.send_image_embed(ctx, url)

    async def image_embed(self, ctx, key, requested_type = None):

        mod = SAUCE_MAP[key]
        isNSFW = ctx.channel.is_nsfw()

        if requested_type is not None:
            
            if requested_type == "nsfw":
                
                if not isNSFW:
                    await ctx.send("NSFW channel is required for NSFW content.")
                    return 

                await self.handle_nsfw(ctx, mod)
                return 

            elif requested_type == "sfw":
                await self.handle_sfw(ctx, mod)
                return 
                

        if isNSFW:
            await self.handle_nsfw(ctx, mod)
            return 

        await self.handle_sfw(ctx, mod)
        


    @commands.command(name = "loli", aliases=['isloli'])
    async def _isloli(self, ctx):
        await self.send_image_embed(ctx, "https://cdn.discordapp.com/attachments/942174974754566204/942302273516748860/the_difference_between_loli_and_petite.png")

    @commands.command(name = "awoo", aliases=['awooo'])
    async def _awooo(self, ctx):
        await self.send_image_embed(ctx, random.choice(constant_media.AWOO_SET))

    @commands.command(name = "bonk")
    async def _bonk(self, ctx):
        await self.send_image_embed(ctx, "https://cdn.discordapp.com/attachments/942174974754566204/942293277485445160/02018.jpg")


    
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
    async def _kemonomimi(self, ctx):
        await self.image_embed(ctx, 'kemonomimi', 'nsfw')

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

