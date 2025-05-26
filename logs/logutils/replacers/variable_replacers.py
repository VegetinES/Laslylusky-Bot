import time

def get_user_from_kwargs(kwargs):
    for key in ["target", "member", "user", "author", "after_message"]:
        if key in kwargs and kwargs[key]:
            return kwargs[key]
    
    if "message" in kwargs and kwargs["message"]:
        return kwargs["message"].author
    
    return None

def get_guild_from_kwargs(kwargs):
    if "guild" in kwargs and kwargs["guild"]:
        return kwargs["guild"]

    for key in ["member", "message", "after_message"]:
        if key in kwargs and kwargs[key] and hasattr(kwargs[key], "guild"):
            return kwargs[key].guild
    
    return None

def get_replacements(log_type, **kwargs):
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
            
            format_attachments_func = get_format_attachments()
            attachments = format_attachments_func(message.attachments)
            
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
            format_attachments_func = get_format_attachments()
            attachments = format_attachments_func(message.attachments)
            
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
    
    elif log_type == "vc_enter":
        member = kwargs.get("member")
        voice_channel = kwargs.get("voice_channel")
        
        if member:
            replacements.update({
                "{userid}": str(member.id),
                "{usertag}": str(member),
                "{user}": member.mention
            })
        
        if voice_channel:
            replacements.update({
                "{channel}": voice_channel.mention,
                "{channelid}": str(voice_channel.id)
            })
    
    elif log_type == "vc_leave":
        member = kwargs.get("member")
        voice_channel = kwargs.get("voice_channel")
        
        if member:
            replacements.update({
                "{userid}": str(member.id),
                "{usertag}": str(member),
                "{user}": member.mention
            })
        
        if voice_channel:
            replacements.update({
                "{channel}": voice_channel.mention,
                "{channelid}": str(voice_channel.id)
            })
    
    elif log_type == "add_usr_rol":
        member = kwargs.get("member")
        role = kwargs.get("role")
        
        if member:
            replacements.update({
                "{userid}": str(member.id),
                "{usertag}": str(member),
                "{user}": member.mention
            })
        
        if role:
            replacements.update({
                "{role}": role.mention,
                "{roleid}": str(role.id)
            })
    
    elif log_type == "rm_usr_rol":
        member = kwargs.get("member")
        role = kwargs.get("role")
        
        if member:
            replacements.update({
                "{userid}": str(member.id),
                "{usertag}": str(member),
                "{user}": member.mention
            })
        
        if role:
            replacements.update({
                "{role}": role.mention,
                "{roleid}": str(role.id)
            })
    
    elif log_type == "add_ch":
        channel = kwargs.get("channel")
        category = kwargs.get("category")
        
        if channel:
            replacements.update({
                "{channel}": channel.mention,
                "{channelid}": str(channel.id)
            })
        
        if category:
            replacements["{category}"] = category.name
        else:
            replacements["{category}"] = "Sin categoría"
    
    elif log_type == "del_ch":
        channel = kwargs.get("channel")
        category = kwargs.get("category")
        
        if channel:
            replacements.update({
                "{channel}": f"#{getattr(channel, 'name', 'desconocido')}",
                "{channelid}": str(channel.id)
            })
        
        if category:
            replacements["{category}"] = category.name
        else:
            replacements["{category}"] = "Sin categoría"
    
    elif log_type == "mod_ch":
        channel = kwargs.get("channel")
        
        if channel:
            replacements.update({
                "{channel}": channel.mention,
                "{channelid}": str(channel.id)
            })

    elif log_type == "add_cat":
        category = kwargs.get("category")
        perms = kwargs.get("perms", "No hay permisos personalizados configurados.")
        
        if category:
            replacements.update({
                "{category}": category.name,
                "{categoryid}": str(category.id),
                "{perms}": perms
            })

    elif log_type == "del_cat":
        category = kwargs.get("category")
        
        if category:
            replacements.update({
                "{category}": category.name,
                "{categoryid}": str(category.id)
            })

    elif log_type == "mod_cat":
        category = kwargs.get("category")
        
        if category:
            replacements.update({
                "{category}": category.name,
                "{categoryid}": str(category.id)
            })
    
    elif log_type == "changed_av":
        user = kwargs.get("user")
        old_avatar = kwargs.get("old_avatar")
        new_avatar = kwargs.get("new_avatar")
        old_name = kwargs.get("old_name")
        new_name = kwargs.get("new_name")
        
        if user:
            replacements.update({
                "{userid}": str(user.id),
                "{usertag}": str(user),
                "{user}": user.mention
            })
        
        if old_avatar:
            replacements["{old_avatar_link}"] = f"[antiguo avatar]({old_avatar})"
        else:
            replacements["{old_avatar_link}"] = ""
        
        if new_avatar:
            replacements["{new_avatar_link}"] = f"[nuevo avatar]({new_avatar})"
        else:
            replacements["{new_avatar_link}"] = ""
        
        replacements["{old_name}"] = old_name if old_name else "El nombre no cambió"
        replacements["{new_name}"] = new_name if new_name else "El nombre no cambió"
    
    return replacements

def replace_variables(text, replacements):
    if not text:
        return ""
        
    result = text.replace(r"{\n}", "\n").replace("{\\n}", "\n")
    
    for key, value in replacements.items():
        result = result.replace(key, str(value))
        
    return result

def format_attachments_fallback(attachments):
    if not attachments:
        return "No hay adjuntos"
    
    result = []
    for attachment in attachments:
        url_parts = attachment.url.split('?')
        clean_url = url_parts[0]
        result.append(f"[{attachment.filename}]({clean_url})")
    
    return "\n".join(result)

def get_format_attachments():
    try:
        from logs.logutils.helpers.format_helpers import format_attachments
        return format_attachments
    except ImportError:
        print("Error importando format_attachments, usando implementación de respaldo")
        return format_attachments_fallback