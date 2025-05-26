import discord
import json
import io

def create_embed_from_data(embed_data):
    if not isinstance(embed_data, dict):
        return None
    
    embed = discord.Embed()
    
    if "title" in embed_data and embed_data["title"] and embed_data["title"].strip():
        embed.title = embed_data["title"]
    
    if "description" in embed_data and embed_data["description"] and embed_data["description"].strip():
        embed.description = embed_data["description"]
    
    if "url" in embed_data and embed_data["url"] and embed_data["url"].strip():
        embed.url = embed_data["url"]
    
    if "color" in embed_data:
        embed.color = discord.Color(embed_data["color"])
    
    if "author" in embed_data and embed_data["author"].get("name"):
        author = embed_data["author"]
        embed.set_author(
            name=author.get("name"),
            url=author.get("url") or None,
            icon_url=author.get("icon_url") or None
        )
    
    if "fields" in embed_data:
        for field in embed_data["fields"]:
            if field.get("name") and field.get("value"):
                embed.add_field(
                    name=field.get("name", ""),
                    value=field.get("value", ""),
                    inline=field.get("inline", False)
                )
    
    if "image" in embed_data and embed_data["image"].get("url"):
        embed.set_image(url=embed_data["image"]["url"])
    
    if "thumbnail" in embed_data and embed_data["thumbnail"].get("url"):
        embed.set_thumbnail(url=embed_data["thumbnail"]["url"])
    
    if "footer" in embed_data and embed_data["footer"].get("text"): 
        footer = embed_data["footer"]
        embed.set_footer(
            text=footer.get("text"),
            icon_url=footer.get("icon_url") or None
        )
    
    if "timestamp" in embed_data and embed_data["timestamp"]:
        embed.timestamp = discord.utils.utcnow()
    
    return embed

def create_view_from_data(view_data):
    return None

def embed_to_dict(embed):
    result = {}
    
    if embed.title:
        result["title"] = embed.title
    
    if embed.description:
        result["description"] = embed.description
    
    if embed.url:
        result["url"] = embed.url
    
    if embed.color:
        result["color"] = embed.color.value
    
    if embed.timestamp:
        result["timestamp"] = True
    
    if embed.author:
        result["author"] = {
            "name": embed.author.name,
            "url": embed.author.url,
            "icon_url": embed.author.icon_url
        }
    
    if embed.fields:
        result["fields"] = []
        for field in embed.fields:
            result["fields"].append({
                "name": field.name,
                "value": field.value,
                "inline": field.inline
            })
    
    if embed.image:
        result["image"] = {"url": embed.image.url}
    
    if embed.thumbnail:
        result["thumbnail"] = {"url": embed.thumbnail.url}
    
    if embed.footer:
        result["footer"] = {
            "text": embed.footer.text,
            "icon_url": embed.footer.icon_url
        }
    
    return result

def save_embed_to_json(content, embeds, webhook_url=None, webhook_name=None, webhook_avatar=None, message_id=None, attachments=None):
    data = {
        "content": content,
        "embeds": [embed_to_dict(embed) for embed in embeds]
    }
    
    if webhook_url:
        data["webhook_url"] = webhook_url
    
    if webhook_name:
        data["webhook_name"] = webhook_name
    
    if webhook_avatar:
        data["webhook_avatar"] = webhook_avatar
    
    if message_id:
        data["message_id"] = message_id
    
    if attachments:
        data["attachments"] = attachments
    
    json_data = json.dumps(data, indent=4)
    return json_data

def load_embed_from_json(json_string):
    data = json.loads(json_string)
    
    embeds = []
    for embed_data in data.get("embeds", []):
        embed = create_embed_from_data(embed_data)
        if embed:
            embeds.append(embed)
    
    return {
        "content": data.get("content"),
        "embeds": embeds,
        "webhook_url": data.get("webhook_url"),
        "webhook_name": data.get("webhook_name"),
        "webhook_avatar": data.get("webhook_avatar"),
        "message_id": data.get("message_id"),
        "attachments": data.get("attachments", [])
    }