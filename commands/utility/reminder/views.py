import asyncio
import discord
from discord.ui import View, Button
import datetime
from .database import (
    get_reminder_by_id,
    save_reminder, 
    get_upcoming_reminders, 
    get_past_reminders, 
    delete_reminder,
    update_reminder
)
from .modals import TitleDescriptionModal, DateTimeModal
from .utils import can_dm_user, format_reminder_time
from .scheduler import schedule_reminder

class ReminderCreateView(View):
    def __init__(self, bot, user):
        super().__init__(timeout=1800)
        self.bot = bot
        self.user = user
        self.title = None
        self.description = None
        self.reminder_date = None
        self.reminder_time = None
        self.timezone_offset = None
        
    @discord.ui.button(label="Título y descripción", style=discord.ButtonStyle.primary, row=0)
    async def title_description_button(self, interaction: discord.Interaction, button: Button):
        modal = TitleDescriptionModal(self.title, self.description)
        modal.callback = self.title_description_callback
        await interaction.response.send_modal(modal)
    
    async def title_description_callback(self, interaction, title, description):
        self.title = title
        self.description = description
        await interaction.response.edit_message(
            content=self._get_status_message(),
            view=self
        )
    
    @discord.ui.button(label="Fecha del recordatorio", style=discord.ButtonStyle.primary, row=0)
    async def date_button(self, interaction: discord.Interaction, button: Button):
        modal = DateTimeModal(self.reminder_date, self.reminder_time, self.timezone_offset)
        modal.callback = self.date_callback
        await interaction.response.send_modal(modal)
    
    async def date_callback(self, interaction, date, time, timezone):
        self.reminder_date = date
        self.reminder_time = time
        self.timezone_offset = timezone
        await interaction.response.edit_message(
            content=self._get_status_message(),
            view=self
        )
    
    @discord.ui.button(label="Guardar recordatorio", style=discord.ButtonStyle.success, row=1)
    async def save_button(self, interaction: discord.Interaction, button: Button):
        if not self.title or not self.description or not self.reminder_date or not self.reminder_time:
            await interaction.response.send_message(
                "Debes completar todos los campos antes de guardar el recordatorio.",
                ephemeral=True
            )
            return
        
        can_send_dm = await can_dm_user(self.user)
        if not can_send_dm:
            await interaction.response.send_message(
                "⚠️ **Atención**: No puedo enviarte mensajes directos. Por favor, habilita los mensajes directos para este servidor en la configuración de privacidad o el recordatorio no podrá ser entregado.",
                ephemeral=True
            )
            return
        
        try:
            date_parts = self.reminder_date.split('/')
            time_parts = self.reminder_time.split(':')
            
            day = int(date_parts[0])
            month = int(date_parts[1])
            year = int(date_parts[2])
            
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            
            timezone_offset = self.timezone_offset.strip()
            offset_hours = 0
            offset_minutes = 0
            
            if timezone_offset:
                if timezone_offset[0] in ('+', '-'):
                    sign = 1 if timezone_offset[0] == '+' else -1
                    tz_parts = timezone_offset[1:].split(':')
                    offset_hours = sign * int(tz_parts[0])
                    if len(tz_parts) > 1:
                        offset_minutes = sign * int(tz_parts[1])
            
            offset = datetime.timedelta(hours=offset_hours, minutes=offset_minutes)
            tzinfo = datetime.timezone(offset)
            local_dt = datetime.datetime(year, month, day, hour, minute, tzinfo=tzinfo)
            
            utc_dt = local_dt.astimezone(datetime.timezone.utc)
            
            now = datetime.datetime.now(datetime.timezone.utc)
            if utc_dt <= now:
                await interaction.response.send_message(
                    "⚠️ La fecha y hora que has seleccionado ya ha pasado. Por favor, elige una fecha y hora futura.",
                    ephemeral=True
                )
                return
            
            reminder_id = await save_reminder(
                self.user.id,
                self.title,
                self.description,
                utc_dt,
                timezone_offset
            )
            
            await schedule_reminder(self.bot, reminder_id, self.user.id, utc_dt)
            
            user_time = f"{self.reminder_date} a las {self.reminder_time} {self.timezone_offset}"
            
            await interaction.response.edit_message(
                content=f"✅ Recordatorio guardado correctamente con ID: `{reminder_id}`\nRecibirás una notificación el {user_time}",
                view=None
            )
            
        except Exception as e:
            await interaction.response.send_message(
                f"Error al guardar el recordatorio: {str(e)}",
                ephemeral=True
            )
    
    @discord.ui.button(label="Restablecer todo", style=discord.ButtonStyle.danger, row=1)
    async def reset_button(self, interaction: discord.Interaction, button: Button):
        confirm_view = ConfirmView()
        confirm_view.callback = self.reset_callback
        await interaction.response.edit_message(
            content="¿Estás seguro de que deseas restablecer toda la información del recordatorio?",
            view=confirm_view
        )
    
    async def reset_callback(self, interaction, confirmed):
        if confirmed:
            self.title = None
            self.description = None
            self.reminder_date = None
            self.reminder_time = None
            self.timezone_offset = None
            await interaction.response.edit_message(
                content="Se ha restablecido toda la información del recordatorio.",
                view=self
            )
        else:
            await interaction.response.edit_message(
                content=self._get_status_message(),
                view=self
            )
    
    def _get_status_message(self):
        status = "Estado actual del recordatorio:\n\n"
        status += f"📌 **Título**: {self.title or 'No establecido'}\n"

        description_preview = None
        if self.description:
            if len(self.description) > 1600:
                description_preview = self.description[:1597] + "..."
            else:
                description_preview = self.description

        status += f"📝 **Descripción**: {description_preview or 'No establecida'}\n"
        status += f"📅 **Fecha + [GMT](https://www.timeanddate.com/time/map/)**: {self.reminder_date or 'No establecida'}\n"
        status += f"⏰ **Hora**: {self.reminder_time + ' ' + self.timezone_offset if self.reminder_time else 'No establecida'}\n"
        return status

