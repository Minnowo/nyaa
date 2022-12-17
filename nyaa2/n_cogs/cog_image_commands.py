import random
import discord
from discord.ext import commands

from .. import n_database as db
from .. import constants
from .. import util 

from .cog_base import BaseNyaaCog

# cog responsible for handling image commands 
class ImageCommands(BaseNyaaCog):

    image_cache_sfw = { 

    }
    image_cache_nsfw = {

    }

    def __init__(self, bot):
        BaseNyaaCog.__init__(self, bot)


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
                
                self.image_cache_nsfw[category_id].extend({ "id" : image['image_id'], "url" : image["image_url"], "s" : image["is_nsfw"]  } for image in self.MEDIA_DB_INSTANCE.get_images_with_rating(category_id, constants.IMAGE_CACHE_SIZE, True))

            if not self.image_cache_nsfw[category_id]:

                return 

            return self.image_cache_nsfw[category_id].pop()


        if category_id not in self.image_cache_sfw:
                
            self.image_cache_sfw[category_id] = [] 

        if not self.image_cache_sfw[category_id]:
            
            self.image_cache_sfw[category_id].extend({ "id" : image['image_id'], "url" : image["image_url"], "s" : image["is_nsfw"] } for image in self.MEDIA_DB_INSTANCE.get_images_with_rating(category_id, constants.IMAGE_CACHE_SIZE, False))

        if not self.image_cache_sfw[category_id]:

            return 

        return self.image_cache_sfw[category_id].pop()

    
    async def send_image_embed(self, ctx, image):


        sfw = "SFW" if image['s'] == 0 else "NSFW"

        embed = discord.Embed(color = constants.EMBED_COLOR)
        embed.set_image(url = image['url'])
        embed.set_footer(text = f"Rating: {sfw} \nImage ID: {image['id']}")

        try:
            
            await ctx.send(embed=embed)

        except discord.HTTPException as e:

            self.logger.error(e, stack_info=True)

        

    # handles sending content for sfw and nsfw channels
    async def image_embed(self, ctx, key, requested_type):
        """
        key is the module name
        requested_type is the content type prefered 
        """
        
        self.logger.debug(f"user has requested {key} with type {requested_type}")

        isNSFW = ctx.channel.is_nsfw()

        if requested_type and requested_type.lower().startswith("s"):
                
            isNSFW = False

        image = self.get_image(constants.IMAGE_CATEGORY_MAP[key], isNSFW)

        if image:
            
            await self.send_image_embed(ctx, image)

        elif isNSFW:
            
            await self.image_embed(ctx, key, "sfw")

        else:
            await self.send_message_wrapped(ctx, "Could not find image")



        
    @commands.command(name = "setr")
    async def _set_rating(self, ctx, image_id : int, rating : str):

        if not self.MISC_DB_INSTANCE.is_user_trusted(ctx.author.id):
            return 

        rating = rating.lower() 

        if not rating.startswith('s') and not rating.startswith('n'):

            return await self.send_message_wrapped(ctx, "Specify SFW or NSFW")

        is_nsfw = rating.startswith('n')

        self.MEDIA_DB_INSTANCE.update_image_sfw_type(image_id, is_nsfw)

        if is_nsfw:
            self.logger.info(f"User {ctx.author.name} with ID {ctx.author.id} has set image {image_id} with rating NSFW")
            await self.send_message_wrapped(ctx, "Image has been updated with NSFW rating")

        else:
            self.logger.info(f"User {ctx.author.name} with ID {ctx.author.id} has set image {image_id} with rating SFW")
            await self.send_message_wrapped(ctx, "Image has been updated with SFW rating")


    @commands.command(name = "listc", aliases = ["listcat", "listcategory"])
    async def _lsit(self, ctx):

        if not self.MISC_DB_INSTANCE.is_user_trusted(ctx.author.id):
            return 

        self.logger.info(f"listing categories for {ctx.author}")

        cats = [ c['category_name'] for c in self.MEDIA_DB_INSTANCE.get_all_categories()]

        await self.send_message_wrapped(ctx, ", ".join(cats))

    @commands.command(name = "addcat", aliases = ["add_category", "addcategory"])
    async def _addc(self, ctx, category : str):

        if not self.MISC_DB_INSTANCE.is_user_trusted(ctx.author.id):
            return 

        category = category.lower().strip()

        if not category or not constants.IS_ONLY_A_TO_Z.match(category):

            return await self.send_message_wrapped(ctx, "category was not added")

        self.logger.info(f"adding category {category}")

        self.MEDIA_DB_INSTANCE.add_image_category(category)

        cat_id = self.MEDIA_DB_INSTANCE.select_category_id_by_name(category)

        if cat_id is None:

            return await self.send_message_wrapped(ctx, "category was not added due to error")

        constants.IMAGE_CATEGORY_MAP[category] = cat_id

        await self.send_message_wrapped(ctx, "added category")


    @commands.command(name = "add", aliases = ["add_image", "addimage"])
    async def _add(self, ctx, category : str, sfw : str):

        if not self.MISC_DB_INSTANCE.is_user_trusted(ctx.author.id):
            return 

        if not ctx.message.attachments:

            return await self.send_message_wrapped(ctx, "attachments required")

        cat_id = self.MEDIA_DB_INSTANCE.select_category_id_by_name(category.lower().strip())
        
        if cat_id is None:

            return await self.send_message_wrapped(ctx, "invalid category")

        is_sfw = sfw.startswith("s")

        with self.MEDIA_DB_INSTANCE as cursor:

            for attachment in ctx.message.attachments:

                self.logger.info(f"adding image {attachment.url} to category {category}")

                self.MEDIA_DB_INSTANCE.add_image(cat_id, attachment.url, not is_sfw)

        await self.send_message_wrapped(ctx, "added image links to category")


    @commands.command(name = "imid", aliases = ["imbyid", "imagebyid"])
    async def _imbyid(self, ctx, id : str):

        id = util.parse_int(id, None)

        if id is None:

            return await self.send_message_wrapped(ctx, "could not parse id")

        im = self.MEDIA_DB_INSTANCE.get_image_by_id(id)

        if im is None:

            return await self.send_message_wrapped(ctx, "image does not exist")

        await self.send_image_embed(ctx, { "id" : im['image_id'], "url" : im["image_url"], "s" : im["is_nsfw"] })

    @commands.command(name = "imcat", aliases = ["imbycat"])
    async def _imbycat(self, ctx, category : str, stf : str = None):

        cat_id = self.MEDIA_DB_INSTANCE.select_category_id_by_name(category.lower().strip())

        if cat_id is None:

            return await self.send_message_wrapped(ctx, "cannot find category")

        await self.image_embed(ctx, category, stf)



    # module commands go here,
    # since its not possible to register commands in a cog without using the decorator,
    # i'm just adding the command for each module myself instead of in a config somewhere else

    # currently just forcin o content for each command cause i don't have time to sort through it all
    
    @commands.command(name = "towa", aliases = ["tokayami_towa"])
    async def _tow(self, ctx, sfw : str = None):
        await self.image_embed(ctx, 'towa', sfw)

    @commands.command(name = "mio", aliases = ["ookami_mio"])
    async def _ookami_mio(self, ctx, sfw : str = None):
        await self.image_embed(ctx, 'ookami_mio', sfw)

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





    AWOO_SET = [
        "https://cdn.discordapp.com/attachments/620023299107192853/1053461781068136468/awoo1.jpg",
        "https://cdn.discordapp.com/attachments/620023299107192853/1053461795567845376/awoo2.gif",
        "https://cdn.discordapp.com/attachments/620023299107192853/1053461801448243220/awoo3.png",
        "https://cdn.discordapp.com/attachments/620023299107192853/1053461804459765820/awoo4.png",
        "https://cdn.discordapp.com/attachments/620023299107192853/1053461808150761492/awoo5.png",
        "https://cdn.discordapp.com/attachments/620023299107192853/1053461818565202050/awoo6.png",
        ]


    DIF_BETWEEN_LOLI_AND_SMOL = "https://cdn.discordapp.com/attachments/620023299107192853/1053462159650209812/the_difference_between_loli_and_petite.png"


    SHONDO_CRYING = 'https://cdn.discordapp.com/attachments/620023299107192853/1053458565815337060/cry.webm'



    @commands.command(name='cry')
    async def _cry(self, ctx):

        await self.send_message_wrapped(ctx, self.SHONDO_CRYING)

    @commands.command(name='awoo')
    async def _awoo(self, ctx):

        awoo = {
            's' : 0,
            'id' : 'awoo',
            'url' : random.choice(self.AWOO_SET)
        }

        await self.send_image_embed(ctx, awoo)

    @commands.command(name='loli', aliases=['cunny','child'])
    async def _loli(self, ctx):

        awoo = {
            's' : 0,
            'id' : 'no cute and funny >>:((',
            'url' : self.DIF_BETWEEN_LOLI_AND_SMOL
        }

        await self.send_image_embed(ctx, awoo)