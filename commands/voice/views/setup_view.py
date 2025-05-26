import discord
from discord import ui
from ..database import save_voice_config

class VoiceSetupView(ui.View):
    def __init__(self, bot, config=None):
        super().__init__(timeout=300)
        self.bot = bot
        self.config = config or {}
    
    @ui.select(
        cls=ui.ChannelSelect,
        channel_types=[discord.ChannelType.voice],
        placeholder="Selecciona el canal generador",
        custom_id="generator_select"
    )
    async def select_generator(self, interaction: discord.Interaction, select: ui.ChannelSelect):
        channel = select.values[0]
        self.config["generator_channel"] = channel.id
        
        embed = discord.Embed(
            title="Canal generador configurado",
            description=f"Has seleccionado {channel.mention} como canal generador.",
            color=discord.Color.green()
        )
        
        await self.update_config_display(interaction, embed)
    
    @ui.select(
        cls=ui.ChannelSelect,
        channel_types=[discord.ChannelType.category],
        placeholder="Selecciona la categoría (opcional)",
        custom_id="category_select"
    )
    async def select_category(self, interaction: discord.Interaction, select: ui.ChannelSelect):
        category = select.values[0]
        self.config["category_id"] = category.id
        
        embed = discord.Embed(
            title="Categoría configurada",
            description=f"Has seleccionado la categoría **{category.name}** para los canales personalizados.",
            color=discord.Color.green()
        )
        
        await self.update_config_display(interaction, embed)
    
    @ui.select(
        cls=ui.RoleSelect,
        placeholder="Selecciona roles de gestión",
        min_values=0,
        max_values=10,
        custom_id="roles_select"
    )
    async def select_roles(self, interaction: discord.Interaction, select: ui.RoleSelect):
        if not select.values:
            if "admin_roles" in self.config:
                del self.config["admin_roles"]
            embed = discord.Embed(
                title="Roles eliminados",
                description="Se han eliminado todos los roles de gestión.",
                color=discord.Color.orange()
            )
        else:
            role_ids = [role.id for role in select.values]
            self.config["admin_roles"] = role_ids
            
            roles_text = "\n".join([f"• {role.mention}" for role in select.values])
            embed = discord.Embed(
                title="Roles de gestión configurados",
                description=f"Has seleccionado los siguientes roles:\n{roles_text}",
                color=discord.Color.green()
            )
        
        await self.update_config_display(interaction, embed)
    
    @ui.button(label="Quitar roles específicos", style=discord.ButtonStyle.secondary, row=4)
    async def remove_specific_roles(self, interaction: discord.Interaction, button: ui.Button):
        admin_roles = self.config.get("admin_roles", [])
        if not admin_roles:
            await interaction.response.send_message(
                "❌ No hay roles de gestión configurados.",
                ephemeral=True
            )
            return
        
        from .admin_roles_view import AdminRoleRemoveView
        view = AdminRoleRemoveView(self.bot, self.config, self)
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="Quitar roles de gestión",
                description="Selecciona los roles que quieres quitar de la gestión.",
                color=discord.Color.blue()
            ),
            view=view
        )
    
    @ui.button(label="Guardar configuración", style=discord.ButtonStyle.success, row=4)
    async def save_config(self, interaction: discord.Interaction, button: ui.Button):
        if not self.config.get("generator_channel"):
            await interaction.response.send_message(
                "❌ Debes configurar al menos un canal generador.",
                ephemeral=True
            )
            return
        
        result = save_voice_config(interaction.guild.id, self.config)
        
        if result:
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Configuración guardada",
                    description="La configuración del sistema de canales de voz dinámicos ha sido guardada correctamente.",
                    color=discord.Color.green()
                ),
                view=None
            )
        else:
            await interaction.response.send_message(
                "❌ Ocurrió un error al guardar la configuración.",
                ephemeral=True
            )
    
    async def update_config_display(self, interaction, embed):
        await interaction.response.edit_message(embed=embed, view=self)