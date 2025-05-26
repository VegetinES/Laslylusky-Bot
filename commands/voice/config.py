import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from .database import get_voice_config, save_voice_config
from .views.setup_view import VoiceSetupView

class VoiceConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="voicesetup", description="Configura el sistema de canales de voz dinámicos")
    @app_commands.checks.has_permissions(administrator=True)
    async def voice_setup(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            member_roles = [role.id for role in interaction.user.roles]
            config = get_voice_config(interaction.guild.id)
            admin_roles = config.get("admin_roles", []) if config else []
            
            if not any(role_id in admin_roles for role_id in member_roles):
                await interaction.response.send_message(
                    "❌ No tienes permisos para configurar el sistema de canales de voz.",
                    ephemeral=True
                )
                return
        
        guild_id = interaction.guild.id
        config = get_voice_config(guild_id)
        
        if not config:
            config = {"guild_id": guild_id}
        else:
            config["guild_id"] = guild_id
        
        view = VoiceSetupView(self.bot, config)
        
        embed = discord.Embed(
            title="Configuración de Canales de Voz Dinámicos",
            description="Usa los selectores de abajo para configurar el sistema:",
            color=discord.Color.blue()
        )
        
        current_config = []
        
        if config and config.get("generator_channel"):
            channel = interaction.guild.get_channel(config["generator_channel"])
            current_config.append(f"🎤 **Canal generador:** {channel.mention if channel else 'Desconocido'}")
        else:
            current_config.append("🎤 **Canal generador:** ❌ No configurado")
        
        if config and config.get("category_id"):
            category = interaction.guild.get_channel(config["category_id"])
            current_config.append(f"📁 **Categoría:** {category.name if category else 'Desconocida'}")
        else:
            current_config.append("📁 **Categoría:** ❌ No configurada")
        
        if config and config.get("admin_roles"):
            roles_text = []
            for role_id in config["admin_roles"]:
                role = interaction.guild.get_role(role_id)
                if role:
                    roles_text.append(role.mention)
            
            if roles_text:
                current_config.append(f"👥 **Roles de gestión:** {', '.join(roles_text)}")
            else:
                current_config.append("👥 **Roles de gestión:** ❌ No configurados")
        else:
            current_config.append("👥 **Roles de gestión:** ❌ No configurados")
        
        embed.add_field(
            name="Configuración actual",
            value="\n".join(current_config),
            inline=False
        )
        
        embed.add_field(
            name="Instrucciones",
            value=(
                "1️⃣ Usa el primer selector para elegir el **canal generador**\n"
                "2️⃣ Usa el segundo selector para elegir la **categoría** (opcional)\n"
                "3️⃣ Usa el tercer selector para añadir **roles de gestión**\n"
                "4️⃣ Usa el botón **'Quitar roles específicos'** si necesitas quitar algunos\n"
                "5️⃣ Presiona **'Guardar configuración'** cuando termines"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @voice_setup.error
    async def voice_setup_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(
                "❌ No tienes permisos de administrador para usar este comando.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"❌ Ocurrió un error al ejecutar el comando: {str(error)}",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(VoiceConfig(bot))