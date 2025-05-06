import discord
from discord import ui
from ..modals.embed_modals import EmbedFooterModal

class FooterView(ui.View):
    def __init__(self, edit_view):
        super().__init__(timeout=1800)
        self.edit_view = edit_view
        self.embed = edit_view.embed
    
    async def show(self, interaction):
        footer_info = discord.Embed(
            title="Gestión de Footer",
            color=discord.Color.blue()
        )
        
        if self.embed.footer:
            footer_info.add_field(name="Texto", value=self.embed.footer.text or "Sin texto", inline=False)
            footer_info.add_field(name="Icono", value=self.embed.footer.icon_url or "Sin icono", inline=False)
        else:
            footer_info.description = "El embed no tiene footer configurado"
        
        if self.embed.timestamp:
            footer_info.add_field(name="Timestamp", value="Activado", inline=True)
        else:
            footer_info.add_field(name="Timestamp", value="Desactivado", inline=True)
        
        try:
            await interaction.response.edit_message(
                content=f"Gestión de footer - Embed {self.edit_view.embed_index + 1}",
                embed=footer_info,
                view=self
            )
        except discord.errors.InteractionResponded:
            print("FooterView.show: Interacción ya respondida, intentando followup")
            try:
                await interaction.followup.edit_message(
                    message_id=interaction.message.id,
                    content=f"Gestión de footer - Embed {self.edit_view.embed_index + 1}",
                    embed=footer_info,
                    view=self
                )
            except Exception as e:
                print(f"FooterView.show: Error en followup: {e}")
                await interaction.followup.send(
                    "Hubo un problema al mostrar la gestión de footer. Intenta nuevamente.",
                    ephemeral=True
                )
    
    @ui.button(label="Volver atrás", style=discord.ButtonStyle.secondary)
    async def go_back(self, interaction: discord.Interaction, button: ui.Button):
        await self.edit_view.show(interaction)
    
    @ui.button(label="Editar footer", style=discord.ButtonStyle.primary)
    async def edit_footer(self, interaction: discord.Interaction, button: ui.Button):
        modal = EmbedFooterModal(self.edit_view)
        await interaction.response.send_modal(modal)
    
    @ui.button(label="Eliminar footer", style=discord.ButtonStyle.danger)
    async def delete_footer(self, interaction: discord.Interaction, button: ui.Button):
        self.embed.set_footer(text=discord.Embed.Empty)
        self.embed.timestamp = None
        await self.show(interaction)