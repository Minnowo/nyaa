
import os
import sys 
import requests
import logging 
from . import constants

def combine_dict(a, b):
    """Recursively combine the contents of 'b' into 'a'"""
    for key, value in b.items():

        if key in a and isinstance(value, dict) and isinstance(a[key], dict):
            combine_dict(a[key], value)
            
        else:
            a[key] = value

    return a


def parse_int(value, default=0):
    """Convert 'value' to int"""
    
    if not value:
        return default

    try:
        return int(value)

    except (ValueError, TypeError):
        return default


def expand_path(path):
    """Expand environment variables and tildes (~)"""
    if not path:
        return path

    if not isinstance(path, str):
        path = os.path.join(*path)

    return os.path.expandvars(os.path.expanduser(path))



def create_directory_from_file_name(path : str) -> bool:
    """Creates a directory from the file path."""
    return create_directory(os.path.dirname(path))


def create_directory(path : str) -> bool:
    """Creates the given directory."""
    try:
        os.makedirs(expand_path(path), exist_ok=True)
    except OSError:
        pass
    return os.path.isdir(path)


def get_filename_ext(filename : str, includeDot = False):

    ext = filename.rsplit(".", 1)

    if len(ext) < 2:
        return ""

    ext = ext[-1]

    
    if includeDot:
        return "." + ext.lower().strip()
    return ext.lower().strip()


def get_url_filename(url : str):
    """Gets a file name from the given url"""
    try:
        return url.split("?")[0].rsplit("/", 1)[-1]
    except (TypeError, AttributeError):
        return ""


def get_url_ext(url, includeDot = False):
    """Gets a file extension from the given url"""
    
    ext = get_url_filename(url).rsplit(".", 1)

    if len(ext) < 2:
        return ""

    ext = ext[-1]

    if includeDot:
        return "." + ext.lower().strip()
    return ext.lower().strip()


def get_channel_id_from_string(channel_mention : str):
    
    m = constants.PARSE_CHANNEL_MENTION.search(channel_mention)
        
    if m:
        id = parse_int(m.group(1))

    else:
        id = parse_int(channel_mention, None)

        if not id:
            return None 

    return id 


def get_mention_id_from_string(mention : str):
    
    m = constants.PARSE_USER_MENTION.search(mention)
        
    if m:
        id = parse_int(m.group(1))

    else:
        id = parse_int(mention, None)

        if not id:
            return None 

    return id 


def get_role_mention_id_from_string(mention : str):
    
    m = constants.PARSE_ROLE_MENTION.search(mention)
        
    if m:
        id = parse_int(m.group(1))

    else:
        id = parse_int(mention, None)

        if not id:
            return None 

    return id 


def get_nhentai_random():
    return requests.get("https://nhentai.net/random").url



def get_logger(name : str, log_file : str = "", log_level = logging.DEBUG):

    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    
    if log_file:
        create_directory_from_file_name(log_file)
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    logger.addHandler(stdout_handler)
    logger.setLevel(log_level)

    return logger

