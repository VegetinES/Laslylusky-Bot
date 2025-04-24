import discord
from discord import ui
import random
import string
from datetime import datetime, timedelta
from .content_view import ContentView
from .embed_builder_view import EmbedBuilderView

class EmbedMainView(ui.View):
    def __init__(self, bot, user, embed_cache):
        super().__init__(timeout=600)
        self.bot = bot
        self.user = user
        self.embed_cache = embed_cache
        self.content = None
        self.embed = None
        
        # Añadir el selector con las opciones principales
        self.add_item(MainDropdown(self))
    
    async def update_message(self, interaction, content=None, embed=None, view=None):
        if view is None:
            view = self
        
        if content is None and embed is None:
            # Mostrar la vista previa real del mensaje
            preview_embed = discord.Embed(
                description="Vista previa de tu mensaje:",
                color=discord.Color.blue()
            )
            
            # Para la vista principal, mostrar una vista previa más simple
            message_content = None
            message_embed = None
            
            if self.content:
                message_content = self.content
                preview_embed.add_field(name="Contenido del mensaje", 
                                      value="Se ha configurado el contenido del mensaje", 
                                      inline=False)
            
            if self.embed:
                message_embed = self.embed
                preview_embed.add_field(name="Embed", 
                                      value="Se ha configurado un embed (visible en la vista previa)", 
                                      inline=False)
            
            await interaction.response.edit_message(content=message_content, embed=message_embed if message_embed else preview_embed, view=view)
        else:
            # Si se proporciona un mensaje y/o embed específico, usarlos directamente
            await interaction.response.edit_message(content=content, embed=embed, view=view)
    
    async def send_final_embed(self, interaction):
        # Generar un código único
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # Guardar el embed en caché con un tiempo de expiración
        self.embed_cache.add_embed(code, {
            "content": self.content,
            "embed": self.embed,
            "expires_at": datetime.now() + timedelta(minutes=5)
        })
        
        # Mostrar el código al usuario
        await interaction.response.edit_message(
            content=f"Tu embed está listo para ser enviado.\nUsa `/embed codigo:{code} canal:@canal` para enviarlo a un canal específico.\nEste código expirará en 5 minutos.",
            embed=None,
            view=None
        )

