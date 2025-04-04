import discord
import re
import aiohttp
import os
import time

LOG_PARAMS = {
    "ban": {
        "name": "Logs de baneo de usuarios",
        "params": ["{userid}", "{usertag}", "{mod}", "{modid}", "{modtag}", "{reason}"],
        "footer_params": ["{userid}", "{usertag}", "{modid}", "{modtag}"]
    },
    "kick": {
        "name": "Logs de expulsión de usuarios",
        "params": ["{userid}", "{usertag}", "{mod}", "{modid}", "{modtag}", "{reason}"],
        "footer_params": ["{userid}", "{usertag}", "{modid}", "{modtag}"]
    },
    "unban": {
        "name": "Logs de desbaneo de usuarios",
        "params": ["{userid}", "{usertag}", "{modtag}", "{modid}", "{mod}"],
        "footer_params": ["{userid}", "{usertag}", "{modtag}", "{modid}"]
    },
    "enter": {
        "name": "Logs de entrada de usuarios",
        "params": ["{userid}", "{usertag}", "{user}", "{accage}", "{acc_age}"],
        "footer_params": ["{userid}", "{usertag}", "{user}"]
    },
    "leave": {
        "name": "Logs de salida de usuarios",
        "params": ["{userid}", "{usertag}", "{acc_age}", "{server_age}"],
        "footer_params": ["{userid}", "{usertag}"]
    },
    "del_msg": {
        "name": "Logs de mensajes eliminados",
        "params": ["{del_msg}", "{usertag}", "{userid}", "{user}", "{channel}", "{channelid}", "{attached}"],
        "footer_params": ["{usertag}", "{userid}", "{channelid}"]
    },
    "edited_msg": {
        "name": "Logs de mensajes editados",
        "params": ["{user}", "{userid}", "{usertag}", "{channel}", "{channelid}", "{old_msg}", "{new_msg}", "{attached}"],
        "footer_params": ["{userid}", "{usertag}", "{channelid}"]
    },
    "warn": {
        "name": "Logs de advertencias",
        "params": ["{user}", "{userid}", "{usertag}", "{reason}", "{mod}", "{modtag}", "{modid}", "{warnid}"],
        "footer_params": ["{userid}", "{usertag}", "{modid}", "{modtag}"]
    },
    "unwarn": {
        "name": "Logs de eliminación de advertencias",
        "params": ["{user}", "{userid}", "{usertag}", "{reason}", "{mod}", "{modtag}", "{modid}", "{warnid}"],
        "footer_params": ["{userid}", "{usertag}", "{modid}", "{modtag}"]
    }
}

VALID_IMAGE_PARAMS = ["{servericon}", "{useravatar}"]

