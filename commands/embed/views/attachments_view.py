import discord
from discord import ui
import re

class AttachmentsView(ui.View):
    def __init__(self, main_view):
        super().__init__(timeout=1800)
        self.main_view = main_view
    
    async def show(self, interaction):
        embed = discord.Embed(
            title="Gestión de Imágenes Adjuntas",
            description=f"Configura hasta 10 imágenes para adjuntar al mensaje. Actualmente tienes {len(self.main_view.attachments)}/10 imágenes.",
            color=discord.Color.blue()
        )
        
        if self.main_view.attachments:
            embed.set_image(url=self.main_view.attachments[0])
        
        content = ""
        
        if self.main_view.attachments:
            content = "Imágenes configuradas:\n\n"
            for i, url in enumerate(self.main_view.attachments):
                content += f"{i+1}. {url}\n"
        else:
            content = "No hay imágenes adjuntas configuradas."
        
        await interaction.response.edit_message(
            content=content,
            embed=embed,
            view=self
        )
    
    @ui.button(label="Volver atrás", style=discord.ButtonStyle.secondary)
    async def go_back(self, interaction: discord.Interaction, button: ui.Button):
        await self.main_view.update_message(interaction)
    
    @ui.button(label="Añadir imagen", style=discord.ButtonStyle.primary)
    async def add_attachment(self, interaction: discord.Interaction, button: ui.Button):
        if len(self.main_view.attachments) >= 10:
            await interaction.response.send_message(
                "Ya has alcanzado el límite máximo de 10 imágenes adjuntas.",
                ephemeral=True
            )
            return
        
        modal = AttachmentModal(self.main_view)
        await interaction.response.send_modal(modal)
    
    @ui.button(label="Ver imágenes", style=discord.ButtonStyle.primary)
    async def view_attachments(self, interaction: discord.Interaction, button: ui.Button):
        if not self.main_view.attachments:
            await interaction.response.send_message(
                "No hay imágenes adjuntas para mostrar.",
                ephemeral=True
            )
            return
        
        await interaction.response.edit_message(
            content="Selecciona una imagen para verla:",
            embed=discord.Embed(
                title="Vista Previa de Imágenes",
                description="Selecciona una imagen para ver su vista previa y gestionarla.",
                color=discord.Color.blue()
            ),
            view=AttachmentPreviewView(self.main_view)
        )
    
    @ui.button(label="Eliminar todas", style=discord.ButtonStyle.danger)
    async def clear_attachments(self, interaction: discord.Interaction, button: ui.Button):
        if not self.main_view.attachments:
            await interaction.response.send_message(
                "No hay imágenes adjuntas para eliminar.",
                ephemeral=True
            )
            return
        
        self.main_view.attachments = []
        
        await interaction.response.edit_message(
            content="Todas las imágenes adjuntas han sido eliminadas.",
            embed=discord.Embed(
                title="Imágenes Eliminadas",
                description="Se han eliminado todas las imágenes adjuntas.",
                color=discord.Color.green()
            ),
            view=self
        )

class AttachmentModal(ui.Modal, title="Añadir Imagen Adjunta"):
    image_url = ui.TextInput(
        label="URL de la imagen",
        style=discord.TextStyle.short,
        placeholder="https://ejemplo.com/imagen.png",
        required=True
    )
    
    def __init__(self, main_view):
        super().__init__()
        self.main_view = main_view
    
    async def on_submit(self, interaction: discord.Interaction):
        url = self.image_url.value.strip()
        
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
        if not re.match(url_pattern, url):
            await interaction.response.send_message(
                "La URL no es válida. Debe comenzar con http:// o https://",
                ephemeral=True
            )
            return
        
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp']
        valid_image = False
        
        for ext in image_extensions:
            if url.lower().endswith(ext):
                valid_image = True
                break
        
        if not valid_image and not url.lower().startswith(('https://cdn.discordapp.com/', 'https://media.discordapp.net/')):
            await interaction.response.send_message(
                "La URL no parece ser una imagen válida. Asegúrate de que termine en .png, .jpg, .jpeg, .gif, .webp o .bmp, o que sea una URL de Discord.",
                ephemeral=True
            )
            return
        
        self.main_view.attachments.append(url)
        
        embed = discord.Embed(
            title="Imagen Añadida",
            description="La imagen ha sido añadida a la lista de adjuntos.",
            color=discord.Color.green()
        )
        embed.set_image(url=url)
        
        await interaction.response.edit_message(
            content=f"Imagen añadida correctamente. Tienes {len(self.main_view.attachments)}/10 imágenes configuradas.",
            embed=embed,
            view=AttachmentsView(self.main_view)
        )

