import discord
from discord.ext import commands
from database.get import get_specific_field, get_server_data
from database.update import update_multiple_fields

async def show_config_cmd(interaction, command: str = None, state: str = None):
    try:
        if not command or not state:
            await interaction.response.send_message(
                "Por favor, proporciona un comando y un estado válido (activado/desactivado).",
                ephemeral=True
            )
            return

        command = command.lower()
        state = state.lower()

        if state not in ['activate', 'deactivate']:
            await interaction.response.send_message(
                "Estado no válido. Debe ser 'activado' o 'desactivado'.",
                ephemeral=True
            )
            return

        server_data = get_server_data(interaction.guild.id)
        if not server_data:
            await interaction.response.send_message(
                "❌ No se pudieron obtener los datos del servidor. Por favor, intenta más tarde.",
                ephemeral=True
            )
            return

        default_cmds = server_data.get('default_cdm', []) or []
        active_cmds = server_data.get('act_cmd', []) or []
        deactive_cmds = server_data.get('deact_cmd', []) or []

        if command not in active_cmds and command not in deactive_cmds:
            await interaction.response.send_message(
                f"El comando `{command}` no existe en la lista de comandos del bot.",
                ephemeral=True
            )
            return

        if command in default_cmds:
            await interaction.response.send_message(
                "No puedes modificar los comandos esenciales del bot.",
                ephemeral=True
            )
            return

        if state == 'activate':
            if command in active_cmds:
                await interaction.response.send_message(
                    f"El comando `{command}` ya está activado.",
                    ephemeral=True
                )
                return

            if command in deactive_cmds:
                deactive_cmds.remove(command)
            active_cmds.append(command)
            
            updates = {
                "act_cmd": active_cmds,
                "deact_cmd": deactive_cmds
            }
            
            if update_multiple_fields(interaction.guild.id, updates):
                await interaction.response.send_message(
                    f"✅ El comando `{command}` ha sido activado exitosamente."
                )
            else:
                await interaction.response.send_message(
                    "❌ Ocurrió un error al actualizar la base de datos.",
                    ephemeral=True
                )

        elif state == 'deactivate':
            if command in deactive_cmds:
                await interaction.response.send_message(
                    f"El comando `{command}` ya está desactivado.",
                    ephemeral=True
                )
                return

            if command in active_cmds:
                active_cmds.remove(command)
            deactive_cmds.append(command)
            
            updates = {
                "act_cmd": active_cmds,
                "deact_cmd": deactive_cmds
            }
            
            if update_multiple_fields(interaction.guild.id, updates):
                await interaction.response.send_message(
                    f"✅ El comando `{command}` ha sido desactivado exitosamente."
                )
            else:
                await interaction.response.send_message(
                    "❌ Ocurrió un error al actualizar la base de datos.",
                    ephemeral=True
                )

    except Exception as e:
        print(f"Error en show_config_cmd: {str(e)}")
        if not interaction.response.is_done():
            await interaction.response.send_message(
                f"❌ Ocurrió un error al procesar el comando: {str(e)}",
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                f"❌ Ocurrió un error al procesar el comando: {str(e)}",
                ephemeral=True
            )

async def check_command(interaction, comando):
    act_commands = get_specific_field(interaction.guild.id, "act_cmd")
    
    if act_commands is None:
        embed = discord.Embed(
            title="<:No:825734196256440340> Error de Configuración",
            description="No hay datos configurados para este servidor. Usa el comando `</config update:1348248454610161751>` si eres administrador para configurar el bot funcione en el servidor",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return False
        
    if comando not in act_commands:
        await interaction.response.send_message(
            "El comando no está activado en este servidor.",
            ephemeral=True
        )
        return False
        
    return True