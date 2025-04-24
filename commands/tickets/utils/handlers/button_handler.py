import discord
import traceback

async def handle_ticket_button(interaction: discord.Interaction, custom_id):
    from ..database import get_ticket_data, increment_ticket_counter
    from .ticket_handler import create_ticket, close_ticket
    from .user_handler import add_user_to_ticket, remove_user_from_ticket
    from ..permissions import check_manage_permission
    
    try:
        parts = custom_id.split(":")
        if len(parts) < 3:
            await interaction.response.send_message(
                "<:No:825734196256440340> Formato de ID inválido.",
                ephemeral=True
            )
            return
        
        action = parts[1]
        channel_id = parts[2]
        button_index = 0
        
        if action == "open":
            ticket_data = get_ticket_data(interaction.guild.id, channel_id)
            if ticket_data is None:
                await interaction.response.send_message(
                    "<:No:825734196256440340> Este ticket ya no está disponible o ha sido eliminado.",
                    ephemeral=True
                )
                return
        
        if len(parts) > 3 and action == "open":
            button_index = int(parts[3])
        elif action == "open" and hasattr(interaction, 'data'):
            if 'component_type' in interaction.data and interaction.data['component_type'] == 3:
                if 'values' in interaction.data and interaction.data['values']:
                    button_index = int(interaction.data['values'][0])
            elif 'values' in interaction.data:
                button_index = int(interaction.data['values'][0])
        
        try:
            await interaction.response.defer(ephemeral=True)
        except Exception as defer_error:
            print(f"Error al diferir respuesta: {defer_error}")
            try:
                await interaction.response.send_message("Procesando ticket...", ephemeral=True)
            except Exception as direct_error:
                print(f"Error al enviar respuesta directa: {direct_error}")
        
        if action == "open":
            await create_ticket(interaction, channel_id, button_index)
        elif action in ["close", "add", "remove"]:
            has_permission = await check_manage_permission(interaction, channel_id)
            
            if has_permission is None:
                await interaction.followup.send(
                    "<:No:825734196256440340> Este ticket ya no está disponible. La configuración ha sido eliminada.",
                    ephemeral=True
                )
                return
            
            if has_permission:
                if action == "close":
                    await close_ticket(interaction, channel_id)
                elif action == "add":
                    await add_user_to_ticket(interaction, channel_id)
                elif action == "remove":
                    await remove_user_from_ticket(interaction, channel_id)
            else:
                await interaction.followup.send(
                    "<:No:825734196256440340> No tienes permiso para realizar esta acción. Necesitas tener permisos de gestión de tickets.",
                    ephemeral=True
                )
    except Exception as e:
        print(f"Error en handle_ticket_button: {e}")
        import traceback
        traceback.print_exc()
        try:
            await interaction.followup.send(
                f"<:No:825734196256440340> Error al procesar la interacción: {str(e)}",
                ephemeral=True
            )
        except Exception as followup_error:
            print(f"Error al enviar followup: {followup_error}")
            try:
                await interaction.response.send_message(
                    f"<:No:825734196256440340> Error al procesar el ticket: {str(e)}",
                    ephemeral=True
                )
            except:
                pass