import discord
from discord import app_commands
from discord.ext import commands
from .database import BirthdayDB
from .views import ConfigView, ConfirmDeleteView
from .utils import parse_date, format_date
import datetime

class Birthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = BirthdayDB()
    
    birthday_group = app_commands.Group(
        name="cumpleaños", 
        description="Gestiona los cumpleaños en el servidor"
    )
    
    @birthday_group.command(name="configurar", description="Configura las opciones de cumpleaños del servidor")
    async def config_birthday(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            from database.get import get_specific_field
            bot_admins = get_specific_field(interaction.guild.id, "perms/admin-users") or []
            bot_admin_roles = get_specific_field(interaction.guild.id, "perms/admin-roles") or []
            
            has_admin_role = False
            for role in interaction.user.roles:
                if role.id in bot_admin_roles:
                    has_admin_role = True
                    break
            
            if not (interaction.user.id in bot_admins or has_admin_role):
                await interaction.response.send_message(
                    "<:No:825734196256440340> No tienes permisos para configurar los cumpleaños. Necesitas ser administrador del servidor o tener el rol de administrador del bot.",
                    ephemeral=True
                )
                return
        
        config = await self.db.get_config(interaction.guild.id)
        view = ConfigView(self.bot, self.db, config)
        
        if config:
            for item in view.children:
                if item.label == "Eliminar configuración":
                    item.disabled = False
        
        embed = discord.Embed(
            title="Configuración de Cumpleaños",
            description="Configura cómo se manejarán los mensajes de cumpleaños en el servidor.",
            color=discord.Color.blue()
        )
        
        if config:
            channel = interaction.guild.get_channel(config.get("channel_id"))
            channel_text = f"{channel.mention}" if channel else "No configurado"
            
            embed.add_field(
                name="Canal de felicitaciones",
                value=channel_text,
                inline=False
            )
            
            embed.add_field(
                name="Mensaje de felicitación",
                value=config.get("message", "No configurado"),
                inline=False
            )
            
            embed.add_field(
                name="Zona horaria",
                value=config.get("timezone", "UTC+00:00"),
                inline=False
            )
        else:
            embed.add_field(
                name="Estado",
                value="No hay configuración establecida. Usa los botones para configurar.",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @birthday_group.command(name="establecer", description="Establece tu cumpleaños")
    @app_commands.describe(fecha="Fecha de cumpleaños (formato: DD/MM)")
    async def set_birthday(self, interaction: discord.Interaction, fecha: str):
        if not fecha:
            await interaction.response.send_message(
                "<:No:825734196256440340> Debes proporcionar una fecha en formato DD/MM.",
                ephemeral=True
            )
            return
        
        date = parse_date(fecha)
        if not date:
            await interaction.response.send_message(
                "<:No:825734196256440340> Formato de fecha incorrecto. Usa el formato DD/MM.",
                ephemeral=True
            )
            return
        
        user_data = {
            "user_id": interaction.user.id,
            "guild_id": interaction.guild.id,
            "day": date.day,
            "month": date.month
        }
        
        await self.db.set_birthday(user_data)
        
        await interaction.response.send_message(
            f"<:Si:825734135116070962> Tu cumpleaños ha sido establecido para el {format_date(date)}.",
            ephemeral=True
        )
    
    @birthday_group.command(name="ver", description="Ver cumpleaños")
    @app_commands.describe(usuario="Usuario para ver su cumpleaños")
    async def view_birthday(self, interaction: discord.Interaction, usuario: discord.User = None):
        if usuario:
            birthday = await self.db.get_birthday(usuario.id, interaction.guild.id)
            
            if birthday:
                date = datetime.datetime(2000, birthday["month"], birthday["day"])
                await interaction.response.send_message(
                    f"El cumpleaños de {usuario.mention} es el {format_date(date)}.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"{usuario.mention} no tiene un cumpleaños establecido en este servidor.",
                    ephemeral=True
                )
        else:
            birthday = await self.db.get_birthday(interaction.user.id, interaction.guild.id)
            
            if birthday:
                date = datetime.datetime(2000, birthday["month"], birthday["day"])
                await interaction.response.send_message(
                    f"Tu cumpleaños está establecido para el {format_date(date)}.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "No tienes un cumpleaños establecido en este servidor. Usa `/cumpleaños establecer fecha:DD/MM` para configurarlo.",
                    ephemeral=True
                )
    
    @birthday_group.command(name="eliminar", description="Elimina tu cumpleaños")
    async def delete_birthday(self, interaction: discord.Interaction):
        birthday = await self.db.get_birthday(interaction.user.id, interaction.guild.id)
        
        if not birthday:
            await interaction.response.send_message(
                "No tienes un cumpleaños establecido en este servidor.",
                ephemeral=True
            )
            return
        
        view = ConfirmDeleteView(self.db, interaction.user.id, interaction.guild.id)
        
        await interaction.response.send_message(
            "¿Estás seguro de que quieres eliminar tu cumpleaños de este servidor?",
            view=view,
            ephemeral=True
        )