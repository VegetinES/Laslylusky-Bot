import discord
from ..constants import COLORS
from .helpers import handle_ticket_button

async def generate_preview(message_type, message_config, guild):
    try:
        if not message_config or not isinstance(message_config, dict):
            return {
                "content": f"**Mensaje para {message_type}**\n\nNo hay configuración de mensaje"
            }
            
        result = {}
        content = ""

        if message_type == "open_message" and "VIEW_MODE" not in message_config:
            content = "**Mensaje para abrir tickets**\n\n"
            if message_config.get("buttons"):
                buttons_preview = ""
                for button in message_config.get("buttons", []):
                    emoji = button.get("emoji", "")
                    label = button.get("label", "Abrir Ticket")
                    buttons_preview += f"[Botón: {emoji} {label}]\n"
                content += buttons_preview
        elif message_type.startswith("opened_message") and "VIEW_MODE" not in message_config:
            content = "**Mensaje para tickets abiertos**\n\n"
            content += "[Botón: 🔒 Cerrar Ticket] [Botón: ➕ Añadir Usuario] [Botón: ➖ Eliminar Usuario]\n"
        
        if "VIEW_MODE" in message_config and message_config.get("plain_message"):
            content = message_config.get("plain_message")
        elif message_config.get("plain_message") and "VIEW_MODE" not in message_config:
            content += message_config.get("plain_message")
        elif "VIEW_MODE" in message_config:
            content = ""
        
        result["content"] = content
        
        if message_config.get("embed"):
            color_name = message_config.get("color", "default") 
            color_value = COLORS.get(color_name, COLORS["default"])[0] if color_name in COLORS else 0x3498db
            
            embed = discord.Embed(
                title=message_config.get("title", ""),
                description=message_config.get("description", ""),
                color=color_value
            )
            
            if message_config.get("footer"):
                embed.set_footer(text=message_config.get("footer"))
            
            if message_config.get("image", {}).get("enabled") and message_config.get("image", {}).get("url"):
                embed.set_image(url=message_config.get("image", {}).get("url") or "https://placehold.co/600x400?text=Imagen")
            
            if message_config.get("thumbnail", {}).get("enabled") and message_config.get("thumbnail", {}).get("url"):
                embed.set_thumbnail(url=message_config.get("thumbnail", {}).get("url") or "https://placehold.co/150x150?text=Thumbnail")
            
            if message_config.get("fields"):
                for field in message_config.get("fields", []):
                    embed.add_field(
                        name=field.get("name", ""),
                        value=field.get("value", ""),
                        inline=field.get("inline", False)
                    )
            
            result["embed"] = embed
        
        return result
    except Exception as e:
        print(f"Error al generar vista previa: {e}")
        return {
            "content": f"**Error al generar vista previa**: {str(e)}"
        }

async def generate_ticket_view(ticket_config, channel_id):
    try:
        if not ticket_config or not isinstance(ticket_config, dict):
            print("Error: ticket_config no es válido")
            return None
            
        buttons = ticket_config.get("open_message", {}).get("buttons", [])
        if not buttons:
            print("Creando botón predeterminado porque no hay botones configurados")
            buttons = [{
                "id": "default",
                "label": "Abrir Ticket",
                "emoji": "🎫",
                "style": 3,
                "name_format": "ticket-{id}"
            }]
        
        if len(buttons) == 1:
            print(f"Creando vista con un solo botón para el canal {channel_id}")
            
            class TicketView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=None)
                    
                    button_config = buttons[0]
                    button = discord.ui.Button(
                        style=discord.ButtonStyle(button_config.get("style", 3)),
                        label=button_config.get("label", "Abrir Ticket"),
                        emoji=button_config.get("emoji", "🎫"),
                        custom_id=f"ticket:open:{channel_id}:0"
                    )
                    self.add_item(button)
            
            return TicketView()
        
        else:
            print(f"Creando vista con múltiples botones ({len(buttons)}) para el canal {channel_id}")
            
            class TicketSelectView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=None)
                    
                    options = []
                    for i, button_config in enumerate(buttons):
                        options.append(
                            discord.SelectOption(
                                label=button_config.get("label", "Abrir Ticket"),
                                value=str(i),
                                emoji=button_config.get("emoji", "🎫"),
                                description=button_config.get("description", f"Abrir ticket de {button_config.get('label', 'soporte')}")
                            )
                        )
                    
                    self.select = discord.ui.Select(
                        placeholder="Selecciona un tipo de ticket",
                        options=options,
                        custom_id=f"ticket:open:{channel_id}"
                    )
                    self.add_item(self.select)
            
            return TicketSelectView()
        
    except Exception as e:
        print(f"Error al generar vista para tickets: {e}")
        import traceback
        traceback.print_exc()
        return None