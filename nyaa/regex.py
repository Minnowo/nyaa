
import re 

# used for getting the channel id from a mention -> <#insert channel id here>
PARSE_CHANNEL_MENTION = re.compile(r"\<\#(\d+)\>")
PARSE_USER_MENTION = re.compile(r"\<\@(\d+)\>")