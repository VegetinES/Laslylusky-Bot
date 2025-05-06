import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
from database.get import get_specific_field

class ID(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def emoji_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if not interaction.guild:
            return []
            
        emojis = interaction.guild.emojis
        if not emojis:
            return []
            
        matches = []
        for emoji in emojis:
            if current.lower() in emoji.name.lower():
                matches.append(app_commands.Choice(name=f"{emoji.name} {str(emoji)}", value=str(emoji.id)))
        
        return matches[:25]

    async def user_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if not interaction.guild:
            return []
            
        members = [member async for member in interaction.guild.fetch_members(limit=1000)]
        if not members:
            return []
            
        matches = []
        for member in members:
            if current.lower() in member.name.lower() or current.lower() in member.display_name.lower():
                matches.append(app_commands.Choice(name=f"{member.name} ({member.display_name})", value=str(member.id)))
        
        return matches[:25]

    async def channel_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if not interaction.guild:
            return []
            
        channels = interaction.guild.channels
        if not channels:
            return []
            
        matches = []
        for channel in channels:
            if hasattr(channel, 'name') and current.lower() in channel.name.lower():
                channel_type = getattr(channel, 'type', None)
                type_name = channel_type.name if channel_type else "unknown"
                matches.append(app_commands.Choice(name=f"{channel.name} ({type_name})", value=str(channel.id)))
        
        return matches[:25]

    async def role_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if not interaction.guild:
            return []
            
        roles = interaction.guild.roles
        if not roles:
            return []
            
        matches = []
        for role in roles:
            if role.id != interaction.guild.default_role.id and current.lower() in role.name.lower():
                matches.append(app_commands.Choice(name=role.name, value=str(role.id)))
        
        return matches[:25]

    @app_commands.command(name="id", description="Muestra información sobre IDs")
    @app_commands.describe(
        opcion="Tipo de elemento del que quieres ver la ID",
        emoji="Selecciona un emoji del servidor",
        usuario="Selecciona un usuario del servidor",
        canal="Selecciona un canal del servidor",
        rol="Selecciona un rol del servidor"
    )
    @app_commands.choices(opcion=[
        app_commands.Choice(name="Emoji", value="emoji"),
        app_commands.Choice(name="Usuario", value="usuario"),
        app_commands.Choice(name="Canal", value="canal"),
        app_commands.Choice(name="Rol", value="rol")
    ])
    @app_commands.autocomplete(
        emoji=emoji_autocomplete,
        usuario=user_autocomplete,
        canal=channel_autocomplete,
        rol=role_autocomplete
    )
    async def id_command(self, interaction: discord.Interaction, opcion: str, 
                       emoji: Optional[str] = None, 
                       usuario: Optional[str] = None,
                       canal: Optional[str] = None,
                       rol: Optional[str] = None):
        
        if isinstance(interaction.channel, discord.DMChannel):
            return
            
        act_commands = get_specific_field(interaction.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return
            
        if "id" not in act_commands:
            await interaction.response.send_message("El comando no está activado en este servidor.")
            return
        
        try:
            embed = discord.Embed(color=0x3498db)
            
            if opcion == "emoji":
                if not emoji:
                    await interaction.response.send_message("Debes seleccionar un emoji.", ephemeral=True)
                    return
                    
                emoji_obj = None
                try:
                    emoji_obj = discord.utils.get(interaction.guild.emojis, id=int(emoji))
                except (ValueError, TypeError):
                    pass
                    
                if not emoji_obj:
                    await interaction.response.send_message("Emoji no encontrado. Por favor, selecciona uno de la lista.", ephemeral=True)
                    return
                    
                embed.title = "Información del Emoji"
                embed.description = f"Emoji: {str(emoji_obj)}\nID: `{emoji_obj.id}`\nFormato: `<:{emoji_obj.name}:{emoji_obj.id}>`"
                embed.set_thumbnail(url=emoji_obj.url)
                
            elif opcion == "usuario":
                if not usuario:
                    await interaction.response.send_message("Debes seleccionar un usuario.", ephemeral=True)
                    return
                    
                user_obj = None
                try:
                    user_obj = interaction.guild.get_member(int(usuario))
                    if not user_obj:
                        user_obj = await interaction.guild.fetch_member(int(usuario))
                except (ValueError, TypeError, discord.errors.NotFound):
                    pass
                    
                if not user_obj:
                    await interaction.response.send_message("Usuario no encontrado. Por favor, selecciona uno de la lista.", ephemeral=True)
                    return
                    
                embed.title = "Información del Usuario"
                embed.description = f"Usuario: {user_obj.mention}\nID: `{user_obj.id}`\nFormato: `<@{user_obj.id}>`"
                embed.set_thumbnail(url=user_obj.display_avatar.url)
                
            elif opcion == "canal":
                if not canal:
                    await interaction.response.send_message("Debes seleccionar un canal.", ephemeral=True)
                    return
                    
                channel_obj = None
                try:
                    channel_obj = interaction.guild.get_channel(int(canal))
                    if not channel_obj:
                        channel_obj = await interaction.guild.fetch_channel(int(canal))
                except (ValueError, TypeError, discord.errors.NotFound):
                    pass
                    
                if not channel_obj:
                    await interaction.response.send_message("Canal no encontrado. Por favor, selecciona uno de la lista.", ephemeral=True)
                    return
                    
                embed.title = "Información del Canal"
                embed.description = f"Canal: {channel_obj.mention}\nID: `{channel_obj.id}`\nFormato: `<#{channel_obj.id}>`"
                
            elif opcion == "rol":
                if not rol:
                    await interaction.response.send_message("Debes seleccionar un rol.", ephemeral=True)
                    return
                    
                role_obj = None
                try:
                    role_obj = interaction.guild.get_role(int(rol))
                except (ValueError, TypeError):
                    pass
                    
                if not role_obj:
                    await interaction.response.send_message("Rol no encontrado. Por favor, selecciona uno de la lista.", ephemeral=True)
                    return
                    
                embed.title = "Información del Rol"
                embed.description = f"Rol: {role_obj.mention}\nID: `{role_obj.id}`\nFormato: `<@&{role_obj.id}>`"
                embed.color = role_obj.color
                
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            error_msg = f"Ocurrió un error: {str(e)}"
            try:
                await interaction.response.send_message(error_msg, ephemeral=True)
            except:
                await interaction.followup.send(error_msg, ephemeral=True)

async def setup(bot):
    await bot.add_cog(ID(bot))