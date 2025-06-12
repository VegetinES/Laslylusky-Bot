import discord
import asyncio
import json
from database.connection import firebase_db
from firebase_admin import db
from ..utils.preview import generate_preview, generate_ticket_view
from ..utils.helpers import find_and_delete_ticket_message
import threading
import time

class TicketDatabaseListener:
    def __init__(self, bot):
        self.bot = bot
        self.listeners = {}
        self.processing_changes = set()
        self.event_loop = None
        self._shutdown = False
        self._ready = False
        
    def start_listening(self):
        try:
            self.event_loop = asyncio.get_event_loop()
            self._ready = True
            
            print(f"Event loop guardado: {self.event_loop}")
            
            ref = firebase_db.get_reference()
            
            for guild in self.bot.guilds:
                self._add_listener_for_guild(guild.id, ref)
                
            print(f"Iniciados {len(self.listeners)} listeners de tickets")
        except Exception as e:
            print(f"Error al iniciar listeners de tickets: {e}")
            import traceback
            traceback.print_exc()
    
    def _add_listener_for_guild(self, guild_id, ref=None):
        try:
            if guild_id in self.listeners:
                return
                
            if ref is None:
                ref = firebase_db.get_reference()
                
            guild_ref = ref.child(str(guild_id)).child('tickets')
            listener = guild_ref.listen(self._create_listener_callback(guild_id))
            self.listeners[guild_id] = listener
            print(f"Iniciado listener de tickets para guild {guild_id}")
        except Exception as e:
            print(f"Error al añadir listener para guild {guild_id}: {e}")
            import traceback
            traceback.print_exc()
    
    def stop_listening(self):
        try:
            self._shutdown = True
            self._ready = False
            for guild_id, listener in self.listeners.items():
                try:
                    listener.close()
                    print(f"Detenido listener de tickets para guild {guild_id}")
                except Exception as e:
                    print(f"Error al detener listener para guild {guild_id}: {e}")
            self.listeners.clear()
        except Exception as e:
            print(f"Error al detener listeners de tickets: {e}")
    
    def add_guild_listener(self, guild_id):
        try:
            if guild_id in self.listeners:
                return
                
            self._add_listener_for_guild(guild_id)
            print(f"Añadido listener de tickets para nueva guild {guild_id}")
        except Exception as e:
            print(f"Error al añadir listener para guild {guild_id}: {e}")
            import traceback
            traceback.print_exc()
    
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
            if self._shutdown or not self._ready:
                return
                
            try:
                print(f"[LISTENER] Evento recibido para guild {guild_id}: {event.event_type} en {event.path}")
                
                if not self.bot or self.bot.is_closed():
                    print(f"[LISTENER] Bot no disponible para guild {guild_id}")
                    return
                
                if not self.event_loop:
                    print(f"[LISTENER] Event loop no disponible para guild {guild_id}")
                    return
                
                if self.event_loop.is_closed():
                    print(f"[LISTENER] Event loop cerrado para guild {guild_id}")
                    return
                
                print(f"[LISTENER] Enviando tarea al event loop para guild {guild_id}")
                
                future = asyncio.run_coroutine_threadsafe(
                    self._handle_database_change(guild_id, event), 
                    self.event_loop
                )
                
                def on_done(fut):
                    try:
                        result = fut.result(timeout=1)
                        print(f"[LISTENER] Tarea completada para guild {guild_id}")
                    except asyncio.TimeoutError:
                        print(f"[LISTENER] Timeout procesando evento para guild {guild_id}")
                    except Exception as e:
                        print(f"[LISTENER] Error en future para guild {guild_id}: {e}")
                        import traceback
                        traceback.print_exc()
                
                future.add_done_callback(on_done)
                    
            except Exception as e:
                print(f"[LISTENER] Error en callback para guild {guild_id}: {e}")
                import traceback
                traceback.print_exc()
        
        return listener_callback
    
    async def _handle_database_change(self, guild_id, event):
        try:
            print(f"[HANDLER] Procesando evento {event.event_type} para guild {guild_id}")
            
            await asyncio.sleep(0.1)
            
            if event.event_type == 'put':
                await self._handle_put_event(guild_id, event)
            elif event.event_type == 'patch':
                await self._handle_patch_event(guild_id, event)
            else:
                print(f"[HANDLER] Tipo de evento no manejado: {event.event_type}")
                
        except Exception as e:
            print(f"[HANDLER] Error al manejar cambio en la base de datos para guild {guild_id}: {e}")
            import traceback
            traceback.print_exc()
    
    async def _handle_put_event(self, guild_id, event):
        try:
            path = event.path
            data = event.data
            
            print(f"[PUT] Path: {path}, Data type: {type(data)}")
            
            if path == '/':
                if data is None:
                    print(f"[PUT] Data es None para guild {guild_id}")
                    return
                    
                if isinstance(data, dict):
                    for channel_id, ticket_data in data.items():
                        change_key = f"{guild_id}_{channel_id}"
                        if change_key not in self.processing_changes:
                            self.processing_changes.add(change_key)
                            try:
                                await self._process_ticket_change(guild_id, channel_id, ticket_data)
                            finally:
                                self.processing_changes.discard(change_key)
                else:
                    print(f"[PUT] Data no es dict para guild {guild_id}: {type(data)}")
            else:
                path_parts = path.strip('/').split('/')
                if len(path_parts) >= 1:
                    channel_id = path_parts[0]
                    print(f"[PUT] Procesando cambio para canal {channel_id}")
                    change_key = f"{guild_id}_{channel_id}"
                    if change_key not in self.processing_changes:
                        self.processing_changes.add(change_key)
                        try:
                            if isinstance(data, dict):
                                await self._process_ticket_change(guild_id, channel_id, data)
                            else:
                                from ..utils.database import get_ticket_data
                                ticket_data = get_ticket_data(guild_id, channel_id)
                                if ticket_data:
                                    await self._process_ticket_change(guild_id, channel_id, ticket_data)
                        finally:
                            self.processing_changes.discard(change_key)
                            
        except Exception as e:
            print(f"[PUT] Error en _handle_put_event: {e}")
            import traceback
            traceback.print_exc()
    
    async def _handle_patch_event(self, guild_id, event):
        try:
            path = event.path
            data = event.data
            
            print(f"[PATCH] Path: {path}, Data: {data}")
            
            if data is None:
                print(f"[PATCH] Data es None para guild {guild_id}")
                return
                
            path_parts = path.strip('/').split('/')
            if len(path_parts) >= 1:
                channel_id = path_parts[0]
                print(f"[PATCH] Procesando patch para canal {channel_id}")
                change_key = f"{guild_id}_{channel_id}"
                if change_key not in self.processing_changes:
                    self.processing_changes.add(change_key)
                    try:
                        from ..utils.database import get_ticket_data
                        ticket_data = get_ticket_data(guild_id, channel_id)
                        if ticket_data:
                            await self._process_ticket_change(guild_id, channel_id, ticket_data)
                        else:
                            print(f"[PATCH] No se encontró ticket_data para canal {channel_id}")
                    finally:
                        self.processing_changes.discard(change_key)
                        
        except Exception as e:
            print(f"[PATCH] Error en _handle_patch_event: {e}")
            import traceback
            traceback.print_exc()
    
    async def _process_ticket_change(self, guild_id, channel_id, ticket_data):
        try:
            print(f"[PROCESS] Iniciando procesamiento para guild {guild_id}, canal {channel_id}")
            
            if not ticket_data or not isinstance(ticket_data, dict):
                print(f"[PROCESS] ticket_data inválido: {type(ticket_data)}")
                return
            
            if ticket_data.get('__deleted', False):
                print(f"[PROCESS] Ticket marcado como eliminado para canal {channel_id}")
                await self._handle_ticket_deletion(guild_id, channel_id)
                return
            
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                print(f"[PROCESS] Guild {guild_id} no encontrado")
                return
            
            channel = guild.get_channel(int(channel_id))
            if not channel:
                print(f"[PROCESS] Canal {channel_id} no encontrado en guild {guild_id}")
                return
            
            print(f"[PROCESS] Aplicando cambios de ticket para canal {channel.name} ({channel_id})")
            
            from ..utils.database import get_ticket_data
            existing_config = get_ticket_data(guild_id, channel_id)
            
            is_new_ticket = not existing_config or existing_config.get('__deleted', False)
            
            await self._apply_channel_permissions(guild, channel, ticket_data)
            
            should_deploy = await self._should_deploy_message(guild_id, channel_id, ticket_data, is_new_ticket)
            if should_deploy:
                await self._deploy_ticket_message(guild, channel, ticket_data)
            
            print(f"[PROCESS] Ticket procesado exitosamente para canal {channel_id}")
            
        except Exception as e:
            print(f"[PROCESS] Error al procesar cambio de ticket: {e}")
            import traceback
            traceback.print_exc()
    
    async def _handle_ticket_deletion(self, guild_id, channel_id):
        try:
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                print(f"[DELETE] Guild {guild_id} no encontrado")
                return
            
            channel = guild.get_channel(int(channel_id))
            if not channel:
                print(f"[DELETE] Canal {channel_id} no encontrado")
                return
            
            print(f"[DELETE] Procesando eliminación de ticket para canal {channel.name} ({channel_id})")
            
            message_deleted = await find_and_delete_ticket_message(
                channel, 
                self.bot.user.id,
                channel_id
            )
            
            if message_deleted:
                print(f"[DELETE] Mensaje de ticket eliminado para canal {channel_id}")
            else:
                print(f"[DELETE] No se encontró mensaje de ticket para eliminar en canal {channel_id}")
                
        except Exception as e:
            print(f"[DELETE] Error al manejar eliminación de ticket: {e}")
            import traceback
            traceback.print_exc()
    
    async def _apply_channel_permissions(self, guild, channel, ticket_config):
        try:
            print(f"[PERMS] Aplicando permisos al canal {channel.name}")
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
                    print(f"[PERMS] Permisos de gestión aplicados al rol {role.name}")
            
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
                        print(f"[PERMS] Permisos de gestión aplicados al usuario {user.display_name}")
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
                    print(f"[PERMS] Permisos de vista aplicados al rol {role.name}")
            
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
                        print(f"[PERMS] Permisos de vista aplicados al usuario {user.display_name}")
                except:
                    pass
                    
            print(f"[PERMS] Permisos aplicados exitosamente al canal {channel.id}")
            
        except Exception as e:
            print(f"[PERMS] Error al aplicar permisos del canal: {e}")
            import traceback
            traceback.print_exc()
    
    async def _should_deploy_message(self, guild_id, channel_id, ticket_config, is_new_ticket):
        try:
            print(f"[DEPLOY] Evaluando si desplegar mensaje - nuevo: {is_new_ticket}")
            return True
            
        except Exception as e:
            print(f"[DEPLOY] Error al determinar si desplegar mensaje: {e}")
            return False
    
    async def _deploy_ticket_message(self, guild, channel, ticket_config):
        try:
            print(f"[MESSAGE] Desplegando mensaje de tickets en {channel.name}")
            
            existing_message = None
            message_count = 0
            async for message in channel.history(limit=100):
                message_count += 1
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
            
            print(f"[MESSAGE] Revisados {message_count} mensajes, mensaje existente encontrado: {existing_message is not None}")
            
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
                    print(f"[MESSAGE] Mensaje de tickets actualizado en el canal {channel.id}")
                except Exception as edit_error:
                    print(f"[MESSAGE] Error al actualizar mensaje existente: {edit_error}")
                    try:
                        await existing_message.delete()
                        await channel.send(
                            content=content,
                            embed=preview.get("embed"),
                            view=view
                        )
                        print(f"[MESSAGE] Mensaje antiguo eliminado y nuevo mensaje enviado al canal {channel.id}")
                    except Exception as delete_error:
                        print(f"[MESSAGE] Error al eliminar mensaje existente: {delete_error}")
                        await channel.send(
                            content=content,
                            embed=preview.get("embed"),
                            view=view
                        )
                        print(f"[MESSAGE] No se pudo eliminar mensaje antiguo, nuevo mensaje enviado al canal {channel.id}")
            else:
                await channel.send(
                    content=content,
                    embed=preview.get("embed"),
                    view=view
                )
                print(f"[MESSAGE] Nuevo mensaje de tickets enviado al canal {channel.id}")
                
        except Exception as e:
            print(f"[MESSAGE] Error al desplegar mensaje de tickets: {e}")
            import traceback
            traceback.print_exc()