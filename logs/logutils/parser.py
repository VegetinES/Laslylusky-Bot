import discord
import re
import aiohttp
import os
import time
from .constants import LOG_PARAMS, VALID_IMAGE_PARAMS
from .helpers.format_helpers import chunk_message, create_paste, format_attachments, is_valid_url
from .replacers.variable_replacers import get_replacements, replace_variables, get_user_from_kwargs, get_guild_from_kwargs
from .senders.log_senders import send_embed_log_new, send_normal_log_new, send_embed_log, send_normal_log
from .formatters.embed_formatters import process_field_attributes, set_safe_thumbnail, set_safe_image
from .formatters.message_formatters import create_deleted_message_log

class LogParser:
    def __init__(self, bot):
        self.bot = bot
        self.max_embed_length = 4096
        self.max_message_length = 2000
        self.max_direct_message_length = 1000
        self.pastebin_api_key = os.getenv("PASTEBIN_API_KEY")
        self.pastebin_user_key = os.getenv("PASTEBIN_USER_KEY")
    
    def chunk_message(self, message, chunk_size):
        return chunk_message(message, chunk_size)
    
    async def create_paste(self, content, title):
        return await create_paste(content, title, self.pastebin_api_key, self.pastebin_user_key)
    
    def format_attachments(self, attachments):
        return format_attachments(attachments)

    def is_valid_url(self, url):
        return is_valid_url(url)
    
    def is_valid_image_param(self, param):
        return param in VALID_IMAGE_PARAMS or self.is_valid_url(param)
    
    def get_user_from_kwargs(self, kwargs):
        return get_user_from_kwargs(kwargs)

    def get_guild_from_kwargs(self, kwargs):
        return get_guild_from_kwargs(kwargs)
    
    def get_replacements(self, log_type, **kwargs):
        return get_replacements(log_type, **kwargs)

    def replace_variables(self, text, replacements):
        return replace_variables(text, replacements)
    
    async def parse_and_send_log(self, log_type, log_channel, message_format, **kwargs):
        replacements = self.get_replacements(log_type, **kwargs)
        
        if isinstance(message_format, dict):
            message_config = message_format
            if message_config.get("embed", False):
                await send_embed_log_new(self, log_type, message_config, replacements, log_channel, **kwargs)
            else:
                await send_normal_log_new(self, log_type, message_config, replacements, log_channel, **kwargs)
        elif message_format.startswith("embed:"):
            await send_embed_log(self, log_type, message_format, replacements, log_channel, **kwargs)
        else:
            await send_normal_log(self, log_type, message_format, replacements, log_channel, **kwargs)
    
    def process_field_attributes(self, field_data, replacements):
        return process_field_attributes(field_data, replacements)
    
    def set_safe_thumbnail(self, embed, thumbnail_param, guild, user):
        set_safe_thumbnail(embed, thumbnail_param, guild, user)
    
    def set_safe_image(self, embed, image_param, guild, user):
        set_safe_image(embed, image_param, guild, user)
        
    async def send_embed_log_new(self, log_type, message_config, replacements, log_channel, **kwargs):
        await send_embed_log_new(self, log_type, message_config, replacements, log_channel, **kwargs)
    
    async def send_normal_log_new(self, log_type, message_config, replacements, log_channel, **kwargs):
        await send_normal_log_new(self, log_type, message_config, replacements, log_channel, **kwargs)
    
    async def send_embed_log(self, log_type, message_format, replacements, log_channel, **kwargs):
        await send_embed_log(self, log_type, message_format, replacements, log_channel, **kwargs)
    
    async def send_normal_log(self, log_type, message_format, replacements, log_channel, **kwargs):
        await send_normal_log(self, log_type, message_format, replacements, log_channel, **kwargs)
    
    async def create_deleted_message_log(self, message_format, message, del_msg_content):
        return await create_deleted_message_log(self, message_format, message, del_msg_content)