class MainDropdown(ui.Select):
    def __init__(self, view):
        self.main_view = view
        
        options = [
            discord.SelectOption(
                label="Añadir contenido del mensaje", 
                description="Añade un mensaje de texto normal",
                value="add_content"
            ),
            discord.SelectOption(
                label="Añadir embed", 
                description="Crea un mensaje embed",
                value="add_embed"
            ),
            discord.SelectOption(
                label="Eliminar", 
                description="Eliminar todo el mensaje",
                value="delete"
            ),
            discord.SelectOption(
                label="Enviar embed", 
                description="Obtén un código para enviar el embed a un canal",
                value="send"
            )
        ]
        
        # Actualizar la opción de contenido si ya existe
        if view.content:
            options[0] = discord.SelectOption(
                label="Gestionar contenido del mensaje", 
                description="Modifica o elimina el contenido del mensaje",
                value="manage_content"
            )
        
        super().__init__(placeholder="Selecciona una opción", options=options)
    
    async def callback(self, interaction: discord.Interaction):
        # Verificar que sea el usuario correcto
        if interaction.user.id != self.main_view.user.id:
            await interaction.response.send_message("No puedes interactuar con este menú.", ephemeral=True)
            return
        
        selected_value = self.values[0]
        
        if selected_value == "add_content" or selected_value == "manage_content":
            if selected_value == "add_content":
                # Mostrar modal para añadir contenido
                modal = ContentModal(self.main_view)
                await interaction.response.send_modal(modal)
            else:
                # Mostrar vista para gestionar el contenido existente
                content_view = ContentView(self.main_view)
                preview_embed = discord.Embed(
                    description=f"Contenido actual del mensaje:\n\n{self.main_view.content}",
                    color=discord.Color.blue()
                )
                await interaction.response.edit_message(embed=preview_embed, view=content_view)
        
        elif selected_value == "add_embed":
            try:
                # Iniciar el constructor de embed
                if not self.main_view.embed:
                    self.main_view.embed = discord.Embed(
                        description="Este es tu nuevo embed. Configúralo usando las opciones del menú desplegable.",
                        color=discord.Color.blue()
                    )
                    
                embed_view = EmbedBuilderView(self.main_view)
                
                # Debug: Mostrar información sobre el contenido y embed
                print(f"Debug - Content: {self.main_view.content}, Has embed: {self.main_view.embed is not None}")
                
                # Mostrar vista previa del embed actual
                preview_content = self.main_view.content if self.main_view.content else None
                
                # Usar un try/except específico para la edición
                try:
                    await interaction.response.edit_message(
                        content=preview_content,
                        embed=self.main_view.embed,
                        view=embed_view
                    )
                except Exception as edit_error:
                    print(f"Error al editar mensaje: {type(edit_error).__name__}: {edit_error}")
                    # Intentar un enfoque alternativo
                    try:
                        await interaction.response.send_message(
                            "Hubo un problema con la interacción. Intenta usar el comando nuevamente.",
                            ephemeral=True
                        )
                    except:
                        pass
                    
            except Exception as e:
                print(f"Error completo en add_embed: {type(e).__name__}: {e}")
                # Intentar informar al usuario sobre el error
                try:
                    await interaction.response.send_message(
                        f"Error al añadir embed: {type(e).__name__}. Por favor, intenta nuevamente.",
                        ephemeral=True
                    )
                except:
                    pass
        
        elif selected_value == "delete":
            # Confirmar eliminación
            confirm_view = ConfirmDeleteView(self.main_view)
            await interaction.response.edit_message(
                content="¿Estás seguro de que deseas eliminar todo el mensaje?",
                embed=None,
                view=confirm_view
            )
        
        elif selected_value == "send":
            # Verificar que haya al menos contenido o embed
            if not self.main_view.content and not self.main_view.embed:
                await interaction.response.send_message("No hay nada que enviar. Añade contenido o un embed primero.", ephemeral=True)
                return
            
            await self.main_view.send_final_embed(interaction)

class ContentModal(ui.Modal, title="Contenido del Mensaje"):
    content = ui.TextInput(
        label="Contenido",
        style=discord.TextStyle.paragraph,
        placeholder="Escribe el contenido del mensaje aquí...",
        max_length=2000,
        required=False
    )
    
    def __init__(self, view):
        super().__init__()
        self.main_view = view
        # Si ya hay contenido, pre-rellenar el campo
        if view.content:
            self.content.default = view.content
    
    async def on_submit(self, interaction: discord.Interaction):
        self.main_view.content = self.content.value
        
        # Actualizar la opción en el menú desplegable
        for child in self.main_view.children:
            if isinstance(child, MainDropdown):
                for option in child.options:
                    if option.value == "add_content":
                        option.label = "Gestionar contenido del mensaje"
                        option.value = "manage_content"
                        break
        
        await self.main_view.update_message(interaction)

class ConfirmDeleteView(ui.View):
    def __init__(self, original_view):
        super().__init__(timeout=180)
        self.original_view = original_view
    
    @ui.button(label="Confirmar", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        # Resetear todo
        self.original_view.content = None
        self.original_view.embed = None
        
        # Actualizar las opciones del menú desplegable
        new_main_view = EmbedMainView(self.original_view.bot, self.original_view.user, self.original_view.embed_cache)
        
        await interaction.response.edit_message(
            content=None,
            embed=discord.Embed(
                description="Mensaje eliminado. Puedes comenzar de nuevo.",
                color=discord.Color.blue()
            ),
            view=new_main_view
        )
    
    @ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.edit_message(
            content=None,
            view=self.original_view
        )
        await self.original_view.update_message(interaction)