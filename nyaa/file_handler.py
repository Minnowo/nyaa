

import os 
from . import constants 
from . import util 


class FileHandler():

    instance = None 
    
    file_map = {
        # "thighs" : {
        #     "handle" : None,
        #     "line"   : 0
        # },
        # "feet" : {
        #     "handle" : None,
        #     "line"   : 0
        # },
        # "cutegirls.moe" : {
        #     "handle" : None,
        #     "line"   : 0
        # },
        # "kemonomimi" : {
        #     "handle" : None,
        #     "line"   : 0
        # }
    }

    @staticmethod 
    def get_instance():
        """ Static access method. """
        if FileHandler.instance == None:
            FileHandler()

        return FileHandler.instance

    def __init__(self):
        """ Virtually private constructor. """

        if FileHandler.instance != None:
            raise Exception("This class is a singleton!")
        self.file_map = {}
        FileHandler.instance = self

    def init_file_handles(self):
        self.deinit_file_handles()

        for i in constants.SAUCE_LINES:
            util.create_directory_from_file_name(i)

            key = os.path.basename(os.path.dirname(i))
            self.file_map[key] = {}

            try:
                self.file_map[key]["line"] = util.parse_int(open(i, 'r').readline().strip())
            except Exception as e:
                print(f"Could not load lines for '{key}' -> {e}")

        for i in constants.SAUCE_LINKS:
            key = os.path.basename(os.path.dirname(i))

            try:
                self.file_map[key]["handle"] = open(i, 'r')
                self.file_map[key]["open"]   = True

                for i in range(self.file_map[key]["line"]):
                    self.file_map[key]["handle"].readline()

            except Exception as e:
                self.file_map[key]["handle"] = None
                self.file_map[key]["open"]   = False 

                print(f"Could not load links for '{key}' -> {e}") 

    def deinit_file_handles(self):

        for key in self.file_map.keys():

            try:
                with open(f"config\\{key}\\{key}_line.txt", "w") as writer:
                    writer.write(str(self.file_map[key]["line"]))

            except Exception as e:
                print(f"Could not save line number for '{key}' -> {e}")  

            try:
                if "open" in self.file_map[key]:
                    if self.file_map[key]["open"]:
                        if self.file_map[key]["handle"] is not None:
                            self.file_map[key]["handle"].close()

            except Exception as e:
                print(f"Could not unload links for '{key}' -> {e}")  