import asyncio
import datetime
from datetime import timezone
from .database import get_pending_reminders, mark_reminder_as_sent
import logging
import discord

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("reminder_scheduler")

scheduled_tasks = {}

async def schedule_reminder(bot, reminder_id, user_id, reminder_time):
    if reminder_time.tzinfo is None:
        reminder_time = reminder_time.replace(tzinfo=datetime.timezone.utc)
    
    if reminder_id in scheduled_tasks and not scheduled_tasks[reminder_id].done():
        scheduled_tasks[reminder_id].cancel()
    
    now = datetime.datetime.now(datetime.timezone.utc)
    time_delta = (reminder_time - now).total_seconds()
    
    if time_delta <= 0:
        await send_reminder(bot, reminder_id, user_id)
    else:
        task = asyncio.create_task(
            delayed_reminder(bot, reminder_id, user_id, time_delta)
        )
        scheduled_tasks[reminder_id] = task
        logger.info(f"Recordatorio {reminder_id} programado para {reminder_time} (en {time_delta:.2f} segundos)")

async def delayed_reminder(bot, reminder_id, user_id, delay):
    try:
        await asyncio.sleep(delay)
        await send_reminder(bot, reminder_id, user_id)
    except asyncio.CancelledError:
        logger.info(f"Recordatorio {reminder_id} cancelado")
    except Exception as e:
        logger.error(f"Error en delayed_reminder: {str(e)}")

async def send_reminder(bot, reminder_id, user_id):
    try:
        from .database import get_reminder_by_id
        
        reminder = await get_reminder_by_id(reminder_id, user_id)
        
        if not reminder:
            logger.warning(f"Recordatorio {reminder_id} no encontrado en la base de datos")
            return
        
        user = bot.get_user(user_id)
        if not user:
            try:
                user = await bot.fetch_user(user_id)
            except Exception as e:
                logger.error(f"No se pudo obtener el usuario {user_id}: {str(e)}")
                return
        
        reminder_time = reminder['reminder_time']
        if reminder_time.tzinfo is None:
            reminder_time = reminder_time.replace(tzinfo=datetime.timezone.utc)
        
        timestamp = int(reminder_time.timestamp())
        
        embed = discord.Embed(
            title="📅 Recordatorio",
            description=f"**{reminder['title']}**",
            color=0x3498db
        )
        embed.add_field(name="Descripción", value=reminder['description'], inline=False)
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
            
        embed.set_footer(text=f"ID: {reminder_id}")
        
        try:
            await user.send(embed=embed)
            logger.info(f"Recordatorio {reminder_id} enviado a {user_id}")
            
            await mark_reminder_as_sent(reminder_id)
        except Exception as e:
            logger.error(f"Error al enviar DM al usuario {user_id}: {str(e)}")
    except Exception as e:
        logger.error(f"Error al enviar recordatorio {reminder_id}: {str(e)}")

async def check_pending_reminders(bot):
    try:
        reminders = await get_pending_reminders()
        logger.info(f"Verificando recordatorios pendientes: {len(reminders)} encontrados")
        
        for reminder in reminders:
            await send_reminder(bot, reminder['_id'], reminder['user_id'])
    except Exception as e:
        logger.error(f"Error al verificar recordatorios pendientes: {str(e)}")

async def start_scheduler(bot):
    try:
        from .database import check_db_connection
        if not await check_db_connection():
            logger.error("No se pudo conectar a la base de datos MongoDB")
            return
        
        logger.info("Iniciando programador de recordatorios")
        
        await check_pending_reminders(bot)
        
        while True:
            await asyncio.sleep(60)
            await check_pending_reminders(bot)
    except Exception as e:
        logger.error(f"Error en start_scheduler: {str(e)}")

async def setup(bot):
    pass