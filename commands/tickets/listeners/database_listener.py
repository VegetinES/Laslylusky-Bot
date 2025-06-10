import discord
import asyncio
import json
from database.connection import firebase_db
from firebase_admin import db
from ..utils.preview import generate_preview, generate_ticket_view
from ..utils.helpers import find_and_delete_ticket_message
import threading

class TicketDatabaseListener:
    def __init__(self, bot):
        self.bot = bot
        self.listeners = {}
        self.processing_changes = set()
        self.loop = None
        
    def start_listening(self):
        try:
            self.loop = asyncio.get_event_loop()
            ref = firebase_db.get_reference()
            
            for guild in self.bot.guilds:
                guild_ref = ref.child(str(guild.id)).child('tickets')
                listener = guild_ref.listen(self._create_listener_callback(guild.id))
                self.listeners[guild.id] = listener
                print(f"Iniciado listener de tickets para guild {guild.id}")
        except Exception as e:
            print(f"Error al iniciar listeners de tickets: {e}")
    
    def stop_listening(self):
        try:
            for guild_id, listener in self.listeners.items():
                listener.close()
                print(f"Detenido listener de tickets para guild {guild_id}")
            self.listeners.clear()
        except Exception as e:
            print(f"Error al detener listeners de tickets: {e}")
    
    def add_guild_listener(self, guild_id):
        try:
            if guild_id in self.listeners:
                return
                
            if not self.loop:
                self.loop = asyncio.get_event_loop()
                
            ref = firebase_db.get_reference()
            guild_ref = ref.child(str(guild_id)).child('tickets')
            listener = guild_ref.listen(self._create_listener_callback(guild_id))
            self.listeners[guild_id] = listener
            print(f"Añadido listener de tickets para nueva guild {guild_id}")
        except Exception as e:
            print(f"Error al añadir listener para guild {guild_id}: {e}")
    
    def remove_guild_listener(self, guild_id):
        try:
            if guild_id in self.listeners:
                self.listeners[guild_id].close()
                del self.listeners[guild_id]
                print(f"Eliminado listener de tickets para guild {guild_id}")
        except Exception as e:
            print(f"Error al eliminar listener para guild {guild_id}: {e}")
    
    def _create_listener_callback(self, guild_id):
        def listener_callback(event):
            try:
                if self.loop and self.loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(
                        self._handle_database_change(guild_id, event), 
                        self.loop
                    )
                else:
                    print(f"No hay bucle de eventos disponible para guild {guild_id}")
            except Exception as e:
                print(f"Error en callback del listener para guild {guild_id}: {e}")
        return listener_callback
    
    async def _handle_database_change(self, guild_id, event):
        try:
            if event.event_type == 'put':
                await self._handle_put_event(guild_id, event)
            elif event.event_type == 'patch':
                await self._handle_patch_event(guild_id, event)
        except Exception as e:
            print(f"Error al manejar cambio en la base de datos para guild {guild_id}: {e}")
            import traceback
            traceback.print_exc()
    
    async def _handle_put_event(self, guild_id, event):
        try:
            path = event.path
            data = event.data
            
            if path == '/':
                if data is None:
                    return
                for channel_id, ticket_data in data.items():
                    change_key = f"{guild_id}_{channel_id}"
                    if change_key not in self.processing_changes:
                        self.processing_changes.add(change_key)
                        try:
                            await self._process_ticket_change(guild_id, channel_id, ticket_data)
                        finally:
                            self.processing_changes.discard(change_key)
            else:
                path_parts = path.strip('/').split('/')
                if len(path_parts) >= 1:
                    channel_id = path_parts[0]
                    change_key = f"{guild_id}_{channel_id}"
                    if change_key not in self.processing_changes:
                        self.processing_changes.add(change_key)
                        try:
                            await self._process_ticket_change(guild_id, channel_id, data)
                        finally:
                            self.processing_changes.discard(change_key)
        except Exception as e:
            print(f"Error en _handle_put_event: {e}")
    
    async def _handle_patch_event(self, guild_id, event):
        try:
            path = event.path
            data = event.data
            
            if data is None:
                return
                
            path_parts = path.strip('/').split('/')
            if len(path_parts) >= 1:
                channel_id = path_parts[0]
                change_key = f"{guild_id}_{channel_id}"
                if change_key not in self.processing_changes:
                    self.processing_changes.add(change_key)
                    try:
                        from ..utils.database import get_ticket_data
                        ticket_data = get_ticket_data(guild_id, channel_id)
                        if ticket_data:
                            await self._process_ticket_change(guild_id, channel_id, ticket_data)
                    finally:
                        self.processing_changes.discard(change_key)
        except Exception as e:
            print(f"Error en _handle_patch_event: {e}")
    
    async def _process_ticket_change(self, guild_id, channel_id, ticket_data):
        try:
            if not ticket_data or not isinstance(ticket_data, dict):
                return
            
            if ticket_data.get('__deleted', False):
                await self._handle_ticket_deletion(guild_id, channel_id)
                return
            
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                return
            
            channel = guild.get_channel(int(channel_id))
            if not channel:
                return
            
            print(f"Procesando cambio de ticket para guild {guild_id}, canal {channel_id}")
            
            from ..utils.database import get_ticket_data
            existing_config = get_ticket_data(guild_id, channel_id)
            
            is_new_ticket = not existing_config or existing_config.get('__deleted', False)
            
            await self._apply_channel_permissions(guild, channel, ticket_data)
            
            should_deploy = await self._should_deploy_message(guild_id, channel_id, ticket_data, is_new_ticket)
            if should_deploy:
                await self._deploy_ticket_message(guild, channel, ticket_data)
            
            print(f"Ticket procesado exitosamente para canal {channel_id}")
            
        except Exception as e:
            print(f"Error al procesar cambio de ticket: {e}")
            import traceback
            traceback.print_exc()
    
    async def _handle_ticket_deletion(self, guild_id, channel_id):
        try:
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                return
            
            channel = guild.get_channel(int(channel_id))
            if not channel:
                return
            
            print(f"Procesando eliminación de ticket para canal {channel_id}")
            
            message_deleted = await find_and_delete_ticket_message(
                channel, 
                self.bot.user.id,
                channel_id
            )
            
            if message_deleted:
                print(f"Mensaje de ticket eliminado para canal {channel_id}")
            else:
                print(f"No se encontró mensaje de ticket para eliminar en canal {channel_id}")
                
        except Exception as e:
            print(f"Error al manejar eliminación de ticket: {e}")
    
    async def _apply_channel_permissions(self, guild, channel, ticket_config):
        try:
            permissions = ticket_config.get("permissions", {})
            
            await channel.set_permissions(
                guild.default_role,
                view_channel=True,
                create_private_threads=False,
                send_messages_in_threads=True,
                manage_threads=False
            )
            
            for role_id in permissions.get("manage", {}).get("roles", []):
                role = guild.get_role(int(role_id))
                if role:
                    await channel.set_permissions(
                        role,
                        view_channel=True,
                        create_private_threads=True,
                        send_messages_in_threads=True,
                        manage_threads=True
                    )
            
            for user_id in permissions.get("manage", {}).get("users", []):
                try:
                    user = await guild.fetch_member(int(user_id))
                    if user:
                        await channel.set_permissions(
                            user,
                            view_channel=True,
                            create_private_threads=True,
                            send_messages_in_threads=True,
                            manage_threads=True
                        )
                except:
                    pass
            
            for role_id in permissions.get("view", {}).get("roles", []):
                role = guild.get_role(int(role_id))
                if role:
                    await channel.set_permissions(
                        role,
                        view_channel=True,
                        create_private_threads=False,
                        send_messages_in_threads=False,
                        manage_threads=False
                    )
            
            for user_id in permissions.get("view", {}).get("users", []):
                try:
                    user = await guild.fetch_member(int(user_id))
                    if user:
                        await channel.set_permissions(
                            user,
                            view_channel=True,
                            create_private_threads=False,
                            send_messages_in_threads=False,
                            manage_threads=False
                        )
                except:
                    pass
                    
            print(f"Permisos aplicados al canal {channel.id}")
            
        except Exception as e:
            print(f"Error al aplicar permisos del canal: {e}")
    
    async def _should_deploy_message(self, guild_id, channel_id, ticket_config, is_new_ticket):
        try:
            if is_new_ticket:
                return True
            
            return True
            
        except Exception as e:
            print(f"Error al determinar si desplegar mensaje: {e}")
            return False
    
    async def _deploy_ticket_message(self, guild, channel, ticket_config):
        try:
            existing_message = None
            async for message in channel.history(limit=100):
                if message.author.id == self.bot.user.id and message.components:
                    for row in message.components:
                        for component in row.children:
                            if component.custom_id and component.custom_id.startswith("ticket:open:"):
                                existing_message = message
                                break
                        if existing_message:
                            break
                if existing_message:
                    break
            
            message_config = ticket_config.get("open_message", {})
            message_config["VIEW_MODE"] = True
            
            preview = await generate_preview("open_message", message_config, guild)
            view = await generate_ticket_view(ticket_config, str(channel.id))
            
            if "VIEW_MODE" in message_config:
                del message_config["VIEW_MODE"]
            
            content = preview.get("content", "")
            if "**Mensaje para abrir tickets**" in content:
                content = content.replace("**Mensaje para abrir tickets**\n\n", "")
            
            if existing_message:
                try:
                    await existing_message.edit(
                        content=content,
                        embed=preview.get("embed"),
                        view=view
                    )
                    print(f"Mensaje de tickets actualizado en el canal {channel.id}")
                except Exception as edit_error:
                    print(f"Error al actualizar mensaje existente: {edit_error}")
                    try:
                        await existing_message.delete()
                        await channel.send(
                            content=content,
                            embed=preview.get("embed"),
                            view=view
                        )
                        print(f"Mensaje antiguo eliminado y nuevo mensaje enviado al canal {channel.id}")
                    except Exception as delete_error:
                        print(f"Error al eliminar mensaje existente: {delete_error}")
                        await channel.send(
                            content=content,
                            embed=preview.get("embed"),
                            view=view
                        )
                        print(f"No se pudo eliminar mensaje antiguo, nuevo mensaje enviado al canal {channel.id}")
            else:
                await channel.send(
                    content=content,
                    embed=preview.get("embed"),
                    view=view
                )
                print(f"Nuevo mensaje de tickets enviado al canal {channel.id}")
                
        except Exception as e:
            print(f"Error al desplegar mensaje de tickets: {e}")
            import traceback
            traceback.print_exc()