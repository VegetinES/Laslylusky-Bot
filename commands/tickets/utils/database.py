import discord
from database.get import get_server_data, get_specific_field
from database.update import update_server_data

def get_tickets_data(guild_id):
    if not guild_id:
        return {}
    
    server_data = get_server_data(guild_id)
    if not server_data or "tickets" not in server_data:
        return {}
    
    tickets_data = server_data.get("tickets", {})
    
    filtered_tickets = {}
    for ticket_id, ticket_data in tickets_data.items():
        if isinstance(ticket_data, dict) and not ticket_data.get("__deleted", False):
            filtered_tickets[ticket_id] = ticket_data
    
    return filtered_tickets

def get_ticket_data(guild_id, channel_id):
    tickets_data = get_tickets_data(guild_id)
    
    if not tickets_data or channel_id not in tickets_data:
        server_data = get_server_data(guild_id)
        if (server_data and "tickets" in server_data and 
            channel_id in server_data["tickets"] and
            isinstance(server_data["tickets"][channel_id], dict) and
            server_data["tickets"][channel_id].get("__deleted", False)):
            return None
        return None
    
    return tickets_data.get(channel_id, None)

async def save_ticket_config(guild_id, channel_id, ticket_config):
    try:
        server_data = get_server_data(guild_id)
        
        if not server_data:
            return False
        
        if "tickets" not in server_data:
            server_data["tickets"] = {}
        
        server_data["tickets"][channel_id] = ticket_config
        
        return update_server_data(guild_id, "tickets", server_data["tickets"])
    except Exception as e:
        print(f"Error al guardar configuración de ticket: {e}")
        return False

async def increment_ticket_counter(guild_id, channel_id):
    try:
        ticket_data = get_ticket_data(guild_id, channel_id)
        
        if not ticket_data:
            return 1
        
        current_count = ticket_data.get("auto_increment", 1)
        new_count = current_count + 1
        
        success = update_server_data(guild_id, f"tickets/{channel_id}/auto_increment", new_count)
        if not success:
            print(f"Error al actualizar el contador de tickets para {guild_id}/{channel_id}")
        
        return current_count
    except Exception as e:
        print(f"Error al incrementar contador de tickets: {e}")
        return 1

async def update_specific_ticket_counter(guild_id, channel_id, button_id, new_count):
    try:
        server_data = get_server_data(guild_id)
        
        if not server_data:
            return False
        
        if "tickets" not in server_data or channel_id not in server_data["tickets"]:
            return False
            
        ticket_data = server_data["tickets"][channel_id]
        
        if "auto_increment" not in ticket_data:
            ticket_data["auto_increment"] = {}
            
        ticket_data["auto_increment"][button_id] = new_count
        
        return update_server_data(guild_id, f"tickets/{channel_id}/auto_increment", ticket_data["auto_increment"])
    except Exception as e:
        print(f"Error al actualizar contador específico de tickets: {e}")
        return False

async def delete_ticket_config(guild_id, channel_id):
    try:
        from database.get import get_server_data, get_specific_field
        from database.update import update_server_data
        
        server_data = get_server_data(guild_id)
        
        if not server_data:
            return False
        
        if "tickets" not in server_data:
            return False
            
        if channel_id not in server_data["tickets"]:
            return False
        
        current_data = server_data["tickets"][channel_id]
        if isinstance(current_data, dict):
            current_data["__deleted"] = True
            success = update_server_data(guild_id, f"tickets/{channel_id}", current_data)
            return success
        else:
            return update_server_data(guild_id, f"tickets/{channel_id}", {"__deleted": True})
            
    except Exception as e:
        import traceback
        print(f"Error al eliminar configuración de ticket: {e}")
        print(traceback.format_exc())
        return False
