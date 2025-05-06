import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
import json
import io
import aiohttp
from database.get import get_specific_field
from .views.main_view import EmbedMainView
from .utils.embed_cache import EmbedCache
from .utils.helpers import load_embed_from_json
from .constants import MAX_EMBEDS, MAX_CONTENT_LENGTH

class EmbedCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed_cache = EmbedCache()

    @app_commands.command(name="embed", description="Crear un mensaje con embeds personalizados")
    @app_commands.describe(
        codigo="Código para enviar un mensaje con embeds previamente creado",
        canal="Canal donde enviar el mensaje",
        cargar="Cargar un archivo JSON con datos de un embed",
        mensaje_id="ID del mensaje a editar (opcional)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def embed_slash(self, interaction: discord.Interaction, codigo: Optional[str] = None, canal: Optional[discord.TextChannel] = None, cargar: Optional[discord.Attachment] = None, mensaje_id: Optional[str] = None):
        try:
            if interaction.guild is None:
                await interaction.response.send_message("Este comando no puede ser usado en mensajes directos.", ephemeral=True)
                return
            
            from database.get import get_specific_field
            
            act_commands = get_specific_field(interaction.guild.id, "act_cmd")
            if act_commands is None:
                embed = discord.Embed(
                    title="<:No:825734196256440340> Error de Configuración",
                    description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el servidor o habilita algún comando",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            if "embed" not in act_commands:
                await interaction.response.send_message("El comando no está activado en este servidor.", ephemeral=True)
                return
            
            bot_admins = get_specific_field(interaction.guild.id, "perms/admin-users")
            bot_admin_roles = get_specific_field(interaction.guild.id, "perms/admin-roles")
            
            if not isinstance(bot_admins, list):
                bot_admins = []
            if not isinstance(bot_admin_roles, list):
                bot_admin_roles = []
            
            has_admin_role = False
            for role in interaction.user.roles:
                if role.id in bot_admin_roles:
                    has_admin_role = True
                    break
            
            if not interaction.user.guild_permissions.administrator and interaction.user.id not in bot_admins and not has_admin_role:
                await interaction.response.send_message(
                    "<:No:825734196256440340> No tienes permisos para usar este comando. Necesitas ser administrador del servidor o tener el rol de administrador del bot.",
                    ephemeral=True
                )
                return
            
            if cargar:
                if not cargar.filename.endswith('.json'):
                    await interaction.response.send_message("El archivo debe ser un archivo JSON.", ephemeral=True)
                    return
                
                await interaction.response.defer(ephemeral=True)
                
                file_content = await cargar.read()
                try:
                    embed_data = load_embed_from_json(file_content.decode('utf-8'))
                    
                    view = EmbedMainView(self.bot, interaction.user, self.embed_cache)
                    view.content = embed_data.get("content")
                    view.embeds = embed_data.get("embeds", [])
                    view.webhook_url = embed_data.get("webhook_url")
                    view.message_id = mensaje_id
                    view.attachments = embed_data.get("attachments", [])
                    
                    preview_embed = discord.Embed(
                        title="Embed cargado correctamente",
                        description="Puedes continuar editando o enviarlo directamente.",
                        color=discord.Color.green()
                    )
                    
                    await interaction.followup.send(embed=preview_embed, view=view, ephemeral=True)
                    return
                except Exception as e:
                    await interaction.followup.send(f"Error al cargar el archivo JSON: {str(e)}", ephemeral=True)
                    return
            
            if codigo:
                embed_data = self.embed_cache.get_embed(codigo)
                if not embed_data:
                    await interaction.response.send_message("El código proporcionado no es válido o ha expirado.", ephemeral=True)
                    return
                    
                if not canal and not embed_data.get("webhook_url"):
                    await interaction.response.send_message("Por favor, especifica un canal donde enviar el mensaje.", ephemeral=True)
                    return
                    
                content = embed_data.get("content")
                embeds = embed_data.get("embeds", [])
                webhook_url = embed_data.get("webhook_url")
                message_id = embed_data.get("message_id") or mensaje_id
                attachments = embed_data.get("attachments", [])
                
                if not embeds and not content and not attachments:
                    await interaction.response.send_message(
                        "El código no contiene ningún contenido válido. Debe tener al menos texto, un embed o una imagen adjunta.",
                        ephemeral=True
                    )
                    return
                
                try:
                    await interaction.response.defer(ephemeral=True)
                    
                    files = []
                    if attachments and not message_id:
                        async with aiohttp.ClientSession() as session:
                            for i, url in enumerate(attachments):
                                try:
                                    async with session.get(url) as resp:
                                        if resp.status == 200:
                                            data = await resp.read()
                                            filename = f"image_{i+1}.png"
                                            files.append(discord.File(io.BytesIO(data), filename=filename))
                                except Exception as e:
                                    print(f"Error al descargar imagen {url}: {e}")
                    
                    if webhook_url:
                        async with aiohttp.ClientSession() as session:
                            webhook = discord.Webhook.from_url(webhook_url, session=session)
                            
                            if message_id:
                                await webhook.edit_message(message_id, content=content, embeds=embeds)
                                await interaction.followup.send(f"Mensaje con ID {message_id} editado exitosamente a través del webhook. Ten en cuenta que no se pueden modificar los adjuntos de un mensaje existente.", ephemeral=True)
                            else:
                                message = await webhook.send(content=content, embeds=embeds, files=files, wait=True)
                                await interaction.followup.send(f"Mensaje enviado exitosamente a través del webhook. ID del mensaje: {message.id}", ephemeral=True)
                    else:
                        if message_id:
                            try:
                                message = await canal.fetch_message(int(message_id))
                                if message.author.id == self.bot.user.id:
                                    await message.edit(content=content, embeds=embeds)
                                    await interaction.followup.send(f"Mensaje con ID {message_id} editado exitosamente.", ephemeral=True)
                                else:
                                    await interaction.followup.send("No puedo editar un mensaje que no fue enviado por mí.", ephemeral=True)
                            except discord.NotFound:
                                await interaction.followup.send("No se encontró el mensaje especificado.", ephemeral=True)
                            except Exception as e:
                                await interaction.followup.send(f"Error al editar el mensaje: {str(e)}", ephemeral=True)
                        else:
                            message = await canal.send(content=content, embeds=embeds, files=files)
                            await interaction.followup.send(f"Mensaje enviado exitosamente al canal {canal.mention}. ID del mensaje: {message.id}", ephemeral=True)
                    
                    for file in files:
                        file.close()
                    
                    self.embed_cache.remove_embed(codigo)
                except Exception as e:
                    await interaction.followup.send(f"Error al enviar/editar el mensaje: {str(e)}", ephemeral=True)
                return
                
            embed = discord.Embed(
                description="Usa el menú desplegable para crear tu mensaje personalizado",
                color=discord.Color.blue()
            )
            
            view = EmbedMainView(self.bot, interaction.user, self.embed_cache)
            view.message_id = mensaje_id
            
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            print(f"Error en comando embed: {type(e).__name__}: {e}")
            await interaction.response.send_message("Ha ocurrido un error al procesar el comando.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(EmbedCommand(bot))