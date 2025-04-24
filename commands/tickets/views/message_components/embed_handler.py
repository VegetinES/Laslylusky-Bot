import discord
from ...utils.modals import EmbedTitleDescriptionModal, EmbedFieldModal, ImageUrlModal, EmbedFooterModal
from .message_base_view import MessageBaseView
from ...constants import COLORS

class EmbedHandlerView:
    @staticmethod
    def setup_embed_options(view):
        title_desc_btn = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Título y Descripción",
            emoji="📋",
            custom_id="edit_title_desc",
            row=0
        )
        title_desc_btn.callback = view.title_desc_callback
        view.add_item(title_desc_btn)
        
        footer_btn = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Footer",
            emoji="📝",
            custom_id="edit_footer",
            row=0
        )
        footer_btn.callback = view.footer_callback
        view.add_item(footer_btn)
        
        color_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Color",
            emoji="🎨",
            custom_id="edit_color",
            row=1
        )
        color_btn.callback = view.color_callback
        view.add_item(color_btn)
        
        if view.message_config.get("image", {}).get("enabled"):
            image_btn = discord.ui.Button(
                style=discord.ButtonStyle.success,
                label="Quitar Imagen",
                emoji="🖼️",
                custom_id="remove_image",
                row=1
            )
        else:
            image_btn = discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label="Añadir Imagen",
                emoji="🖼️",
                custom_id="add_image",
                row=1
            )
        image_btn.callback = view.image_callback
        view.add_item(image_btn)
        
        if view.message_config.get("thumbnail", {}).get("enabled"):
            thumbnail_btn = discord.ui.Button(
                style=discord.ButtonStyle.success,
                label="Quitar Thumbnail",
                emoji="🔍",
                custom_id="remove_thumbnail",
                row=2
            )
        else:
            thumbnail_btn = discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label="Añadir Thumbnail",
                emoji="🔍",
                custom_id="add_thumbnail",
                row=2
            )
        thumbnail_btn.callback = view.thumbnail_callback
        view.add_item(thumbnail_btn)
        
        field_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Añadir Campo",
            emoji="➕",
            custom_id="add_field",
            row=2
        )
        field_btn.callback = view.add_field_callback
        view.add_item(field_btn)
        
        if view.message_config.get("fields") and len(view.message_config["fields"]) > 0:
            manage_fields_btn = discord.ui.Button(
                style=discord.ButtonStyle.primary,
                label="Gestionar Campos",
                emoji="📊",
                custom_id="manage_fields",
                row=3
            )
            manage_fields_btn.callback = view.manage_fields_callback
            view.add_item(manage_fields_btn)

    @staticmethod
    async def handle_embed_creation(view, interaction):
        view.message_config["embed"] = True
        view.message_config["title"] = ""
        view.message_config["description"] = ""
        view.message_config["footer"] = ""
        view.message_config["color"] = "blue"
        
        modal = EmbedTitleDescriptionModal()
        await interaction.response.send_modal(modal)
        
        modal.callback = lambda i, title, description: EmbedHandlerView.update_embed_title_desc(view, i, title, description)
    
    @staticmethod
    async def update_embed_title_desc(view, interaction, title, description):
        view.message_config["title"] = title
        view.message_config["description"] = description
        
        await MessageBaseView.update_view_with_preview(view, interaction)
    
    @staticmethod
    async def handle_title_desc_edit(view, interaction):
        try:
            modal = EmbedTitleDescriptionModal(
                view.message_config.get("title", ""), 
                view.message_config.get("description", "")
            )
            await interaction.response.send_modal(modal)
            
            async def title_desc_callback(modal_interaction, title, description):
                try:
                    view.message_config["title"] = title
                    view.message_config["description"] = description
                    
                    await MessageBaseView.update_view_with_preview(view, modal_interaction)
                except Exception as e:
                    print(f"Error en callback de título y descripción: {e}")
                    await modal_interaction.response.send_message(
                        f"<:No:825734196256440340> Error al actualizar título y descripción: {str(e)}",
                        ephemeral=True
                    )
            
            modal.callback = title_desc_callback
        except Exception as e:
            print(f"Error al abrir modal de título y descripción: {e}")
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error al abrir el editor de título y descripción: {str(e)}",
                ephemeral=True
            )
    
    @staticmethod
    async def handle_footer_edit(view, interaction):
        modal = EmbedFooterModal(
            view.message_config.get("footer", "")
        )
        await interaction.response.send_modal(modal)
        
        modal.callback = lambda i, footer: EmbedHandlerView.update_embed_footer(view, i, footer)
    
    @staticmethod
    async def update_embed_footer(view, interaction, footer):
        view.message_config["footer"] = footer
        
        await MessageBaseView.update_view_with_preview(view, interaction)
    
    @staticmethod
    async def handle_color_selection(view, interaction):
        options = []
        for color_name, (color_value, color_label) in COLORS.items():
            if color_name in ["default", "blue"] and color_name != "default":
                continue
                
            options.append(
                discord.SelectOption(
                    label=color_label,
                    value=color_name,
                    description=f"Color {color_label}"
                )
            )
        
        select = discord.ui.Select(
            placeholder="Selecciona un color",
            options=options,
            custom_id="select_color"
        )
        
        async def color_select_callback(select_interaction):
            try:
                color_name = select_interaction.data["values"][0]
                view.message_config["color"] = color_name
                
                await MessageBaseView.update_view_with_preview(view, select_interaction)
            except Exception as e:
                print(f"Error al seleccionar color: {e}")
                await select_interaction.response.send_message(
                    f"<:No:825734196256440340> Error al seleccionar color: {str(e)}",
                    ephemeral=True
                )
        
        select.callback = color_select_callback
        
        temp_view = discord.ui.View(timeout=60)
        temp_view.add_item(select)
        
        back_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Cancelar",
            custom_id="cancel_color"
        )
        
        async def cancel_callback(btn_interaction):
            await MessageBaseView.update_view_with_preview(view, btn_interaction)
        
        back_btn.callback = cancel_callback
        temp_view.add_item(back_btn)
        
        await interaction.response.edit_message(
            content="Selecciona un color para el embed:",
            embed=None,
            view=temp_view
        )
    
    @staticmethod
    async def handle_image_toggle(view, interaction, image_type):
        if view.message_config.get(image_type, {}).get("enabled"):
            view.message_config[image_type]["enabled"] = False
            
            await MessageBaseView.update_view_with_preview(view, interaction)
        else:
            modal = ImageUrlModal(image_type)
            await interaction.response.send_modal(modal)
            
            modal.callback = lambda i, url: EmbedHandlerView.update_image_url(view, i, url, image_type)
    
    @staticmethod
    async def update_image_url(view, interaction, url, image_type):
        if image_type not in view.message_config:
            view.message_config[image_type] = {}
        
        view.message_config[image_type]["url"] = url
        view.message_config[image_type]["enabled"] = True
        
        await MessageBaseView.update_view_with_preview(view, interaction)
    
    @staticmethod
    async def handle_field_add(view, interaction):
        if "fields" not in view.message_config:
            view.message_config["fields"] = []
        
        modal = EmbedFieldModal()
        await interaction.response.send_modal(modal)
        
        modal.callback = lambda i, name, value, inline: EmbedHandlerView.add_field(view, i, name, value, inline)
    
    @staticmethod
    async def add_field(view, interaction, name, value, inline):
        if "fields" not in view.message_config:
            view.message_config["fields"] = []
        
        view.message_config["fields"].append({
            "name": name,
            "value": value,
            "inline": inline
        })
        
        await MessageBaseView.update_view_with_preview(view, interaction)
    
    @staticmethod
    async def handle_fields_management(view, interaction):
        options = []
        
        for i, field in enumerate(view.message_config.get("fields", [])):
            options.append(
                discord.SelectOption(
                    label=f"Campo {i+1}: {field.get('name', '')[:20]}",
                    value=str(i),
                    description=field.get("value", "")[:50] + ("..." if len(field.get("value", "")) > 50 else "")
                )
            )
        
        if options:
            select = discord.ui.Select(
                placeholder="Selecciona un campo para editarlo",
                options=options,
                custom_id="select_field"
            )
            
            select.callback = lambda select_interaction: EmbedHandlerView.field_select_action(view, select_interaction)
            
            temp_view = discord.ui.View(timeout=60)
            temp_view.add_item(select)
            
            back_btn = discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label="Volver",
                custom_id="back_to_message"
            )
            
            back_btn.callback = lambda btn_interaction: MessageBaseView.update_view_with_preview(view, btn_interaction)
            temp_view.add_item(back_btn)
            
            await interaction.response.edit_message(
                content="Selecciona un campo para gestionarlo:",
                embed=None,
                view=temp_view
            )

    @staticmethod
    async def field_select_action(view, interaction):
        field_index = int(interaction.data["values"][0])
        field = view.message_config["fields"][field_index]
        
        inline_btn = discord.ui.Button(
            style=discord.ButtonStyle.success if field.get("inline") else discord.ButtonStyle.secondary,
            label="Inline: Sí" if field.get("inline") else "Inline: No",
            custom_id="toggle_inline"
        )
        
        edit_btn = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Editar Campo",
            custom_id="edit_field"
        )
        
        delete_btn = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="Eliminar Campo",
            custom_id="delete_field"
        )
        
        back_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Volver",
            custom_id="back_to_fields"
        )
        
        field_view = discord.ui.View(timeout=60)
        field_view.add_item(inline_btn)
        field_view.add_item(edit_btn)
        field_view.add_item(delete_btn)
        field_view.add_item(back_btn)
        
        inline_btn.callback = lambda btn_interaction: EmbedHandlerView.toggle_field_inline(
            view, btn_interaction, field_index, field, field_view
        )
        
        edit_btn.callback = lambda btn_interaction: EmbedHandlerView.edit_field_modal(
            view, btn_interaction, field_index, field
        )
        
        delete_btn.callback = lambda btn_interaction: EmbedHandlerView.delete_field(
            view, btn_interaction, field_index
        )
        
        back_btn.callback = lambda btn_interaction: MessageBaseView.update_view_with_preview(
            view, btn_interaction
        )
        
        await interaction.response.edit_message(
            content=f"**Editar Campo {field_index+1}**\n**Nombre:** {field.get('name', '')}\n**Valor:** {field.get('value', '')}\n**Inline:** {'Sí' if field.get('inline') else 'No'}",
            embed=None,
            view=field_view
        )
    
    @staticmethod
    async def toggle_field_inline(view, interaction, field_index, field, field_view):
        field["inline"] = not field.get("inline", False)
        
        for item in field_view.children:
            if item.custom_id == "toggle_inline":
                item.style = discord.ButtonStyle.success if field["inline"] else discord.ButtonStyle.secondary
                item.label = "Inline: Sí" if field["inline"] else "Inline: No"
        
        await interaction.response.edit_message(
            content=f"**Editar Campo {field_index+1}**\n**Nombre:** {field.get('name', '')}\n**Valor:** {field.get('value', '')}\n**Inline:** {'Sí' if field.get('inline') else 'No'}",
            view=field_view
        )
    
    @staticmethod
    async def edit_field_modal(view, interaction, field_index, field):
        modal = EmbedFieldModal(
            field.get("name", ""), 
            field.get("value", ""), 
            field.get("inline", False)
        )
        await interaction.response.send_modal(modal)
        
        modal.callback = lambda i, name, value, inline: EmbedHandlerView.update_field(
            view, i, name, value, inline, field_index
        )
    
    @staticmethod
    async def update_field(view, interaction, name, value, inline, field_index):
        view.message_config["fields"][field_index] = {
            "name": name,
            "value": value,
            "inline": inline
        }
        
        await MessageBaseView.update_view_with_preview(view, interaction)
    
    @staticmethod
    async def delete_field(view, interaction, field_index):
        view.message_config["fields"].pop(field_index)
        
        await MessageBaseView.update_view_with_preview(view, interaction)