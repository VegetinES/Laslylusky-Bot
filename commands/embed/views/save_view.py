import discord
from discord import ui
import io
from ..utils.helpers import save_embed_to_json

class SaveView(ui.View):
    def __init__(self, main_view):
        super().__init__(timeout=1800)
        self.main_view = main_view
    
    async def show(self, interaction):
        if not self.main_view.content and not self.main_view.embeds:
            await interaction.response.edit_message(
                content="No hay contenido para guardar. Primero debes crear algún contenido o embed.",
                embed=discord.Embed(
                    title="Sin Contenido",
                    description="No hay contenido que guardar.",
                    color=discord.Color.red()
                ),
                view=self
            )
            return
        
        await interaction.response.edit_message(
            content="¿Qué quieres hacer con los datos del embed?",
            embed=discord.Embed(
                title="Guardar Datos",
                description="Puedes descargar el embed como un archivo JSON para usarlo posteriormente.",
                color=discord.Color.blue()
            ),
            view=self
        )
    
    @ui.button(label="Volver atrás", style=discord.ButtonStyle.secondary)
    async def go_back(self, interaction: discord.Interaction, button: ui.Button):
        await self.main_view.update_message(interaction)
    
    @ui.button(label="Descargar JSON", style=discord.ButtonStyle.primary)
    async def download_json(self, interaction: discord.Interaction, button: ui.Button):
        try:
            json_data = save_embed_to_json(
                self.main_view.content, 
                self.main_view.embeds,
                webhook_url=self.main_view.webhook_url,
                webhook_name=self.main_view.webhook_name,
                webhook_avatar=self.main_view.webhook_avatar,
                message_id=self.main_view.message_id,
                attachments=self.main_view.attachments
            )
            
            file = discord.File(
                io.BytesIO(json_data.encode()),
                filename="embed_data.json"
            )
            
            await interaction.response.send_message(
                "Aquí está tu archivo JSON con los datos del embed:",
                file=file,
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"Error al generar el archivo JSON: {str(e)}",
                ephemeral=True
            )