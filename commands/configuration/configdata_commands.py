import discord
from datetime import datetime

class CommandsBackView(discord.ui.View):
    def __init__(self, author_id, guild_data):
        super().__init__(timeout=180)
        self.author_id = author_id
        self.guild_data = guild_data
        
        self.back_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Volver atrás",
            custom_id="back_commands"
        )
        self.back_button.callback = self.back_callback
        self.add_item(self.back_button)

        self.cancel_button = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="Cancelar",
            custom_id="cancel_commands"
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
    
    async def back_callback(self, interaction):
        from .configdata import ConfigDataMainView
        
        view = ConfigDataMainView(self.author_id, self.guild_data, interaction)
        await interaction.response.edit_message(
            content="Selecciona qué información quieres ver:",
            view=view,
            embed=None
        )
    
    async def cancel_callback(self, interaction):
        for child in self.children:
            child.disabled = True
        
        await interaction.response.edit_message(
            content="Visualización de datos cancelada.",
            view=self,
            embed=None
        )
        self.stop()

async def create_commands_embed(guild_data, interaction):
    embed = discord.Embed(
        title=f"Comandos del servidor {interaction.guild.name}",
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

async def show_commands_data(interaction, guild_data, author_id):
    try:
        embed = await create_commands_embed(guild_data, interaction)
        view = CommandsBackView(author_id, guild_data)
        
        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=view
        )
    except Exception as e:
        print(f"Error en show_commands_data: {e}")
        await interaction.response.send_message(
            f"Error al mostrar los datos de comandos: {e}",
            ephemeral=True
        )