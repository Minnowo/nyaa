
import discord

MEMBER_JOIN = "member_join"
MEMBER_LEAVE = "member_leave"
REACTION_CHANGED = "reaction_changed"
MESSAGE_DELETED = "message_deleted"

class ServerEventHanlder():
    
    instance = None

    event_map = {
        "member_join" : {
            # serverid           : channels
            # 381952489655894016 : [],
        },
        "member_leave" : {

        },
        "reaction_changed" : {

        },
        "message_deleted" : {

        }
    }

    @staticmethod 
    def get_instance():
        """ Static access method. """
        if ServerEventHanlder.instance == None:
            ServerEventHanlder()

        return ServerEventHanlder.instance

    def __init__(self):
        """ Virtually private constructor. """
        
        if ServerEventHanlder.instance != None:
            raise Exception("This class is a singleton!")
        
        ServerEventHanlder.instance = self


    def subscribe_channel(self, event, server_id, channel_id):
        print("adding channel:", channel_id, "for event:", event)

        server_id = str(server_id)

        if event not in self.event_map:
            print ("invalid event map:", event)
            return False

        if server_id in self.event_map[event]:
            self.event_map[event][server_id].add(channel_id)
            return True
        
        self.event_map[event][server_id] = set()
        self.event_map[event][server_id].add(channel_id)
        return True


    def unsubscribe_channel(self, event, server_id, channel_id):
        print("removing channel:", channel_id, "for event:", event)

        server_id = str(server_id)

        if event not in self.event_map:
            print ("invalid event map:", event)
            return False

        if server_id in self.event_map[event]:
            self.event_map[event][server_id].remove(channel_id)
            return True
        
    def is_event_subscribed(self, event, server_id, channel_id):

        server_id = str(server_id)

        if event not in self.event_map:
            print ("invalid event map:", event)
            return False

        if server_id in self.event_map[event]:
            return channel_id in self.event_map[event][server_id]

        return False 

    def get_event_subscribed_channels(self, event, server_id):
        
        server_id = str(server_id)

        if event not in self.event_map:
            print("invalid event map:", event)
            return

        if server_id not in self.event_map[event]:
            return

        for channel_id in self.event_map[event][server_id]:
            yield channel_id
