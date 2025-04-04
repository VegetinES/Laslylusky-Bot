import discord

async def create_deleted_message_log(parser, message_format, message, del_msg_content):
    try:
        if not del_msg_content:
            del_msg_content = "No hay contenido del mensaje"
            
        attachments = parser.format_attachments(message.attachments)
        
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

                title = parser.replace_variables(message_format.get("title", ""), replacements)
                description = parser.replace_variables(message_format.get("description", ""), replacements)
                footer = parser.replace_variables(message_format.get("footer", ""), replacements)
                
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
                        parser.set_safe_thumbnail(embed, thumbnail_param, message.guild, message.author)

                if message_format.get("image", {}).get("has", False):
                    image_param = message_format["image"].get("param", "")
                    if image_param:
                        parser.set_safe_image(embed, image_param, message.guild, message.author)
                
                if "fields" in message_format:
                    fields_data = message_format["fields"]

                    if isinstance(fields_data, list):
                        for i, field_data in enumerate(fields_data):
                            try:
                                if field_data is None or not isinstance(field_data, dict):
                                    continue
                                
                                field_name = parser.replace_variables(field_data.get("name", ""), replacements)
                                field_value = parser.replace_variables(field_data.get("value", ""), replacements)

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
                                
                                field_name = parser.replace_variables(field_data.get("name", ""), replacements)
                                field_value = parser.replace_variables(field_data.get("value", ""), replacements)
                                
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

                content = parser.replace_variables(message_text, replacements)
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