import discord
import asyncio
import json
from database.connection import mongo_db
from database.get import get_specific_field
from ..utils.preview import generate_preview, generate_ticket_view
from ..utils.helpers import find_and_delete_ticket_message
import threading
import time

class TicketDatabaseListener:
    def __init__(self, bot):
        self.bot = bot
        self.processing_changes = set()
        self._shutdown = False
        self._ready = False
        
    def start_listening(self):
        try:
            self._ready = True
            print("Ticket listener iniciado (modo bajo demanda)")
        except Exception as e:
            print(f"Error al iniciar listeners de tickets: {e}")
            import traceback
            traceback.print_exc()
    
    def stop_listening(self):
        try:
            self._shutdown = True
            self._ready = False
            print("Ticket listener detenido")
        except Exception as e:
            print(f"Error al detener listeners de tickets: {e}")
    
    def add_guild_listener(self, guild_id):
        try:
            print(f"Guild {guild_id} registrado para tickets (modo bajo demanda)")
        except Exception as e:
            print(f"Error al añadir listener para guild {guild_id}: {e}")
    
    def remove_guild_listener(self, guild_id):
        try:
            print(f"Guild {guild_id} removido del sistema de tickets")
        except Exception as e:
            print(f"Error al eliminar listener para guild {guild_id}: {e}")
    
    async def process_ticket_change(self, guild_id, channel_id, ticket_data):
        try:
            change_key = f"{guild_id}_{channel_id}"
            if change_key in self.processing_changes:
                print(f"[PROCESS] Ya se está procesando el ticket {change_key}, omitiendo")
                return
                
            self.processing_changes.add(change_key)
            try:
                await self._process_ticket_change(guild_id, channel_id, ticket_data)
            finally:
                self.processing_changes.discard(change_key)
        except Exception as e:
            print(f"Error al procesar cambio de ticket: {e}")
            import traceback
            traceback.print_exc()
    
    async def process_ticket_deletion(self, guild_id, channel_id):
        try:
            change_key = f"{guild_id}_{channel_id}_delete"
            if change_key in self.processing_changes:
                print(f"[DELETE] Ya se está procesando la eliminación del ticket {change_key}, omitiendo")
                return
                
            self.processing_changes.add(change_key)
            try:
                await self._handle_ticket_deletion(guild_id, channel_id)
            finally:
                self.processing_changes.discard(change_key)
        except Exception as e:
            print(f"Error al procesar eliminación de ticket: {e}")
            import traceback
            traceback.print_exc()
    
    async def _process_ticket_change(self, guild_id, channel_id, ticket_data):
        try:
            print(f"[PROCESS] Procesando cambios para guild {guild_id}, canal {channel_id}")
            
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
            
            await self._apply_channel_permissions(guild, channel, ticket_data)
            
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