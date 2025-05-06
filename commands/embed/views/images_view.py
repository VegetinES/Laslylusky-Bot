import discord
from discord import ui
from ..modals.embed_modals import EmbedImageModal

class ImagesView(ui.View):
    def __init__(self, edit_view):
        super().__init__(timeout=1800)
        self.edit_view = edit_view
        self.embed = edit_view.embed
    
    async def show(self, interaction):
        images_info = discord.Embed(
            title="Gestión de Imágenes",
            color=discord.Color.blue()
        )
        
        if self.embed.image:
            images_info.add_field(
                name="Imagen Principal",
                value=f"URL: {self.embed.image.url}",
                inline=False
            )
        else:
            images_info.add_field(
                name="Imagen Principal",
                value="No configurada",
                inline=False
            )
        
        if self.embed.thumbnail:
            images_info.add_field(
                name="Thumbnail",
                value=f"URL: {self.embed.thumbnail.url}",
                inline=False
            )
        else:
            images_info.add_field(
                name="Thumbnail",
                value="No configurado",
                inline=False
            )
        
        try:
            await interaction.response.edit_message(
                content=f"Gestión de imágenes - Embed {self.edit_view.embed_index + 1}",
                embed=images_info,
                view=self
            )
        except discord.errors.InteractionResponded:
            print("ImagesView.show: Interacción ya respondida, intentando followup")
            try:
                await interaction.followup.edit_message(
                    message_id=interaction.message.id,
                    content=f"Gestión de imágenes - Embed {self.edit_view.embed_index + 1}",
                    embed=images_info,
                    view=self
                )
            except Exception as e:
                print(f"ImagesView.show: Error en followup: {e}")
                await interaction.followup.send(
                    "Hubo un problema al mostrar la gestión de imágenes. Intenta nuevamente.",
                    ephemeral=True
                )
    
    @ui.button(label="Volver atrás", style=discord.ButtonStyle.secondary)
    async def go_back(self, interaction: discord.Interaction, button: ui.Button):
        await self.edit_view.show(interaction)
    
    @ui.button(label="Editar imágenes", style=discord.ButtonStyle.primary)
    async def edit_images(self, interaction: discord.Interaction, button: ui.Button):
        modal = EmbedImageModal(self.edit_view)
        await interaction.response.send_modal(modal)
    
    @ui.button(label="Eliminar imágenes", style=discord.ButtonStyle.danger)
    async def delete_images(self, interaction: discord.Interaction, button: ui.Button):
        self.embed.set_image(url=discord.Embed.Empty)
        self.embed.set_thumbnail(url=discord.Embed.Empty)
        await self.show(interaction)