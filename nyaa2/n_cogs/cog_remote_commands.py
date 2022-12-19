

import subprocess
import os 
from discord.ext import commands
import discord

from .. import config
from .. import constants
# from .. import n_database as db 
from .. import util

from .cog_base import BaseNyaaCog



class RemoteCommandsCog(BaseNyaaCog):
    """ remote commands used by the dev """

    def __init__(self, bot) -> None:
        BaseNyaaCog.__init__(self, bot)

        self.developer_id = config.get(("bot"), "dev_user_id")

        self.COMMAND_MAP = { 
            "shutdown": self.shutdown,
            "gallery" : self.gallery,
            "ytdl"    : self.ytdl
        }


    class NotDeveloper(commands.CheckFailure): 
        """ """

    async def cog_check(self, ctx):

        if not ctx.author.id == self.developer_id:

            raise self.NotDeveloper()

        return True


    async def cog_command_error(self, ctx, error):

        if isinstance(error, self.NotDeveloper):
            return 

        self.logger.error('Ignoring exception in command {}:'.format(ctx.command))
        self.logger.error(error)


    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.id != self.developer_id or \
           message.content[0:3].lower() != "run": 
            return 

        self.logger.info("Remote command prefix invoked")

        match = constants.PARSE_COMMAND.search(message.content)

        if not match:
            return 

        command = match.group(1)
        args    = match.group(2)

        self.logger.info(f"Remote command: {command}")

        callback = self.COMMAND_MAP.get(command, None)

        if callback is None:
            return 

        await callback(message, args)



    async def shutdown(self, *args):
        
        self.logger.info("Remote shutdown of bot called")

        instance = config.get(("bot"), "instance")

        if instance:
            await instance.close()

    def get_url(self, *args):

        url = set() 

        for a in args:
            
            if not isinstance(a, str):
                continue

            for m in constants.MATCH_GENERAL_URL.findall(a):

                url.add(m)

                self.logger.info(f"url matched: {m}")

        return url


    async def gallery(self, *args):
        
        if not args:
            return 

        if not os.path.isfile(constants.GALLERY_DL):

            self.logger.warning(f"Path to gallery-dl does not exist {constants.GALLERY_DL}")
            return

        message  = args[0]

        url = self.get_url(*args)

        if not url:
            return 

        self.logger.info(f"Gallery called with {len(url)} urls")

        try:

            dump_file = util.get_temp_filename(constants.CONFIG_LOGS_DIR, "gallery", "log")

            cmd = [ 
                constants.GALLERY_DL, "--write-log", dump_file,
                "--no-skip", "--no-mtime", "-d", constants.GALLERY_DL_DIR
            ]

            cmd.extend(url)

            self.logger.debug(f"Running gallery-dl with arguments: {cmd}")

            util.subprocess_communicate(subprocess.Popen(cmd, shell=False))

            if os.path.isfile(dump_file):

                if os.stat(dump_file).st_size > 0:

                    channel = await message.author.create_dm()
                    
                    await channel.send(file=discord.File(dump_file))

                else:

                    util.remove_file(dump_file)

        except OSError as e:
            self.logger.error(e, stack_info=True)

        except Exception as e:
            self.logger.error(e, stack_info=True)


    async def ytdl(self, *args):
            
        url = self.get_url(*args)

        if not url:
            return 

        self.logger.info(f"YTDL called with {len(url)} urls")
