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
        url_pattern = re.compile(
            r'^(https?://)?'
            r'([a-zA-Z0-9]+\.)+[a-zA-Z]{2,}'
            r'(/[a-zA-Z0-9._~:/?#[\]@!$&\'()*+,;=]*)?'
            r'$'
        )
        return bool(url_pattern.match(url))
    
    def is_valid_image_param(self, param):
        return param in VALID_IMAGE_PARAMS or self.is_valid_url(param)
    
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
    
    async def send_embed_log_new(self, log_type, message_config, replacements, log_channel, **kwargs):
        try:
            from commands.configuration.configlogs_constants import COLORS
            
            color_name = message_config.get("color", "default")
            color_value = COLORS.get(color_name, COLORS["default"])[0] if color_name else 0x3498db
            
            embed = discord.Embed(
                title=self.replace_variables(message_config.get("title", ""), replacements),
                description=self.replace_variables(message_config.get("description", ""), replacements),
                color=color_value
            )

            if message_config.get("footer"):
                footer_text = self.replace_variables(message_config["footer"], replacements)
                embed.set_footer(text=footer_text)

            if message_config.get("thumbnail", {}).get("has", False):
                thumbnail_param = message_config["thumbnail"].get("param", "")
                if thumbnail_param:
                    if thumbnail_param == "{servericon}" and kwargs.get("guild") and kwargs["guild"].icon:
                        embed.set_thumbnail(url=kwargs["guild"].icon.url)
                    elif thumbnail_param == "{useravatar}":
                        target = kwargs.get("target") or kwargs.get("member") or kwargs.get("user")
                        if target and target.avatar:
                            embed.set_thumbnail(url=target.avatar.url)
                    elif self.is_valid_url(thumbnail_param):
                        embed.set_thumbnail(url=thumbnail_param)

            if message_config.get("image", {}).get("has", False):
                image_param = message_config["image"].get("param", "")
                if image_param:
                    if image_param == "{servericon}" and kwargs.get("guild") and kwargs["guild"].icon:
                        embed.set_image(url=kwargs["guild"].icon.url)
                    elif image_param == "{useravatar}":
                        target = kwargs.get("target") or kwargs.get("member") or kwargs.get("user")
                        if target and target.avatar:
                            embed.set_image(url=target.avatar.url)
                    elif self.is_valid_url(image_param):
                        embed.set_image(url=image_param)

            if message_config.get("fields") and isinstance(message_config["fields"], dict):
                sorted_fields = sorted(message_config["fields"].items(), key=lambda x: int(x[0]) if x[0].isdigit() else x[0])
                for field_id, field_data in sorted_fields:
                    field_name = self.replace_variables(field_data.get("name", ""), replacements)
                    field_value = self.replace_variables(field_data.get("value", ""), replacements)
                    field_inline = field_data.get("inline", False)
                    
                    embed.add_field(
                        name=field_name,
                        value=field_value,
                        inline=field_inline
                    )
            
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
    
    async def send_embed_log(self, log_type, message_format, replacements, log_channel, **kwargs):
        try:
            temp_marker = "__NEWLINE__"
            processed_format = message_format.replace(r"{\n}", temp_marker).replace("{\\n}", temp_marker)
            
            parts = processed_format[6:].split(" ")
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
                title_with_markers = embed_data["title"].replace(temp_marker, "\n")
                title = self.replace_variables(title_with_markers, replacements)
                embed.title = title
            
            if "description" in embed_data:
                desc_with_markers = embed_data["description"].replace(temp_marker, "\n")
                description = self.replace_variables(desc_with_markers, replacements)
                embed.description = description

            if "footer" in embed_data:
                footer_with_markers = embed_data["footer"].replace(temp_marker, "\n")
                footer = self.replace_variables(footer_with_markers, replacements)
                embed.set_footer(text=footer)

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
            print(f"Error al enviar el log embed (formato antiguo): {e}")
    
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
                "{channelid}": str(message.channel.id)
            }

            if isinstance(message_format, dict):
                if message_format.get("embed", False):
                    from commands.configuration.configlogs_constants import COLORS

                    color_name = message_format.get("color", "default")
                    color_value = COLORS.get(color_name, COLORS["default"])[0] if color_name else 0x3498db

                    title = self.replace_variables(message_format.get("title", ""), replacements)
                    description = self.replace_variables(message_format.get("description", ""), replacements)
                    footer = self.replace_variables(message_format.get("footer", ""), replacements)

                    description = description.replace("{del_msg}", del_msg_content)
                    description = description.replace("{attached}", attachments)
                    
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
                            if thumbnail_param == "{servericon}" and message.guild and message.guild.icon:
                                embed.set_thumbnail(url=message.guild.icon.url)
                            elif thumbnail_param == "{useravatar}" and message.author.avatar:
                                embed.set_thumbnail(url=message.author.avatar.url)
                            elif self.is_valid_url(thumbnail_param):
                                embed.set_thumbnail(url=thumbnail_param)

                    if message_format.get("image", {}).get("has", False):
                        image_param = message_format["image"].get("param", "")
                        if image_param:
                            if image_param == "{servericon}" and message.guild and message.guild.icon:
                                embed.set_image(url=message.guild.icon.url)
                            elif image_param == "{useravatar}" and message.author.avatar:
                                embed.set_image(url=message.author.avatar.url)
                            elif self.is_valid_url(image_param):
                                embed.set_image(url=image_param)
                    
                    if message_format.get("fields") and isinstance(message_format["fields"], dict):
                        sorted_fields = sorted(message_format["fields"].items(), key=lambda x: int(x[0]) if x[0].isdigit() else x[0])
                        for field_id, field_data in sorted_fields:
                            field_name = self.replace_variables(field_data.get("name", ""), replacements)
                            field_value = self.replace_variables(field_data.get("value", ""), replacements)

                            field_name = field_name.replace("{del_msg}", del_msg_content)
                            field_name = field_name.replace("{attached}", attachments)
                            field_value = field_value.replace("{del_msg}", del_msg_content)
                            field_value = field_value.replace("{attached}", attachments)
                            
                            field_inline = field_data.get("inline", False)
                            
                            embed.add_field(
                                name=field_name,
                                value=field_value,
                                inline=field_inline
                            )
                    
                    return {"embed": embed}
                else:
                    message_text = message_format.get("message", "")
                    if not message_text:
                        return {"content": "No hay mensaje configurado"}

                    content = self.replace_variables(message_text, replacements)

                    content = content.replace("{del_msg}", del_msg_content)
                    content = content.replace("{attached}", attachments)
                    
                    return {"content": content}
            else:
                result = message_format.replace(r"{\n}", "\n").replace("{\\n}", "\n")
                for key, value in replacements.items():
                    result = result.replace(key, str(value))
                
                result = result.replace("{del_msg}", del_msg_content)
                result = result.replace("{attached}", attachments)
                
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
            return {"content": "Error al procesar el log del mensaje eliminado."}