
import discord
import os 
import random 
import json 
import traceback
import sys

from discord.ext import commands

from . import constants
from . import constant_media
from . import util 

# constants used
CONFIG_FORMAT = "config\\sauce\\{0}\\{0}_lines.json"
LINKS_SFW_FORMAT = "config\\sauce\\{0}\\{0}_links_sfw.txt"
LINKS_NSFW_FORMAT = "config\\sauce\\{0}\\{0}_links_nsfw.txt"

LINK_FILE_END   = "--links-end--"

MODULES = ["appleworm", "bondage", "cutegirls", "feet", "femboy", "fubuki", "gura", "hutao", 
           "kemonomimi", "mori", "navel", "okayu", "panties", "pekora", "rushia", "suisei", "thighs", "witch", "nyaa"]

SAUCE_MAP = { }

# cog responsible for handling image commands 
class ImageCommands(commands.Cog):

    # lets the __init__.py identify this as a cog 
    nyaa_cog = True 
    

    # on delete save all configs 
    def __del__(self):
        
        print("\nImageCommands Cog Closing:")

        for i in SAUCE_MAP:

            print(f"   Saving Module: {constants.bcolors.OKCYAN}{i}...{constants.bcolors.ENDC}  ->", end="", flush=True)

            # close all open file handles 
            for ii in SAUCE_MAP[i]["handles"]:

                if SAUCE_MAP[i]["handles"][ii] is not None:
                    SAUCE_MAP[i]["handles"][ii].close()

            try:
                # write config for the module
                with open(SAUCE_MAP[i]["paths"]["config"], "w") as writer:
                    json.dump(SAUCE_MAP[i]["config"], writer, indent=5)

                print(constants.bcolors.OKGREEN + " Done" + constants.bcolors.ENDC)

            except Exception as e:
                print(constants.bcolors.FAIL + f" {e}" + + constants.bcolors.ENDC)
    

    def __init__(self, bot):
        
        print(f"   Loading {constants.bcolors.WARNING}ImageCommands{constants.bcolors.ENDC} ->", end="", flush=True)

        self.bot = bot 

        # lambda only used here 
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

        # build the SAUCE_MAP 
        for i in MODULES:

            config_path     = CONFIG_FORMAT.format(i)
            links_sfw_path  = LINKS_SFW_FORMAT.format(i)
            links_nsfw_path = LINKS_NSFW_FORMAT.format(i)

            SAUCE_MAP[i] = {}                                         # create new dict for module 
            SAUCE_MAP[i]["paths"] = {}                                # create path sub dict
            SAUCE_MAP[i]["paths"]["config"]      = config_path        # set config path
            SAUCE_MAP[i]["paths"]["links-sfw"]   = links_sfw_path     # set sfw links path
            SAUCE_MAP[i]["paths"]["links-nsfw"]  = links_nsfw_path    # set nsfw links path

            SAUCE_MAP[i]["handles"] = {}           # file handles
            SAUCE_MAP[i]["handles"]["sfw"] = None  # sfw links
            SAUCE_MAP[i]["handles"]["nsfw"] = None # nsfw links

            SAUCE_MAP[i]["config"] = {"nsfw" : 0, "sfw" : 0 }   # default config

            # if not module config folder exists create all files and continue 
            if not os.path.isdir(os.path.dirname(config_path)):
                
                os.makedirs(os.path.dirname(config_path), exist_ok=True)

                write_file(config_path, SAUCE_MAP[i]["config"])
                write_file(links_sfw_path , "\n" + LINK_FILE_END)
                write_file(links_nsfw_path, "\n" + LINK_FILE_END)
                continue
            
            # no config found write default 
            if not os.path.isfile(config_path):
                write_file(config_path, SAUCE_MAP[i]["config"])

            # read existing config 
            else:
                SAUCE_MAP[i]["config"] = load_config(config_path)


            # no sfw links file found, write default
            if not os.path.isfile(links_sfw_path):
                write_file(links_sfw_path , "\n" + LINK_FILE_END)

            # set file handle for existing sfw links
            else:
                handle = load_link_file(links_sfw_path) 
                
                if handle is not None:
                    
                    # seek to the line saved in the config  (1 url per line)
                    for ii in range(SAUCE_MAP[i]["config"]["sfw"]):
                        line = handle.readline().strip()
                        
                        # end of file, seek to start
                        if line == LINK_FILE_END:
                            SAUCE_MAP[i]["config"]["sfw"] = 0
                            handle.seek(0)
                            break 
                    
                    # set the handle
                    SAUCE_MAP[i]["handles"]["sfw"] = handle


            # no nsfw links file found, write default
            if not os.path.isfile(links_nsfw_path):
                write_file(links_nsfw_path , "\n" + LINK_FILE_END)

            # set file handles for existing nsfw links
            else:
                
                handle = load_link_file(links_nsfw_path) 
                
                if handle is not None:
                    
                    # seek to line saved in config
                    for ii in range(SAUCE_MAP[i]["config"]["nsfw"]):
                        line = handle.readline().strip()

                        # end of file, seek to start
                        if line == LINK_FILE_END:
                            SAUCE_MAP[i]["config"]["nsfw"] = 0
                            handle.seek(0)
                            break 
                    
                    # set the handle
                    SAUCE_MAP[i]["handles"]["nsfw"] = handle
        
        print(constants.bcolors.OKGREEN + " Done" + constants.bcolors.ENDC)


    async def cog_command_error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        
        # if any commands raise NoPrivateMessage error, it will be delt with here 
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('This command can not be used in Private Messages.')
            except discord.HTTPException:
                pass

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

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



    # sends and iamge embed 
    async def send_image_embed(self, ctx, url):
        """sends a discord emebd with an image set to the given url"""
        embed = discord.Embed(color = constants.EMBED_COLOR)
        embed.set_image(url = url)
        await ctx.send(embed=embed)


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
    @commands.command(name = "loli", aliases=['isloli'])
    async def _isloli(self, ctx):
        # send loli diagram
        await self.send_image_embed(ctx, constant_media.DIF_BETWEEN_LOLI_AND_SMOL)

    @commands.command(name = "awoo", aliases=['awooo'])
    async def _awooo(self, ctx):
        # send random awoo content
        await self.send_image_embed(ctx, random.choice(constant_media.AWOO_SET))

    @commands.command(name = "bonk")
    async def _bonk(self, ctx):
        # send bonk
        await self.send_image_embed(ctx, "https://cdn.discordapp.com/attachments/942174974754566204/942293277485445160/02018.jpg")

   

    

    # module commands go here,
    # since its not possible to register commands in a cog without using the decorator,
    # i'm just adding the command for each module myself instead of in a config somewhere else

    # currently just forcing 'sfw' or 'nsfw' content for each command cause i don't have time to sort through it all
    
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

