import datetime
import discord
from discord.ui import Modal, TextInput
import re

class TitleDescriptionModal(Modal, title="Título y descripción del recordatorio"):
    def __init__(self, current_title=None, current_description=None):
        super().__init__(timeout=None)
        
        self.title_input = TextInput(
            label="Título del recordatorio",
            placeholder="Introduce un título para el recordatorio",
            default=current_title if current_title else None,
            min_length=1,
            max_length=256,
            required=True
        )
        
        self.description_input = TextInput(
            label="Descripción del recordatorio",
            placeholder="Introduce una descripción detallada",
            default=current_description if current_description else None,
            min_length=1,
            max_length=3000,
            style=discord.TextStyle.paragraph,
            required=True
        )
        
        self.add_item(self.title_input)
        self.add_item(self.description_input)
        
        self.callback = None
    
    async def on_submit(self, interaction: discord.Interaction):
        title = self.title_input.value.strip()
        description = self.description_input.value.strip()
        
        if self.callback:
            await self.callback(interaction, title, description)
        else:
            await interaction.response.send_message(
                "Título y descripción guardados correctamente.",
                ephemeral=True
            )

class DateTimeModal(Modal, title="Fecha y hora del recordatorio"):
    def __init__(self, current_date=None, current_time=None, current_timezone=None):
        super().__init__(timeout=None)
        
        self.date_input = TextInput(
            label="Fecha (dd/mm/aaaa)",
            placeholder="31/12/2023",
            default=current_date if current_date else None,
            required=True
        )
        
        self.time_input = TextInput(
            label="Hora (hh:mm)",
            placeholder="23:59",
            default=current_time if current_time else None,
            required=True
        )
        
        self.timezone_input = TextInput(
            label="Zona horaria (±hh:mm)",
            placeholder="+01:00",
            default=current_timezone if current_timezone else "+00:00",
            required=True
        )
        
        self.add_item(self.date_input)
        self.add_item(self.time_input)
        self.add_item(self.timezone_input)
        
        self.callback = None
    
    async def on_submit(self, interaction: discord.Interaction):
        date = self.date_input.value.strip()
        time = self.time_input.value.strip()
        timezone = self.timezone_input.value.strip()
        
        if not re.match(r"^\d{1,2}/\d{1,2}/\d{4}$", date):
            await interaction.response.send_message(
                "Formato de fecha inválido. Debe ser dd/mm/aaaa.",
                ephemeral=True
            )
            return
        
        if not re.match(r"^\d{1,2}:\d{2}$", time):
            await interaction.response.send_message(
                "Formato de hora inválido. Debe ser hh:mm.",
                ephemeral=True
            )
            return
        
        if not re.match(r"^[+-]\d{1,2}:\d{2}$", timezone):
            await interaction.response.send_message(
                "Formato de zona horaria inválido. Debe ser ±hh:mm.",
                ephemeral=True
            )
            return
        
        try:
            date_parts = date.split('/')
            day = int(date_parts[0])
            month = int(date_parts[1])
            year = int(date_parts[2])
            
            if not (1 <= day <= 31 and 1 <= month <= 12 and year >= 2023):
                await interaction.response.send_message(
                    "La fecha introducida no es válida.",
                    ephemeral=True
                )
                return
            
            time_parts = time.split(':')
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                await interaction.response.send_message(
                    "La hora introducida no es válida.",
                    ephemeral=True
                )
                return
            
            timezone_parts = timezone[1:].split(':')
            timezone_hour = int(timezone_parts[0])
            timezone_minute = int(timezone_parts[1])
            
            if not (0 <= timezone_hour <= 14 and 0 <= timezone_minute <= 59):
                await interaction.response.send_message(
                    "La zona horaria introducida no es válida.",
                    ephemeral=True
                )
                return
            
            offset_hours = int(timezone_hour) * (-1 if timezone[0] == '-' else 1)
            offset_minutes = int(timezone_minute) * (-1 if timezone[0] == '-' else 1)
            
            offset = datetime.timedelta(hours=offset_hours, minutes=offset_minutes)
            tzinfo = datetime.timezone(offset)
            
            local_dt = datetime.datetime(year, month, day, hour, minute, tzinfo=tzinfo)
            utc_dt = local_dt.astimezone(datetime.timezone.utc)
            
            now = datetime.datetime.now(datetime.timezone.utc)
            if utc_dt <= now:
                await interaction.response.send_message(
                    "⚠️ La fecha y hora que has seleccionado ya ha pasado. El recordatorio no se guardará con esta fecha.",
                    ephemeral=True
                )
            
            if self.callback:
                await self.callback(interaction, date, time, timezone)
            else:
                await interaction.response.send_message(
                    "Fecha y hora guardadas correctamente.",
                    ephemeral=True
                )
                
        except ValueError:
            await interaction.response.send_message(
                "Se ha producido un error al validar la fecha y hora. Asegúrate de que el formato es correcto.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"Error inesperado: {str(e)}",
                ephemeral=True
            )

async def setup(bot):
    pass