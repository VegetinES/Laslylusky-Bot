import discord
from ...utils.modals import ButtonConfigModal
from .message_base_view import MessageBaseView

class ButtonHandlerView:
    @staticmethod
    def setup_button_options(view):
        add_button_btn = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Añadir Botón",
            emoji="➕",
            custom_id="add_button",
            row=3
        )
        add_button_btn.callback = view.add_button_callback
        view.add_item(add_button_btn)
        
        if view.message_config.get("buttons") and len(view.message_config["buttons"]) > 0:
            manage_buttons_btn = discord.ui.Button(
                style=discord.ButtonStyle.primary,
                label="Gestionar Botones",
                emoji="🔘",
                custom_id="manage_buttons",
                row=3
            )
            manage_buttons_btn.callback = view.manage_buttons_callback
            view.add_item(manage_buttons_btn)
    
    @staticmethod
    async def handle_button_add(view, interaction):
        try:
            if "buttons" not in view.message_config:
                view.message_config["buttons"] = []
            
            if len(view.message_config["buttons"]) >= 5:
                await interaction.response.send_message(
                    "<:No:825734196256440340> Has alcanzado el límite máximo de botones (5).",
                    ephemeral=True
                )
                return
            
            from ...utils.modals import ButtonConfigModal
            modal = ButtonConfigModal()
            await interaction.response.send_modal(modal)
            
            modal.callback = lambda i, label, emoji, name_format, description: ButtonHandlerView.add_new_button(
                view, i, label, emoji, name_format, description
            )
        except Exception as e:
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error al añadir botón: {str(e)}",
                ephemeral=True
            )

    @staticmethod
    async def add_new_button(view, interaction, label, emoji, name_format, description=""):
        try:
            if "buttons" not in view.message_config:
                view.message_config["buttons"] = []
            
            import uuid
            button_id = f"btn_{uuid.uuid4().hex[:8]}"
            
            view.message_config["buttons"].append({
                "id": button_id,
                "label": label,
                "emoji": emoji,
                "style": 3,
                "name_format": name_format,
                "description": description
            })
            
            if "opened_messages" not in view.ticket_config:
                view.ticket_config["opened_messages"] = {}
                
            view.ticket_config["opened_messages"][button_id] = {
                "embed": True,
                "title": f"Ticket de {label}",
                "description": f"Gracias por abrir un ticket de {label}. Un miembro del equipo te atenderá lo antes posible.",
                "footer": "",
                "color": "green",
                "fields": [],
                "image": {"url": "", "enabled": False},
                "thumbnail": {"url": "", "enabled": False},
                "plain_message": ""
            }
            
            if "auto_increment" not in view.ticket_config:
                view.ticket_config["auto_increment"] = {}
            view.ticket_config["auto_increment"][button_id] = 1
            
            await MessageBaseView.update_view_with_preview(view, interaction)
        except Exception as e:
            print(f"Error al añadir botón: {e}")
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error al añadir botón: {str(e)}",
                ephemeral=True
            )
    
    @staticmethod
    async def handle_buttons_management(view, interaction):
        try:
            options = []
            
            for i, button in enumerate(view.message_config.get("buttons", [])):
                options.append(
                    discord.SelectOption(
                        label=f"Botón {i+1}: {button.get('label', '')[:20]}",
                        value=str(i),
                        description=f"Formato: {button.get('name_format', '')[:30]}"
                    )
                )
            
            if options:
                select = discord.ui.Select(
                    placeholder="Selecciona un botón para editarlo",
                    options=options,
                    custom_id="select_button"
                )
                
                async def button_select_callback(select_interaction):
                    await ButtonHandlerView.button_select_action(
                        view, select_interaction
                    )
                
                select.callback = button_select_callback
                
                temp_view = discord.ui.View(timeout=60)
                temp_view.add_item(select)
                
                back_btn = discord.ui.Button(
                    style=discord.ButtonStyle.secondary,
                    label="Volver",
                    custom_id="back_to_message"
                )
                
                async def back_callback(btn_interaction):
                    await MessageBaseView.update_view_with_preview(
                        view, btn_interaction
                    )
                
                back_btn.callback = back_callback
                temp_view.add_item(back_btn)
                
                await interaction.response.edit_message(
                    content="Selecciona un botón para gestionarlo:",
                    embed=None,
                    view=temp_view
                )
            else:
                await interaction.response.send_message(
                    "<:No:825734196256440340> No hay botones configurados.",
                    ephemeral=True
                )
        except Exception as e:
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error al gestionar botones: {str(e)}",
                ephemeral=True
            )
    
    @staticmethod
    async def button_select_action(view, interaction):
        try:
            button_index = int(interaction.data["values"][0])
            button = view.message_config["buttons"][button_index]
            
            style_options = [
                discord.SelectOption(label="Azul (Primario)", value="1", emoji="🔵"),
                discord.SelectOption(label="Gris (Secundario)", value="2", emoji="⚪"),
                discord.SelectOption(label="Verde (Éxito)", value="3", emoji="🟢"),
                discord.SelectOption(label="Rojo (Peligro)", value="4", emoji="🔴")
            ]
            
            style_select = discord.ui.Select(
                placeholder="Cambiar estilo del botón",
                options=style_options,
                custom_id="change_style"
            )
            
            edit_btn = discord.ui.Button(
                style=discord.ButtonStyle.primary,
                label="Editar Botón",
                custom_id="edit_button"
            )
            
            delete_btn = discord.ui.Button(
                style=discord.ButtonStyle.danger,
                label="Eliminar Botón",
                custom_id="delete_button"
            )
            
            back_btn = discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label="Volver",
                custom_id="back_to_buttons"
            )
            
            button_view = discord.ui.View(timeout=60)
            button_view.add_item(style_select)
            button_view.add_item(edit_btn)
            button_view.add_item(delete_btn)
            button_view.add_item(back_btn)
            
            async def style_callback(style_interaction):
                await ButtonHandlerView.change_button_style(
                    view, style_interaction, button, button_index, button_view
                )
            
            style_select.callback = style_callback
            
            async def edit_callback(btn_interaction):
                await ButtonHandlerView.edit_button_modal(
                    view, btn_interaction, button, button_index
                )
            
            edit_btn.callback = edit_callback
            
            async def delete_callback(btn_interaction):
                await ButtonHandlerView.delete_button(
                    view, btn_interaction, button_index
                )
            
            delete_btn.callback = delete_callback
            
            async def back_callback(btn_interaction):
                await ButtonHandlerView.handle_buttons_management(
                    view, btn_interaction
                )
                    
            back_btn.callback = back_callback
            
            description_text = f"\n**Descripción:** {button.get('description', 'No definida')}" if button.get('description') else ""
            
            await interaction.response.edit_message(
                content=f"**Editar Botón {button_index+1}**\n" +
                f"**Texto:** {button.get('label', '')}\n" +
                f"**Emoji:** {button.get('emoji', '')}\n" +
                f"**Formato de nombre:** {button.get('name_format', '')}" +
                description_text,
                embed=None,
                view=button_view
            )
        except Exception as e:
            print(f"Error al seleccionar botón: {e}")
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error al seleccionar botón: {str(e)}",
                ephemeral=True
            )
    
    @staticmethod
    async def change_button_style(view, interaction, button, button_index, button_view):
        try:
            style_value = int(interaction.data["values"][0])
            button["style"] = style_value
            
            await interaction.response.edit_message(
                content=f"**Estilo cambiado a: {['', 'Azul (Primario)', 'Gris (Secundario)', 'Verde (Éxito)', 'Rojo (Peligro)'][style_value]}**\n\n" +
                f"**Editar Botón {button_index+1}**\n" +
                f"**Texto:** {button.get('label', '')}\n" +
                f"**Emoji:** {button.get('emoji', '')}\n" +
                f"**Formato de nombre:** {button.get('name_format', '')}",
                view=button_view
            )
        except Exception as e:
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error al cambiar estilo: {str(e)}",
                ephemeral=True
            )
    
    @staticmethod
    async def edit_button_modal(view, interaction, button, button_index):
        try:
            current_label = button.get("label", "")
            current_emoji = button.get("emoji", "")
            current_name_format = button.get("name_format", "ticket-{id}")
            current_description = button.get("description", "")
            
            from ...utils.modals import ButtonConfigModal
            modal = ButtonConfigModal(
                current_label,
                current_emoji,
                current_name_format,
                current_description
            )
            await interaction.response.send_modal(modal)
            
            modal.callback = lambda i, label, emoji, name_format, description: ButtonHandlerView.update_button(
                view, i, label, emoji, name_format, description, button_index, button.get("style", 3)
            )
        except Exception as e:
            print(f"Error al editar botón: {e}")
            await interaction.followup.send(
                f"<:No:825734196256440340> Error al editar botón: {str(e)}",
                ephemeral=True
            )

    @staticmethod
    async def update_button(view, interaction, label, emoji, name_format, description, button_index, style):
        try:
            view.message_config["buttons"][button_index] = {
                "label": label,
                "emoji": emoji,
                "style": style,
                "name_format": name_format,
                "description": description
            }
            
            await MessageBaseView.update_view_with_preview(view, interaction)
        except Exception as e:
            print(f"Error al actualizar botón: {e}")
            await interaction.followup.send(
                f"<:No:825734196256440340> Error al actualizar botón: {str(e)}",
                ephemeral=True
            )
    
    @staticmethod
    async def delete_button(view, interaction, button_index):
        try:
            button_id = view.message_config["buttons"][button_index].get("id")
            
            view.message_config["buttons"].pop(button_index)
            
            if button_id and "opened_messages" in view.ticket_config and button_id in view.ticket_config["opened_messages"]:
                del view.ticket_config["opened_messages"][button_id]
                print(f"Eliminado mensaje asociado al botón {button_id}")
            
            if button_id and "auto_increment" in view.ticket_config and button_id in view.ticket_config["auto_increment"]:
                del view.ticket_config["auto_increment"][button_id]
                print(f"Eliminado contador asociado al botón {button_id}")
            
            await MessageBaseView.update_view_with_preview(view, interaction)
        except Exception as e:
            print(f"Error al eliminar botón: {e}")
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error al eliminar botón: {str(e)}",
                ephemeral=True
            )