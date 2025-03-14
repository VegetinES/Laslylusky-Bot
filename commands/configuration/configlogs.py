import discord
from discord.ext import commands
from database.get import get_specific_field
from database.update import update_server_data
import re

LOG_TYPES = {
    "ban": {
        "params": ["{userid}", "{usertag}", "{mod}", "{modid}", "{modtag}", "{reason}"],
        "footer_params": ["{userid}", "{usertag}", "{modid}", "{modtag}"],
        "needs_limit": False
    },
    "kick": {
        "params": ["{userid}", "{usertag}", "{mod}", "{modid}", "{modtag}", "{reason}"],
        "footer_params": ["{userid}", "{usertag}", "{modid}", "{modtag}"],
        "needs_limit": False
    },
    "unban": {
        "params": ["{userid}", "{usertag}", "{modtag}", "{modid}", "{mod}"],
        "footer_params": ["{userid}", "{usertag}", "{modtag}", "{modid}"],
        "needs_limit": False
    },
    "enter": {
        "params": ["{userid}", "{usertag}", "{user}", "{accage}"],
        "footer_params": ["{userid}", "{usertag}", "{user}"],
        "needs_limit": False
    },
    "leave": {
        "params": ["{userid}", "{usertag}"],
        "footer_params": ["{userid}", "{usertag}"],
        "needs_limit": False
    },
    "del_msg": {
        "params": ["{del_msg}", "{usertag}", "{userid}", "{user}", "{channel}", "{channelid}"],
        "footer_params": ["{usertag}", "{userid}", "{channelid}"],
        "needs_limit": True
    },
    "edited_msg": {
        "params": ["{user}", "{userid}", "{usertag}", "{channel}", "{channelid}", "{old_msg}", "{new_msg}"],
        "footer_params": ["{userid}", "{usertag}", "{channelid}"],
        "needs_limit": True
    },
    "warn": {
        "params": ["{user}", "{userid}", "{usertag}", "{reason}", "{mod}", "{modtag}", "{modid}"],
        "footer_params": ["{userid}", "{usertag}", "{modid}", "{modtag}"],
        "needs_limit": False
    },
    "unwarn": {
        "params": ["{user}", "{userid}", "{usertag}", "{reason}", "{mod}", "{modtag}", "{modid}"],
        "footer_params": ["{userid}", "{usertag}", "{modid}", "{modtag}"],
        "needs_limit": False
    }
}

MAX_NORMAL_MESSAGE = 1400
MAX_EMBED_TITLE = 60
MAX_EMBED_DESCRIPTION = 200
MAX_EMBED_FOOTER = 30

def process_newlines(text):
    if text is None:
        return None
    return text.replace("{\\n}", "\n")

def validate_message_params(log_type, message, is_footer=False):
    if log_type not in LOG_TYPES:
        return False, f"Tipo de log no válido: {log_type}"

    temp_message = message.replace("{\\n}", "TEMP_NEWLINE_MARKER")
    
    params = re.findall(r'\{[^}]+\}', temp_message)
    
    params = [param.replace("TEMP_NEWLINE_MARKER", "{\\n}") for param in params]
    
    valid_params = LOG_TYPES[log_type]["footer_params"] if is_footer else LOG_TYPES[log_type]["params"]
    valid_params = valid_params + ["{\\n}"]
    
    for param in params:
        if param not in valid_params:
            return False, f"Parámetro no válido para {log_type}: {param}"
    
    return True, "Parámetros válidos"

