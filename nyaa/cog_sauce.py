
import traceback
import discord
import asyncio
import sys
import datetime

# handles metadata / content for sauce see -> https://github.com/Minnowo/hentai-dl
import hentai_dl

from discord.ext import commands
from requests.utils import requote_uri

from . import constants
from . import util 

class Sauce(commands.Cog):
    """ """

    # locks a server while sauce_urls command is running for it
    server_lock = {}

    nyaa_cog = True

    def __del__(self):
        pass 
    
    def __init__(self, bot):
        
        self.bot = bot 
    

    async def cog_check(self, ctx):
        """A local check which applies to all commands in this cog."""
        
        if not ctx.channel.is_nsfw():
            raise commands.NSFWChannelRequired(ctx.channel.name)
        
        return True

        

    async def cog_command_error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        
        # handle nsfw filter
        if isinstance(error, commands.NSFWChannelRequired):
            try:
                return await ctx.send("NSFW channel is required.")
            except discord.HTTPException:
                pass 

        # if command raises NoPrivateMessage it will be handled here
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('This command can not be used in Private Messages.')
            except discord.HTTPException:
                pass

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    # gets metadata for given sauce url
    async def get_sauce_meta(self, sauce, use_api, full=False, limit=-1):

        # not using a bool cause idk???
        # use api if user wants that pretty sure default
        if not use_api or use_api.lower() in ("true","yes","y","t","1","+"):
            use_api = True 

        else:
            use_api = False 

        # no sauce get nhentai random
        if not sauce:
            sauce = util.get_nhentai_random()
 
        # parse int, assuming nhentai code
        else:
            nid = util.parse_int(sauce, None)

            # if the given sauce is an int, assume nhentai id
            # otherwise it is assumed a url
            if nid is not None:
                sauce = "https://nhentai.net/g/" + str(nid)

        # register using api 
        hentai_dl.config.set((), "use-api", use_api)

        # search for extractor for the given sauce
        extractor = hentai_dl.extractor.find(sauce)

        # if not found doesn't support given url
        if not extractor:
            return None, sauce

        # extractor found, set the url and get the metadata
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

            # api returns timestamp not string
            timestamp = util.parse_int(metadata['date'], None)

            if timestamp is None:
                embed.set_footer(text="Uploaded: {}".format(metadata['date']))

            else:
                embed.set_footer(text="Uploaded: {}".format(datetime.datetime.fromtimestamp(timestamp)))

        await ctx.send(embed=embed)