class ReminderListView(View):
    def __init__(self, bot, user):
        super().__init__(timeout=1800)
        self.bot = bot
        self.user = user
        self.page = 0
        self.reminders = []
        self.reminder_type = None
    
    @discord.ui.button(label="Próximos recordatorios", style=discord.ButtonStyle.primary, row=0)
    async def upcoming_button(self, interaction: discord.Interaction, button: Button):
        self.reminders = await get_upcoming_reminders(self.user.id)
        self.page = 0
        self.reminder_type = 'upcoming'
        await self._show_reminders_page(interaction)
    
    @discord.ui.button(label="Recordatorios anteriores", style=discord.ButtonStyle.secondary, row=0)
    async def past_button(self, interaction: discord.Interaction, button: Button):
        self.reminders = await get_past_reminders(self.user.id)
        self.page = 0
        self.reminder_type = 'past'
        await self._show_reminders_page(interaction)
    
    async def _show_reminders_page(self, interaction):
        if not self.reminders:
            await interaction.response.edit_message(
                content=None,
                embed=discord.Embed(
                    title="Sin recordatorios",
                    description=f"No tienes recordatorios {'próximos' if self.reminder_type == 'upcoming' else 'anteriores'}.",
                    color=discord.Color.red()
                ),
                view=self
            )
            return
        
        reminders_per_page = 5
        start_idx = self.page * reminders_per_page
        end_idx = min(start_idx + reminders_per_page, len(self.reminders))
        
        embed = discord.Embed(
            title=f"{'Próximos recordatorios' if self.reminder_type == 'upcoming' else 'Recordatorios anteriores'}",
            description=f"Página {self.page + 1}/{(len(self.reminders) + reminders_per_page - 1) // reminders_per_page}",
            color=discord.Color.blue()
        )
        
        for i in range(start_idx, end_idx):
            reminder = self.reminders[i]
            description_preview = reminder['description'][:300] + "..." if len(reminder['description']) > 300 else reminder['description']
            
            reminder_time = reminder['reminder_time']
            if reminder_time.tzinfo is None:
                reminder_time = reminder_time.replace(tzinfo=datetime.timezone.utc)
            
            timestamp = int(reminder_time.timestamp())
            
            embed.add_field(
                name=f"📌 {reminder['title']}",
                value=(
                    f"**ID:** `{reminder['_id']}`\n"
                    f"**Descripción:** {description_preview}\n"
                    f"**Fecha:** <t:{timestamp}:F>\n"
                    f"{'**Enviado:** ✅' if reminder.get('sent', False) else ''}"
                ),
                inline=False
            )
        
        pagination_view = EnhancedPaginationView(self, len(self.reminders), reminders_per_page)
        await interaction.response.edit_message(embed=embed, view=pagination_view)

