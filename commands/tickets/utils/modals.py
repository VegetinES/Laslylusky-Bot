import discord

class TicketNameModal(discord.ui.Modal, title="Nombre de tickets"):
    def __init__(self, current_name="ticket-{id}"):
        super().__init__()
        
        self.ticket_name = discord.ui.TextInput(
            label="Formato de nombre para tickets",
            placeholder="ticket-{id}",
            default=current_name,
            required=True,
            max_length=30
        )
        
        self.add_item(self.ticket_name)
        self.callback = None
    
    async def on_submit(self, interaction: discord.Interaction):
        if self.callback:
            await self.callback(interaction, self.ticket_name.value)
        else:
            await interaction.response.send_message(
                f"Nombre configurado: {self.ticket_name.value}",
                ephemeral=True
            )

class EmbedTitleDescriptionModal(discord.ui.Modal, title="Configurar Embed"):
    def __init__(self, current_title="", current_description=""):
        super().__init__()
        
        self.title_input = discord.ui.TextInput(
            label="Título (opcional)",
            placeholder="Título del embed",
            default=current_title,
            required=False,
            max_length=256
        )
        
        self.description_input = discord.ui.TextInput(
            label="Descripción (obligatoria)",
            placeholder="Descripción del embed",
            default=current_description,
            required=True,
            style=discord.TextStyle.paragraph,
            max_length=4000
        )
        
        self.add_item(self.title_input)
        self.add_item(self.description_input)
        self.callback = None
    
    async def on_submit(self, interaction: discord.Interaction):
        if self.callback:
            await self.callback(interaction, self.title_input.value, self.description_input.value)
        else:
            await interaction.response.send_message(
                "Embed configurado",
                ephemeral=True
            )

class MessageTextModal(discord.ui.Modal, title="Mensaje de texto"):
    def __init__(self, current_message=""):
        super().__init__()
        
        self.message = discord.ui.TextInput(
            label="Mensaje",
            placeholder="Escribe el mensaje",
            default=current_message,
            required=True,
            style=discord.TextStyle.paragraph,
            max_length=2000
        )
        
        self.add_item(self.message)
        self.callback = None
    
    async def on_submit(self, interaction: discord.Interaction):
        if self.callback:
            await self.callback(interaction, self.message.value)
        else:
            await interaction.response.send_message(
                "Mensaje configurado",
                ephemeral=True
            )

class EmbedFieldModal(discord.ui.Modal, title="Campo de Embed"):
    def __init__(self, current_name="", current_value="", current_inline=False):
        super().__init__()
        
        self.name = discord.ui.TextInput(
            label="Nombre del campo",
            placeholder="Título del campo",
            default=current_name,
            required=True,
            max_length=256
        )
        
        self.value = discord.ui.TextInput(
            label="Valor del campo",
            placeholder="Contenido del campo",
            default=current_value,
            required=True,
            style=discord.TextStyle.paragraph,
            max_length=1024
        )
        
        self.inline = discord.ui.TextInput(
            label="Inline (si/no)",
            placeholder="Escribe 'si' para que sea inline",
            default="si" if current_inline else "no",
            required=True,
            max_length=3
        )
        
        self.add_item(self.name)
        self.add_item(self.value)
        self.add_item(self.inline)
        self.callback = None
    
    async def on_submit(self, interaction: discord.Interaction):
        inline = self.inline.value.lower() in ["si", "sí", "s", "yes", "y", "true", "t"]
        
        if self.callback:
            await self.callback(interaction, self.name.value, self.value.value, inline)
        else:
            await interaction.response.send_message(
                f"Campo configurado: {self.name.value}",
                ephemeral=True
            )

