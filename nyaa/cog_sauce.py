
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

from discord.ext import commands
from discord.ext.commands import has_permissions
from requests.utils import requote_uri

from . import constants
from . import util 
from . import file_handler

class Sauce(commands.Cog):
    """ """

    thigh_file  = {"line" : 0, "file" : None }
    server_lock = {}

    file_instance = None 

    nyaa_cog = True

    def __init__(self, bot):
        
        self.file_instance = file_handler.FileHandler.get_instance()
        self.file_instance.init_file_handles()
        
    def _save_file(self, file, key):
        try:
            print(f"Saving '{key}' line count: {str(self.file_instance.file_map[key]['line'])}")

            with open(file, "w")  as writer:
                writer.write(str(self.file_instance.file_map[key]["line"]))

        except Exception as e :
            print(f"Cannot save '{key}'-> {e}")

    async def cog_command_error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('This command can not be used in Private Messages.')
            except discord.HTTPException:
                pass

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    async def image_embed(self, ctx, url):
        embed = discord.Embed(color = constants.EMBED_COLOR)
        embed.set_image(url = url)
        await ctx.send(embed=embed)

    async def _specific_sauce(self, ctx, link, config, key):

        thigh = self.file_instance.file_map[key]

        if not thigh["open"] or thigh["handle"] is None:
            await ctx.send("Config could not be loaded.")
            return 

        url = thigh["handle"].readline()

        if url:
            thigh["line"] += 1

            embed = discord.Embed(color = constants.EMBED_COLOR)
            embed.set_image(url = url)
            await ctx.send(embed=embed)

            if thigh["line"] % 10 == 0:
                self._save_file(config, key)

            return 

        thigh["line"] = 0
        thigh["handle"].close()

        try:
            thigh["handle"] = open(link)
            await self._specific_sauce(ctx, link, config, key)
        except:
            thigh["handle"] = None 
            thigh["open"]   = False


    @commands.command(name = "thighs", aliases=['thigh'])
    async def _thighs(self, ctx):
        if not ctx.channel.is_nsfw():
            await self._bonk(ctx)
            await ctx.send("This channel is not NSFW")
            return 
        await self._specific_sauce(ctx, constants.THIGH_LINKS, constants.THIGH_CONFIG, constants.THIGH_KEY) 

    @commands.command(name = "girl", aliases=['cutegirl'])
    async def _girl(self, ctx):
        await self._specific_sauce(ctx, constants.CUTE_GIRLS_MOE_LINKS, constants.CUTE_GIRLS_MOE_CONFIG, constants.CUTE_GIRLS_MOE_KEY) 

    @commands.command(name = "feet")
    async def _feet(self, ctx):
        if not ctx.channel.is_nsfw():
            await self._bonk(ctx)
            await ctx.send("This channel is not NSFW")
            return 
        await self._specific_sauce(ctx, constants.FEET_LINKS, constants.FEET_CONFIG, constants.FEET_KEY) 

    @commands.command(name = "kemo", aliases=['kemonomimi', 'neko'])
    async def _neko(self, ctx):
        if not ctx.channel.is_nsfw():
            await self._bonk(ctx)
            await ctx.send("This channel is not NSFW")
            return 
        await self._specific_sauce(ctx, constants.KEMONOMIMI_LINKS, constants.KEMONOMIMI_CONFIG, constants.KEMONOMIMI_KEY) 

    @commands.command(name = "loli", aliases=['isloli'])
    async def _isloli(self, ctx):
        await self.image_embed(ctx, "https://cdn.discordapp.com/attachments/942174974754566204/942302273516748860/the_difference_between_loli_and_petite.png")

    @commands.command(name = "awoo", aliases=['awooo'])
    async def _awooo(self, ctx):
        await self.image_embed(ctx, "https://cdn.discordapp.com/attachments/942174974754566204/942287252132859994/01101.jpg")
        
    @commands.command(name = "bonk")
    async def _bonk(self, ctx):
        await self.image_embed(ctx, "https://cdn.discordapp.com/attachments/942174974754566204/942293277485445160/02018.jpg")

    async def get_sauce_meta(self, sauce, use_api, full=False, limit=-1):

        if not use_api or use_api.lower() in ("true","yes","y","t","1","+"):
            use_api = True 
        else:
            use_api = False 

        if not sauce:
            sauce = util.get_nhentai_random()
 
        else:
            nid = util.parse_int(sauce, None)

            # if the given sauce is an int, assume nhentai id
            # otherwise it is assumed a url
            if nid is not None:
                sauce = "https://nhentai.net/g/" + str(nid)

        hentai_dl.config.set((), "use-api", use_api)
        extractor = hentai_dl.extractor.find(sauce)

        if not extractor:
            return None, sauce

        url = sauce

        c = 0
        for i in extractor:
            # first element is always metadata
            if c == 0:
                metadata = i[1]
                c += 1
            # second element is always the first image url
            elif c == 1:
                if full:
                    metadata["urls"] = [i[1]]
                    c += 1

                else:
                    metadata["__thumb_url"] = i[1]
                    break 

            else:
                metadata["urls"].append(i[1])
                c += 1

                if c > limit:
                    break

        
        return metadata, url


    @commands.command(name = "sauce_page")
    async def sauce_page_(self, ctx, sauce : str = None, page : str = None, use_api : str = None):
        
        page = util.parse_int(page, None)

        if not page:
            await ctx.send("invalid page")
            return

        metadata, url = await self.get_sauce_meta(sauce, use_api, True, page)

        if not metadata:
            await ctx.send("could not find extractor for given sauce")
            return

        embed = discord.Embed(color = constants.EMBED_COLOR)
        embed.set_image(url = metadata["urls"][-1])

        await ctx.send(embed=embed)


    @commands.command(name = "sauce_urls")
    async def sauce_urls_(self, ctx, sauce : str = None, limit : str = None, use_api : str = None):
        
        if not ctx.guild:
            # not gonna allow this command in dms because of the server lock
            raise commands.NoPrivateMessage()

        server_id = str(ctx.guild.id)

        if self.server_lock.get(server_id, False):
            await ctx.send("server lock. must wait until the other sauce url command is finished")
            return

        limit = util.parse_int(limit, 30)
        if limit > 30:
            limit = 30
        metadata, url = await self.get_sauce_meta(sauce, use_api, True, limit)

        if not metadata:
            await ctx.send("could not find extractor for given sauce")
            return

        self.server_lock[str(ctx.guild.id)] = True 

        c = 0
        i = 0
        buffer = []
        delay = len(metadata['urls']) / 100

        while i < len(metadata['urls']):

            if len(buffer) == 4:
                await ctx.send("\n".join(buffer))
                await asyncio.sleep(1 + delay)
                buffer = []

            buffer.append(metadata['urls'][i])
            c += 1
            i += 1

        await ctx.send("\n".join(buffer))
        await asyncio.sleep(1 + delay)

        self.server_lock[str(ctx.guild.id)] = False 
            


    @commands.command(name = "sauce")
    async def sauce_(self, ctx, sauce : str = None, use_api : str = None):
        
        metadata, url = await self.get_sauce_meta(sauce, use_api, False)

        if not metadata:
            await ctx.send("could not find extractor for given sauce")
            return
       
        embed = discord.Embed(color = constants.EMBED_COLOR, title=metadata.get("title", "----"))

        embed.add_field(name="URL", value = requote_uri(url), inline=False)

        if "artists" in metadata and len(metadata["artists"]) > 0:
            embed.add_field(name="Artists", value=", ".join(metadata["artists"]))
        else :
            embed.add_field(name="Artists", value="None")
        
        if "languages" in metadata and len(metadata["languages"]) > 0:   
            embed.add_field(name="Languages", value=", ".join(metadata["languages"]))
        else:
            embed.add_field(name="Languages", value="None")

        if "count" in metadata:
            embed.add_field(name="Page / Gallery Count", value=metadata['count'])

        if "tags" in metadata and len(metadata["tags"]) > 0:
            embed.add_field(name="Tags", value=", ".join(metadata["tags"]), inline=False)
        else:
            embed.add_field(name="Tags", value="None", inline=False)

        if "__thumb_url" in metadata:
            embed.set_image(url = metadata["__thumb_url"])

        if "date" in metadata:
            embed.set_footer(text="Uploaded: {}".format(metadata['date']))

        await ctx.send(embed=embed)