class EnhancedPaginationView(View):
    def __init__(self, parent_view, total_items, items_per_page):
        super().__init__(timeout=1800)
        self.parent_view = parent_view
        self.total_pages = (total_items + items_per_page - 1) // items_per_page
        
        self._add_reminder_selector()
        
        self._add_navigation_buttons()
    
    def _add_reminder_selector(self):
        reminders_per_page = 5
        start_idx = self.parent_view.page * reminders_per_page
        end_idx = min(start_idx + reminders_per_page, len(self.parent_view.reminders))
        
        options = []
        for i in range(start_idx, end_idx):
            reminder = self.parent_view.reminders[i]
            title = reminder['title']
            if len(title) > 25:
                title = title[:22] + "..."
            
            options.append(
                discord.SelectOption(
                    label=f"{title}",
                    value=str(reminder['_id']),
                    description=f"ID: {reminder['_id'][:10]}..."
                )
            )
        
        if options:
            select = discord.ui.Select(
                placeholder="Ver detalles de un recordatorio",
                options=options
            )
            select.callback = self.reminder_select_callback
            self.add_item(select)
    
    def _add_navigation_buttons(self):
        back_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary, 
            label="Volver", 
            emoji="🔙", 
            custom_id="back",
            row=2
        )
        back_button.callback = self.back_callback
        self.add_item(back_button)
        
        if self.total_pages > 1:
            prev_button = discord.ui.Button(
                style=discord.ButtonStyle.primary, 
                label="Anterior", 
                emoji="◀️", 
                custom_id="prev",
                disabled=self.parent_view.page == 0,
                row=1
            )
            prev_button.callback = self.prev_callback
            self.add_item(prev_button)
            
            next_button = discord.ui.Button(
                style=discord.ButtonStyle.primary, 
                label="Siguiente", 
                emoji="▶️", 
                custom_id="next",
                disabled=self.parent_view.page >= self.total_pages - 1,
                row=1
            )
            next_button.callback = self.next_callback
            self.add_item(next_button)
    
    async def reminder_select_callback(self, interaction: discord.Interaction):
        reminder_id = interaction.data["values"][0]
        
        reminder = await get_reminder_by_id(reminder_id, self.parent_view.user.id)
        
        if not reminder:
            await interaction.response.send_message(
                "No se pudo encontrar el recordatorio seleccionado.",
                ephemeral=True
            )
            return
        
        reminder_time = reminder['reminder_time']
        
        if reminder_time.tzinfo is None:
            reminder_time = reminder_time.replace(tzinfo=datetime.timezone.utc)
        
        timestamp = int(reminder_time.timestamp())
        
        embed = discord.Embed(
            title=f"📌 {reminder['title']}",
            description=reminder['description'],
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Fecha programada",
            value=f"<t:{timestamp}:F>",
            inline=False
        )
        
        if reminder.get('user_timezone'):
            embed.add_field(
                name="Zona horaria configurada",
                value=reminder['user_timezone'],
                inline=True
            )
        
        embed.add_field(
            name="Estado",
            value="Enviado ✅" if reminder.get('sent', False) else "Pendiente ⏳",
            inline=True
        )
        
        embed.add_field(
            name="ID",
            value=f"`{reminder['_id']}`",
            inline=False
        )
        
        created_at = reminder.get('created_at')
        if created_at and created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=datetime.timezone.utc)
        
        embed.set_footer(text=f"Creado: {created_at.strftime('%d/%m/%Y %H:%M')} UTC")
        
        view = ReminderDetailView(self, reminder)
        
        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=view
        )
    
    async def back_callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            content=None,
            embed=discord.Embed(
                title="Sistema de recordatorios",
                description="Selecciona una opción para ver tus recordatorios:",
                color=discord.Color.blue()
            ),
            view=self.parent_view
        )
    
    async def prev_callback(self, interaction: discord.Interaction):
        if self.parent_view.page > 0:
            self.parent_view.page -= 1
            await self.parent_view._show_reminders_page(interaction)
    
    async def next_callback(self, interaction: discord.Interaction):
        if self.parent_view.page < self.total_pages - 1:
            self.parent_view.page += 1
            await self.parent_view._show_reminders_page(interaction)

