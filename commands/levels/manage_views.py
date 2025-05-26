import discord
from .level_manager import LevelManager

class ManageUserView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.level_manager = LevelManager(bot)
        self.user_id = user_id
    
    @discord.ui.button(label="Cambiar Nivel", style=discord.ButtonStyle.primary, row=0)
    async def change_level(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ChangeLevelModal(self))
    
    @discord.ui.button(label="Reiniciar", style=discord.ButtonStyle.danger, row=0)
    async def reset_level(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = ConfirmResetView(self.bot, self.user_id)
        
        user = await self.bot.fetch_user(self.user_id)
        username = user.name if user else f"Usuario ID: {self.user_id}"
        
        await interaction.response.edit_message(
            content=f"¿Estás seguro de que quieres reiniciar el nivel de {username}? Esta acción no se puede deshacer.",
            view=view,
            embed=None
        )
    
    @discord.ui.button(label="Transferir Nivel", style=discord.ButtonStyle.secondary, row=0)
    async def transfer_level(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = TransferLevelView(self.bot, self.user_id)
        
        user = await self.bot.fetch_user(self.user_id)
        username = user.name if user else f"Usuario ID: {self.user_id}"
        
        await interaction.response.edit_message(
            content=f"Selecciona el usuario al que quieres transferir la experiencia de {username}:",
            view=view,
            embed=None
        )

class ChangeLevelModal(discord.ui.Modal, title="Cambiar Nivel"):
    def __init__(self, view):
        super().__init__()
        self.view = view
        
        self.level = discord.ui.TextInput(
            label="Nuevo Nivel",
            placeholder="Introduce el nuevo nivel",
            required=True,
            min_length=1,
            max_length=5
        )
        
        self.add_item(self.level)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            level = int(self.level.value)
            
            if level < 0:
                await interaction.response.send_message("El nivel no puede ser negativo.", ephemeral=True)
                return
            
            guild_id = interaction.guild.id
            user_id = self.view.user_id
            
            self.view.level_manager.set_user_level(guild_id, user_id, level)
            
            user = await self.view.bot.fetch_user(user_id)
            username = user.name if user else f"Usuario ID: {user_id}"
            
            await interaction.response.send_message(
                f"Nivel de {username} cambiado a {level} correctamente.",
                ephemeral=True
            )
        except ValueError:
            await interaction.response.send_message("Por favor, introduce un número válido.", ephemeral=True)

class ConfirmResetView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.level_manager = LevelManager(bot)
        self.user_id = user_id
    
    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild.id
        self.level_manager.reset_user_level(guild_id, self.user_id)
        
        user = await self.bot.fetch_user(self.user_id)
        username = user.name if user else f"Usuario ID: {self.user_id}"
        
        await interaction.response.edit_message(
            content=f"El nivel de {username} ha sido reiniciado correctamente.",
            view=None
        )
    
    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="Operación cancelada.",
            view=None
        )

class TransferLevelView(discord.ui.View):
    def __init__(self, bot, from_user_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.level_manager = LevelManager(bot)
        self.from_user_id = from_user_id
        self.to_user_id = None
    
    @discord.ui.button(label="Seleccionar Usuario", style=discord.ButtonStyle.primary)
    async def select_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(UserIDModal(self))
    
    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="Operación cancelada.",
            view=None
        )

class UserIDModal(discord.ui.Modal, title="Seleccionar Usuario"):
    def __init__(self, view):
        super().__init__()
        self.view = view
        
        self.user_id = discord.ui.TextInput(
            label="ID del Usuario",
            placeholder="Introduce la ID del usuario destino",
            required=True,
            min_length=17,
            max_length=20
        )
        
        self.add_item(self.user_id)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            to_user_id = int(self.user_id.value)
            self.view.to_user_id = to_user_id
            
            if to_user_id == self.view.from_user_id:
                await interaction.response.send_message("No puedes transferir experiencia al mismo usuario.", ephemeral=True)
                return
            
            from_user = await self.view.bot.fetch_user(self.view.from_user_id)
            to_user = await self.view.bot.fetch_user(to_user_id)
            
            if not to_user:
                await interaction.response.send_message("Usuario no encontrado.", ephemeral=True)
                return
            
            from_username = from_user.name if from_user else f"Usuario ID: {self.view.from_user_id}"
            to_username = to_user.name if to_user else f"Usuario ID: {to_user_id}"
            
            confirm_view = ConfirmTransferView(self.view.bot, self.view.from_user_id, to_user_id)
            
            await interaction.response.edit_message(
                content=f"¿Estás seguro de que quieres transferir toda la experiencia de {from_username} a {to_username}?\n\nEsta acción no se puede deshacer y {from_username} perderá todos sus niveles y roles de recompensa.",
                view=confirm_view
            )
        except ValueError:
            await interaction.response.send_message("ID de usuario inválida.", ephemeral=True)

class ConfirmTransferView(discord.ui.View):
    def __init__(self, bot, from_user_id, to_user_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.level_manager = LevelManager(bot)
        self.from_user_id = from_user_id
        self.to_user_id = to_user_id
    
    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild.id
        
        from_user = await self.bot.fetch_user(self.from_user_id)
        to_user = await self.bot.fetch_user(self.to_user_id)
        
        from_username = from_user.name if from_user else f"Usuario ID: {self.from_user_id}"
        to_username = to_user.name if to_user else f"Usuario ID: {self.to_user_id}"
        
        self.level_manager.transfer_level(guild_id, self.from_user_id, self.to_user_id)
        
        await interaction.response.edit_message(
            content=f"La experiencia de {from_username} ha sido transferida correctamente a {to_username}.",
            view=None
        )
        
        try:
            from_data = self.level_manager.get_user_level(guild_id, self.from_user_id)
            to_data = self.level_manager.get_user_level(guild_id, self.to_user_id)
            
            from_member = interaction.guild.get_member(self.from_user_id)
            to_member = interaction.guild.get_member(self.to_user_id)
            
            if from_member and to_member:
                await self.level_manager.handle_role_rewards(interaction.guild, to_member, to_data["level"])
        except Exception as e:
            print(f"Error al actualizar roles después de transferir: {e}")
    
    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="Operación cancelada.",
            view=None
        )