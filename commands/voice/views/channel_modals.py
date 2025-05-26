import discord
from discord import ui
from ..database import get_voice_channels, save_voice_channel
from .channel_message import create_channel_control_message

class ChannelNameModal(ui.Modal, title="Cambiar nombre del canal"):
    name = ui.TextInput(
        label="Nuevo nombre",
        placeholder="Introduce el nuevo nombre",
        max_length=100,
        required=True
    )
    
    def __init__(self, channel):
        super().__init__()
        self.channel = channel
        self.name.default = channel.name
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            await self.channel.edit(name=self.name.value)
            
            voice_channels = get_voice_channels(interaction.guild.id)
            if str(self.channel.id) in voice_channels:
                channel_data = voice_channels[str(self.channel.id)]
                channel_data["name"] = self.name.value
                save_voice_channel(interaction.guild.id, self.channel.id, channel_data)
            
            await create_channel_control_message(self.channel, update=True)
            
            await interaction.response.send_message(
                f"✅ Nombre del canal cambiado a: {self.name.value}",
                ephemeral=True
            )
        except discord.HTTPException as e:
            await interaction.response.send_message(
                f"❌ Error al cambiar el nombre: {str(e)}",
                ephemeral=True
            )

class ChannelLimitModal(ui.Modal, title="Cambiar límite de usuarios"):
    limit = ui.TextInput(
        label="Nuevo límite",
        placeholder="0 = sin límite, máximo 99",
        max_length=2,
        required=True
    )
    
    def __init__(self, channel):
        super().__init__()
        self.channel = channel
        self.limit.default = str(channel.user_limit)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            try:
                limit = int(self.limit.value)
                if limit < 0 or limit > 99:
                    await interaction.response.send_message(
                        "❌ El límite debe estar entre 0 y 99.",
                        ephemeral=True
                    )
                    return
            except ValueError:
                await interaction.response.send_message(
                    "❌ El límite debe ser un número.",
                    ephemeral=True
                )
                return
            
            await self.channel.edit(user_limit=limit)
            
            await create_channel_control_message(self.channel, update=True)
            
            limit_text = "sin límite" if limit == 0 else str(limit)
            await interaction.response.send_message(
                f"✅ Límite de usuarios establecido a: {limit_text}",
                ephemeral=True
            )
        except discord.HTTPException as e:
            await interaction.response.send_message(
                f"❌ Error al cambiar el límite: {str(e)}",
                ephemeral=True
            )