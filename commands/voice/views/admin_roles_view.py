import discord
from discord import ui

class AdminRoleRemoveView(ui.View):
    def __init__(self, bot, config, parent_view):
        super().__init__(timeout=300)
        self.bot = bot
        self.config = config
        self.parent_view = parent_view
        
        admin_roles = self.config.get("admin_roles", [])
        if admin_roles:
            options = []
            guild = bot.get_guild(self.config.get("guild_id"))
            if guild:
                for role_id in admin_roles:
                    role = guild.get_role(role_id)
                    if role:
                        options.append(
                            discord.SelectOption(
                                label=role.name[:25],
                                description=f"ID: {role.id}",
                                value=str(role.id)
                            )
                        )
            
            if options:
                remove_select = ui.Select(
                    placeholder="Selecciona roles para quitar",
                    options=options[:25],
                    min_values=1,
                    max_values=min(len(options), 25),
                    custom_id="remove_roles_select"
                )
                remove_select.callback = self.remove_roles_callback
                self.add_item(remove_select)
    
    async def remove_roles_callback(self, interaction: discord.Interaction):
        selected_role_ids = [int(role_id) for role_id in interaction.data["values"]]
        
        admin_roles = self.config.get("admin_roles", [])
        for role_id in selected_role_ids:
            if role_id in admin_roles:
                admin_roles.remove(role_id)
        
        self.config["admin_roles"] = admin_roles
        
        removed_roles = []
        for role_id in selected_role_ids:
            role = interaction.guild.get_role(role_id)
            if role:
                removed_roles.append(role.mention)
        
        roles_text = ", ".join(removed_roles)
        embed = discord.Embed(
            title="Roles eliminados",
            description=f"Se han eliminado los siguientes roles de gestión:\n{roles_text}",
            color=discord.Color.orange()
        )
        
        await interaction.response.edit_message(embed=embed, view=self.parent_view)
    
    @ui.button(label="Volver", style=discord.ButtonStyle.secondary)
    async def back_button(self, interaction: discord.Interaction, button: ui.Button):
        embed = discord.Embed(
            title="Configuración de Canales de Voz Dinámicos",
            description="Configura el sistema de canales de voz dinámicos usando los selectores superiores.",
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(embed=embed, view=self.parent_view)

async def setup_admin_roles_view(setup_view, interaction):
    pass

async def handle_remove_roles(setup_view, interaction):
    pass