class ReminderDetailView(View):
    def __init__(self, list_view, reminder):
        super().__init__(timeout=1800)
        self.list_view = list_view
        self.reminder = reminder
        
        back_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary, 
            label="Volver a la lista", 
            emoji="🔙", 
            row=0
        )
        back_button.callback = self.back_callback
        self.add_item(back_button)
    
    async def back_callback(self, interaction: discord.Interaction):
        parent_list_view = self.list_view.parent_view
        await parent_list_view._show_reminders_page(interaction)


class PaginationView(View):
    def __init__(self, parent_view, total_items, items_per_page):
        super().__init__(timeout=1800)
        self.parent_view = parent_view
        self.total_pages = (total_items + items_per_page - 1) // items_per_page
        
        self.add_item(Button(style=discord.ButtonStyle.secondary, label="Volver", custom_id="back"))
        
        if self.total_pages > 1:
            self.add_item(Button(
                style=discord.ButtonStyle.primary, 
                label="Anterior", 
                custom_id="prev",
                disabled=parent_view.page == 0
            ))
            self.add_item(Button(
                style=discord.ButtonStyle.primary, 
                label="Siguiente", 
                custom_id="next",
                disabled=parent_view.page >= self.total_pages - 1
            ))
            
        for item in self.children:
            item.callback = self.button_callback
    
    async def button_callback(self, interaction: discord.Interaction):
        custom_id = interaction.data["custom_id"]
        
        if custom_id == "back":
            await interaction.response.edit_message(
                content="Selecciona una opción para ver tus recordatorios:",
                view=self.parent_view
            )
        elif custom_id == "prev":
            if self.parent_view.page > 0:
                self.parent_view.page -= 1
                await self.parent_view._show_reminders_page(interaction)
        elif custom_id == "next":
            if self.parent_view.page < self.total_pages - 1:
                self.parent_view.page += 1
                await self.parent_view._show_reminders_page(interaction)

