import discord
from discord import ui
import re

class WebhookView(ui.View):
    def __init__(self, main_view):
        super().__init__(timeout=1800)
        self.main_view = main_view
    
    async def show(self, interaction):
        embed = discord.Embed(
            title="Gestión de Webhook",
            description="Configura un webhook para enviar o editar mensajes.",
            color=discord.Color.blue()
        )
        
        content = ""
        
        if self.main_view.webhook_url:
            content += f"URL del webhook: {self.main_view.webhook_url}\n\n"
            
            if self.main_view.webhook_name:
                content += f"Nombre personalizado: {self.main_view.webhook_name}\n"
            
            if self.main_view.webhook_avatar:
                content += f"Avatar personalizado: {self.main_view.webhook_avatar}\n"
            
            if self.main_view.message_id:
                content += f"\nID del mensaje a editar: {self.main_view.message_id}"
                embed.add_field(
                    name="Modo de edición",
                    value="Se editará un mensaje existente con la ID especificada.",
                    inline=False
                )
            else:
                embed.add_field(
                    name="Modo de envío",
                    value="Se enviará un nuevo mensaje a través del webhook.",
                    inline=False
                )
        else:
            content = "No hay ningún webhook configurado."
            
        await interaction.response.edit_message(
            content=content,
            embed=embed,
            view=self
        )
    
    @ui.button(label="Volver atrás", style=discord.ButtonStyle.secondary)
    async def go_back(self, interaction: discord.Interaction, button: ui.Button):
        await self.main_view.update_message(interaction)
    
    @ui.button(label="Configurar webhook", style=discord.ButtonStyle.primary)
    async def set_webhook(self, interaction: discord.Interaction, button: ui.Button):
        modal = WebhookModal(self.main_view)
        await interaction.response.send_modal(modal)
    
    @ui.button(label="Configurar apariencia", style=discord.ButtonStyle.primary)
    async def set_appearance(self, interaction: discord.Interaction, button: ui.Button):
        if not self.main_view.webhook_url:
            await interaction.response.send_message(
                "Primero debes configurar un webhook antes de personalizar su apariencia.",
                ephemeral=True
            )
            return
            
        modal = WebhookAppearanceModal(self.main_view)
        await interaction.response.send_modal(modal)
    
    @ui.button(label="Configurar ID de mensaje", style=discord.ButtonStyle.primary)
    async def set_message_id(self, interaction: discord.Interaction, button: ui.Button):
        if not self.main_view.webhook_url:
            await interaction.response.send_message(
                "Primero debes configurar un webhook antes de especificar un ID de mensaje.",
                ephemeral=True
            )
            return
            
        modal = MessageIdModal(self.main_view)
        await interaction.response.send_modal(modal)
    
    @ui.button(label="Eliminar configuración", style=discord.ButtonStyle.danger, row=1)
    async def delete_webhook(self, interaction: discord.Interaction, button: ui.Button):
        self.main_view.webhook_url = None
        self.main_view.webhook_name = None
        self.main_view.webhook_avatar = None
        self.main_view.message_id = None
        await interaction.response.edit_message(
            content="Configuración de webhook y mensaje eliminada correctamente.",
            embed=discord.Embed(
                title="Configuración Eliminada",
                description="La configuración de webhook y mensaje ha sido eliminada.",
                color=discord.Color.green()
            ),
            view=self
        )

class WebhookModal(ui.Modal, title="Configurar Webhook"):
    webhook_url = ui.TextInput(
        label="URL del Webhook",
        style=discord.TextStyle.paragraph,
        placeholder="https://discord.com/api/webhooks/...",
        required=True
    )
    
    def __init__(self, main_view):
        super().__init__()
        self.main_view = main_view
        
        if main_view.webhook_url:
            self.webhook_url.default = main_view.webhook_url
    
    async def on_submit(self, interaction: discord.Interaction):
        webhook_url = self.webhook_url.value.strip()
        
        webhook_pattern = r'https://(?:ptb\.|canary\.)?discord\.com/api/webhooks/\d+/.+'
        if not re.match(webhook_pattern, webhook_url):
            await interaction.response.send_message(
                "La URL del webhook no es válida. Debe ser una URL de webhook de Discord.",
                ephemeral=True
            )
            return
        
        self.main_view.webhook_url = webhook_url
        
        await interaction.response.edit_message(
            content=f"Webhook configurado correctamente: {webhook_url}",
            embed=discord.Embed(
                title="Webhook Configurado",
                description="El webhook ha sido configurado y se utilizará al enviar el mensaje.",
                color=discord.Color.green()
            ),
            view=WebhookView(self.main_view)
        )

class WebhookAppearanceModal(ui.Modal, title="Configurar Apariencia del Webhook"):
    webhook_name = ui.TextInput(
        label="Nombre del Webhook",
        style=discord.TextStyle.short,
        placeholder="Nombre personalizado para el webhook",
        required=False,
        max_length=80
    )
    
    webhook_avatar = ui.TextInput(
        label="Avatar del Webhook",
        style=discord.TextStyle.short,
        placeholder="URL de la imagen del avatar",
        required=False
    )
    
    def __init__(self, main_view):
        super().__init__()
        self.main_view = main_view
        
        if main_view.webhook_name:
            self.webhook_name.default = main_view.webhook_name
        
        if main_view.webhook_avatar:
            self.webhook_avatar.default = main_view.webhook_avatar
    
    async def on_submit(self, interaction: discord.Interaction):
        webhook_name = self.webhook_name.value.strip() if self.webhook_name.value else None
        webhook_avatar = self.webhook_avatar.value.strip() if self.webhook_avatar.value else None
        
        if webhook_avatar and not webhook_avatar.startswith(('http://', 'https://')):
            await interaction.response.send_message(
                "La URL del avatar debe comenzar con http:// o https://",
                ephemeral=True
            )
            return
        
        self.main_view.webhook_name = webhook_name
        self.main_view.webhook_avatar = webhook_avatar
        
        description = "La apariencia del webhook ha sido configurada."
        if webhook_name:
            description += f"\nNombre: {webhook_name}"
        if webhook_avatar:
            description += f"\nAvatar: Configurado"
        
        await interaction.response.edit_message(
            content="Apariencia del webhook configurada correctamente.",
            embed=discord.Embed(
                title="Apariencia Configurada",
                description=description,
                color=discord.Color.green()
            ),
            view=WebhookView(self.main_view)
        )

class MessageIdModal(ui.Modal, title="Configurar ID de Mensaje"):
    message_id = ui.TextInput(
        label="ID del Mensaje",
        style=discord.TextStyle.short,
        placeholder="ID del mensaje a editar",
        required=True
    )
    
    def __init__(self, main_view):
        super().__init__()
        self.main_view = main_view
        
        if main_view.message_id:
            self.message_id.default = main_view.message_id
    
    async def on_submit(self, interaction: discord.Interaction):
        message_id = self.message_id.value.strip()
        
        if not message_id.isdigit():
            await interaction.response.send_message(
                "La ID del mensaje debe ser un número.",
                ephemeral=True
            )
            return
        
        self.main_view.message_id = message_id
        
        await interaction.response.edit_message(
            content=f"ID de mensaje configurado: {message_id}",
            embed=discord.Embed(
                title="ID de Mensaje Configurado",
                description="El mensaje con esta ID será editado en lugar de enviar uno nuevo.",
                color=discord.Color.green()
            ),
            view=WebhookView(self.main_view)
        )