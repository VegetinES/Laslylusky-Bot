import discord
from discord.ext import commands
from datetime import datetime
import asyncio
from database.get import get_server_data
from database.get import get_specific_field

async def check_admin_perms(interaction, guild_data):
    try:
        if interaction.user.guild_permissions.administrator:
            return True
        
        if interaction.user.id in guild_data["perms"]["admin-users"]:
            return True
        
        user_roles = [role.id for role in interaction.user.roles]
        if any(role_id in user_roles for role_id in guild_data["perms"]["admin-roles"] if role_id != 0):
            return True
        
        return False
    except Exception as e:
        print(f"Error al verificar permisos: {e}")
        return False

async def show_config_data(interaction):
    guild_data = get_server_data(interaction.guild.id)
    if not guild_data:
        await interaction.response.send_message(
            "No se encontraron datos de configuración para este servidor. Ejecuta </config update:1348545246988079118> si eres administrador",
            ephemeral=True
        )
        return
    
    if not await check_admin_perms(interaction, guild_data):
        await interaction.response.send_message(
            "No tienes permisos para usar este comando. Se requieren permisos de administrador.",
            ephemeral=True
        )
        return

    try:
        view = ConfigDataMainView(interaction.user.id, guild_data, interaction)
        await interaction.response.send_message(
            "Selecciona qué información quieres ver:",
            view=view
        )
                
    except Exception as e:
        print(f"Error en show_config_data: {str(e)}")
        if not interaction.response.is_done():
            await interaction.response.send_message(
                f"Ocurrió un error al mostrar los datos: {str(e)}",
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                f"Ocurrió un error al mostrar los datos: {str(e)}",
                ephemeral=True
            )

class ConfigDataMainView(discord.ui.View):
    def __init__(self, author_id, guild_data, interaction):
        super().__init__(timeout=180)
        self.author_id = author_id
        self.guild_data = guild_data
        self.interaction = interaction

        options = [
            discord.SelectOption(label="Comandos activados/desactivados", value="commands", 
                                description="Ver comandos activos, desactivados y por defecto", 
                                emoji="📝"),
            discord.SelectOption(label="Permisos", value="permissions", 
                                description="Ver configuración de permisos", 
                                emoji="🔒"),
            discord.SelectOption(label="Logs", value="logs", 
                                description="Ver configuración de logs", 
                                emoji="📋"),
            discord.SelectOption(label="Tickets", value="tickets", 
                                description="Ver configuración de tickets", 
                                emoji="🎫")
        ]
        
        self.category_select = discord.ui.Select(
            placeholder="Selecciona una categoría",
            options=options
        )
        self.category_select.callback = self.category_select_callback
        self.add_item(self.category_select)

        self.cancel_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Cancelar",
            custom_id="cancel_main"
        )
        self.cancel_button.callback = self.cancel_callback
        self.add_item(self.cancel_button)
    
    async def interaction_check(self, interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Solo la persona que ejecutó el comando puede usar estos controles.",
                ephemeral=True
            )
            return False
        return True
    
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        
        try:
            message = await self.interaction.original_response()
            await message.edit(view=self)
        except:
            pass
    
    async def cancel_callback(self, interaction):
        for child in self.children:
            child.disabled = True
        
        await interaction.response.edit_message(
            content="Visualización de datos cancelada.",
            view=self,
            embed=None
        )
        self.stop()
    
    async def category_select_callback(self, interaction):
        from .configdata_commands import show_commands_data
        from .configdata_permissions import show_permissions_data
        from .configdata_logs import show_logs_data
        from .configdata_tickets import show_tickets_data
        
        selected_value = self.category_select.values[0]
        
        if selected_value == "commands":
            await show_commands_data(interaction, self.guild_data, self.author_id)
        elif selected_value == "permissions":
            await show_permissions_data(interaction, self.guild_data, self.author_id)
        elif selected_value == "logs":
            await show_logs_data(interaction, self.guild_data, self.author_id)
        elif selected_value == "tickets":
            await show_tickets_data(interaction, self.guild_data, self.author_id)

async def check_command(ctx, comando):
    act_commands = get_specific_field(ctx.guild.id, "act_cmd")
    
    if act_commands is None:
        embed = discord.Embed(
            title="<:No:825734196256440340> Error de Configuración",
            description="No hay datos configurados para este servidor. Usa el comando `</config update:1348248454610161751>` si eres administrador para configurar el bot funcione en el servidor",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return False
        
    if comando not in act_commands:
        await ctx.reply("El comando no está activado en este servidor.")
        return False
        
    return True