class ReminderManageView(View):
    def __init__(self, bot, user, reminder):
        super().__init__(timeout=1800)
        self.bot = bot
        self.user = user
        self.reminder = reminder
        self.title = reminder["title"]
        self.description = reminder["description"]
        
        reminder_time_utc = reminder["reminder_time"]
        self.reminder_date = reminder_time_utc.strftime("%d/%m/%Y")
        self.reminder_time = reminder_time_utc.strftime("%H:%M")
        self.timezone_offset = "+00:00"
    
    @discord.ui.button(label="Título y descripción", style=discord.ButtonStyle.primary, row=0)
    async def title_description_button(self, interaction: discord.Interaction, button: Button):
        modal = TitleDescriptionModal(self.title, self.description)
        modal.callback = self.title_description_callback
        await interaction.response.send_modal(modal)
    
    async def title_description_callback(self, interaction, title, description):
        self.title = title
        self.description = description
        await interaction.response.edit_message(
            content=self._get_status_message(),
            view=self
        )
    
    @discord.ui.button(label="Fecha del recordatorio", style=discord.ButtonStyle.primary, row=0)
    async def date_button(self, interaction: discord.Interaction, button: Button):
        modal = DateTimeModal(self.reminder_date, self.reminder_time, self.timezone_offset)
        modal.callback = self.date_callback
        await interaction.response.send_modal(modal)
    
    async def date_callback(self, interaction, date, time, timezone):
        self.reminder_date = date
        self.reminder_time = time
        self.timezone_offset = timezone
        await interaction.response.edit_message(
            content=self._get_status_message(),
            view=self
        )
    
    @discord.ui.button(label="Guardar cambios", style=discord.ButtonStyle.success, row=1)
    async def save_button(self, interaction: discord.Interaction, button: Button):
        if not self.title or not self.description or not self.reminder_date or not self.reminder_time:
            await interaction.response.send_message(
                "Debes completar todos los campos antes de guardar los cambios.",
                ephemeral=True
            )
            return
        
        can_send_dm = await can_dm_user(self.user)
        if not can_send_dm:
            await interaction.response.send_message(
                "⚠️ **Atención**: No puedo enviarte mensajes directos. Por favor, habilita los mensajes directos para este servidor en la configuración de privacidad o el recordatorio no podrá ser entregado.",
                ephemeral=True
            )
            return
        
        try:
            date_parts = self.reminder_date.split('/')
            time_parts = self.reminder_time.split(':')
            
            day = int(date_parts[0])
            month = int(date_parts[1])
            year = int(date_parts[2])
            
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            
            timezone_offset = self.timezone_offset.strip()
            offset_hours = 0
            offset_minutes = 0
            
            if timezone_offset:
                if timezone_offset[0] in ('+', '-'):
                    sign = 1 if timezone_offset[0] == '+' else -1
                    tz_parts = timezone_offset[1:].split(':')
                    offset_hours = sign * int(tz_parts[0])
                    if len(tz_parts) > 1:
                        offset_minutes = sign * int(tz_parts[1])
            
            offset = datetime.timedelta(hours=offset_hours, minutes=offset_minutes)
            tzinfo = datetime.timezone(offset)
            local_dt = datetime.datetime(year, month, day, hour, minute, tzinfo=tzinfo)
            
            utc_dt = local_dt.astimezone(datetime.timezone.utc)
            
            now = datetime.datetime.now(datetime.timezone.utc)
            if utc_dt <= now:
                await interaction.response.send_message(
                    "⚠️ La fecha y hora que has seleccionado ya ha pasado. Por favor, elige una fecha y hora futura.",
                    ephemeral=True
                )
                return
            
            await update_reminder(
                str(self.reminder["_id"]),
                self.user.id,
                self.title,
                self.description,
                utc_dt,
                timezone_offset
            )
            
            await schedule_reminder(self.bot, str(self.reminder["_id"]), self.user.id, utc_dt)
            
            user_time = f"{self.reminder_date} a las {self.reminder_time} {self.timezone_offset}"
            
            await interaction.response.edit_message(
                content=f"✅ Recordatorio actualizado correctamente.\nRecibirás una notificación el {user_time}",
                view=None
            )
            
        except Exception as e:
            await interaction.response.send_message(
                f"Error al actualizar el recordatorio: {str(e)}",
                ephemeral=True
            )
    
    @discord.ui.button(label="Eliminar recordatorio", style=discord.ButtonStyle.danger, row=1)
    async def delete_button(self, interaction: discord.Interaction, button: Button):
        confirm_view = ConfirmView()
        confirm_view.callback = self.delete_callback
        await interaction.response.edit_message(
            content=f"¿Estás seguro de que deseas eliminar el recordatorio '{self.title}'?",
            view=confirm_view
        )
    
    async def delete_callback(self, interaction, confirmed):
        if confirmed:
            try:
                await delete_reminder(str(self.reminder["_id"]), self.user.id)
                await interaction.response.edit_message(
                    content=f"✅ El recordatorio '{self.title}' ha sido eliminado.",
                    view=None
                )
            except Exception as e:
                await interaction.response.send_message(
                    f"Error al eliminar el recordatorio: {str(e)}",
                    ephemeral=True
                )
        else:
            await interaction.response.edit_message(
                content=self._get_status_message(),
                view=self
            )
    
    def _get_status_message(self):
        status = f"Gestionando recordatorio ID: `{self.reminder['_id']}`\n\n"
        status += f"📌 **Título**: {self.title or 'No establecido'}\n"
        status += f"📝 **Descripción**: {self.description[:50] + '...' if self.description and len(self.description) > 50 else self.description or 'No establecida'}\n"
        status += f"📅 **Fecha + [GMT](https://www.timeanddate.com/time/map/)**: {self.reminder_date or 'No establecida'}\n"
        status += f"⏰ **Hora**: {self.reminder_time + ' ' + self.timezone_offset if self.reminder_time else 'No establecida'}\n"
        return status

class ConfirmView(View):
    def __init__(self):
        super().__init__(timeout=300)
        self.callback = None
    
    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.danger)
    async def confirm_button(self, interaction: discord.Interaction, button: Button):
        if self.callback:
            await self.callback(interaction, True)
    
    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancel_button(self, interaction: discord.Interaction, button: Button):
        if self.callback:
            await self.callback(interaction, False)

async def setup(bot):
    pass