def process_field_attributes(field_data, replacements):
    try:
        if not isinstance(field_data, dict):
            return None
        
        field_name_raw = field_data.get("name", "")
        field_name = replace_variables(field_name_raw, replacements)
        
        if not field_name:
            field_name = "\u200b"
        
        field_value_raw = field_data.get("value", "")
        field_value = replace_variables(field_value_raw, replacements)
        
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

def set_safe_thumbnail(embed, thumbnail_param, guild, user):
    try:
        if thumbnail_param == "{servericon}":
            if guild and guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
        elif thumbnail_param == "{useravatar}":
            if user and hasattr(user, "avatar") and user.avatar:
                embed.set_thumbnail(url=user.avatar.url)
        elif is_valid_url(thumbnail_param):
            embed.set_thumbnail(url=thumbnail_param)
    except Exception as e:
        print(f"Error al establecer thumbnail: {e}")

def set_safe_image(embed, image_param, guild, user):
    try:
        if image_param == "{servericon}":
            if guild and guild.icon:
                embed.set_image(url=guild.icon.url)
        elif image_param == "{useravatar}":
            if user and hasattr(user, "avatar") and user.avatar:
                embed.set_image(url=user.avatar.url)
        elif is_valid_url(image_param):
            embed.set_image(url=image_param)
    except Exception as e:
        print(f"Error al establecer imagen: {e}")

def replace_variables(text, replacements):
    if not text:
        return ""
        
    result = text.replace(r"{\n}", "\n").replace("{\\n}", "\n")
    
    for key, value in replacements.items():
        result = result.replace(key, str(value))
        
    return result

def is_valid_url(url):
    import re
    if not url:
        return False
        
    url_pattern = re.compile(
        r'^(https?://)?'
        r'([a-zA-Z0-9]+\.)+[a-zA-Z]{2,}'
        r'(/[a-zA-Z0-9._~:/?#[\]@!$&\'()*+,;=]*)?'
        r'$'
    )
    return bool(url_pattern.match(url))