class LogParser:
    def __init__(self, bot):
        self.bot = bot
        self.max_embed_length = 4096
        self.max_message_length = 2000
        self.max_direct_message_length = 1000
        self.pastebin_api_key = os.getenv("PASTEBIN_API_KEY")
        self.pastebin_user_key = os.getenv("PASTEBIN_USER_KEY")
    
    def chunk_message(self, message, chunk_size):
        return [message[i:i + chunk_size] for i in range(0, len(message), chunk_size)]
    
    async def create_paste(self, content, title):
        try:
            if not self.pastebin_api_key:
                return None

            data = {
                'api_dev_key': self.pastebin_api_key,
                'api_option': 'paste',
                'api_paste_code': content,
                'api_paste_name': title,
                'api_paste_private': '1',
                'api_paste_expire_date': '1W'
            }
            
            if self.pastebin_user_key:
                data['api_user_key'] = self.pastebin_user_key

            async with aiohttp.ClientSession() as session:
                async with session.post('https://pastebin.com/api/api_post.php', data=data) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        error_text = await response.text()
                        print(f"Error de Pastebin: {error_text}")
                        return None
        except Exception as e:
            print(f"Error al crear paste: {e}")
            return None
    
    def format_attachments(self, attachments):
        if not attachments:
            return "No hay adjuntos"
        
        result = []
        for attachment in attachments:
            url_parts = attachment.url.split('?')
            clean_url = url_parts[0]
            result.append(f"[{attachment.filename}]({clean_url})")
        
        return "\n".join(result)

    def is_valid_url(self, url):
        if not url:
            return False
            
        url_pattern = re.compile(
            r'^(https?://)?'
            r'([a-zA-Z0-9]+\.)+[a-zA-Z]{2,}'
            r'(/[a-zA-Z0-9._~:/?#[\]@!$&\'()*+,;=]*)?'
            r'$'
        )
        return bool(url_pattern.match(url))
    
    def is_valid_image_param(self, param):
        return param in VALID_IMAGE_PARAMS or self.is_valid_url(param)
    
    def get_user_from_kwargs(self, kwargs):
        for key in ["target", "member", "user", "author", "after_message"]:
            if key in kwargs and kwargs[key]:
                return kwargs[key]
        
        if "message" in kwargs and kwargs["message"]:
            return kwargs["message"].author
        
        return None

    def get_guild_from_kwargs(self, kwargs):
        if "guild" in kwargs and kwargs["guild"]:
            return kwargs["guild"]

        for key in ["member", "message", "after_message"]:
            if key in kwargs and kwargs[key] and hasattr(kwargs[key], "guild"):
                return kwargs[key].guild
        
        return None
    
    def get_replacements(self, log_type, **kwargs):
        replacements = {}

        if log_type == "ban":
            target = kwargs.get("target")
            moderator = kwargs.get("moderator")
            reason = kwargs.get("reason", "No especificada")
            
            if target:
                replacements.update({
                    "{userid}": str(target.id),
                    "{usertag}": str(target),
                    "{user}": getattr(target, "mention", f"<@{target.id}>")
                })
            
            if moderator:
                replacements.update({
                    "{modid}": str(moderator.id),
                    "{modtag}": str(moderator),
                    "{mod}": getattr(moderator, "mention", f"<@{moderator.id}>")
                })
            
            replacements["{reason}"] = str(reason)

        elif log_type == "kick":
            target = kwargs.get("target")
            moderator = kwargs.get("moderator")
            reason = kwargs.get("reason", "No especificada")
            
            if target:
                replacements.update({
                    "{userid}": str(target.id),
                    "{usertag}": str(target),
                    "{user}": getattr(target, "mention", f"<@{target.id}>")
                })
            
            if moderator:
                replacements.update({
                    "{modid}": str(moderator.id),
                    "{modtag}": str(moderator),
                    "{mod}": getattr(moderator, "mention", f"<@{moderator.id}>")
                })
            
            replacements["{reason}"] = str(reason)

        elif log_type == "unban":
            target = kwargs.get("target")
            moderator = kwargs.get("moderator")
            
            if target:
                replacements.update({
                    "{userid}": str(target.id),
                    "{usertag}": str(target)
                })
            
            if moderator:
                replacements.update({
                    "{modid}": str(moderator.id),
                    "{modtag}": str(moderator),
                    "{mod}": getattr(moderator, "mention", f"<@{moderator.id}>")
                })

        elif log_type == "enter":
            member = kwargs.get("member")
            accage = kwargs.get("accage", "")
            
            if member:
                replacements.update({
                    "{userid}": str(member.id),
                    "{usertag}": str(member),
                    "{user}": member.mention,
                    "{acc_age}": f"<t:{int(member.created_at.timestamp())}:f>"
                })
            
            replacements["{accage}"] = str(accage)

        elif log_type == "leave":
            member = kwargs.get("member")
            
            if member:
                joined_at = member.joined_at.timestamp() if member.joined_at else time.time()
                replacements.update({
                    "{userid}": str(member.id),
                    "{usertag}": str(member),
                    "{acc_age}": f"<t:{int(member.created_at.timestamp())}:f>",
                    "{server_age}": f"<t:{int(joined_at)}:R>"
                })

        elif log_type == "del_msg":
            message = kwargs.get("message")
            author = kwargs.get("author")
            
            if message:
                del_msg_content = kwargs.get("del_msg_content", message.content)
                if not del_msg_content:
                    del_msg_content = "No hay contenido del mensaje"
                
                attachments = self.format_attachments(message.attachments)
                
                replacements.update({
                    "{del_msg}": del_msg_content,
                    "{channel}": message.channel.mention,
                    "{channelid}": str(message.channel.id),
                    "{attached}": attachments
                })
            
            if author:
                replacements.update({
                    "{userid}": str(author.id),
                    "{usertag}": str(author),
                    "{user}": author.mention
                })
            elif message and message.author:
                replacements.update({
                    "{userid}": str(message.author.id),
                    "{usertag}": str(message.author),
                    "{user}": message.author.mention
                })

        elif log_type == "edited_msg":
            message = kwargs.get("message")
            old_content = kwargs.get("old_content", "")
            new_content = kwargs.get("new_content", "")
            old_url = kwargs.get("old_url")
            new_url = kwargs.get("new_url")

            if not old_content:
                old_content = "No hay contenido del mensaje anterior"
            if not new_content:
                new_content = "No hay contenido del mensaje nuevo"
            
            if message:
                attachments = self.format_attachments(message.attachments)
                
                replacements.update({
                    "{channel}": message.channel.mention,
                    "{channelid}": str(message.channel.id),
                    "{userid}": str(message.author.id),
                    "{usertag}": str(message.author),
                    "{user}": message.author.mention,
                    "{attached}": attachments
                })
            
            if old_url:
                replacements["{old_msg}"] = f"Texto largo, se ha subido a pastebin [click aquí]({old_url})"
            else:
                replacements["{old_msg}"] = old_content
            
            if new_url:
                replacements["{new_msg}"] = f"Texto largo, se ha subido a pastebin [click aquí]({new_url})"
            else:
                replacements["{new_msg}"] = new_content

        elif log_type == "warn":
            user_id = kwargs.get("user_id")
            user_mention = kwargs.get("user_mention")
            user_tag = kwargs.get("user_tag")
            reason = kwargs.get("reason", "No especificada")
            mod_id = kwargs.get("mod_id")
            mod_mention = kwargs.get("mod_mention")
            mod_tag = kwargs.get("mod_tag")
            warn_id = kwargs.get("warn_id", "desconocido")
            
            replacements.update({
                "{userid}": str(user_id),
                "{user}": user_mention,
                "{usertag}": user_tag,
                "{reason}": reason,
                "{modid}": str(mod_id),
                "{mod}": mod_mention,
                "{modtag}": mod_tag,
                "{warnid}": str(warn_id)
            })
        
        elif log_type == "unwarn":
            user_id = kwargs.get("user_id")
            user_mention = kwargs.get("user_mention")
            user_tag = kwargs.get("user_tag")
            reason = kwargs.get("reason", "No especificada")
            mod_id = kwargs.get("mod_id")
            mod_mention = kwargs.get("mod_mention")
            mod_tag = kwargs.get("mod_tag")
            warn_id = kwargs.get("warn_id", "desconocido")
            
            replacements.update({
                "{userid}": str(user_id),
                "{user}": user_mention,
                "{usertag}": user_tag,
                "{reason}": reason,
                "{modid}": str(mod_id),
                "{mod}": mod_mention,
                "{modtag}": mod_tag,
                "{warnid}": str(warn_id)
            })
        
        return replacements

    def replace_variables(self, text, replacements):
        if not text:
            return ""
            
        result = text.replace(r"{\n}", "\n").replace("{\\n}", "\n")
        
        for key, value in replacements.items():
            result = result.replace(key, str(value))
            
        return result
    
    async def parse_and_send_log(self, log_type, log_channel, message_format, **kwargs):
        replacements = self.get_replacements(log_type, **kwargs)
        
        if isinstance(message_format, dict):
            message_config = message_format
            if message_config.get("embed", False):
                await self.send_embed_log_new(log_type, message_config, replacements, log_channel, **kwargs)
            else:
                await self.send_normal_log_new(log_type, message_config, replacements, log_channel, **kwargs)
        elif message_format.startswith("embed:"):
            await self.send_embed_log(log_type, message_format, replacements, log_channel, **kwargs)
        else:
            await self.send_normal_log(log_type, message_format, replacements, log_channel, **kwargs)
    
    def process_field_attributes(self, field_data, replacements):
        try:
            if not isinstance(field_data, dict):
                return None
            
            field_name_raw = field_data.get("name", "")
            field_name = self.replace_variables(field_name_raw, replacements)
            
            if not field_name:
                field_name = "\u200b"
            
            field_value_raw = field_data.get("value", "")
            field_value = self.replace_variables(field_value_raw, replacements)
            
            if not field_value:
                field_value = "\u200b"
            
            field_inline = field_data.get("inline", False)
            
            if isinstance(field_inline, str):
                field_inline = field_inline.lower() in ["true", "yes", "1"]
            
            result = {
                "name": field_name,
                "value": field_value,
                "inline": field_inline
            }
            return result
        except Exception as e:
            import traceback
            traceback.print_exc()
            return None
    
    def set_safe_thumbnail(self, embed, thumbnail_param, guild, user):
        try:
            if thumbnail_param == "{servericon}":
                if guild and guild.icon:
                    embed.set_thumbnail(url=guild.icon.url)
            elif thumbnail_param == "{useravatar}":
                if user and hasattr(user, "avatar") and user.avatar:
                    embed.set_thumbnail(url=user.avatar.url)
            elif self.is_valid_url(thumbnail_param):
                embed.set_thumbnail(url=thumbnail_param)
        except Exception as e:
            print(f"Error al establecer thumbnail: {e}")
    
    def set_safe_image(self, embed, image_param, guild, user):
        try:
            if image_param == "{servericon}":
                if guild and guild.icon:
                    embed.set_image(url=guild.icon.url)
            elif image_param == "{useravatar}":
                if user and hasattr(user, "avatar") and user.avatar:
                    embed.set_image(url=user.avatar.url)
            elif self.is_valid_url(image_param):
                embed.set_image(url=image_param)
        except Exception as e:
            print(f"Error al establecer imagen: {e}")
        
    async def send_embed_log_new(self, log_type, message_config, replacements, log_channel, **kwargs):
        try:
            from commands.configuration.configlogs_constants import COLORS
            
            color_name = message_config.get("color", "default")
            try:
                color_value = COLORS.get(color_name, COLORS["default"])[0] if color_name in COLORS else 0x3498db
            except (KeyError, IndexError, TypeError):
                color_value = 0x3498db
            
            embed = discord.Embed(
                title=self.replace_variables(message_config.get("title", ""), replacements),
                description=self.replace_variables(message_config.get("description", ""), replacements),
                color=color_value
            )

            if message_config.get("footer"):
                footer_text = self.replace_variables(message_config["footer"], replacements)
                embed.set_footer(text=footer_text)

            guild = self.get_guild_from_kwargs(kwargs)
            user = self.get_user_from_kwargs(kwargs)

            if message_config.get("thumbnail", {}).get("has", False):
                thumbnail_param = message_config["thumbnail"].get("param", "")
                if thumbnail_param:
                    self.set_safe_thumbnail(embed, thumbnail_param, guild, user)

            if message_config.get("image", {}).get("has", False):
                image_param = message_config["image"].get("param", "")
                if image_param:
                    self.set_safe_image(embed, image_param, guild, user)

            if message_config.get("fields") and isinstance(message_config["fields"], dict):
                sorted_fields = []
                for field_id, field_data in message_config["fields"].items():
                    try:
                        field_num = int(field_id) if field_id.isdigit() else float('inf')
                        field_name = self.replace_variables(field_data.get("name", ""), replacements)
                        field_value = self.replace_variables(field_data.get("value", ""), replacements)
                        field_inline = field_data.get("inline", False)

                        if not field_name.strip() and not field_value.strip():
                            continue

                        if not field_name.strip():
                            field_name = "\u200b"
                        if not field_value.strip():
                            field_value = "\u200b"
                        
                        sorted_fields.append((field_num, {
                            "name": field_name,
                            "value": field_value,
                            "inline": field_inline
                        }))
                    except Exception as e:
                        print(f"Error procesando campo {field_id}: {e}")

                sorted_fields.sort(key=lambda x: x[0])

                for field_num, field_attrs in sorted_fields:
                    try:
                        embed.add_field(
                            name=field_attrs["name"],
                            value=field_attrs["value"],
                            inline=field_attrs["inline"]
                        )
                    except Exception as e:
                        print(f"Error al añadir campo al embed: {e}")

            embed.timestamp = discord.utils.utcnow()

            view = None
            if log_type == "edited_msg":
                message = kwargs.get("message") or kwargs.get("after_message")
                if message and hasattr(message, "jump_url"):
                    view = discord.ui.View()
                    view.add_item(discord.ui.Button(
                        label="Ir al mensaje",
                        url=message.jump_url,
                        style=discord.ButtonStyle.link
                    ))

            await log_channel.send(embed=embed, view=view)
            
        except Exception as e:
            print(f"Error al enviar el log embed (nuevo formato): {e}")
            import traceback
            traceback.print_exc()
    
    async def send_normal_log_new(self, log_type, message_config, replacements, log_channel, **kwargs):
        try:
            message_text = message_config.get("message", "")
            if not message_text:
                print(f"No hay mensaje configurado para el log {log_type}")
                return

            content = self.replace_variables(message_text, replacements)

            chunks = self.chunk_message(content, self.max_message_length)

            for chunk in chunks:
                await log_channel.send(chunk)
                
        except Exception as e:
            print(f"Error al enviar el log normal (nuevo formato): {e}")
    
    async def send_embed_log_new(self, log_type, message_config, replacements, log_channel, **kwargs):
        try:
            from commands.configuration.configlogs_constants import COLORS
            
            color_name = message_config.get("color", "default")
            try:
                color_value = COLORS.get(color_name, COLORS["default"])[0] if color_name in COLORS else 0x3498db
            except (KeyError, IndexError, TypeError):
                color_value = 0x3498db
            
            embed = discord.Embed(
                title=self.replace_variables(message_config.get("title", ""), replacements),
                description=self.replace_variables(message_config.get("description", ""), replacements),
                color=color_value
            )

            if message_config.get("footer"):
                footer_text = self.replace_variables(message_config["footer"], replacements)
                embed.set_footer(text=footer_text)

            guild = self.get_guild_from_kwargs(kwargs)
            user = self.get_user_from_kwargs(kwargs)

            if message_config.get("thumbnail", {}).get("has", False):
                thumbnail_param = message_config["thumbnail"].get("param", "")
                if thumbnail_param:
                    self.set_safe_thumbnail(embed, thumbnail_param, guild, user)

            if message_config.get("image", {}).get("has", False):
                image_param = message_config["image"].get("param", "")
                if image_param:
                    self.set_safe_image(embed, image_param, guild, user)

            if "fields" in message_config:
                fields_data = message_config["fields"]

                if isinstance(fields_data, list):
                    for i, field_data in enumerate(fields_data):
                        try:
                            if field_data is None or not isinstance(field_data, dict):
                                continue
                            
                            field_name = self.replace_variables(field_data.get("name", ""), replacements)
                            field_value = self.replace_variables(field_data.get("value", ""), replacements)

                            if not field_name and not field_value:
                                continue

                            if not field_name:
                                field_name = "\u200b"
                            if not field_value:
                                field_value = "\u200b"
                            
                            field_inline = field_data.get("inline", False)
                            if isinstance(field_inline, str):
                                field_inline = field_inline.lower() in ["true", "yes", "1", "si", "sí"]
                            
                            embed.add_field(
                                name=field_name,
                                value=field_value,
                                inline=bool(field_inline)
                            )
                        except Exception as e:
                            print(f"Error procesando field {i}: {e}")
                            import traceback
                            traceback.print_exc()

                elif isinstance(fields_data, dict):
                    sorted_fields = []
                    for field_id, field_data in fields_data.items():
                        try:
                            field_num = int(field_id) if field_id.isdigit() else float('inf')
                            
                            if not isinstance(field_data, dict):
                                continue
                            
                            field_name = self.replace_variables(field_data.get("name", ""), replacements)
                            field_value = self.replace_variables(field_data.get("value", ""), replacements)
                            
                            if not field_name and not field_value:
                                continue
                            
                            if not field_name:
                                field_name = "\u200b"
                            if not field_value:
                                field_value = "\u200b"

                            field_inline = field_data.get("inline", False)
                            if isinstance(field_inline, str):
                                field_inline = field_inline.lower() in ["true", "yes", "1", "si", "sí"]
                            
                            sorted_fields.append((field_num, {
                                "name": field_name,
                                "value": field_value,
                                "inline": bool(field_inline)
                            }))
                        except Exception as e:
                            print(f"Error procesando field {field_id}: {e}")
                            import traceback
                            traceback.print_exc()
                    
                    sorted_fields.sort(key=lambda x: x[0])
                    
                    for field_num, field_attrs in sorted_fields:
                        try:
                            embed.add_field(
                                name=field_attrs["name"],
                                value=field_attrs["value"],
                                inline=field_attrs["inline"]
                            )
                        except Exception as e:
                            print(f"Error añadiendo field al embed: {e}")
                            import traceback
                            traceback.print_exc()

            embed.timestamp = discord.utils.utcnow()

            view = None
            if log_type == "edited_msg":
                message = kwargs.get("message") or kwargs.get("after_message")
                if message and hasattr(message, "jump_url"):
                    view = discord.ui.View()
                    view.add_item(discord.ui.Button(
                        label="Ir al mensaje",
                        url=message.jump_url,
                        style=discord.ButtonStyle.link
                    ))

            await log_channel.send(embed=embed, view=view)
            
        except Exception as e:
            print(f"Error al enviar el log embed (nuevo formato): {e}")
            import traceback
            traceback.print_exc()
    
    async def send_normal_log(self, log_type, message_format, replacements, log_channel, **kwargs):
        try:
            message_with_newlines = message_format.replace(r"{\n}", "\n").replace("{\\n}", "\n")

            content = self.replace_variables(message_with_newlines, replacements)

            chunks = self.chunk_message(content, self.max_message_length)

            for chunk in chunks:
                await log_channel.send(chunk)
                
        except Exception as e:
            print(f"Error al enviar el log normal (formato antiguo): {e}")
    
    async def create_deleted_message_log(self, message_format, message, del_msg_content):
        try:
            if not del_msg_content:
                del_msg_content = "No hay contenido del mensaje"
                
            attachments = self.format_attachments(message.attachments)
            
            replacements = {
                "{user}": message.author.mention,
                "{userid}": str(message.author.id),
                "{usertag}": str(message.author),
                "{channel}": message.channel.mention,
                "{channelid}": str(message.channel.id),
                "{del_msg}": del_msg_content,
                "{attached}": attachments
            }

            if isinstance(message_format, dict):
                if message_format.get("embed", False):
                    from commands.configuration.configlogs_constants import COLORS

                    color_name = message_format.get("color", "default")
                    try:
                        color_value = COLORS.get(color_name, COLORS["default"])[0] if color_name in COLORS else 0x3498db
                    except (KeyError, IndexError, TypeError):
                        color_value = 0x3498db

                    title = self.replace_variables(message_format.get("title", ""), replacements)
                    description = self.replace_variables(message_format.get("description", ""), replacements)
                    footer = self.replace_variables(message_format.get("footer", ""), replacements)
                    
                    embed = discord.Embed(
                        title=title,
                        description=description,
                        color=color_value,
                        timestamp=discord.utils.utcnow()
                    )
                    
                    if footer:
                        embed.set_footer(text=footer)

                    if message_format.get("thumbnail", {}).get("has", False):
                        thumbnail_param = message_format["thumbnail"].get("param", "")
                        if thumbnail_param:
                            self.set_safe_thumbnail(embed, thumbnail_param, message.guild, message.author)

                    if message_format.get("image", {}).get("has", False):
                        image_param = message_format["image"].get("param", "")
                        if image_param:
                            self.set_safe_image(embed, image_param, message.guild, message.author)
                    
                    if "fields" in message_format:
                        fields_data = message_format["fields"]

                        if isinstance(fields_data, list):
                            for i, field_data in enumerate(fields_data):
                                try:
                                    if field_data is None or not isinstance(field_data, dict):
                                        continue
                                    
                                    field_name = self.replace_variables(field_data.get("name", ""), replacements)
                                    field_value = self.replace_variables(field_data.get("value", ""), replacements)

                                    if not field_name and not field_value:
                                        continue

                                    if not field_name:
                                        field_name = "\u200b"
                                    if not field_value:
                                        field_value = "\u200b"

                                    field_inline = field_data.get("inline", False)
                                    if isinstance(field_inline, str):
                                        field_inline = field_inline.lower() in ["true", "yes", "1", "si", "sí"]
                                    
                                    embed.add_field(
                                        name=field_name,
                                        value=field_value,
                                        inline=bool(field_inline)
                                    )
                                except Exception as e:
                                    print(f"Error procesando field {i}: {e}")
                                    import traceback
                                    traceback.print_exc()
                        
                        elif isinstance(fields_data, dict):
                            sorted_fields = []
                            for field_id, field_data in fields_data.items():
                                try:
                                    field_num = int(field_id) if field_id.isdigit() else float('inf')

                                    if not isinstance(field_data, dict):
                                        continue
                                    
                                    field_name = self.replace_variables(field_data.get("name", ""), replacements)
                                    field_value = self.replace_variables(field_data.get("value", ""), replacements)
                                    
                                    if not field_name and not field_value:
                                        continue

                                    if not field_name:
                                        field_name = "\u200b"
                                    if not field_value:
                                        field_value = "\u200b"

                                    field_inline = field_data.get("inline", False)
                                    if isinstance(field_inline, str):
                                        field_inline = field_inline.lower() in ["true", "yes", "1", "si", "sí"]
                                    
                                    sorted_fields.append((field_num, {
                                        "name": field_name,
                                        "value": field_value,
                                        "inline": bool(field_inline)
                                    }))
                                except Exception as e:
                                    print(f"Error procesando field {field_id}: {e}")
                                    import traceback
                                    traceback.print_exc()
                            
                            sorted_fields.sort(key=lambda x: x[0])
                            
                            for field_num, field_attrs in sorted_fields:
                                try:
                                    embed.add_field(
                                        name=field_attrs["name"],
                                        value=field_attrs["value"],
                                        inline=field_attrs["inline"]
                                    )
                                except Exception as e:
                                    print(f"Error al añadir field al embed: {e}")
                                    import traceback
                                    traceback.print_exc()
                    
                    return {"embed": embed}
                else:
                    message_text = message_format.get("message", "")
                    if not message_text:
                        return {"content": "No hay mensaje configurado"}

                    content = self.replace_variables(message_text, replacements)
                    return {"content": content}
            else:
                result = message_format.replace(r"{\n}", "\n").replace("{\\n}", "\n")
                for key, value in replacements.items():
                    result = result.replace(key, str(value))
                
                if message_format.startswith("embed:"):
                    parts = result[6:].split(" ")
                    embed_data = {}
                    current_key = None
                    current_value = []
                    
                    for part in parts:
                        if part.startswith("tl:"):
                            if current_key:
                                embed_data[current_key] = " ".join(current_value)
                            current_key = "title"
                            current_value = [part[3:]]
                        elif part.startswith("dp:"):
                            if current_key:
                                embed_data[current_key] = " ".join(current_value)
                            current_key = "description"
                            current_value = [part[3:]]
                        elif part.startswith("ft:"):
                            if current_key:
                                embed_data[current_key] = " ".join(current_value)
                            current_key = "footer"
                            current_value = [part[3:]]
                        else:
                            current_value.append(part)
                    
                    if current_key:
                        embed_data[current_key] = " ".join(current_value)
                    
                    embed = discord.Embed(color=discord.Color.blue())
                    
                    if "title" in embed_data:
                        embed.title = embed_data["title"]
                    if "description" in embed_data:
                        embed.description = embed_data["description"]
                    if "footer" in embed_data:
                        embed.set_footer(text=embed_data["footer"])
                    
                    embed.timestamp = discord.utils.utcnow()
                    
                    return {"embed": embed}
                else:
                    return {"content": result}
                
        except Exception as e:
            print(f"Error creando log de mensaje eliminado: {e}")
            import traceback
            traceback.print_exc()
            return {"content": "Error al procesar el log del mensaje eliminado."}