class AttachmentPreviewView(ui.View):
    def __init__(self, main_view):
        super().__init__(timeout=1800)
        self.main_view = main_view
        self.current_index = 0
        self.update_preview()
    
    def update_preview(self):
        for item in list(self.children):
            if not isinstance(item, ui.Button) or item.custom_id not in ["back_to_list", "prev_image", "next_image", "delete_image"]:
                self.remove_item(item)
        
        options = []
        for i, url in enumerate(self.main_view.attachments):
            filename = url.split('/')[-1]
            if len(filename) > 25:
                filename = filename[:22] + "..."
            
            options.append(
                discord.SelectOption(
                    label=f"Imagen {i+1}",
                    value=str(i),
                    description=filename,
                    default=(i == self.current_index)
                )
            )
        
        select = ui.Select(
            placeholder="Selecciona una imagen para ver",
            options=options
        )
        
        select.callback = self.select_callback
        self.add_item(select)
    
    async def select_callback(self, interaction: discord.Interaction):
        try:
            self.current_index = int(interaction.data["values"][0])
            self.update_preview()
            
            embed = discord.Embed(
                title=f"Vista Previa - Imagen {self.current_index+1}/{len(self.main_view.attachments)}",
                description=f"URL: {self.main_view.attachments[self.current_index]}",
                color=discord.Color.blue()
            )
            embed.set_image(url=self.main_view.attachments[self.current_index])
            
            await interaction.response.edit_message(
                content=f"Mostrando imagen {self.current_index+1} de {len(self.main_view.attachments)}",
                embed=embed,
                view=self
            )
        except Exception as e:
            await interaction.response.send_message(
                f"Error al mostrar la imagen: {str(e)}",
                ephemeral=True
            )
    
    @ui.button(label="Volver a la lista", style=discord.ButtonStyle.secondary, custom_id="back_to_list", row=2)
    async def back_to_list(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.edit_message(
            content="Gestión de imágenes adjuntas",
            embed=discord.Embed(
                title="Gestión de Imágenes Adjuntas",
                description=f"Configura hasta 10 imágenes para adjuntar al mensaje. Actualmente tienes {len(self.main_view.attachments)}/10 imágenes.",
                color=discord.Color.blue()
            ),
            view=AttachmentsView(self.main_view)
        )
    
    @ui.button(label="← Anterior", style=discord.ButtonStyle.primary, custom_id="prev_image", row=1)
    async def prev_image(self, interaction: discord.Interaction, button: ui.Button):
        if len(self.main_view.attachments) <= 1:
            return
            
        self.current_index = (self.current_index - 1) % len(self.main_view.attachments)
        self.update_preview()
        
        embed = discord.Embed(
            title=f"Vista Previa - Imagen {self.current_index+1}/{len(self.main_view.attachments)}",
            description=f"URL: {self.main_view.attachments[self.current_index]}",
            color=discord.Color.blue()
        )
        embed.set_image(url=self.main_view.attachments[self.current_index])
        
        await interaction.response.edit_message(
            content=f"Mostrando imagen {self.current_index+1} de {len(self.main_view.attachments)}",
            embed=embed,
            view=self
        )
    
    @ui.button(label="Siguiente →", style=discord.ButtonStyle.primary, custom_id="next_image", row=1)
    async def next_image(self, interaction: discord.Interaction, button: ui.Button):
        if len(self.main_view.attachments) <= 1:
            return
            
        self.current_index = (self.current_index + 1) % len(self.main_view.attachments)
        self.update_preview()
        
        embed = discord.Embed(
            title=f"Vista Previa - Imagen {self.current_index+1}/{len(self.main_view.attachments)}",
            description=f"URL: {self.main_view.attachments[self.current_index]}",
            color=discord.Color.blue()
        )
        embed.set_image(url=self.main_view.attachments[self.current_index])
        
        await interaction.response.edit_message(
            content=f"Mostrando imagen {self.current_index+1} de {len(self.main_view.attachments)}",
            embed=embed,
            view=self
        )
    
    @ui.button(label="Eliminar imagen", style=discord.ButtonStyle.danger, custom_id="delete_image", row=1)
    async def delete_image(self, interaction: discord.Interaction, button: ui.Button):
        if not self.main_view.attachments:
            return
            
        deleted_url = self.main_view.attachments.pop(self.current_index)
        
        if not self.main_view.attachments:
            await interaction.response.edit_message(
                content="La última imagen ha sido eliminada.",
                embed=discord.Embed(
                    title="Imagen Eliminada",
                    description="Ya no hay imágenes adjuntas configuradas.",
                    color=discord.Color.green()
                ),
                view=AttachmentsView(self.main_view)
            )
            return
        
        if self.current_index >= len(self.main_view.attachments):
            self.current_index = len(self.main_view.attachments) - 1
        
        self.update_preview()
        
        embed = discord.Embed(
            title=f"Imagen Eliminada - Mostrando {self.current_index+1}/{len(self.main_view.attachments)}",
            description=f"La imagen ha sido eliminada. URL: {deleted_url}",
            color=discord.Color.green()
        )
        
        if self.main_view.attachments:
            embed.set_image(url=self.main_view.attachments[self.current_index])
        
        await interaction.response.edit_message(
            content=f"Imagen eliminada. Mostrando imagen {self.current_index+1} de {len(self.main_view.attachments)}",
            embed=embed,
            view=self
        )