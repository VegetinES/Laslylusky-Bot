import discord
import asyncio

async def show_config_help(interaction):
    embed = discord.Embed(
        title="Configuración del Bot",
        description="Para obtener información detallada sobre los comandos de configuración, por favor visita la documentación:",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Comandos disponibles",
        value=(
            "`/config help` - Muestra esta ayuda\n"
            "`/config data` - Muestra la configuración actual del servidor\n"
            "`/config update` - Restablece la configuración a los valores predeterminados\n"
            "`/config cmd comando estado` - Activa o desactiva comandos específicos\n"
            "`/config logs` - Configuración de registros de auditoría\n"
            "`/config perms` - Configuración de permisos\n"
            "`/config tickets help` - Muestra la ayuda de configuración de los tickets"
        ),
        inline=False
    )
    
    embed.add_field(
        name="Documentación",
        value="[Ver documentación en GitHub](https://github.com/VegetinES/Laslylusky-Bot/tree/main/docs/user/Configuration.md)",
        inline=False
    )

    view = ConfigHelpView()
    
    await interaction.response.send_message(embed=embed, view=view)
    
    view.message = await interaction.original_response()

class ConfigHelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.message = None
        
        self.add_item(discord.ui.Button(label="Ayuda /config logs", custom_id="logs_help", style=discord.ButtonStyle.secondary, row=0))
        self.add_item(discord.ui.Button(label="Ayuda /config update", custom_id="update_help", style=discord.ButtonStyle.secondary, row=0))
        self.add_item(discord.ui.Button(label="Ayuda /config data", custom_id="data_help", style=discord.ButtonStyle.secondary, row=1))
        self.add_item(discord.ui.Button(label="Ayuda /config cmd", custom_id="cmd_help", style=discord.ButtonStyle.secondary, row=1))
        self.add_item(discord.ui.Button(label="Ayuda /config perms", custom_id="perms_help", style=discord.ButtonStyle.secondary, row=2))
        self.add_item(discord.ui.Button(label="Ayuda /config tickets help", custom_id="tickets_help", style=discord.ButtonStyle.secondary, row=2))
    
    async def interaction_check(self, interaction):
        for child in self.children:
            if child.custom_id == interaction.data["custom_id"]:
                await self.handle_button_click(interaction, child.custom_id)
                return False
        return True

    async def handle_button_click(self, interaction, custom_id):
        if custom_id == "logs_help":
            await self.show_logs_help(interaction)
        elif custom_id == "update_help":
            await self.show_update_help(interaction)
        elif custom_id == "data_help":
            await self.show_data_help(interaction)
        elif custom_id == "cmd_help":
            await self.show_cmd_help(interaction)
        elif custom_id == "perms_help":
            await self.show_perms_help(interaction)
        elif custom_id == "tickets_help":
            await self.show_tickets_help(interaction)
    
    async def show_logs_help(self, interaction):
        pages = create_logs_help_pages()
        await interaction.response.edit_message(embeds=pages, view=None)
    
    async def show_update_help(self, interaction):
        embed = discord.Embed(
            title="Config update",
            description="Ejecución de `/config update`\n\n`/config update`\n\nEste comando restablece la configuración del servidor a los valores predeterminados.",
            colour=0x00b0f4
        )
        await interaction.response.edit_message(embed=embed, view=None)
    
    async def show_data_help(self, interaction):
        embed = discord.Embed(
            title="Config data",
            description="Ejecución de `/config data`\n\n`/config data`\n\nEste comando muestra la configuración actual del servidor.",
            colour=0x00b0f4
        )
        await interaction.response.edit_message(embed=embed, view=None)
    
    async def show_cmd_help(self, interaction):
        embed = discord.Embed(
            title="Config cmd",
            description="Ejecución de `/config cmd`\n\n`/config cmd {comando} {estado}`\n\n- `{comando}`: el comando que se quiere activar o desactivar\n- `{estado}`: activar o desactivar el comando",
            colour=0x00b0f4
        )
        await interaction.response.edit_message(embed=embed, view=None)
    
    async def show_perms_help(self, interaction):
        embed = discord.Embed(
            title="Config perms",
            description="Ejecución de `/config perms`\n\n`/config perms {permiso} {accion} ({roles}/{usuarios})`\n\n- `{permiso}`: el permiso que se quiere configurar\n- `{accion}`: añadir o eliminar el permiso\n\nAl menos uno de estos campos es obligatorio:\n\n- `{roles}`: menciona o pon los roles que quieres añadir o eliminar, separados por espacios\n- `{usuarios}`: menciona o pon los usuarios que quieres añadir o eliminar, separados por espacios",
            colour=0x00b0f4
        )
        await interaction.response.edit_message(embed=embed, view=None)
    
    async def show_tickets_help(self, interaction):
        embed = discord.Embed(
            title="Config tickets help",
            description="Ejecución de `/config tickets help`\n\n`/config tickets help`\n\nEste comando muestra la ayuda específica para configurar el sistema de tickets.",
            colour=0x00b0f4
        )
        await interaction.response.edit_message(embed=embed, view=None)
    
    async def on_timeout(self):
        if self.message:
            try:
                for child in self.children:
                    child.disabled = True
                await self.message.edit(view=self)
            except:
                pass

