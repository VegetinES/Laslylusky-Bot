import discord
from discord import ui
from ..modals.embed_modals import EmbedBasicModal, EmbedAuthorModal, EmbedFieldModal, EmbedImageModal, EmbedColorModal
from .embeds_views import EmbedsView

class EmbedEditView(ui.View):
    def __init__(self, main_view, embed_index):
        super().__init__(timeout=1800)
        self.main_view = main_view
        self.embed_index = embed_index
        self.embed = main_view.embeds[embed_index]
        
        print(f"EmbedEditView.__init__: Creando vista para embed {embed_index}")
        self.add_item(EmbedOptionsDropdown(self))
    
    async def show(self, interaction):
        print(f"EmbedEditView.show: Mostrando embed {self.embed_index}")
        preview_embed = self.embed.copy()

        if not preview_embed.color:
            preview_embed.color = discord.Color.blue()
        
        try:
            try:
                await interaction.response.edit_message(
                    content=f"Editando embed {self.embed_index + 1}",
                    embed=preview_embed,
                    view=self
                )
                print("EmbedEditView.show: Mensaje editado correctamente con response.edit_message")
            except discord.errors.InteractionResponded:
                print("EmbedEditView.show: Interacción ya respondida, intentando editar mensaje original")
                try:
                    await interaction.edit_original_response(
                        content=f"Editando embed {self.embed_index + 1}",
                        embed=preview_embed,
                        view=self
                    )
                    print("EmbedEditView.show: Mensaje editado correctamente con edit_original_response")
                except Exception as e:
                    print(f"EmbedEditView.show: Error en edit_original_response: {e}")
                    try:
                        await interaction.followup.edit_message(
                            message_id=interaction.message.id,
                            content=f"Editando embed {self.embed_index + 1}",
                            embed=preview_embed,
                            view=self
                        )
                        print("EmbedEditView.show: Mensaje editado correctamente con followup.edit_message")
                    except Exception as e2:
                        print(f"EmbedEditView.show: Error en followup.edit_message: {e2}")
                        await interaction.followup.send(
                            "Error al mostrar el editor de embeds. Intenta nuevamente.",
                            ephemeral=True
                        )
        except Exception as e:
            print(f"EmbedEditView.show: Error general: {e}")
            try:
                await interaction.followup.send(
                    "Hubo un problema al mostrar el editor de embeds. Intenta nuevamente.",
                    ephemeral=True
                )
            except:
                pass
    
    @ui.button(label="Eliminar embed", style=discord.ButtonStyle.danger, row=4)
    async def delete_embed(self, interaction: discord.Interaction, button: ui.Button):
        from .confirm_delete_view import ConfirmDeleteEmbedView
        confirm_view = ConfirmDeleteEmbedView(self.main_view, self.embed_index)
        try:
            await interaction.response.edit_message(
                content=f"¿Seguro que deseas eliminar el embed {self.embed_index + 1}?",
                embed=None,
                view=confirm_view
            )
        except discord.errors.InteractionResponded:
            await interaction.followup.edit_message(
                message_id=interaction.message.id,
                content=f"¿Seguro que deseas eliminar el embed {self.embed_index + 1}?",
                embed=None,
                view=confirm_view
            )
    
    @ui.button(label="Volver a la lista", style=discord.ButtonStyle.secondary, row=4)
    async def back_to_list(self, interaction: discord.Interaction, button: ui.Button):
        embeds_view = EmbedsView(self.main_view)
        await embeds_view.show(interaction)

