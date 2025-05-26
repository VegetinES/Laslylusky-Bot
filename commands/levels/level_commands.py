import discord
from discord import app_commands
from discord.ext import commands
from .level_manager import LevelManager
from .helpers import has_level_admin_perms, create_level_embed
from .config_views import ConfigMainView
from .level_views import LeaderboardView
from .manage_views import ManageUserView

class LevelCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.level_manager = LevelManager(bot)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        
        try:
            await self.level_manager.process_message(message)
        except Exception as e:
            print(f"Error procesando mensaje para XP: {e}")
    
    nivel_group = app_commands.Group(name="nivel", description="Comandos relacionados con el sistema de niveles")
    
    @nivel_group.command(name="configurar", description="Configurar el sistema de niveles")
    async def level_config(self, interaction: discord.Interaction):
        if not await has_level_admin_perms(interaction):
            await interaction.response.send_message("No tienes permisos para configurar el sistema de niveles.", ephemeral=True)
            return
        
        view = ConfigMainView(self.bot)
        await interaction.response.send_message("Configuración del sistema de niveles:", ephemeral=True, view=view)
    
    @nivel_group.command(name="ver", description="Ver tu nivel o el de otro usuario")
    @app_commands.describe(usuario="Usuario del que quieres ver el nivel")
    async def level_view(self, interaction: discord.Interaction, usuario: discord.User = None):
        if not usuario:
            usuario = interaction.user
        
        guild_id = interaction.guild.id
        user_id = usuario.id
        
        user_data = self.level_manager.get_user_level(guild_id, user_id)
        
        if user_data["xp"] == 0:
            if usuario == interaction.user:
                await interaction.response.send_message("No tienes ningún nivel todavía. Sigue enviando mensajes para ganar experiencia.", ephemeral=True)
            else:
                await interaction.response.send_message(f"{usuario.name} no tiene ningún nivel todavía.", ephemeral=True)
            return
        
        rank = self.level_manager.get_user_rank(guild_id, user_id)
        total_users = self.level_manager.count_ranked_users(guild_id)
        
        embed = create_level_embed(usuario, user_data, rank, total_users)
        
        await interaction.response.send_message(embed=embed)
    
    @nivel_group.command(name="top", description="Ver el ranking de niveles del servidor")
    async def level_top(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        
        total_users = self.level_manager.count_ranked_users(guild_id)
        if total_users == 0:
            await interaction.response.send_message("No hay usuarios con niveles en este servidor.", ephemeral=True)
            return
        
        view = LeaderboardView(self.bot, guild_id)
        
        users_data = self.level_manager.get_top_users(guild_id, 0, 10)
        total_pages = (total_users + 9) // 10
        
        embed = discord.Embed(
            title=f"Top Niveles de {interaction.guild.name}",
            description=f"Página 1/{total_pages}",
            color=discord.Color.gold()
        )
        
        for i, user_data in enumerate(users_data):
            user = interaction.guild.get_member(user_data["user_id"])
            if not user:
                continue
                
            medal = ""
            if i == 0:
                medal = "🥇"
            elif i == 1:
                medal = "🥈"
            elif i == 2:
                medal = "🥉"
            
            embed.add_field(
                name=f"{medal} #{i+1} {user.display_name}",
                value=f"Nivel {user_data['level']} | {user_data['xp']:,} XP | {user_data['messages']:,} mensajes",
                inline=False
            )
        
        embed.set_footer(text="Usa los botones para navegar por el ranking")
        
        await interaction.response.send_message(embed=embed, view=view)
    
    @nivel_group.command(name="gestionar", description="Gestionar el nivel de un usuario")
    @app_commands.describe(usuario="Usuario a gestionar")
    async def level_manage(self, interaction: discord.Interaction, usuario: discord.User):
        if not await has_level_admin_perms(interaction):
            await interaction.response.send_message("No tienes permisos para gestionar niveles.", ephemeral=True)
            return
        
        guild_id = interaction.guild.id
        user_id = usuario.id
        
        user_data = self.level_manager.get_user_level(guild_id, user_id)
        
        embed = discord.Embed(
            title=f"Gestionar Nivel de {usuario.name}",
            description=f"Nivel actual: {user_data['level']}\nExperiencia: {user_data['xp']:,} XP\nMensajes: {user_data['messages']:,}",
            color=discord.Color.blue()
        )
        
        view = ManageUserView(self.bot, user_id)
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)