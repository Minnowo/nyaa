
import discord
import random
from discord.errors import HTTPException

from discord.ext import commands
import discord.ext.commands.errors

from .. import util
from .. import constants
from .. import n_database as db
from .. import config

from . import (
    BaseNyaaCog
)

class ServerUtil(BaseNyaaCog):
    """ server utility functions """

    def __init__(self, bot) -> None:
        BaseNyaaCog.__init__(self, bot)


    async def cog_command_error(self, ctx, error):
        
        if isinstance(error, commands.NoPrivateMessage):

            return await self.send_message_wrapped(ctx, 'This command can not be used in Private Messages.')
        
        self.logger.error('Ignoring exception in command {}:'.format(ctx.command))
        self.logger.error(error)

        # print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        # traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        


    @commands.command(name='help')
    async def help_(self, ctx, *, search: str = None):

        if self.MISC_DB_INSTANCE.is_user_trusted(ctx.author.id):

            return await self.send_message_wrapped(ctx, constants.JOKE_HELP[-1])

        await self.send_message_wrapped(ctx, random.choice(constants.JOKE_HELP))



    @commands.command(name='invite', aliases=['getinvite'])
    async def invite_(self, ctx): 
        await ctx.send(f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot")


    # @commands.command(name='err')
    # async def error_test(self, ctx): 

    #     with self.MISC_DB_INSTANCE as cursor:

    #         raise TypeError
        


    @commands.hybrid_command(name='random', aliases=["rand", "rnd", 'rng'], description="Gets a number between x and y")
    # @discord.app_commands.guilds(discord.Object(id=constants.TEST_SERVER_ID))
    async def random_(self, ctx, a : str, b : str): 
        
        a = util.parse_int(a, None)
        b = util.parse_int(b, None)

        if not a or not b:
            
            return await self.send_message_wrapped(ctx, "Please enter a min and max number")

        if a > b:

            return await self.send_message_wrapped(ctx, str(random.randint(b, a)))
            
        return await self.send_message_wrapped(ctx, str(random.randint(a, b)))



    @commands.hybrid_command(name='clear', aliases=["delete", "purge"], description="Deletes x number of messages")
    # @discord.app_commands.guilds(discord.Object(id=constants.TEST_SERVER_ID))
    async def clear_(self, ctx, amount = 5): 

        if not ctx.guild:
            
            return await self.send_message_wrapped(ctx, "can't purge dms, sorry </3")

        perms = ctx.channel.permissions_for(ctx.author)

        if perms is None:
    
            return await self.send_message_wrapped(ctx, "Could not detect any permissions for given channel")

        if perms.manage_messages:
            
            return await ctx.channel.purge(limit = amount + 1)

        return await self.send_message_wrapped(ctx, "I lack permission. ~~master pwease give me admin <3~~")



    @commands.hybrid_command(name='getuser', aliases=["getmember", "fetchuser", "user", "member"], description="Get information about a user")
    # @discord.app_commands.guilds(discord.Object(id=constants.TEST_SERVER_ID))
    async def getuser_(self, ctx, *, id : str = None): 
        
        if id is None:
            return await self.send_message_wrapped(ctx, "Pwease specify a User or their ID <3")

        id = util.get_mention_id_from_string(id)

        if id is None:
            return await self.send_message_wrapped(ctx, "Invalid ID or @")

        try:
            
            member = await self.bot.fetch_user(id)

        except HTTPException as e:
            
            self.logger.error(e, stack_info=True)
            
            return await self.send_message_wrapped(ctx, "There was an error making the request")

        except (discord.errors.NotFound, discord.ext.commands.errors.MemberNotFound):

            return await self.send_message_wrapped(ctx, "Could not find the user </3")

        embed = discord.Embed(color = constants.EMBED_COLOR)
        embed.set_author(name = f"{member.name}#{member.discriminator}", icon_url = member.avatar)
        embed.set_thumbnail(url=member.avatar)
        embed.add_field(name =f"**User:**", 
                        value = f'Mention: <@{member.id}>\n' + \
                                f'Name: {member} \n' + \
                                f'Id: {member.id}', inline=False)
                                
        embed.add_field(name =f"**Account Created On:**", value = member.created_at, inline=False)

        await ctx.send(embed=embed)



    @commands.hybrid_command(name='getserver', aliases=["server", "fetchserver", "guild", "getguild"], description="Get information about a server the bot is in")
    # @discord.app_commands.guilds(discord.Object(id=constants.TEST_SERVER_ID))
    async def getguild_(self, ctx, *, id : discord.Guild = None): 
        
        if isinstance(id, str):
            id = util.parse_int(id)

        if id is None:
            guild = ctx.guild

        elif isinstance(id, discord.Guild):
            guild = id 
        
        else:
            
            try:
            
                guild = self.bot.get_guild(id)
            
            except HTTPException as e:
                
                self.logger.error(e, stack_info=True)

                return await self.send_message_wrapped(ctx, "There was an error making the request")
                
            except (discord.errors.NotFound, discord.ext.commands.errors.GuildNotFound):

                return await self.send_message_wrapped(ctx, "I'm not in this server </3")

        if not guild:

            return await self.send_message_wrapped(ctx, "I'm not in this server ;w;")

        embed = discord.Embed(color = constants.EMBED_COLOR)
        embed.set_author(name = f"{guild.name}", icon_url = guild.icon)
        embed.set_thumbnail(url=guild.icon)
        embed.add_field(name =f"**Server:**", 
                        value = f'Name: {guild.name} \n' + \
                                f'Owner ID: {guild.owner_id}\n' + \
                                f'Server ID: {guild.id}\n' + \
                                f'Member Count: {guild.member_count} \n' + \
                                f'Channel Count: {len(guild.channels)} \n' + \
                                f'Filesize Limit: {util.size_suffix(guild.filesize_limit)} \n', inline=False)

        embed.add_field(name =f"**Created On:**", value = guild.created_at, inline=False)

        await ctx.send(embed=embed)




    # add user to trusted list for debugging 
    @commands.command(name='trust')
    async def _trust(self, ctx, member : str):

        if not self.MISC_DB_INSTANCE.is_user_trusted(ctx.author.id):

            return 

        id = util.get_mention_id_from_string(member)

        if id is None:
            return await self.send_message_wrapped(ctx, "Invalid ID or @")

        try:
            
            member = await self.bot.fetch_user(id)

        except HTTPException as e:
            
            self.logger.error(e, stack_info=True)
            
            return await self.send_message_wrapped(ctx, "There was an error making the request")

        except (discord.errors.NotFound, discord.ext.commands.errors.MemberNotFound):

            return await self.send_message_wrapped(ctx, "Could not find the user </3")

        if member.bot:

            return await self.send_message_wrapped(ctx, "This user is a bot")

        self.MISC_DB_INSTANCE.add_trusted_user(member.name, member.id)
        
        self.logger.info(f"User {ctx.author.name} with ID {ctx.author.id} has trusted {id}")

        await self.send_message_wrapped(ctx, f"{member.name} has been trusted")


    @commands.command(name='untrust')
    async def _untrust(self, ctx, member : str):

        if not self.MISC_DB_INSTANCE.is_user_trusted(ctx.author.id):

            return 

        id = util.get_mention_id_from_string(member)

        if config.get(('bot'), "dev_user_id", -1) == id:

            self.logger.info(f"User {ctx.author.name} with ID {ctx.author.id} has tried to untrust you.")

            return await self._untrust(ctx, str(ctx.author.id))


        if id is None:
            return await self.send_message_wrapped(ctx, "Invalid ID or @")

        
        self.MISC_DB_INSTANCE.remove_trusted_user(id)
        
        self.logger.info(f"User {ctx.author.name} with ID {ctx.author.id} has removed trust from {id}")

        await self.send_message_wrapped(ctx, f"user {id} has been untrusted")


    
    @commands.command(name='trusted')
    async def _trusted(self, ctx):
        
        if not self.MISC_DB_INSTANCE.is_user_trusted(ctx.author.id):

            return 

        self.logger.info(f"User {ctx.author.name} with ID {ctx.author.id} has requested the trusted list")
        self.logger.info("Trusted Users:")
        self.logger.info("====================================")

        for trusted in self.MISC_DB_INSTANCE.get_all_trusted():

            self.logger.info(f"[{trusted['user_id']}] [  {trusted['username']}")

        self.logger.info("====================================")
