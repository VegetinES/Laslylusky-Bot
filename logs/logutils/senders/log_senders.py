import discord

async def send_embed_log_new(parser, log_type, message_config, replacements, log_channel, **kwargs):
    try:
        from commands.configuration.configlogs_constants import COLORS
        
        color_name = message_config.get("color", "default")
        try:
            color_value = COLORS.get(color_name, COLORS["default"])[0] if color_name in COLORS else 0x3498db
        except (KeyError, IndexError, TypeError):
            color_value = 0x3498db
        
        embed = discord.Embed(
            title=parser.replace_variables(message_config.get("title", ""), replacements),
            description=parser.replace_variables(message_config.get("description", ""), replacements),
            color=color_value
        )

        if message_config.get("footer"):
            footer_text = parser.replace_variables(message_config["footer"], replacements)
            embed.set_footer(text=footer_text)

        guild = parser.get_guild_from_kwargs(kwargs)
        user = parser.get_user_from_kwargs(kwargs)

        if message_config.get("thumbnail", {}).get("has", False):
            thumbnail_param = message_config["thumbnail"].get("param", "")
            if thumbnail_param:
                parser.set_safe_thumbnail(embed, thumbnail_param, guild, user)

        if message_config.get("image", {}).get("has", False):
            image_param = message_config["image"].get("param", "")
            if image_param:
                parser.set_safe_image(embed, image_param, guild, user)

        if "fields" in message_config:
            fields_data = message_config["fields"]

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

async def send_normal_log_new(parser, log_type, message_config, replacements, log_channel, **kwargs):
    try:
        message_text = message_config.get("message", "")
        if not message_text:
            print(f"No hay mensaje configurado para el log {log_type}")
            return

        content = parser.replace_variables(message_text, replacements)

        chunks = parser.chunk_message(content, parser.max_message_length)

        for chunk in chunks:
            await log_channel.send(chunk)
            
    except Exception as e:
        print(f"Error al enviar el log normal (nuevo formato): {e}")

async def send_embed_log(parser, log_type, message_format, replacements, log_channel, **kwargs):
    try:
        embed_text = message_format[6:]

        parts = []
        current_part = ""
        current_type = None
        
        for word in embed_text.split():
            if word.startswith("tl:"):
                if current_type:
                    parts.append((current_type, current_part))
                current_type = "title"
                current_part = word[3:]
            elif word.startswith("dp:"):
                if current_type:
                    parts.append((current_type, current_part))
                current_type = "description"
                current_part = word[3:]
            elif word.startswith("ft:"):
                if current_type:
                    parts.append((current_type, current_part))
                current_type = "footer"
                current_part = word[3:]
            else:
                if current_part:
                    current_part += " " + word
                else:
                    current_part = word
        
        if current_type and current_part:
            parts.append((current_type, current_part))

        embed = discord.Embed(color=discord.Color.blue())
        embed.timestamp = discord.utils.utcnow()
        
        for part_type, part_text in parts:
            part_text = parser.replace_variables(part_text, replacements)
            if part_type == "title":
                embed.title = part_text
            elif part_type == "description":
                embed.description = part_text
            elif part_type == "footer":
                embed.set_footer(text=part_text)

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
        import traceback
        traceback.print_exc()

async def send_normal_log(parser, log_type, message_format, replacements, log_channel, **kwargs):
    try:
        message_with_newlines = message_format.replace(r"{\n}", "\n").replace("{\\n}", "\n")

        content = parser.replace_variables(message_with_newlines, replacements)

        chunks = parser.chunk_message(content, parser.max_message_length)

        for chunk in chunks:
            await log_channel.send(chunk)
            
    except Exception as e:
        print(f"Error al enviar el log normal (formato antiguo): {e}")