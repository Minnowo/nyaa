
# code from: https://gist.github.com/makupi/c508c9d33bb01dcc04e57d1a93c23ae1
# has been modified by me 


import discord
import sys 
from discord.ext import commands
import uuid
import traceback
import argparse
import shlex

from . import util
from . import constants

class ReactionRoles(commands.Cog):

    reaction_roles_data = {}

    nyaa_cog = True

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        """A local check which applies to all commands in this cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage

        if not ctx.author.permissions_in(ctx.channel).manage_channels:
            raise commands.MissingPermissions(["manage_channels"])
            
        return True

    async def cog_command_error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('This command can not be used in Private Messages ;w;')
            except discord.HTTPException:
                pass

        if isinstance(error, commands.MissingPermissions):
            try:
                return await ctx.send("You are missing permissions to use this command >:3")
            except discord.HTTPException:
                pass
        
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
                  


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload : discord.RawReactionActionEvent):

        role, user = self.parse_reaction_payload(payload)
        
        if role is not None and user is not None and not user.bot:
            try:
                await user.add_roles(role, reason="ReactionRole")
            except discord.errors.Forbidden:
                await self.bot.get_channel(payload.channel_id).send("I do not have perms to give this role", delete_after = 5)


    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload : discord.RawReactionActionEvent):

        role, user = self.parse_reaction_payload(payload)

        if role is not None and user is not None and not user.bot:
            try:
                await user.remove_roles(role, reason="ReactionRole")
            except discord.errors.Forbidden:
                await self.bot.get_channel(payload.channel_id).send("I do not have perms to remove this role", delete_after = 5)


    @commands.command(name="embed")
    async def embed_(self, ctx, *, message : str):

        parser = argparse.ArgumentParser(
            usage="%(prog)s [OPTION]... URL...",
            add_help=False,
        )

        rename = parser.add_argument_group("Embed Options")
        rename.add_argument(
            "-t", "--title",
            dest="title", metavar="STR",
            help="Embed title"
        )
        rename.add_argument(
            "-f", "--field",
            dest="field", metavar="title$|$text", action="append",
            help="Add field to embed"
        )
        rename.add_argument(
            "-F", "--footer",
            dest="footer", metavar="STR",
            help="Add footer"
        )

        try:
            args = parser.parse_args(shlex.split(message))
        except Exception:
            await ctx.send("Invalid input")
            return

        title = args.title or ""
        
        embed = discord.Embed(color = constants.EMBED_COLOR, title = title)

        if args.footer:
            embed.add_footer(text = args.footer)

        for i in args.field:
            t, _, v = i.partition("$|$")

            embed.add_field(name=t, value=v, inline=False)

        await ctx.send(embed = embed)


    @commands.command(name = "add_reaction")
    async def reaction_add_(self, ctx, emote, role : str, message_id : str, channel : str = None):

        if not channel:
            cid = ctx.channel.id
        
        else:
            cid = util.get_channel_id_from_string(channel)

        rid = util.get_role_mention_id_from_string(role)
        mid = util.parse_int(message_id)

        if not mid:
            await ctx.send("Invalid message id")
            return
        
        if not cid:
            await ctx.send("Invalid channel")
            return

        if not rid:
            await ctx.send("Invalid role")
            return

        channel = ctx.guild.get_channel(cid)
        role = ctx.guild.get_role(rid)

        if not isinstance(channel, discord.TextChannel):
            await ctx.send("Text channel is required")
            return 

        if not role:
            await ctx.send("Could not find role")
            return

        try:
            message = await channel.fetch_message(message_id)
            await message.add_reaction(emote)
        except Exception:
            await ctx.send("Could not get / react to message")
            return

        self.add_reaction(ctx.guild.id, emote, role.id, channel.id, mid)
        
        


    @commands.command(name="reactions")
    async def reactions_(self, ctx):
        
        guild_id = ctx.guild.id
        data = self.reaction_roles_data.get(str(guild_id), None)
        embed = discord.Embed(title="Reaction Roles")

        if data is None:
            embed.description = "There are no reaction roles set up right now."

        else:
            for index, rr in enumerate(data):
                emote = rr.get("emote")
                role_id = rr.get("roleID")
                role = ctx.guild.get_role(role_id)
                channel_id = rr.get("channelID")
                message_id = rr.get("messageID")
                embed.add_field(
                    name=index,
                    value=f"{emote} - @{role} - [message](https://www.discordapp.com/channels/{guild_id}/{channel_id}/{message_id})",
                    inline=False,
                )
        await ctx.send(embed=embed)


    @commands.command(name = "remove_reaction")
    async def reaction_remove_(self, ctx, index: int):

        guild_id = ctx.guild.id
        data = self.reaction_roles_data.get(str(guild_id), None)
        embed = discord.Embed(title=f"Remove Reaction Role {index}")
        rr = None

        if data is None:
            embed.description = "Given Reaction Role was not found."
        
        else:
            if index > len(data) :
                await ctx.send("Invalid index")
                return

            embed.description = (
                "Do you wish to remove the reaction role below? Please react with 🗑️."
            )
            rr = data[index]
            emote = rr.get("emote")
            role_id = rr.get("roleID")
            role = ctx.guild.get_role(role_id)
            channel_id = rr.get("channelID")
            message_id = rr.get("messageID")
            _id = rr.get("id")
            embed.set_footer(text=_id)
            embed.add_field(
                name=index,
                value=f"{emote} - @{role} - [message](https://www.discordapp.com/channels/{guild_id}/{channel_id}/{message_id})",
                inline=False,
            )

        msg = await ctx.send(embed=embed)
        
        if rr is not None:
            await msg.add_reaction("🗑️")

            def check(reaction, user):
                return (
                    reaction.message.id == msg.id
                    and user == ctx.message.author
                    and str(reaction.emoji) == "🗑️"
                )

            reaction, user = await self.bot.wait_for("reaction_add", check=check)
            data.remove(rr)
            self.reaction_roles_data[str(guild_id)] = data


    @commands.command(name = "sync_reactions")
    async def sync_reactions_(self, ctx, message_id : str = None, channel : str = None):

        server_id = str(ctx.guild.id)

        if server_id not in self.reaction_roles_data:
            await ctx.send("This guild does not have any reaction roles")
            return 

        message_id = util.parse_int(message_id, None)

        if not message_id:
            await ctx.send("Invalid message id")
            return

        if not channel:
            channel = ctx.channel

        else:
            channel = util.get_channel_id_from_string(channel)
            channel = ctx.guild.get_channel(channel)

            if not channel:
                await ctx.send("Invalid channel")
                return

        try:
            
            message = await channel.fetch_message(message_id)

        except:
            await ctx.send("Could not find message in the given channel")
            return
        
        data = []
        for reaction in message.reactions:
            
            # get the emote and all of the users who have reacted
            data.append({
                "emote" : str(reaction.emoji),
                # filter out any bots we only want actualy people 
                "users" : filter(lambda x : not x.bot, await reaction.users().flatten())
            })
        
        # get only reaction roles for the server where the emote is found on the message 
        for i in filter(lambda x : any(i["emote"] == x["emote"] for i in data), self.reaction_roles_data[server_id]):

            role = ctx.guild.get_role(i["roleID"])
            
            if not role:
                continue

            # shitty nested loop but idc, you shouldn't really be using this command much its just something to use if the bot goes down
            for ii in data:

                if ii["emote"] == i["emote"]:

                    for user in ii["users"]:

                        if role not in user.roles:
                            try:
                                await user.add_roles(role, "reaction role")
                            except Exception as e:
                                print(e)



    def add_reaction(self, guild_id, emote, role_id, channel_id, message_id):
        
        if not str(guild_id) in self.reaction_roles_data:
            self.reaction_roles_data[str(guild_id)] = []
        
        self.reaction_roles_data[str(guild_id)].append(
            {
                "id": str(uuid.uuid4()),
                "emote": emote,
                "roleID": role_id,
                "channelID": channel_id,
                "messageID": message_id,
            }
        )
        


    def parse_reaction_payload(self, payload: discord.RawReactionActionEvent):
        
        guild_id = payload.guild_id
        data = self.reaction_roles_data.get(str(guild_id), None)
        
        if data is None:
            return None, None 

        for rr in data:
            
            emote = rr.get("emote")

            if payload.message_id != rr.get("messageID"):
                continue
            
            if payload.channel_id != rr.get("channelID"):
                continue
            
            if str(payload.emoji) == emote:
                guild = self.bot.get_guild(guild_id)
                role = guild.get_role(rr.get("roleID"))
                user = guild.get_member(payload.user_id)
                return role, user

        return None, None
