import discord
import asyncio

async def show_config_help(interaction, tipo=None):
    if tipo and tipo.lower() == "logs":
        pages = create_logs_help_pages()

        current_page = 0

        previous_button = discord.ui.Button(label="Anterior", style=discord.ButtonStyle.secondary, disabled=True)
        next_button = discord.ui.Button(label="Siguiente", style=discord.ButtonStyle.primary)
        
        async def previous_callback(interaction):
            nonlocal current_page
            current_page -= 1
            
            previous_button.disabled = current_page == 0
            next_button.disabled = current_page == len(pages) - 1
            
            view = discord.ui.View()
            view.add_item(previous_button)
            view.add_item(next_button)
            await interaction.response.edit_message(embed=pages[current_page], view=view)
        
        async def next_callback(interaction):
            nonlocal current_page
            current_page += 1

            previous_button.disabled = current_page == 0
            next_button.disabled = current_page == len(pages) - 1

            view = discord.ui.View()
            view.add_item(previous_button)
            view.add_item(next_button)
            await interaction.response.edit_message(embed=pages[current_page], view=view)
        
        previous_button.callback = previous_callback
        next_button.callback = next_callback
        
        view = discord.ui.View(timeout=60.0)
        view.add_item(previous_button)
        view.add_item(next_button)

        await interaction.response.send_message(embed=pages[current_page], view=view)

        try:
            msg = await interaction.original_response()
            await view.wait()
            await msg.edit(view=None)
        except Exception as e:
            print(f"Error handling view timeout: {e}")
    
    elif tipo and tipo.lower() == "perms":
        embed = discord.Embed(
            title="Config perms",
            description="Ejecución de `/config perms`\n\n`/config perms {permiso} {accion} ({roles}/{usuarios})`\n\n- `{permiso}`: el permiso que se quiere configurar\n- `{accion}`: añadir o eliminar el permiso\n\nAl menos uno de estos campos es obligatorio:\n\n- `{roles}`: menciona o pon los roles que quieres añadir o eliminar, separados por espacios\n- `{usuarios}`: menciona o pon los usuarios que quieres añadir o eliminar, separados por espacios",
            colour=0x00b0f4
        )
        await interaction.response.send_message(embed=embed)
    
    elif tipo and tipo.lower() == "cmd":
        embed = discord.Embed(
            title="Config cmd",
            description="Ejecución de `/config cmd`\n\n`/config cmd {comando} {estado}`\n\n- `{comando}`: el comando que se quiere activar o desactivar\n- `{estado}`: activar o desactivar el comando",
            colour=0x00b0f4
        )
        await interaction.response.send_message(embed=embed)
    
    elif tipo and tipo.lower() == "update":
        embed = discord.Embed(
            title="Config update",
            description="Ejecución de `/config update`\n\n`/config update`\n\nEste comando restablece la configuración del servidor a los valores predeterminados.",
            colour=0x00b0f4
        )
        await interaction.response.send_message(embed=embed)
    
    elif tipo and tipo.lower() == "data":
        embed = discord.Embed(
            title="Config data",
            description="Ejecución de `/config data`\n\n`/config data`\n\nEste comando muestra la configuración actual del servidor.",
            colour=0x00b0f4
        )
        await interaction.response.send_message(embed=embed)
    
    else:
        embed = discord.Embed(
            title="Configuración del Bot",
            description="Para obtener información detallada sobre los comandos de configuración, por favor visita la documentación:",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Comandos disponibles",
            value=(
                "`/config help` - Muestra esta ayuda\n"
                "`/config help tipo:logs` - Muestra ayuda específica sobre logs\n"
                "`/config help tipo:perms` - Muestra ayuda específica sobre permisos\n"
                "`/config help tipo:cmd` - Muestra ayuda específica sobre comandos\n"
                "`/config help tipo:update` - Muestra ayuda específica sobre actualización\n"
                "`/config help tipo:data` - Muestra ayuda específica sobre datos\n"
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
        
        await interaction.response.send_message(embed=embed)

def create_logs_help_pages():
    page1 = discord.Embed(
        title="Config logs",
        description="Ejecución de `/config logs`:\n\n`/config logs {log} {estado} {canal} {tipoMensaje} ({mensaje}/<footer> {descripcion} <titulo>) ({limite})`\n\n- `{log}`: el log que se quiere configurar.\n- `{estado}`: para activar o desactivar los logs\n- `{canal}`: establecer el canal donde se mandarán los logs.\n- `{tipoMensaje}`: poner el tipo de mensaje del log (embed o normal)\n\nEn caso de ser mensaje embed, solo se tendrán que poner los siguientes parámetros:\n- `<titulo>`: establecer el título del embed.\n- `{descripción}`: establecer la descripción del embed (obligatorio)\n- `<footer>`: establecer el footer del embed.\n\nEn caso de ser mensaje normal, solo se tendrá que poner el siguiente parámetro:\n- `{mensaje}`: establecer el mensaje del log.\n\nEn caso de que el log sea de mensajes editados o eliminados, este parámetros es obligatorio:\n- `{límite}`: establecer el tiempo en el que saldrán logs de mensajes editados, mínimo 7 días, máximo 30 días, poner el número de días solo\n\n**Parámetros a poner en los mensajes de logs:**",
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
        value="**Mensaje y descripción:**\n`{userid}` | `{usertag}` | `{user}` | `{accage}`\n**Footer:**\n`{userid}` | `{usertag}` | `{user}`",
        inline=True
    )
    
    page2.add_field(
        name="Salidas",
        value="**Mensaje y descripción:**\n`{userid}` | `{usertag}`\n**Footer:**\n`{userid}` | `{usertag}`",
        inline=True
    )
    
    page2.add_field(
        name="Mensajes eliminados",
        value="**Mensaje y descripción:**\n`{del_msg}` | `{usertag}` | `{userid}` | `{user}` | `{channel}` | `{channelid}`\n**Footer:**\n`{usertag}` | `{userid}` | `{channelid}`",
        inline=True
    )
    
    page2.add_field(
        name="Mensajes editados",
        value="**Mensaje y descripción:**\n`{usertag}` | `{userid}` | `{user}` | `{channel}` | `{channelid}` | `{old_msg}` | `{new_msg}`\n**Footer:**\n`{usertag}` | `{userid}` | `{channelid}`",
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
    
    page2.add_field(
        name="Parámetros",
        value="`{reason}`: razón de la sanción\n`{user}`: mención del usuario sancionado, que borra o edita el mensaje o que entra al servidor\n`{userid}`: id del usuario sancionado, que borra o edita el mensaje o que entra al servidor\n`{usertag}`: nombre de usuario normal del usuario sancionado, que borra o edita el mensaje o que entra al servidor\n`{mod}`: mención del mod que sanciona\n`{modid}`: id del mod que sanciona\n`{modtag}`: nombre de usuario normal del mod que sanciona\n`{channel}`: mención del canal\n`{channelid}`: id del canal\n`{channel}`: mención del usuario sancionado, que borra o edita el mensaje o que entra al servidor\n`{del_msg}`: contenido del mensaje eliminado\n`{old_msg}`: contenido anterior del mensaje editado\n`{new_msg}`: contenido del nuevo mensaje editado\n`{accage}`: edad de la cuenta de Discord\n`{\\n}`: para representar el salto de línea en los logs",
        inline=False
    )
    
    return [page1, page2]