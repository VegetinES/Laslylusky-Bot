import discord
import datetime
from .level_manager import LevelManager
from .helpers import parse_time_string
from .constants import DEFAULT_ANNOUNCEMENT_MESSAGE, MULTIPLIER_OPTIONS

class ConfigMainView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
        self.level_manager = LevelManager(bot)
    
    @discord.ui.button(label="Activar/Desactivar", style=discord.ButtonStyle.primary, row=0)
    async def toggle_levels(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild.id
        config = self.level_manager.get_guild_config(guild_id)
        
        new_state = not config["enabled"]
        self.level_manager.update_guild_config(guild_id, {"enabled": new_state})
        
        await interaction.response.send_message(
            f"Sistema de niveles {'activado' if new_state else 'desactivado'} correctamente.",
            ephemeral=True
        )
    
    @discord.ui.button(label="Multiplicador", style=discord.ButtonStyle.primary, row=0)
    async def multiplier_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        multiplier_view = MultiplierView(self.bot)
        await multiplier_view.show_menu(interaction)
    
    @discord.ui.button(label="Roles por Nivel", style=discord.ButtonStyle.primary, row=1)
    async def reward_roles(self, interaction: discord.Interaction, button: discord.ui.Button):
        reward_view = RewardRolesView(self.bot)
        await reward_view.show_menu(interaction)
    
    @discord.ui.button(label="Exclusiones", style=discord.ButtonStyle.primary, row=1)
    async def exclusions(self, interaction: discord.Interaction, button: discord.ui.Button):
        exclusion_view = ExclusionView(self.bot)
        await exclusion_view.show_menu(interaction)
    
    @discord.ui.button(label="Anuncios", style=discord.ButtonStyle.primary, row=2)
    async def announcement_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        announcement_view = AnnouncementView(self.bot)
        await announcement_view.show_menu(interaction)

class MultiplierView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
        self.level_manager = LevelManager(bot)
        self._add_multiplier_buttons()
    
    def _add_multiplier_buttons(self):
        buttons_to_remove = []
        for item in self.children:
            if isinstance(item, discord.ui.Button) and item.custom_id and item.custom_id.startswith("multiplier_"):
                buttons_to_remove.append(item)
        
        for button in buttons_to_remove:
            self.remove_item(button)
        
        row1 = 0
        row2 = 1
        row3 = 2
        
        for option in MULTIPLIER_OPTIONS:
            value = option["value"]
            label = option["label"]
            style = option["style"]
            
            row = row2
            if value < 1.0:
                row = row1
            elif value > 1.5:
                row = row3
            
            button = discord.ui.Button(
                style=style,
                label=label,
                custom_id=f"multiplier_{value}",
                row=row
            )
            
            async def callback(interaction, mult_value=value):
                await self.set_multiplier(interaction, mult_value)
            
            button.callback = callback
            self.add_item(button)
    
    async def show_menu(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        config = self.level_manager.get_guild_config(guild_id)
        
        multiplier = config["multiplier"]
        end_time = config.get("multiplier_end_time")
        end_time_str = ""
        
        if end_time:
            try:
                end_time_dt = datetime.datetime.fromisoformat(end_time)
                now = datetime.datetime.utcnow()
                
                if end_time_dt > now:
                    time_left = end_time_dt - now
                    hours, remainder = divmod(time_left.seconds, 3600)
                    minutes, _ = divmod(remainder, 60)
                    end_time_str = f"Tiempo restante: {hours}h {minutes}m"
                else:
                    self.level_manager.update_guild_config(guild_id, {
                        "multiplier": 1.0,
                        "multiplier_end_time": None
                    })
                    multiplier = 1.0
                    end_time_str = "Expirado"
            except:
                end_time_str = "Formato inválido"
        
        embed = discord.Embed(
            title="Configuración de Multiplicador",
            description=f"Multiplica la experiencia ganada por un período de tiempo.\nMultiplicador actual: x{multiplier}",
            color=discord.Color.blue()
        )
        
        if end_time_str:
            embed.add_field(name="Estado", value=end_time_str, inline=False)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Establecer Duración", style=discord.ButtonStyle.primary, row=3)
    async def set_duration(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MultiplierDurationModal(self))
    
    @discord.ui.button(label="Volver", style=discord.ButtonStyle.secondary, row=4)
    async def go_back(self, interaction: discord.Interaction, button: discord.ui.Button):
        main_view = ConfigMainView(self.bot)
        await interaction.response.edit_message(
            content="Configuración del sistema de niveles:",
            embed=None,
            view=main_view
        )
    
    async def set_multiplier(self, interaction: discord.Interaction, multiplier):
        guild_id = interaction.guild.id
        self.level_manager.update_guild_config(guild_id, {"multiplier": multiplier})
        await self.show_menu(interaction)

class MultiplierDurationModal(discord.ui.Modal, title="Establecer Duración del Multiplicador"):
    def __init__(self, view):
        super().__init__()
        self.view = view
        
        self.duration = discord.ui.TextInput(
            label="Duración",
            placeholder="Ejemplo: 2h, 30m, 1d, 600s",
            required=True,
            max_length=10
        )
        
        self.add_item(self.duration)
    
    async def on_submit(self, interaction: discord.Interaction):
        seconds = parse_time_string(self.duration.value)
        
        if seconds is None:
            await interaction.response.send_message(
                "Formato de tiempo inválido. Usa un número seguido de s, m, h o d. Ejemplo: 2h, 30m, 1d",
                ephemeral=True
            )
            return
        
        end_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds)
        
        guild_id = interaction.guild.id
        self.view.level_manager.update_guild_config(guild_id, {"multiplier_end_time": end_time.isoformat()})
        
        await self.view.show_menu(interaction)

class RewardRolesView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
        self.level_manager = LevelManager(bot)
    
    async def show_menu(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        config = self.level_manager.get_guild_config(guild_id)
        reward_roles = config.get("reward_roles", {})
        
        embed = discord.Embed(
            title="Configuración de Roles por Nivel",
            description="Asigna roles como recompensa al alcanzar ciertos niveles.",
            color=discord.Color.blue()
        )
        
        if reward_roles:
            roles_text = ""
            for level, role_id in sorted(reward_roles.items(), key=lambda x: int(x[0])):
                role = interaction.guild.get_role(role_id)
                role_name = role.name if role else "Rol no encontrado"
                roles_text += f"Nivel {level}: {role_name}\n"
            
            embed.add_field(name="Roles Configurados", value=roles_text, inline=False)
        else:
            embed.add_field(name="Roles Configurados", value="No hay roles configurados", inline=False)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Añadir Rol", style=discord.ButtonStyle.success, row=0)
    async def add_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = AddRoleSelectView(self.bot, self)
        await interaction.response.edit_message(
            content="Selecciona un rol para añadir:",
            embed=None,
            view=view
        )
    
    @discord.ui.button(label="Eliminar Rol", style=discord.ButtonStyle.danger, row=0)
    async def remove_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild.id
        config = self.level_manager.get_guild_config(guild_id)
        reward_roles = config.get("reward_roles", {})
        
        if not reward_roles:
            await interaction.response.send_message("No hay roles configurados para eliminar.", ephemeral=True)
            return
        
        view = RemoveRoleView(self.bot, self)
        await view.show_menu(interaction)
    
    @discord.ui.button(label="Volver", style=discord.ButtonStyle.secondary, row=1)
    async def go_back(self, interaction: discord.Interaction, button: discord.ui.Button):
        main_view = ConfigMainView(self.bot)
        await interaction.response.edit_message(
            content="Configuración del sistema de niveles:",
            embed=None,
            view=main_view
        )

class AddRoleSelectView(discord.ui.View):
    def __init__(self, bot, parent_view):
        super().__init__(timeout=300)
        self.bot = bot
        self.parent_view = parent_view
        self.level_manager = LevelManager(bot)
    
    @discord.ui.select(cls=discord.ui.RoleSelect, placeholder="Selecciona un rol")
    async def role_select(self, interaction: discord.Interaction, select: discord.ui.RoleSelect):
        selected_role = select.values[0]
        
        guild_id = interaction.guild.id
        config = self.level_manager.get_guild_config(guild_id)
        reward_roles = config.get("reward_roles", {})
        
        if str(selected_role.id) in [str(role_id) for role_id in reward_roles.values()]:
            await interaction.response.send_message("Este rol ya está configurado.", ephemeral=True)
            return
        
        await interaction.response.send_modal(SetRoleLevelModal(self, selected_role))
    
    @discord.ui.button(label="Volver", style=discord.ButtonStyle.secondary)
    async def go_back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.parent_view.show_menu(interaction)

class SetRoleLevelModal(discord.ui.Modal, title="Establecer Nivel del Rol"):
    def __init__(self, view, role):
        super().__init__()
        self.view = view
        self.role = role
        
        self.level = discord.ui.TextInput(
            label="Nivel Requerido",
            placeholder="Nivel requerido para obtener este rol",
            required=True,
            max_length=5
        )
        
        self.add_item(self.level)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            level = int(self.level.value)
            
            if level < 1:
                await interaction.response.send_message("El nivel debe ser mayor que 0.", ephemeral=True)
                return
            
            guild_id = interaction.guild.id
            config = self.view.level_manager.get_guild_config(guild_id)
            reward_roles = config.get("reward_roles", {})
            
            reward_roles[str(level)] = self.role.id
            
            self.view.level_manager.update_guild_config(guild_id, {"reward_roles": reward_roles})
            
            await self.view.parent_view.show_menu(interaction)
        except ValueError:
            await interaction.response.send_message("Por favor, introduce un número válido.", ephemeral=True)

class RemoveRoleView(discord.ui.View):
    def __init__(self, bot, parent_view):
        super().__init__(timeout=300)
        self.bot = bot
        self.parent_view = parent_view
        self.level_manager = LevelManager(bot)
    
    async def show_menu(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        config = self.level_manager.get_guild_config(guild_id)
        reward_roles = config.get("reward_roles", {})
        
        options = []
        for level, role_id in sorted(reward_roles.items(), key=lambda x: int(x[0])):
            role = interaction.guild.get_role(role_id)
            role_name = role.name if role else "Rol no encontrado"
            options.append(
                discord.SelectOption(
                    label=f"Nivel {level}",
                    description=f"{role_name}",
                    value=level
                )
            )
        
        select = RoleRemoveSelect(options)
        self.add_item(select)
        
        await interaction.response.edit_message(
            content="Selecciona el rol a eliminar:",
            embed=None,
            view=self
        )
    
    @discord.ui.button(label="Volver", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.parent_view.show_menu(interaction)

class RoleRemoveSelect(discord.ui.Select):
    def __init__(self, options):
        super().__init__(
            placeholder="Selecciona un nivel",
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        level = self.values[0]
        view = self.view
        
        guild_id = interaction.guild.id
        config = view.level_manager.get_guild_config(guild_id)
        reward_roles = config.get("reward_roles", {})
        
        if level in reward_roles:
            del reward_roles[level]
            view.level_manager.update_guild_config(guild_id, {"reward_roles": reward_roles})
        
        await view.parent_view.show_menu(interaction)

class ExclusionView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
        self.level_manager = LevelManager(bot)
    
    async def show_menu(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        config = self.level_manager.get_guild_config(guild_id)
        
        excluded_roles = config.get("excluded_roles", [])
        excluded_channels = config.get("excluded_channels", [])
        
        embed = discord.Embed(
            title="Configuración de Exclusiones",
            description="Roles y canales excluidos del sistema de niveles.",
            color=discord.Color.blue()
        )
        
        roles_text = ""
        for role_id in excluded_roles:
            role = interaction.guild.get_role(role_id)
            if role:
                roles_text += f"• {role.name}\n"
        
        if not roles_text:
            roles_text = "No hay roles excluidos"
        
        channels_text = ""
        for channel_id in excluded_channels:
            channel = interaction.guild.get_channel(channel_id)
            if channel:
                channels_text += f"• {channel.name}\n"
        
        if not channels_text:
            channels_text = "No hay canales excluidos"
        
        embed.add_field(name="Roles Excluidos", value=roles_text, inline=False)
        embed.add_field(name="Canales Excluidos", value=channels_text, inline=False)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Gestionar Roles", style=discord.ButtonStyle.primary, row=0)
    async def manage_roles(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = RoleExclusionView(self.bot, self)
        await view.show_menu(interaction)
    
    @discord.ui.button(label="Gestionar Canales", style=discord.ButtonStyle.primary, row=0)
    async def manage_channels(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = ChannelExclusionView(self.bot, self)
        await view.show_menu(interaction)
    
    @discord.ui.button(label="Volver", style=discord.ButtonStyle.secondary, row=1)
    async def go_back(self, interaction: discord.Interaction, button: discord.ui.Button):
        main_view = ConfigMainView(self.bot)
        await interaction.response.edit_message(
            content="Configuración del sistema de niveles:",
            embed=None,
            view=main_view
        )

class RoleExclusionView(discord.ui.View):
    def __init__(self, bot, parent_view):
        super().__init__(timeout=300)
        self.bot = bot
        self.parent_view = parent_view
        self.level_manager = LevelManager(bot)
    
    async def show_menu(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Gestión de Roles Excluidos",
            description="Selecciona qué roles quieres excluir o incluir en el sistema de niveles.",
            color=discord.Color.blue()
        )
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Excluir Rol", style=discord.ButtonStyle.primary, row=0)
    async def exclude_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = ExcludeRoleSelectView(self.bot, self)
        await interaction.response.edit_message(
            content="Selecciona un rol para excluir:",
            embed=None,
            view=view
        )
    
    @discord.ui.button(label="Incluir Rol", style=discord.ButtonStyle.success, row=0)
    async def include_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild.id
        config = self.level_manager.get_guild_config(guild_id)
        excluded_roles = config.get("excluded_roles", [])
        
        if not excluded_roles:
            await interaction.response.send_message("No hay roles excluidos.", ephemeral=True)
            return
        
        options = []
        for role_id in excluded_roles:
            role = interaction.guild.get_role(role_id)
            if role:
                options.append(
                    discord.SelectOption(
                        label=role.name,
                        value=str(role.id)
                    )
                )
        
        view = discord.ui.View()
        select = RoleIncludeSelect(options, self.level_manager, self)
        view.add_item(select)
        
        await interaction.response.edit_message(
            content="Selecciona un rol para volver a incluirlo:",
            embed=None,
            view=view
        )
    
    @discord.ui.button(label="Volver", style=discord.ButtonStyle.secondary, row=1)
    async def go_back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.parent_view.show_menu(interaction)

class ExcludeRoleSelectView(discord.ui.View):
    def __init__(self, bot, parent_view):
        super().__init__(timeout=300)
        self.bot = bot
        self.parent_view = parent_view
        self.level_manager = LevelManager(bot)
    
    @discord.ui.select(cls=discord.ui.RoleSelect, placeholder="Selecciona un rol")
    async def role_select(self, interaction: discord.Interaction, select: discord.ui.RoleSelect):
        selected_role = select.values[0]
        
        guild_id = interaction.guild.id
        config = self.level_manager.get_guild_config(guild_id)
        excluded_roles = config.get("excluded_roles", [])
        
        if selected_role.id in excluded_roles:
            await interaction.response.send_message("Este rol ya está excluido.", ephemeral=True)
            return
        
        excluded_roles.append(selected_role.id)
        self.level_manager.update_guild_config(guild_id, {"excluded_roles": excluded_roles})
        
        await self.parent_view.show_menu(interaction)
    
    @discord.ui.button(label="Volver", style=discord.ButtonStyle.secondary)
    async def go_back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.parent_view.show_menu(interaction)

class RoleIncludeSelect(discord.ui.Select):
    def __init__(self, options, level_manager, parent_view):
        super().__init__(
            placeholder="Selecciona un rol",
            options=options
        )
        self.level_manager = level_manager
        self.parent_view = parent_view
    
    async def callback(self, interaction: discord.Interaction):
        role_id = int(self.values[0])
        
        guild_id = interaction.guild.id
        config = self.level_manager.get_guild_config(guild_id)
        excluded_roles = config.get("excluded_roles", [])
        
        if role_id in excluded_roles:
            excluded_roles.remove(role_id)
            self.level_manager.update_guild_config(guild_id, {"excluded_roles": excluded_roles})
        
        await self.parent_view.parent_view.show_menu(interaction)

class ChannelExclusionView(discord.ui.View):
    def __init__(self, bot, parent_view):
        super().__init__(timeout=300)
        self.bot = bot
        self.parent_view = parent_view
        self.level_manager = LevelManager(bot)
    
    async def show_menu(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Gestión de Canales Excluidos",
            description="Selecciona qué canales quieres excluir o incluir en el sistema de niveles.",
            color=discord.Color.blue()
        )
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Excluir Canal", style=discord.ButtonStyle.primary, row=0)
    async def exclude_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = ExcludeChannelSelectView(self.bot, self)
        await interaction.response.edit_message(
            content="Selecciona un canal para excluir:",
            embed=None,
            view=view
        )
    
    @discord.ui.button(label="Incluir Canal", style=discord.ButtonStyle.success, row=0)
    async def include_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild.id
        config = self.level_manager.get_guild_config(guild_id)
        excluded_channels = config.get("excluded_channels", [])
        
        if not excluded_channels:
            await interaction.response.send_message("No hay canales excluidos.", ephemeral=True)
            return
        
        options = []
        for channel_id in excluded_channels:
            channel = interaction.guild.get_channel(channel_id)
            if channel:
                options.append(
                    discord.SelectOption(
                        label=channel.name,
                        value=str(channel.id)
                    )
                )
        
        view = discord.ui.View()
        select = ChannelIncludeSelect(options, self.level_manager, self)
        view.add_item(select)
        
        await interaction.response.edit_message(
            content="Selecciona un canal para volver a incluirlo:",
            embed=None,
            view=view
        )
    
    @discord.ui.button(label="Volver", style=discord.ButtonStyle.secondary, row=1)
    async def go_back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.parent_view.show_menu(interaction)

class ExcludeChannelSelectView(discord.ui.View):
    def __init__(self, bot, parent_view):
        super().__init__(timeout=300)
        self.bot = bot
        self.parent_view = parent_view
        self.level_manager = LevelManager(bot)
    
    @discord.ui.select(
        cls=discord.ui.ChannelSelect, 
        placeholder="Selecciona un canal",
        channel_types=[discord.ChannelType.text]
    )
    async def channel_select(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        selected_channel = select.values[0]
        
        guild_id = interaction.guild.id
        config = self.level_manager.get_guild_config(guild_id)
        excluded_channels = config.get("excluded_channels", [])
        
        if selected_channel.id in excluded_channels:
            await interaction.response.send_message("Este canal ya está excluido.", ephemeral=True)
            return
        
        excluded_channels.append(selected_channel.id)
        self.level_manager.update_guild_config(guild_id, {"excluded_channels": excluded_channels})
        
        await self.parent_view.show_menu(interaction)
    
    @discord.ui.button(label="Volver", style=discord.ButtonStyle.secondary)
    async def go_back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.parent_view.show_menu(interaction)

class ChannelIncludeSelect(discord.ui.Select):
    def __init__(self, options, level_manager, parent_view):
        super().__init__(
            placeholder="Selecciona un canal",
            options=options
        )
        self.level_manager = level_manager
        self.parent_view = parent_view
    
    async def callback(self, interaction: discord.Interaction):
        channel_id = int(self.values[0])
        
        guild_id = interaction.guild.id
        config = self.level_manager.get_guild_config(guild_id)
        excluded_channels = config.get("excluded_channels", [])
        
        if channel_id in excluded_channels:
            excluded_channels.remove(channel_id)
            self.level_manager.update_guild_config(guild_id, {"excluded_channels": excluded_channels})
        
        await self.parent_view.parent_view.show_menu(interaction)

class AnnouncementView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
        self.level_manager = LevelManager(bot)
    
    async def show_menu(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        config = self.level_manager.get_guild_config(guild_id)
        announcement = config.get("announcement", {})
        
        enabled = announcement.get("enabled", False)
        channel_type = announcement.get("channel_type", "same")
        message = announcement.get("message", DEFAULT_ANNOUNCEMENT_MESSAGE)
        
        channel_text = ""
        if channel_type == "same":
            channel_text = "Mismo canal del mensaje"
        elif channel_type == "dm":
            channel_text = "Mensaje directo al usuario"
        elif channel_type == "custom" and announcement.get("custom_channel_id"):
            channel_id = announcement.get("custom_channel_id")
            channel = interaction.guild.get_channel(channel_id)
            if channel:
                channel_text = f"Canal específico: #{channel.name}"
            else:
                channel_text = "Canal específico (no encontrado)"
        
        embed = discord.Embed(
            title="Configuración de Anuncios",
            description=f"Estado: {'Activado' if enabled else 'Desactivado'}",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Mensaje", value=message, inline=False)
        embed.add_field(name="Canal", value=channel_text, inline=False)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Activar/Desactivar", style=discord.ButtonStyle.primary, row=0)
    async def toggle_announcements(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild.id
        config = self.level_manager.get_guild_config(guild_id)
        announcement = config.get("announcement", {})
        
        enabled = not announcement.get("enabled", False)
        
        self.level_manager.update_guild_config(guild_id, {
            "announcement.enabled": enabled
        })
        
        await self.show_menu(interaction)
    
    @discord.ui.button(label="Editar Mensaje", style=discord.ButtonStyle.primary, row=0)
    async def edit_message(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild.id
        config = self.level_manager.get_guild_config(guild_id)
        announcement = config.get("announcement", {})
        
        await interaction.response.send_modal(AnnouncementMessageModal(self, announcement.get("message", DEFAULT_ANNOUNCEMENT_MESSAGE)))
    
    @discord.ui.button(label="Canal: Mismo", style=discord.ButtonStyle.secondary, row=1)
    async def set_same_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild.id
        
        self.level_manager.update_guild_config(guild_id, {
            "announcement.channel_type": "same",
            "announcement.custom_channel_id": None
        })
        
        await self.show_menu(interaction)
    
    @discord.ui.button(label="Canal: MD", style=discord.ButtonStyle.secondary, row=1)
    async def set_dm_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild.id
        
        self.level_manager.update_guild_config(guild_id, {
            "announcement.channel_type": "dm",
            "announcement.custom_channel_id": None
        })
        
        await self.show_menu(interaction)
    
    @discord.ui.button(label="Canal: Personalizado", style=discord.ButtonStyle.secondary, row=2)
    async def set_custom_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = CustomChannelSelectView(self.bot, self)
        await interaction.response.edit_message(
            content="Selecciona un canal para los anuncios:",
            embed=None,
            view=view
        )
    
    @discord.ui.button(label="Volver", style=discord.ButtonStyle.secondary, row=3)
    async def go_back(self, interaction: discord.Interaction, button: discord.ui.Button):
        main_view = ConfigMainView(self.bot)
        await interaction.response.edit_message(
            content="Configuración del sistema de niveles:",
            embed=None,
            view=main_view
        )

class AnnouncementMessageModal(discord.ui.Modal, title="Editar Mensaje de Anuncio"):
    def __init__(self, view, current_message):
        super().__init__()
        self.view = view
        
        self.message = discord.ui.TextInput(
            label="Mensaje de Anuncio",
            placeholder="Usa {usuario} para la mención y {nivel} para el nivel",
            default=current_message,
            required=True,
            max_length=200,
            style=discord.TextStyle.paragraph
        )
        
        self.add_item(self.message)
    
    async def on_submit(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        
        self.view.level_manager.update_guild_config(guild_id, {
            "announcement.message": self.message.value
        })
        
        await self.view.show_menu(interaction)

class CustomChannelSelectView(discord.ui.View):
    def __init__(self, bot, parent_view):
        super().__init__(timeout=300)
        self.bot = bot
        self.parent_view = parent_view
        self.level_manager = LevelManager(bot)
    
    @discord.ui.select(
        cls=discord.ui.ChannelSelect, 
        placeholder="Selecciona un canal",
        channel_types=[discord.ChannelType.text]
    )
    async def channel_select(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        selected_channel = select.values[0]
        
        guild_id = interaction.guild.id
        self.level_manager.update_guild_config(guild_id, {
            "announcement.channel_type": "custom",
            "announcement.custom_channel_id": selected_channel.id
        })
        
        await self.parent_view.show_menu(interaction)
    
    @discord.ui.button(label="Volver", style=discord.ButtonStyle.secondary)
    async def go_back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.parent_view.show_menu(interaction)