class EmbedOptionsDropdown(ui.Select):
    def __init__(self, edit_view):
        self.edit_view = edit_view
        self.embed = edit_view.embed
        
        options = [
            discord.SelectOption(
                label="Editar básico",
                description="Título, descripción y URL",
                value="basic"
            ),
            discord.SelectOption(
                label="Gestionar autor",
                description="Autor del embed",
                value="author"
            ),
            discord.SelectOption(
                label="Gestionar campos",
                description="Añadir o editar campos",
                value="fields"
            ),
            discord.SelectOption(
                label="Gestionar imágenes",
                description="Imagen y thumbnail",
                value="images"
            ),
            discord.SelectOption(
                label="Editar color",
                description="Color del embed",
                value="color"
            ),
            discord.SelectOption(
                label="Editar footer",
                description="Footer y timestamp",
                value="footer"
            )
        ]
        
        super().__init__(placeholder="Selecciona una opción", options=options)
    
    async def callback(self, interaction: discord.Interaction):
        value = self.values[0]
        print(f"EmbedOptionsDropdown.callback: Opción seleccionada: {value}")
        
        try:
            if value == "basic":
                modal = EmbedBasicModal(self.edit_view)
                await interaction.response.send_modal(modal)
            
            elif value == "author":
                modal = EmbedAuthorModal(self.edit_view)
                await interaction.response.send_modal(modal)
            
            elif value == "fields":
                from .fields_view import FieldsView
                fields_view = FieldsView(self.edit_view)
                try:
                    await interaction.response.edit_message(
                        content=f"Gestión de campos - Embed {self.edit_view.embed_index + 1}",
                        embed=discord.Embed(
                            title="Campos del Embed",
                            description=f"Campos actuales: {len(self.embed.fields)}/25",
                            color=discord.Color.blue()
                        ),
                        view=fields_view
                    )
                except discord.errors.InteractionResponded:
                    print("EmbedOptionsDropdown.callback: Interacción ya respondida, intentando followup")
                    try:
                        await interaction.followup.edit_message(
                            message_id=interaction.message.id,
                            content=f"Gestión de campos - Embed {self.edit_view.embed_index + 1}",
                            embed=discord.Embed(
                                title="Campos del Embed",
                                description=f"Campos actuales: {len(self.embed.fields)}/25",
                                color=discord.Color.blue()
                            ),
                            view=fields_view
                        )
                    except Exception as e:
                        print(f"EmbedOptionsDropdown.callback (fields): Error en followup: {e}")
                        await interaction.followup.send(
                            "Hubo un problema al mostrar la gestión de campos. Intenta nuevamente.",
                            ephemeral=True
                        )
            
            elif value == "images":
                from .images_view import ImagesView
                images_view = ImagesView(self.edit_view)
                try:
                    await interaction.response.edit_message(
                        content=f"Gestión de imágenes - Embed {self.edit_view.embed_index + 1}",
                        embed=discord.Embed(
                            title="Imágenes del Embed",
                            color=discord.Color.blue()
                        ),
                        view=images_view
                    )
                except discord.errors.InteractionResponded:
                    print("EmbedOptionsDropdown.callback: Interacción ya respondida, intentando followup")
                    try:
                        await interaction.followup.edit_message(
                            message_id=interaction.message.id,
                            content=f"Gestión de imágenes - Embed {self.edit_view.embed_index + 1}",
                            embed=discord.Embed(
                                title="Imágenes del Embed",
                                color=discord.Color.blue()
                            ),
                            view=images_view
                        )
                    except Exception as e:
                        print(f"EmbedOptionsDropdown.callback (images): Error en followup: {e}")
                        await interaction.followup.send(
                            "Hubo un problema al mostrar la gestión de imágenes. Intenta nuevamente.",
                            ephemeral=True
                        )
            
            elif value == "color":
                modal = EmbedColorModal(self.edit_view)
                await interaction.response.send_modal(modal)
            
            elif value == "footer":
                from .footer_view import FooterView
                footer_view = FooterView(self.edit_view)
                try:
                    await interaction.response.edit_message(
                        content=f"Gestión de footer - Embed {self.edit_view.embed_index + 1}",
                        embed=discord.Embed(
                            title="Footer del Embed",
                            color=discord.Color.blue()
                        ),
                        view=footer_view
                    )
                except discord.errors.InteractionResponded:
                    print("EmbedOptionsDropdown.callback: Interacción ya respondida, intentando followup")
                    try:
                        await interaction.followup.edit_message(
                            message_id=interaction.message.id,
                            content=f"Gestión de footer - Embed {self.edit_view.embed_index + 1}",
                            embed=discord.Embed(
                                title="Footer del Embed",
                                color=discord.Color.blue()
                            ),
                            view=footer_view
                        )
                    except Exception as e:
                        print(f"EmbedOptionsDropdown.callback (footer): Error en followup: {e}")
                        await interaction.followup.send(
                            "Hubo un problema al mostrar la gestión de footer. Intenta nuevamente.",
                            ephemeral=True
                        )
        except Exception as e:
            print(f"EmbedOptionsDropdown.callback: Error general: {e}")
            await interaction.followup.send(
                "Ocurrió un error inesperado. Por favor, intenta de nuevo.",
                ephemeral=True
            )