import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
import random
import string
import traceback
from database.get import get_specific_field
from .views.embed_main_view import EmbedMainView
from .utils.embed_cache import EmbedCache

class EmbedCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed_cache = EmbedCache()

    @app_commands.command(name="embed", description="Crear un mensaje embed personalizado")
    @app_commands.describe(
        codigo="Código para enviar un embed previamente creado",
        canal="Canal donde enviar el embed"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def embed_slash(self, interaction: discord.Interaction, codigo: Optional[str] = None, canal: Optional[discord.TextChannel] = None):
        try:
            if interaction.guild is None:
                await interaction.response.send_message("Este comando no puede ser usado en mensajes directos.", ephemeral=True)
                return
            
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
            
            if codigo:
                # Verificar si el código existe y es válido
                embed_data = self.embed_cache.get_embed(codigo)
                if not embed_data:
                    await interaction.response.send_message("El código proporcionado no es válido o ha expirado.", ephemeral=True)
                    return
                    
                if not canal:
                    await interaction.response.send_message("Por favor, especifica un canal donde enviar el embed.", ephemeral=True)
                    return
                    
                # Enviar el embed al canal especificado
                await canal.send(content=embed_data.get("content"), embed=embed_data.get("embed"))
                self.embed_cache.remove_embed(codigo)
                
                await interaction.response.send_message(f"Embed enviado exitosamente al canal {canal.mention}.", ephemeral=True)
                return
                
            # Iniciar el proceso de creación de embed
            embed = discord.Embed(
                description="Usa el menú desplegable para crear tu mensaje embed personalizado",
                color=discord.Color.blue()
            )
            
            view = EmbedMainView(self.bot, interaction.user, self.embed_cache)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        except Exception as e:
            print(f"Error en comando embed: {type(e).__name__}: {e}")
            print(traceback.format_exc())
            await interaction.response.send_message(
                "Ha ocurrido un error al procesar el comando. Por favor, inténtalo nuevamente.", 
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(EmbedCommand(bot))