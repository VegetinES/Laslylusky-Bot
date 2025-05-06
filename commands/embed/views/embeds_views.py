import discord
from discord import ui
from ..constants import MAX_EMBEDS

class EmbedsView(ui.View):
    def __init__(self, main_view):
        super().__init__(timeout=1800)
        self.main_view = main_view
        self.update_selector()
    
    def update_selector(self):
        for item in list(self.children):
            if isinstance(item, EmbedSelector):
                self.remove_item(item)
        
        self.add_item(EmbedSelector(self))
    
    async def show(self, interaction):
        print(f"EmbedsView.show: Mostrando {len(self.main_view.embeds)} embeds")
        self.update_selector()
        
        try:
            await interaction.response.edit_message(
                content=None,
                embed=discord.Embed(
                    title="Gestión de Embeds",
                    description=f"Embeds actuales: {len(self.main_view.embeds)}/{MAX_EMBEDS}",
                    color=discord.Color.blue()
                ),
                view=self
            )
        except discord.errors.InteractionResponded:
            print("EmbedsView.show: La interacción ya fue respondida, usando followup")
            try:
                await interaction.followup.edit_message(
                    message_id=interaction.message.id,
                    content=None,
                    embed=discord.Embed(
                        title="Gestión de Embeds",
                        description=f"Embeds actuales: {len(self.main_view.embeds)}/{MAX_EMBEDS}",
                        color=discord.Color.blue()
                    ),
                    view=self
                )
            except Exception as e:
                print(f"EmbedsView.show: Error en followup: {e}")
                await interaction.followup.send(
                    "Hubo un problema al mostrar los embeds. Intenta usar el comando nuevamente.",
                    ephemeral=True
                )
    
    @ui.button(label="Volver atrás", style=discord.ButtonStyle.secondary)
    async def go_back(self, interaction: discord.Interaction, button: ui.Button):
        await self.main_view.update_message(interaction)
    
    @ui.button(label="Añadir embed", style=discord.ButtonStyle.success)
    async def add_embed(self, interaction: discord.Interaction, button: ui.Button):
        if self.main_view.add_embed():
            print(f"EmbedsView.add_embed: Embed añadido, total: {len(self.main_view.embeds)}")
            self.update_selector()
            try:
                await interaction.response.edit_message(
                    embed=discord.Embed(
                        title="Embed añadido",
                        description=f"Embeds actuales: {len(self.main_view.embeds)}/{MAX_EMBEDS}",
                        color=discord.Color.green()
                    ),
                    view=self
                )
            except discord.errors.InteractionResponded:
                print("EmbedsView.add_embed: La interacción ya fue respondida, usando followup")
                await interaction.followup.edit_message(
                    message_id=interaction.message.id,
                    embed=discord.Embed(
                        title="Embed añadido",
                        description=f"Embeds actuales: {len(self.main_view.embeds)}/{MAX_EMBEDS}",
                        color=discord.Color.green()
                    ),
                    view=self
                )
        else:
            await interaction.response.send_message(
                f"Has alcanzado el límite máximo de {MAX_EMBEDS} embeds.",
                ephemeral=True
            )

class EmbedSelector(ui.Select):
    def __init__(self, embeds_view):
        self.embeds_view = embeds_view
        self.main_view = embeds_view.main_view
        
        options = []
        
        for i, embed in enumerate(self.main_view.embeds):
            title = embed.title if embed.title else f"Embed {i+1}"
            if len(title) > 25:
                title = title[:22] + "..."
            
            description = "Sin descripción"
            if embed.description and embed.description.strip():
                description = embed.description[:50]
                if len(description) > 50:
                    description = description[:47] + "..."
            
            options.append(discord.SelectOption(
                label=title,
                value=str(i),
                description=description
            ))
        
        if not options:
            options.append(discord.SelectOption(
                label="No hay embeds",
                value="none",
                description="Añade un embed para empezar"
            ))
        
        super().__init__(placeholder="Selecciona un embed para editar", options=options)
    
    async def callback(self, interaction: discord.Interaction):
        print(f"EmbedSelector.callback: Valor seleccionado: {self.values[0]}")
        if self.values[0] == "none":
            return
        
        try:
            embed_index = int(self.values[0])
            from .embed_edit_view import EmbedEditView
            edit_view = EmbedEditView(self.main_view, embed_index)
            print(f"EmbedSelector.callback: Creada vista EmbedEditView para index {embed_index}")
            
            embed = self.main_view.embeds[embed_index]
            if not embed.description:
                embed.description = "Descripción del embed. Edita este texto."
            
            preview_embed = embed.copy()
            if not preview_embed.color:
                preview_embed.color = discord.Color.blue()
            
            try:
                await interaction.response.edit_message(
                    content=f"Editando embed {embed_index + 1}",
                    embed=preview_embed,
                    view=edit_view
                )
                print(f"EmbedSelector.callback: Mensaje editado correctamente")
            except Exception as e:
                print(f"EmbedSelector.callback: Error al editar mensaje: {e}")
                if "404 Not Found" in str(e):
                    await interaction.followup.send(
                        content=f"Editando embed {embed_index + 1}",
                        embed=preview_embed,
                        view=edit_view,
                        ephemeral=True
                    )
                else:
                    try:
                        await interaction.followup.edit_message(
                            message_id=interaction.message.id,
                            content=f"Editando embed {embed_index + 1}",
                            embed=preview_embed,
                            view=edit_view
                        )
                    except:
                        await interaction.followup.send(
                            content=f"Editando embed {embed_index + 1}",
                            embed=preview_embed,
                            view=edit_view,
                            ephemeral=True
                        )
        except ValueError as e:
            print(f"EmbedSelector.callback: Error de conversión: {e}")
        except Exception as e:
            print(f"EmbedSelector.callback: Error general: {e}")
            await interaction.followup.send(
                "Ocurrió un error inesperado. Por favor, intenta de nuevo.",
                ephemeral=True
            )