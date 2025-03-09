import discord
from discord.ext import commands
from datetime import datetime
import asyncio
from database.get import get_server_data
from database.get import get_specific_field

def get_guild_data(guild_id: int):
    return get_server_data(guild_id)

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

async def create_commands_embed(interaction, guild_data):
    embed = discord.Embed(
        title=f"Datos {interaction.guild.name} (1/3)",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )

    default_cmds = guild_data.get("default_cdm", []) or []
    active_cmds = guild_data.get("act_cmd", []) or []
    deactive_cmds = guild_data.get("deact_cmd", []) or []
    
    embed.add_field(
        name="Comandos predeterminados",
        value=" | ".join(f"`{cmd}`" for cmd in default_cmds) if default_cmds else "Ninguno",
        inline=False
    )
    embed.add_field(
        name="Comandos activados",
        value=" | ".join(f"`{cmd}`" for cmd in active_cmds) if active_cmds else "Ninguno",
        inline=False
    )
    embed.add_field(
        name="Comandos desactivados",
        value=" | ".join(f"`{cmd}`" for cmd in deactive_cmds) if deactive_cmds else "Ninguno",
        inline=False
    )

    mute_role_id = guild_data.get("mute_role", 0)
    mute_role = interaction.guild.get_role(mute_role_id) if mute_role_id else None
    embed.add_field(
        name="Rol de mute",
        value=f"{mute_role.mention} `[ID: {mute_role.id}]`" if mute_role else "no establecido",
        inline=False
    )
    
    embed.set_footer(text=f"Solicitado por {interaction.user.name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
    return embed

async def create_permissions_embed(interaction, guild_data):
    embed = discord.Embed(
        title=f"Datos {interaction.guild.name} (2/3)",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    perm_titles = {
        "admin": "Administrador",
        "mg-ch": "Gestionar canales",
        "mg-rl": "Gestionar roles",
        "mg-srv": "Gestionar servidor",
        "kick": "Expulsar miembros",
        "ban": "Banear miembros",
        "mute": "Mutear miembros",
        "deafen": "Ensordecer miembros",
        "mg-msg": "Gestionar mensajes",
        "warn": "Advertir miembros",
        "unwarn": "Quitar advertencias"
    }

    for base_perm in perm_titles:
        roles_key = f"{base_perm}-roles"
        users_key = f"{base_perm}-users"
        if roles_key in guild_data["perms"] and users_key in guild_data["perms"]:
            perms_text = ""
            users = guild_data["perms"][users_key]
            user_text = "ninguno"
            if users != [0]:
                user_mentions = []
                for uid in users:
                    if uid != 0:
                        member = interaction.guild.get_member(uid)
                        if member:
                            user_mentions.append(f"{member.mention} `[ID: {member.id}]`")
                user_text = " | ".join(user_mentions) if user_mentions else "ninguno"
            
            roles = guild_data["perms"][roles_key]
            role_text = "ninguno"
            if roles != [0]:
                role_mentions = []
                for rid in roles:
                    if rid != 0:
                        role = interaction.guild.get_role(rid)
                        if role:
                            role_mentions.append(f"{role.mention} `[ID: {role.id}]`")
                role_text = " | ".join(role_mentions) if role_mentions else "ninguno"
            
            perms_text += f"• Usuarios: {user_text}\n• Roles: {role_text}"
            embed.add_field(name=perm_titles[base_perm], value=perms_text, inline=False)
    
    embed.set_footer(text=f"Solicitado por {interaction.user.name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
    return embed

async def create_logs_embed(interaction, guild_data):
    embed = discord.Embed(
        title=f"Datos {interaction.guild.name} (3/3)",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    log_groups = {
        "Moderación": ["ban", "kick", "mute", "unmute", "unban", "warn", "unwarn"],
        "Usuarios": ["enter", "leave"],
        "Mensajes": ["del_msg", "edited_msg"]
    }

    for group_name, log_types in log_groups.items():
        logs_text = ""
        for log_type in log_types:
            if log_type in guild_data["audit_logs"]:
                log_data = guild_data["audit_logs"][log_type]
                log_names = {
                    "ban": "Ban", "kick": "Kick", "mute": "Mute",
                    "unmute": "Unmute", "unban": "Unban",
                    "enter": "Entrada", "leave": "Salida",
                    "del_msg": "Mensajes eliminados",
                    "edited_msg": "Mensajes editados",
                    "warn": "Advertencia",
                    "unwarn": "Quitar advertencia"
                }
                
                logs_text += f"**{log_names.get(log_type, log_type)}:**\n"
                logs_text += f"• Estado: {'Activado' if log_data['activated'] else 'Desactivado'}\n"
                
                channel = interaction.guild.get_channel(log_data['log_channel'])
                channel_text = f"{channel.mention} `[ID: {channel.id}]`" if channel else "no establecido"
                logs_text += f"• Canal: {channel_text}\n"
                
                msg_key = f"{log_type}_messages"
                if msg_key in log_data:
                    logs_text += f"• Mensaje: `{log_data[msg_key]}`\n"
                
                if "ago" in log_data:
                    logs_text += f"• Máxima antigüedad: {log_data['ago']} días\n"
                
                logs_text += "\n"
        
        if logs_text:
            embed.add_field(name=f"Logs - {group_name}", value=logs_text, inline=False)
    
    embed.set_footer(text=f"Solicitado por {interaction.user.name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
    return embed

async def show_config_data(interaction):
    guild_data = get_guild_data(interaction.guild.id)
    if not guild_data:
        await interaction.response.send_message(
            "No se encontraron datos de configuración para este servidor. Ejecuta </config update:1348248454610161751> si eres administrador",
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
        current_page = 1
        embed = await create_commands_embed(interaction, guild_data)
        
        view = ConfigDataPagination(interaction.user.id, guild_data, interaction)
        
        await interaction.response.send_message(embed=embed, view=view)
                
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

class ConfigDataPagination(discord.ui.View):
    def __init__(self, author_id, guild_data, interaction):
        super().__init__(timeout=120)
        self.author_id = author_id
        self.guild_data = guild_data
        self.interaction = interaction
        self.current_page = 1
        self.max_pages = 3

        self.children[0].disabled = True
    
    async def interaction_check(self, interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Solo la persona que ejecutó el comando puede usar estos botones.",
                ephemeral=True
            )
            return False
        return True
    
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        
        message = await self.interaction.original_response()
        await message.edit(view=self)
    
    @discord.ui.button(label="◀ Anterior", style=discord.ButtonStyle.secondary)
    async def previous_button(self, interaction, button):
        if self.current_page > 1:
            self.current_page -= 1
            
            self.children[0].disabled = self.current_page == 1
            self.children[1].disabled = False
            
            if self.current_page == 1:
                embed = await create_commands_embed(interaction, self.guild_data)
            elif self.current_page == 2:
                embed = await create_permissions_embed(interaction, self.guild_data)
            
            await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Siguiente ▶", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction, button):
        if self.current_page < self.max_pages:
            self.current_page += 1
            
            self.children[0].disabled = False
            self.children[1].disabled = self.current_page == self.max_pages
            
            if self.current_page == 2:
                embed = await create_permissions_embed(interaction, self.guild_data)
            elif self.current_page == 3:
                embed = await create_logs_embed(interaction, self.guild_data)
            
            await interaction.response.edit_message(embed=embed, view=self)

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