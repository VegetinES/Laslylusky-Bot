import traceback

async def find_and_delete_ticket_message(channel, bot_id, channel_id):
    try:
        print(f"Buscando mensaje de ticket en el canal {channel.id} para tickets del canal {channel_id}")
        
        async for message in channel.history(limit=200):
            if message.author.id == bot_id:
                if message.components:
                    for row in message.components:
                        for component in row.children:
                            if hasattr(component, 'custom_id') and component.custom_id:
                                custom_id = component.custom_id
                                if custom_id.startswith(f"ticket:open:{channel_id}") or custom_id == f"ticket:open:{channel_id}":
                                    print(f"Mensaje encontrado con ID {message.id}, intentando eliminar")
                                    await message.delete()
                                    print(f"Mensaje eliminado con éxito")
                                    return True
                
                if "Sistema de Tickets" in message.content or "ticket" in message.content.lower():
                    print(f"Posible mensaje de ticket encontrado con ID {message.id} basado en contenido")
                    if message.embeds:
                        for embed in message.embeds:
                            if embed.title and ("ticket" in embed.title.lower() or "Sistema de Tickets" == embed.title):
                                print(f"Embed de ticket confirmado, intentando eliminar mensaje")
                                await message.delete()
                                print(f"Mensaje eliminado con éxito")
                                return True
        
        print(f"No se encontró mensaje de ticket en el canal {channel.id}")
        return False
    except Exception as e:
        print(f"Error al buscar/eliminar mensaje de ticket: {e}")
        import traceback
        traceback.print_exc()
        return False