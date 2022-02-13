
import discord
from re import compile

class RSSHandler():
    
    instance = None

    rss_channel_map = {

    }

    channels = set()

    RE_DISCORD_LINK = compile(r"(https?://)?(cdn\.discordapp\.com)|(media\.discordapp\.net)/attachments/(\d+)/(\d+)/([^\s]+)")
    MATCH_RE_DISCORD_LINK = compile(r"(https?://)?(?:cdn\.discordapp\.com)|(?:media\.discordapp\.net)/attachments/\d+/\d+/[^\s]+")

    @staticmethod 
    def get_instance():
        """ Static access method. """
        if RSSHandler.instance == None:
            RSSHandler()

        return RSSHandler.instance

    def __init__(self):
        """ Virtually private constructor. """

        if RSSHandler.instance != None:
            raise Exception("This class is a singleton!")
        
        RSSHandler.instance = self
        self.channels = set()


    def subscribe_channel(self, server_id, channel_id):
        print("adding channe:", channel_id)
        
        server_id = str(server_id)

        if server_id in self.rss_channel_map:
            self.rss_channel_map[server_id].add(channel_id)
            return True

        self.rss_channel_map[server_id] = set()
        self.rss_channel_map[server_id].add(channel_id)
        return True 

    def unsubscribe_channel(self, server_id, channel_id):
        print("removing channel:", channel_id)

        server_id = str(server_id)

        if server_id in self.rss_channel_map:
            self.rss_channel_map[server_id].remove(channel_id)
            return True 

            
    def handle_discord_message(self, message : discord.message):

        if not message.guild:
            return

        i_server_id = message.guild.id
        s_server_id = str(message.guild.id)
        channel_id = message.channel.id

        if s_server_id not in self.rss_channel_map:
            return 

        if channel_id not in self.rss_channel_map[s_server_id]:
            return

        links = set()
        
        for i in self.MATCH_RE_DISCORD_LINK.findall(message.content):
            links.add("https://" + i)

        for i in message.attachments:
            links.add(i.url)

        if links:
            with open("config\\links.txt", "a") as writer:
                
                for i in links:
                    print("adding " + i)    
                    writer.write(i.strip() + "\n")

        # print("message recieved for channel")

