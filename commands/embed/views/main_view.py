import discord
from discord import ui
import random
import string
import json
import io
from datetime import datetime, timedelta
from ..constants import MAX_EMBEDS, MAX_CONTENT_LENGTH, MAX_TOTAL_CHARACTERS
from ..utils.helpers import create_embed_from_data, save_embed_to_json

class EmbedMainView(ui.View):
    def __init__(self, bot, user, embed_cache):
        super().__init__(timeout=1800)
        self.bot = bot
        self.user = user
        self.embed_cache = embed_cache
        self.content = None
        self.embeds = []
        self.webhook_url = None
        self.message_id = None
        self.attachments = []
        
        self.add_item(MainDropdown(self))
    
    def add_embed(self):
        if len(self.embeds) >= MAX_EMBEDS:
            return False
        
        new_embed = discord.Embed(
            color=discord.Color.blue()
        )
        self.embeds.append(new_embed)
        return True
    
    def remove_embed(self, index):
        if 0 <= index < len(self.embeds):
            self.embeds.pop(index)
            return True
        return False
    
    def get_total_characters(self):
        total = 0
        if self.content:
            total += len(self.content)
        
        for embed in self.embeds:
            total += len(str(embed.title)) if embed.title else 0
            total += len(str(embed.description)) if embed.description else 0
            total += len(str(embed.footer.text)) if embed.footer else 0
            
            for field in embed.fields:
                total += len(field.name) + len(field.value)
        
        return total
    
    async def update_message(self, interaction):
        try:
            dropdown = MainDropdown(self)
            for i, item in enumerate(self.children):
                if isinstance(item, MainDropdown):
                    self.children[i] = dropdown
                    break
            else:
                self.add_item(dropdown)
            
            preview_embed = discord.Embed(
                title="Vista previa de tu mensaje",
                color=discord.Color.blue()
            )
            
            if self.content:
                preview_embed.add_field(
                    name="Contenido",
                    value=f"```{self.content[:100]}{'...' if len(self.content) > 100 else ''}```",
                    inline=False
                )
            
            if self.embeds:
                preview_embed.add_field(
                    name="Embeds",
                    value=f"Se han creado {len(self.embeds)} embed(s)",
                    inline=False
                )
            
            if self.webhook_url:
                preview_embed.add_field(
                    name="Webhook",
                    value="✅ Configurado",
                    inline=False
                )
                
            if self.message_id:
                preview_embed.add_field(
                    name="Mensaje a editar",
                    value=f"ID: {self.message_id}",
                    inline=False
                )
            
            if self.attachments:
                preview_embed.add_field(
                    name="Imágenes adjuntas",
                    value=f"{len(self.attachments)}/10 imágenes configuradas",
                    inline=False
                )
            
            total_chars = self.get_total_characters()
            preview_embed.add_field(
                name="Total de caracteres",
                value=f"{total_chars}/{MAX_TOTAL_CHARACTERS}",
                inline=False
            )
            
            await interaction.response.edit_message(embed=preview_embed, view=self)
        except Exception as e:
            print(f"Error al actualizar mensaje: {e}")
            await interaction.response.send_message("Error al actualizar el mensaje.", ephemeral=True)
    
    async def send_final_message(self, interaction):
        if not self.content and not self.embeds and not self.attachments:
            await interaction.response.send_message(
                "No hay nada que enviar. Añade contenido, embeds o al menos una imagen adjunta.",
                ephemeral=True
            )
            return

        if self.webhook_url:
            try:
                await interaction.response.defer(ephemeral=True)
                
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    webhook = discord.Webhook.from_url(self.webhook_url, session=session)
                    
                    files = []
                    for i, url in enumerate(self.attachments):
                        try:
                            async with session.get(url) as resp:
                                if resp.status == 200:
                                    data = await resp.read()
                                    filename = f"image_{i+1}.png"
                                    files.append(discord.File(io.BytesIO(data), filename=filename))
                        except Exception as e:
                            print(f"Error al descargar imagen {url}: {e}")
                    
                    if self.message_id:
                        await webhook.edit_message(self.message_id, content=self.content, embeds=self.embeds)
                        await interaction.followup.send(f"Mensaje con ID {self.message_id} editado exitosamente a través del webhook. Ten en cuenta que no se pueden modificar los adjuntos de un mensaje existente.", ephemeral=True)
                    else:
                        message = await webhook.send(content=self.content, embeds=self.embeds, files=files, wait=True)
                        await interaction.followup.send(f"Mensaje enviado exitosamente a través del webhook. ID del mensaje: {message.id}", ephemeral=True)
                
                for file in files:
                    file.close()
                
                return
            except Exception as e:
                await interaction.followup.send(f"Error al enviar a través del webhook: {str(e)}\nSe generará un código para usar con un canal específico.", ephemeral=True)
        
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        self.embed_cache.add_embed(code, {
            "content": self.content,
            "embeds": self.embeds.copy(),
            "webhook_url": self.webhook_url,
            "message_id": self.message_id,
            "attachments": self.attachments.copy(),
            "expires_at": datetime.now() + timedelta(minutes=5)
        })
        
        await interaction.response.edit_message(
            content=f"Tu mensaje está listo para ser enviado.\nUsa `/embed codigo:{code} canal:@canal` para enviarlo a un canal específico.\nEste código expirará en 5 minutos.",
            embed=None,
            view=None
        )