def create_logs_help_pages():
    page1 = discord.Embed(
        title="Config logs",
        description="Ejecución de `/config logs`:\n\n`/config logs {log}`\n\n- `{log}`: el log que se quiere configurar\n\n**Parámetros a poner en los mensajes de logs:**",
        color=0x00b0f4
    )
    
    page2 = discord.Embed(
        title="Config logs",
        description="Parámetros a establecer en los logs",
        color=0x00b0f4
    )
    
    page2.add_field(
        name="Ban",
        value="**Mensaje y descripción:**\n`{userid}` | `{usertag}` | `{mod}` | `{modid}` | `{modtag}` | `{reason}`\n**Footer:**\n`{userid}` | `{usertag}` | `{modid}` | `{modtag}`",
        inline=True
    )
    
    page2.add_field(
        name="Kick",
        value="**Mensaje y descripción:**\n`{userid}` | `{usertag}` | `{mod}` | `{modid}` | `{modtag}` | `{reason}`\n**Footer:**\n`{userid}` | `{usertag}` | `{modid}` | `{modtag}`",
        inline=True
    )
    
    page2.add_field(
        name="Unban",
        value="**Mensaje y descripción:**\n`{userid}` | `{usertag}` | `{mod}` | `{modid}` | `{modtag}`\n**Footer:**\n`{userid}` | `{usertag}` | `{modid}` | `{modtag}`",
        inline=True
    )
    
    page2.add_field(
        name="Entradas",
        value="**Mensaje y descripción:**\n`{userid}` | `{usertag}` | `{user}` | `{accage}` | `{acc_age}`\n**Footer:**\n`{userid}` | `{usertag}` | `{user}`",
        inline=True
    )
    
    page2.add_field(
        name="Salidas",
        value="**Mensaje y descripción:**\n`{userid}` | `{usertag}` | `{acc_age}` | `{server_age}`\n**Footer:**\n`{userid}` | `{usertag}`",
        inline=True
    )
    
    page2.add_field(
        name="Mensajes eliminados",
        value="**Mensaje y descripción:**\n`{del_msg}` | `{usertag}` | `{userid}` | `{user}` | `{channel}` | `{channelid}` | `{attached}`\n**Footer:**\n`{usertag}` | `{userid}` | `{channelid}`",
        inline=True
    )
    
    page2.add_field(
        name="Mensajes editados",
        value="**Mensaje y descripción:**\n`{usertag}` | `{userid}` | `{user}` | `{channel}` | `{channelid}` | `{old_msg}` | `{new_msg}` | `{attached}`\n**Footer:**\n`{usertag}` | `{userid}` | `{channelid}`",
        inline=True
    )
    
    page2.add_field(
        name="Warns",
        value="**Mensaje y descripción:**\n`{userid}` | `{usertag}` | `{mod}` | `{modid}` | `{modtag}` | `{reason}` | `{user}`\n**Footer:**\n`{userid}` | `{usertag}` | `{modid}` | `{modtag}`",
        inline=True
    )
    
    page2.add_field(
        name="Unwarns",
        value="**Mensaje y descripción:**\n`{userid}` | `{usertag}` | `{mod}` | `{modid}` | `{modtag}` | `{reason}` | `{user}`\n**Footer:**\n`{userid}` | `{usertag}` | `{modid}` | `{modtag}`",
        inline=True
    )
    
    page3 = discord.Embed(
        title="Config logs",
        description="Parámetros a establecer en los logs (continuación)",
        color=0x00b0f4
    )
    
    page3.add_field(
        name="Entrada a canales de voz",
        value="**Mensaje y descripción:**\n`{user}` | `{usertag}` | `{userid}` | `{channel}` | `{channelid}`\n**Footer:**\n`{usertag}` | `{userid}` | `{channelid}`",
        inline=True
    )
    
    page3.add_field(
        name="Salida de canales de voz",
        value="**Mensaje y descripción:**\n`{user}` | `{usertag}` | `{userid}` | `{channel}` | `{channelid}`\n**Footer:**\n`{usertag}` | `{userid}` | `{channelid}`",
        inline=True
    )
    
    page3.add_field(
        name="Roles añadidos a usuarios",
        value="**Mensaje y descripción:**\n`{user}` | `{usertag}` | `{userid}` | `{role}` | `{roleid}`\n**Footer:**\n`{usertag}` | `{userid}` | `{roleid}`",
        inline=True
    )
    
    page3.add_field(
        name="Roles removidos de usuarios",
        value="**Mensaje y descripción:**\n`{user}` | `{usertag}` | `{userid}` | `{role}` | `{roleid}`\n**Footer:**\n`{usertag}` | `{userid}` | `{roleid}`",
        inline=True
    )
    
    page3.add_field(
        name="Canales creados",
        value="**Mensaje y descripción:**\n`{channel}` | `{channelid}` | `{category}`\n**Footer:**\n`{channelid}`",
        inline=True
    )
    
    page3.add_field(
        name="Canales eliminados",
        value="**Mensaje y descripción:**\n`{channel}` | `{channelid}` | `{category}`\n**Footer:**\n`{channelid}`",
        inline=True
    )
    
    page3.add_field(
        name="Actualización de avatar o nombre",
        value="**Mensaje y descripción:**\n`{user}` | `{usertag}` | `{userid}` | `{old_avatar_link}` | `{new_avatar_link}` | `{old_name}` | `{new_name}`\n**Footer:**\n`{usertag}` | `{userid}`",
        inline=True
    )
    
    page4 = discord.Embed(
        title="Config logs",
        description="Explicación de parámetros",
        color=0x00b0f4
    )
    
    page4.add_field(
        name="Parámetros básicos",
        value="`{reason}`: razón de la sanción\n`{user}`: mención del usuario sancionado, que borra o edita el mensaje o que entra al servidor\n`{userid}`: id del usuario sancionado, que borra o edita el mensaje o que entra al servidor\n`{usertag}`: nombre de usuario normal del usuario sancionado, que borra o edita el mensaje o que entra al servidor\n`{mod}`: mención del mod que sanciona\n`{modid}`: id del mod que sanciona\n`{modtag}`: nombre de usuario normal del mod que sanciona\n`{channel}`: mención del canal\n`{channelid}`: id del canal\n`{del_msg}`: contenido del mensaje eliminado\n`{old_msg}`: contenido anterior del mensaje editado\n`{new_msg}`: contenido del nuevo mensaje editado\n`{attached}`: contenido de archivos adjuntos en caso de haberlos\n`{acc_age}`: edad de la cuenta de Discord\n`{server_age}`: tiempo que lleva el usuario en el servidor\n`{\\n}`: para representar el salto de línea en los logs",
        inline=False
    )
    
    page4.add_field(
        name="Parámetros adicionales",
        value="`{role}`: mención del rol que se añade o quita\n`{roleid}`: id del rol que se añade o quita\n`{category}`: nombre de la categoría del canal (o \"sin categoría\")\n`{old_avatar_link}`: link del antiguo avatar del usuario, formato [antiguo avatar](link)\n`{new_avatar_link}`: link del nuevo avatar del usuario, formato [nuevo avatar](link)\n`{old_name}`: antiguo nombre del usuario (o \"el nombre no cambió\")\n`{new_name}`: nuevo nombre del usuario (o \"el nombre no cambió\")",
        inline=False
    )
    
    return [page1, page2, page3, page4]