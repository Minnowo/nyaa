
from re import compile 

# used for getting the channel id from a mention -> <#insert channel id here>
PARSE_CHANNEL_MENTION = compile(r"\<\#(\d+)\>")
PARSE_USER_MENTION    = compile(r"\<\@(\d+)\>")
PARSE_ROLE_MENTION    = compile(r"\<\@\&(\d+)\>")

MATCH_RE_DISCORD_LINK = compile(r"(?:https?://)(?:(?:cdn\.discordapp\.com)|(?:media\.discordapp\.net))/attachments/\d+/\d+/[^\s]+")