class ImageUrlModal(discord.ui.Modal, title="URL de imagen"):
    def __init__(self, image_type="imagen"):
        super().__init__()
        
        self.url = discord.ui.TextInput(
            label=f"URL de {image_type}",
            placeholder="https://ejemplo.com/imagen.png",
            required=True
        )
        
        self.add_item(self.url)
        self.callback = None
    
    async def on_submit(self, interaction: discord.Interaction):
        if self.callback:
            await self.callback(interaction, self.url.value)
        else:
            await interaction.response.send_message(
                "URL configurada",
                ephemeral=True
            )

class ButtonConfigModal(discord.ui.Modal, title="Configurar botón"):
    def __init__(self, current_label="Abrir Ticket", current_emoji="🎫", current_name_format="ticket-{id}", current_description=""):
        super().__init__()
        
        self.label = discord.ui.TextInput(
            label="Texto del botón",
            placeholder="Abrir Ticket",
            default=current_label,
            required=True,
            max_length=80
        )
        
        self.emoji = discord.ui.TextInput(
            label="Emoji (opcional)",
            placeholder="🎫",
            default=current_emoji,
            required=False,
            max_length=5
        )
        
        self.name_format = discord.ui.TextInput(
            label="Formato del nombre del ticket",
            placeholder="ticket-{id}",
            default=current_name_format,
            required=True,
            max_length=100
        )
        
        self.description = discord.ui.TextInput(
            label="Descripción (opcional)",
            placeholder="Descripción para el menú desplegable",
            default=current_description,
            required=False,
            max_length=100
        )
        
        self.add_item(self.label)
        self.add_item(self.emoji)
        self.add_item(self.name_format)
        self.add_item(self.description)
        self.callback = None
    
    async def on_submit(self, interaction: discord.Interaction):
        if self.callback:
            await self.callback(interaction, self.label.value, self.emoji.value, self.name_format.value, self.description.value)
        else:
            await interaction.response.send_message(
                "Botón configurado",
                ephemeral=True
            )

class UserIdModal(discord.ui.Modal, title="ID de usuario"):
    def __init__(self):
        super().__init__()
        
        self.user_id = discord.ui.TextInput(
            label="ID del usuario",
            placeholder="123456789012345678",
            required=True
        )
        
        self.add_item(self.user_id)
        self.callback = None
    
    async def on_submit(self, interaction: discord.Interaction):
        if self.callback:
            await self.callback(interaction, self.user_id.value)
        else:
            await interaction.response.send_message(
                f"Usuario ID: {self.user_id.value}",
                ephemeral=True
            )

class EmbedFooterModal(discord.ui.Modal, title="Configurar Footer"):
    def __init__(self, current_footer=""):
        super().__init__()
        
        self.footer = discord.ui.TextInput(
            label="Footer (opcional)",
            placeholder="Texto del footer",
            default=current_footer,
            required=False,
            max_length=256
        )
        
        self.add_item(self.footer)
        self.callback = None
    
    async def on_submit(self, interaction: discord.Interaction):
        if self.callback:
            await self.callback(interaction, self.footer.value)
        else:
            await interaction.response.send_message(
                "Footer configurado",
                ephemeral=True
            )

class TicketCloseModal(discord.ui.Modal, title="Cerrar Ticket"):
    def __init__(self):
        super().__init__()
        
        self.reason = discord.ui.TextInput(
            label="Razón del cierre",
            placeholder="Escribe la razón por la que se cierra el ticket",
            required=True,
            style=discord.TextStyle.paragraph,
            max_length=1000
        )
        
        self.resolved = discord.ui.TextInput(
            label="¿Se resolvió el problema? (si/no)",
            placeholder="si",
            default="si",
            required=True,
            max_length=3
        )
        
        self.add_item(self.reason)
        self.add_item(self.resolved)
        self.callback = None
    
    async def on_submit(self, interaction: discord.Interaction):
        resolved = self.resolved.value.lower() in ["si", "sí", "s", "yes", "y", "true", "t"]
        
        if self.callback:
            await self.callback(interaction, self.reason.value, resolved)
        else:
            await interaction.response.send_message(
                "Ticket cerrado",
                ephemeral=True
            )