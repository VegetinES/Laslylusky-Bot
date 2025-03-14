import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
from database.get import get_server_data
from .confighelp import show_config_help
from .configdata import show_config_data
from .configcmd import show_config_cmd
from .configupdate import show_config_update
from .configlogs import show_config_logs
from .configperms import show_config_perms, permission_autocomplete
from ..tickets.configtickets import show_tickets_channel, show_tickets_messages, show_tickets_perms, channel_autocomplete, color_autocomplete, show_tickets_help, show_tickets_modify

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.valid_params = ['help', 'logs', 'perms', 'cmd', 'data', 'update', 'tickets']

    def get_available_commands(self, guild_id):
        server_data = get_server_data(guild_id)
        if not server_data:
            return []
            
        active_cmds = server_data.get("act_cmd", []) or []
        deactive_cmds = server_data.get("deact_cmd", []) or []

        available_commands = list(set(active_cmds + deactive_cmds))
        return available_commands

    async def command_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        available_commands = self.get_available_commands(interaction.guild.id)
        return [
            app_commands.Choice(name=cmd, value=cmd)
            for cmd in available_commands if current.lower() in cmd.lower()
        ][:25]
    
    async def log_type_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        log_types = ["ban", "kick", "unban", "enter", "leave", "del_msg", "edited_msg", "warn", "unwarn"]
        return [
            app_commands.Choice(name=log_type, value=log_type)
            for log_type in log_types if current.lower() in log_type.lower()
        ]
    
    async def help_type_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        help_types = ["logs", "perms", "cmd", "update", "data"]
        return [
            app_commands.Choice(name=help_type, value=help_type)
            for help_type in help_types if current.lower() in help_type.lower()
        ]
    
    async def is_admin(self, interaction: discord.Interaction) -> bool:
        if interaction.user.guild_permissions.administrator:
            return True
        
        await interaction.response.send_message(
            "No tienes permisos para usar este comando. Se requiere ser Administrador del servidor.",
            ephemeral=True
        )
        return False
    
    def admin_check(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            return False
        return True

    @commands.command(name="config")
    @commands.check(admin_check)
    async def config_text_command(self, ctx):
        await ctx.send("Ejecuta `/config help` para saber como ejecutar los comandos de configuración")

    config_group = app_commands.Group(name="config", description="Configura el bot para este servidor")

    @config_group.command(name="help", description="Muestra la ayuda de configuración")
    @app_commands.describe(
        tipo="Tipo de ayuda a mostrar"
    )
    @app_commands.autocomplete(tipo=help_type_autocomplete)
    async def config_help(self, interaction: discord.Interaction, tipo: Optional[str] = None):
        if not await self.is_admin(interaction):
            return
        await show_config_help(interaction, tipo)

    @config_group.command(name="data", description="Muestra la configuración actual del servidor")
    async def config_data(self, interaction: discord.Interaction):
        if not await self.is_admin(interaction):
            return
        await show_config_data(interaction)

    @config_group.command(name="update", description="Restablece la configuración a valores predeterminados")
    async def config_update(self, interaction: discord.Interaction):
        if not await self.is_admin(interaction):
            return
        await show_config_update(interaction, self.bot)

    @config_group.command(name="cmd", description="Activa o desactiva comandos específicos")
    @app_commands.describe(
        comando="El comando a modificar",
        estado="Nuevo estado del comando"
    )
    @app_commands.autocomplete(comando=command_autocomplete)
    @app_commands.choices(estado=[
        app_commands.Choice(name="activado", value="activate"),
        app_commands.Choice(name="desactivado", value="deactivate")
    ])
    async def config_cmd(self, interaction: discord.Interaction, comando: str, estado: str):
        if not await self.is_admin(interaction):
            return
        await show_config_cmd(interaction, comando, estado)

    @config_group.command(name="logs", description="Configura los registros de auditoría")
    @app_commands.describe(
        log="Tipo de log a configurar",
        estado="Activar o desactivar este log",
        canal="Canal donde se enviarán los logs",
        tipo_mensaje="Formato del mensaje (embed o normal)"
    )
    @app_commands.autocomplete(log=log_type_autocomplete)
    @app_commands.choices(estado=[
        app_commands.Choice(name="activado", value="activado"),
        app_commands.Choice(name="desactivado", value="desactivado")
    ])
    @app_commands.choices(tipo_mensaje=[
        app_commands.Choice(name="embed", value="embed"),
        app_commands.Choice(name="normal", value="normal")
    ])
    async def config_logs(
        self, 
        interaction: discord.Interaction, 
        log: str, 
        estado: str, 
        canal: discord.TextChannel, 
        tipo_mensaje: str,
        mensaje: Optional[str] = None,
        título: Optional[str] = None,
        descripción: Optional[str] = None,
        footer: Optional[str] = None,
        límite: Optional[int] = None
    ):
        if not await self.is_admin(interaction):
            return
        await show_config_logs(
            interaction, 
            log, 
            estado, 
            canal, 
            tipo_mensaje, 
            mensaje=mensaje,
            título=título,
            descripción=descripción,
            footer=footer,
            límite=límite
        )

    @config_group.command(name="perms", description="Configura los permisos del bot")
    @app_commands.describe(
        permiso="El permiso a configurar",
        accion="Añadir o eliminar permisos",
        roles="Los roles a los que asignar/quitar el permiso (separa múltiples roles con espacios)",
        usuarios="Los usuarios a los que asignar/quitar el permiso (separa múltiples usuarios con espacios)"
    )
    @app_commands.autocomplete(permiso=permission_autocomplete)
    @app_commands.choices(accion=[
        app_commands.Choice(name="añadir", value="añadir"),
        app_commands.Choice(name="eliminar", value="eliminar")
    ])
    async def config_perms(
        self, 
        interaction: discord.Interaction, 
        permiso: str, 
        accion: str,
        roles: Optional[str] = None,
        usuarios: Optional[str] = None
    ):
        if not await self.is_admin(interaction):
            return
        await show_config_perms(interaction, permiso, accion, roles, usuarios)

    tickets_group = app_commands.Group(name="tickets", description="Configura el sistema de tickets", parent=config_group)
    
    @tickets_group.command(name="help", description="Muestra la ayuda para el sistema de tickets")
    async def tickets_help(self, interaction: discord.Interaction):
        if not await self.is_admin(interaction):
            return
        await show_tickets_help(interaction)

    @tickets_group.command(name="canal", description="Configura el canal para los tickets")
    @app_commands.describe(
        canal_abrir_ticket="Canal donde estará el mensaje para abrir tickets",
        canal_logs="Canal donde se enviarán los logs de tickets",
        nombre_ticket="Nombre base para los tickets (máximo 15 caracteres, usa {id} para numerar automáticamente)"
    )
    async def tickets_channel(
        self,
        interaction: discord.Interaction,
        canal_abrir_ticket: discord.TextChannel,
        canal_logs: discord.TextChannel,
        nombre_ticket: str
    ):
        if not await self.is_admin(interaction):
            return
        await show_tickets_channel(interaction, canal_abrir_ticket, canal_logs, nombre_ticket)

    @tickets_group.command(name="mensajes", description="Configura los mensajes de tickets")
    @app_commands.describe(
        canal="Canal de tickets configurado",
        tipo="Tipo de mensaje a configurar",
        título="Título del mensaje",
        descripción="Descripción del mensaje",
        imagen="URL de la imagen para el embed (opcional)",
        footer="Texto del footer para el embed (opcional)",
        color="Color del embed (opcional)",
        mensaje="Mensaje adicional (solo para ticket abierto). Puedes usar {user}, {usertag} y {\\n} (opcional)"
    )
    @app_commands.autocomplete(canal=channel_autocomplete, color=color_autocomplete)
    @app_commands.choices(tipo=[
        app_commands.Choice(name="ticket abierto", value="ticket-abierto"),
        app_commands.Choice(name="abrir ticket", value="abrir-ticket")
    ])
    async def tickets_messages(
        self,
        interaction: discord.Interaction,
        canal: str,
        tipo: str,
        título: str,
        descripción: str,
        imagen: Optional[str] = None,
        footer: Optional[str] = None,
        color: Optional[str] = None,
        mensaje: Optional[str] = None
    ):
        if not await self.is_admin(interaction):
            return
        await show_tickets_messages(
            interaction, 
            self.bot,
            canal, 
            tipo, 
            título, 
            descripción, 
            imagen, 
            footer, 
            color,
            mensaje
        )

    @tickets_group.command(name="permisos", description="Configura los permisos de tickets")
    @app_commands.describe(
        canal="Canal de tickets configurado",
        permiso="Tipo de permiso a configurar",
        accion="Añadir o eliminar permisos",
        roles="Roles a asignar/quitar (separados por espacios)",
        usuarios="Usuarios a asignar/quitar (separados por espacios)"
    )
    @app_commands.autocomplete(canal=channel_autocomplete)
    @app_commands.choices(permiso=[
        app_commands.Choice(name="Gestionar tickets", value="manage"),
        app_commands.Choice(name="Ver tickets", value="see"),
        app_commands.Choice(name="Cerrar tickets", value="close"),
        app_commands.Choice(name="Añadir/eliminar usuarios", value="add-del-usr")
    ])
    @app_commands.choices(accion=[
        app_commands.Choice(name="añadir", value="añadir"),
        app_commands.Choice(name="eliminar", value="eliminar")
    ])
    async def tickets_perms(
        self,
        interaction: discord.Interaction,
        canal: str,
        permiso: str,
        accion: str,
        roles: Optional[str] = None,
        usuarios: Optional[str] = None
    ):
        if not await self.is_admin(interaction):
            return
        await show_tickets_perms(interaction, canal, permiso, accion, roles, usuarios)
        
    @tickets_group.command(name="modificar", description="Modifica o elimina la configuración de tickets")
    @app_commands.describe(
        canal="Canal de tickets configurado",
        accion="Acción a realizar"
    )
    @app_commands.autocomplete(canal=channel_autocomplete)
    @app_commands.choices(accion=[
        app_commands.Choice(name="restablecer", value="restablecer"),
        app_commands.Choice(name="eliminar", value="eliminar")
    ])
    async def tickets_modify(
        self,
        interaction: discord.Interaction,
        canal: str,
        accion: str
    ):
        if not await self.is_admin(interaction):
            return
        await show_tickets_modify(interaction, canal, accion)

async def setup(bot):
    await bot.add_cog(Config(bot))