class MainDropdown(ui.Select):
    def __init__(self, view):
        self.main_view = view
        
        options = [
            discord.SelectOption(
                label="Gestionar contenido", 
                description="Añadir o modificar el contenido del mensaje",
                value="manage_content"
            ),
            discord.SelectOption(
                label="Gestionar embeds", 
                description="Crear, modificar o eliminar embeds",
                value="manage_embeds"
            ),
            discord.SelectOption(
                label="Gestionar Webhook", 
                description="Configurar webhook para enviar mensaje",
                value="manage_webhook"
            ),
            discord.SelectOption(
                label="Imágenes adjuntas", 
                description="Configurar imágenes adjuntas al mensaje",
                value="manage_attachments"
            ),
            discord.SelectOption(
                label="Guardar datos", 
                description="Guardar el embed en un archivo JSON",
                value="save_data"
            ),
            discord.SelectOption(
                label="Enviar mensaje", 
                description="Obtener código para enviar el mensaje",
                value="send"
            ),
            discord.SelectOption(
                label="Eliminar todo", 
                description="Eliminar todo el contenido",
                value="delete"
            )
        ]
        
        super().__init__(placeholder="Selecciona una opción", options=options)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.main_view.user.id:
            await interaction.response.send_message("No puedes interactuar con este menú.", ephemeral=True)
            return
        
        selected_value = self.values[0]
        
        if selected_value == "manage_content":
            from .content_view import ContentView
            content_view = ContentView(self.main_view)
            await content_view.show(interaction)
        
        elif selected_value == "manage_embeds":
            from .embeds_views import EmbedsView
            embeds_view = EmbedsView(self.main_view)
            await embeds_view.show(interaction)
        
        elif selected_value == "manage_webhook":
            from .webhook_view import WebhookView
            webhook_view = WebhookView(self.main_view)
            await webhook_view.show(interaction)
        
        elif selected_value == "manage_attachments":
            from .attachments_view import AttachmentsView
            attachments_view = AttachmentsView(self.main_view)
            await attachments_view.show(interaction)
        
        elif selected_value == "save_data":
            from .save_view import SaveView
            save_view = SaveView(self.main_view)
            await save_view.show(interaction)
        
        elif selected_value == "send":
            if not self.main_view.content and not self.main_view.embeds and not self.main_view.attachments:
                await interaction.response.send_message(
                    "No hay nada que enviar. Añade contenido, embeds o al menos una imagen adjunta.",
                    ephemeral=True
                )
                return
            
            await self.main_view.send_final_message(interaction)
        
        elif selected_value == "delete":
            from .confirm_delete_view import ConfirmDeleteView
            confirm_view = ConfirmDeleteView(self.main_view)
            await interaction.response.edit_message(
                content="¿Estás seguro de que deseas eliminar todo el contenido?",
                embed=None,
                view=confirm_view
            )