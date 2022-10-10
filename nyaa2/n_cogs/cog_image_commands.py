
from discord.ext import commands

from .. import n_database as db
from .. import constants
from .. import util 

from .cog_base import BaseNyaaCog

# cog responsible for handling image commands 
class ImageCommands(BaseNyaaCog):

    IMAGE_COMMANDS_LOGGER = util.get_logger(*constants.IMAGE_COMMANDS_LOGGER)

    image_cache_sfw = { 

    }
    image_cache_nsfw = {

    }

    def __init__(self, bot):
        BaseNyaaCog.__init__(self, bot)
        self.logger = self.IMAGE_COMMANDS_LOGGER
        self.IMAGE_TABLE_INST = db.MediaUrlDB.get_instance()
        self.last_image = {"image_id":-1, "category_id" : -1}


    async def cog_command_error(self, ctx, error):
        
        if isinstance(error, commands.NoPrivateMessage):

            return await self.send_message_wrapped(ctx, 'This command can not be used in Private Messages.')

        self.logger.error('Ignoring exception in command {}:'.format(ctx.command))
        self.logger.error(error)


    def get_image(self, category_id, is_nsfw):

        if is_nsfw:

            if category_id not in self.image_cache_nsfw:
                
                self.image_cache_nsfw[category_id] = [] 

            if not self.image_cache_nsfw[category_id]:
                
                self.image_cache_nsfw[category_id].extend(image["image_url"] for image in self.IMAGE_TABLE_INST.get_images_with_rating(category_id, constants.IMAGE_CACHE_SIZE, True))

            if not self.image_cache_nsfw[category_id]:

                return 

            return self.image_cache_nsfw[category_id].pop()


        if category_id not in self.image_cache_sfw:
                
            self.image_cache_sfw[category_id] = [] 

        if not self.image_cache_sfw[category_id]:
            
            self.image_cache_sfw[category_id].extend(image["image_url"] for image in self.IMAGE_TABLE_INST.get_images_with_rating(category_id, constants.IMAGE_CACHE_SIZE, False))

        if not self.image_cache_sfw[category_id]:

            return 

        return self.image_cache_sfw[category_id].pop()

        

        

    # handles sending content for sfw and nsfw channels
    async def image_embed(self, ctx, key, requested_type):
        """
        key is the module name
        requested_type is the content type prefered 
        """
        
        isNSFW = ctx.channel.is_nsfw()

        if requested_type and requested_type.startswith("s"):
                
            isNSFW = False

        image = self.get_image(constants.IMAGE_CATEGORY_MAP[key], isNSFW)

        if image:
            
            await self.send_image_embed(ctx, image)

        else:

            await self.send_message_wrapped(ctx, "Could not find image")


    # module commands go here,
    # since its not possible to register commands in a cog without using the decorator,
    # i'm just adding the command for each module myself instead of in a config somewhere else

    # currently just forcin o content for each command cause i don't have time to sort through it all
    
    @commands.command(name = "baelz", aliases = ["hakos", "hakosbaelz", "bae"])
    async def _bae(self, ctx, sfw : str = None):
        await self.image_embed(ctx, 'baelz', sfw)

    @commands.command(name = "subaru")
    async def _subaru(self, ctx, sfw : str = None):
        await self.image_embed(ctx, 'subaru', sfw)

    @commands.command(name = "laplus", aliases=["la+"])
    async def _laplus(self, ctx, sfw : str = None):
        await self.image_embed(ctx, 'laplus', sfw)

    @commands.command(name = "ranni")
    async def _ranni(self, ctx, sfw : str = None):
        await self.image_embed(ctx, 'ranni', sfw)

    @commands.command(name = "nyaa", aliases=["nyah", "nya", "nyaaa", "nyaaaa", "nyaaaaa", "nyaaaaaa"])
    async def _nyaa(self, ctx, sfw : str = None):
        await self.image_embed(ctx, 'nyaa', sfw)

    @commands.command(name='appleworm', aliases=['worm'])
    async def _appleworm(self, ctx, sfw : str = None):
        await self.image_embed(ctx, 'appleworm', sfw)
    
    @commands.command(name='bondage', aliases=['bdsm'])
    async def _bondage(self, ctx, sfw : str = None):
        await self.image_embed(ctx, 'bondage', sfw)
    
    @commands.command(name='cutegirls', aliases=['girl'])
    async def _cutegirls(self, ctx, sfw : str = None):
        await self.image_embed(ctx, 'cutegirls', sfw)
    
    @commands.command(name='feet', aliases=[])
    async def _feet(self, ctx, sfw : str = None):
        await self.image_embed(ctx, 'feet', sfw)
    
    @commands.command(name='femboy', aliases=['trap'])
    async def _femboy(self, ctx, sfw : str = None):
        await self.image_embed(ctx, 'femboy', sfw)

    @commands.command(name='fubuki', aliases=[])
    async def _fubuki(self, ctx, sfw : str = None):
        await self.image_embed(ctx, 'fubuki', sfw)

    @commands.command(name='gura', aliases=[])
    async def _gura(self, ctx, sfw : str = None):
        await self.image_embed(ctx, 'gura', sfw)

    @commands.command(name='hutao', aliases=[])
    async def _hutao(self, ctx, sfw : str = None):
        await self.image_embed(ctx, 'hutao', sfw)

    @commands.command(name='kemonomimi', aliases=['kemo', 'neko'])
    async def _kemonomimi(self, ctx, sfw : str = None):
        await self.image_embed(ctx, 'kemonomimi', sfw)

    @commands.command(name='mori', aliases=['cali'])
    async def _mori(self, ctx, sfw : str = None):
        await self.image_embed(ctx, 'mori', sfw)

    @commands.command(name='navel', aliases=['stomach'])
    async def _navel(self, ctx, sfw : str = None):
        await self.image_embed(ctx, 'navel', sfw)

    @commands.command(name='okayu', aliases=[])
    async def _okayu(self, ctx, sfw : str = None):
        await self.image_embed(ctx, 'okayu', sfw)

    @commands.command(name='panties', aliases=['pantsu'])
    async def _panties(self, ctx, sfw : str = None):
        await self.image_embed(ctx, 'panties', sfw)

    @commands.command(name='pekora', aliases=['peko'])
    async def _pekora(self, ctx, sfw : str = None):
        await self.image_embed(ctx, 'pekora', sfw)

    @commands.command(name='rushia', aliases=[])
    async def _rushia(self, ctx, sfw : str = None):
        await self.image_embed(ctx, 'rushia', sfw)

    @commands.command(name='suisei', aliases=['sui'])
    async def _suisei(self, ctx, sfw : str = None):
        await self.image_embed(ctx, 'suisei', sfw)

    @commands.command(name='thighs', aliases=['thigh'])
    async def _thighs(self, ctx, sfw : str = None):
        await self.image_embed(ctx, 'thighs', sfw)

    @commands.command(name='witch', aliases=[])
    async def _witch(self, ctx, sfw : str = None):
        await self.image_embed(ctx, 'witch', sfw)