async def show_config_logs(
    ctx_or_interaction, 
    log_type, 
    estado, 
    canal, 
    tipo_mensaje, 
    mensaje=None,
    título=None,
    descripción=None,
    footer=None,
    límite=None,
    is_prefix_command=False
):
    is_interaction = isinstance(ctx_or_interaction, discord.Interaction)
    
    guild_id = ctx_or_interaction.guild.id
    
    act_commands = get_specific_field(guild_id, "act_cmd")
    
    if act_commands is None:
        embed = discord.Embed(
            title="<:No:825734196256440340> Error de Configuración",
            description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
            color=discord.Color.red()
        )
        await ctx_or_interaction.response.send_message(embed=embed, ephemeral=True)
        return False
    
    if log_type not in LOG_TYPES:
        response = f"Tipo de log no válido. Opciones: {', '.join(LOG_TYPES.keys())}"
        if is_interaction:
            await ctx_or_interaction.response.send_message(response, ephemeral=True)
        else:
            await ctx_or_interaction.send(response)
        return
    
    if estado not in ["activado", "desactivado"]:
        response = "Estado no válido. Debe ser 'activado' o 'desactivado'"
        if is_interaction:
            await ctx_or_interaction.response.send_message(response, ephemeral=True)
        else:
            await ctx_or_interaction.send(response)
        return
    
    if LOG_TYPES[log_type]["needs_limit"]:
        if límite is None:
            response = f"El tipo de log '{log_type}' requiere especificar un límite de días"
            if is_interaction:
                await ctx_or_interaction.response.send_message(response, ephemeral=True)
            else:
                await ctx_or_interaction.send(response)
            return
        
        if not isinstance(límite, int) or límite < 7 or límite > 30:
            response = "El límite debe ser un número entre 7 y 30 días"
            if is_interaction:
                await ctx_or_interaction.response.send_message(response, ephemeral=True)
            else:
                await ctx_or_interaction.send(response)
            return
    
    log_message = ""
    
    if tipo_mensaje.lower() == "normal":
        if not mensaje:
            response = "Debes proporcionar un mensaje para el tipo 'normal'"
            if is_interaction:
                await ctx_or_interaction.response.send_message(response, ephemeral=True)
            else:
                await ctx_or_interaction.send(response)
            return
        
        if len(mensaje) > MAX_NORMAL_MESSAGE:
            response = f"El mensaje normal no puede exceder {MAX_NORMAL_MESSAGE} caracteres"
            if is_interaction:
                await ctx_or_interaction.response.send_message(response, ephemeral=True)
            else:
                await ctx_or_interaction.send(response)
            return
        
        is_valid, error_msg = validate_message_params(log_type, mensaje)
        if not is_valid:
            if is_interaction:
                await ctx_or_interaction.response.send_message(error_msg, ephemeral=True)
            else:
                await ctx_or_interaction.send(error_msg)
            return
        
        log_message = process_newlines(mensaje)
        
    elif tipo_mensaje.lower() == "embed":
        if not descripción:
            response = "Debes proporcionar una descripción para el mensaje embed"
            if is_interaction:
                await ctx_or_interaction.response.send_message(response, ephemeral=True)
            else:
                await ctx_or_interaction.send(response)
            return
        
        if título and len(título) > MAX_EMBED_TITLE:
            response = f"El título del embed no puede exceder {MAX_EMBED_TITLE} caracteres"
            if is_interaction:
                await ctx_or_interaction.response.send_message(response, ephemeral=True)
            else:
                await ctx_or_interaction.send(response)
            return
            
        if len(descripción) > MAX_EMBED_DESCRIPTION:
            response = f"La descripción del embed no puede exceder {MAX_EMBED_DESCRIPTION} caracteres"
            if is_interaction:
                await ctx_or_interaction.response.send_message(response, ephemeral=True)
            else:
                await ctx_or_interaction.send(response)
            return
            
        if footer and len(footer) > MAX_EMBED_FOOTER:
            response = f"El footer del embed no puede exceder {MAX_EMBED_FOOTER} caracteres"
            if is_interaction:
                await ctx_or_interaction.response.send_message(response, ephemeral=True)
            else:
                await ctx_or_interaction.send(response)
            return
        
        is_valid, error_msg = validate_message_params(log_type, descripción)
        if not is_valid:
            if is_interaction:
                await ctx_or_interaction.response.send_message(error_msg, ephemeral=True)
            else:
                await ctx_or_interaction.send(error_msg)
            return
        
        if footer:
            is_valid, error_msg = validate_message_params(log_type, footer, is_footer=True)
            if not is_valid:
                if is_interaction:
                    await ctx_or_interaction.response.send_message(error_msg, ephemeral=True)
                else:
                    await ctx_or_interaction.send(error_msg)
                return
        
        embed_parts = []
        if título:
            embed_parts.append(f"tl: {process_newlines(título)}")
        embed_parts.append(f"dp: {process_newlines(descripción)}")
        if footer:
            embed_parts.append(f"ft: {process_newlines(footer)}")
        
        log_message = f"embed: {' '.join(embed_parts)}"
    else:
        response = "Tipo de mensaje no válido. Debe ser 'normal' o 'embed'"
        if is_interaction:
            await ctx_or_interaction.response.send_message(response, ephemeral=True)
        else:
            await ctx_or_interaction.send(response)
        return
    
    update_data = {
        "log_channel": canal.id,
        f"{log_type}_messages": log_message,
        "activated": estado == "activado"
    }
    
    if LOG_TYPES[log_type]["needs_limit"]:
        update_data["ago"] = límite
    
    success = update_server_data(guild_id, f"audit_logs/{log_type}", update_data)
    
    if success:
        display_mensaje = mensaje.replace("{\\n}", "↵") if mensaje else None
        display_titulo = título.replace("{\\n}", "↵") if título else None
        display_descripcion = descripción.replace("{\\n}", "↵") if descripción else None
        display_footer = footer.replace("{\\n}", "↵") if footer else None
        
        confirmation = (
            f"<:Si:825734135116070962> Configuración de logs actualizada:\n"
            f"- Tipo: **{log_type}**\n"
            f"- Estado: **{estado}**\n"
            f"- Canal: {canal.mention}\n"
            f"- Formato: **{tipo_mensaje}**\n"
        )
        
        if tipo_mensaje.lower() == "normal":
            confirmation += f"- Mensaje: {display_mensaje[:50]}{'...' if len(display_mensaje) > 50 else ''}\n"
        else:
            if display_titulo:
                confirmation += f"- Título: {display_titulo[:30]}{'...' if len(display_titulo) > 30 else ''}\n"
            confirmation += f"- Descripción: {display_descripcion[:50]}{'...' if len(display_descripcion) > 50 else ''}\n"
            if display_footer:
                confirmation += f"- Footer: {display_footer[:30]}{'...' if len(display_footer) > 30 else ''}\n"
        
        if LOG_TYPES[log_type]["needs_limit"]:
            confirmation += f"- Límite: **{límite} días**\n"
        
        if is_interaction:
            await ctx_or_interaction.response.send_message(confirmation)
        else:
            await ctx_or_interaction.send(confirmation)
    else:
        error_msg = "<:No:825734196256440340> Error al actualizar la configuración de logs. Inténtalo de nuevo."
        if is_interaction:
            await ctx_or_interaction.response.send_message(error_msg, ephemeral=True)
        else:
            await ctx_or_interaction.send(error_msg)