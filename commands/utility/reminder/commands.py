from .utils import can_dm_user
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
from .views import ReminderCreateView, ReminderListView, ReminderManageView
from .database import get_reminder_by_id, get_upcoming_reminders, get_past_reminders

class ReminderCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    reminder_group = app_commands.Group(name="recordatorio", description="Comandos para gestionar recordatorios")
    
    @reminder_group.command(name="crear", description="Crear un nuevo recordatorio")
    async def crear_recordatorio(self, interaction: discord.Interaction):
        try:
            can_send_dm = await can_dm_user(interaction.user)
            
            if not can_send_dm:
                await interaction.response.send_message(
                    "⚠️ **Atención**: No puedo enviarte mensajes directos. Por favor, habilita los mensajes directos para este servidor en la configuración de privacidad o los recordatorios no podrán ser entregados.",
                    ephemeral=True
                )
                return
                
            view = ReminderCreateView(self.bot, interaction.user)
            await interaction.response.send_message(
                "Configura tu recordatorio usando los botones a continuación:",
                view=view,
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"Ocurrió un error al crear el recordatorio: {str(e)}",
                ephemeral=True
            )
    
    @reminder_group.command(name="listar", description="Ver tus recordatorios")
    async def ver_recordatorios(self, interaction: discord.Interaction):
        try:
            view = ReminderListView(self.bot, interaction.user)
            await interaction.response.send_message(
                "Selecciona una opción para ver tus recordatorios:",
                view=view,
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"Ocurrió un error al ver los recordatorios: {str(e)}",
                ephemeral=True
            )
    
    @reminder_group.command(name="gestionar", description="Gestionar un recordatorio específico")
    @app_commands.describe(id="ID del recordatorio a gestionar")
    async def gestionar_recordatorio(self, interaction: discord.Interaction, id: str):
        try:
            reminder = await get_reminder_by_id(id, interaction.user.id)
            
            if not reminder:
                await interaction.response.send_message(
                    f"No se encontró ningún recordatorio con ID {id} o no tienes permisos para gestionarlo.",
                    ephemeral=True
                )
                return
            
            view = ReminderManageView(self.bot, interaction.user, reminder)
            await interaction.response.send_message(
                f"Gestionando recordatorio: {reminder['title']}",
                view=view,
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"Ocurrió un error al gestionar el recordatorio: {str(e)}",
                ephemeral=True
            )

    @gestionar_recordatorio.autocomplete('id')
    async def gestionar_recordatorio_autocomplete(self, interaction: discord.Interaction, current: str):
        try:
            upcoming_reminders = await get_upcoming_reminders(interaction.user.id)
            past_reminders = await get_past_reminders(interaction.user.id)
            all_reminders = upcoming_reminders + past_reminders
            
            choices = []
            for reminder in all_reminders:
                reminder_id = str(reminder['_id'])
                title = reminder['title']
                
                if len(title) > 80:
                    title = title[:77] + "..."
                
                choice_name = f"{reminder_id} - {title}"
                if len(choice_name) > 100:
                    choice_name = choice_name[:97] + "..."
                
                if current.lower() in choice_name.lower():
                    choices.append(app_commands.Choice(name=choice_name, value=reminder_id))
                
                if len(choices) >= 25:
                    break
            
            return choices
        except Exception:
            return []