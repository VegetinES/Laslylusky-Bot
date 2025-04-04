import discord
from datetime import datetime
import traceback
from .configdata_logs_preview import create_preview
import os

class LogsListView(discord.ui.View):
    def __init__(self, author_id, guild_data):
        super().__init__(timeout=180)
        self.author_id = author_id
        self.guild_data = guild_data
        
        options = []
        log_types = {
            "ban": "Logs de baneos",
            "kick": "Logs de expulsiones",
            "unban": "Logs de desbaneos",
            "enter": "Logs de entradas",
            "leave": "Logs de salidas",
            "del_msg": "Logs de mensajes eliminados",
            "edited_msg": "Logs de mensajes editados",
            "warn": "Logs de advertencias",
            "unwarn": "Logs de eliminación de advertencias"
        }
        
        for log_key, log_name in log_types.items():
            if log_key in guild_data.get("audit_logs", {}):
                log_config = guild_data["audit_logs"][log_key]
                status = "✅" if log_config.get("activated", False) else "❌"
                
                channel_id = log_config.get("log_channel", 0)
                has_channel = channel_id != 0 and channel_id is not None
                channel_status = "📢" if has_channel else "🔕"
                
                message_config = log_config.get("message", {})
                has_message = False
                if message_config:
                    if message_config.get("embed", False):
                        has_message = bool(message_config.get("description", ""))
                    else:
                        has_message = bool(message_config.get("message", ""))
                
                message_status = "📝" if has_message else "❓"
                
                options.append(
                    discord.SelectOption(
                        label=f"{log_name}",
                        value=log_key,
                        description=f"Estado: {status} | Canal: {channel_status} | Mensaje: {message_status}",
                        emoji="📋"
                    )
                )

        options.append(
            discord.SelectOption(
                label="Volver atrás",
                value="back",
                description="Volver al menú principal",
                emoji="⬅️"
            )
        )
        options.append(
            discord.SelectOption(
                label="Cancelar",
                value="cancel",
                description="Cancelar visualización",
                emoji="❌"
            )
        )
        
        self.logs_select = discord.ui.Select(
            placeholder="Selecciona un tipo de log",
            options=options
        )
        self.logs_select.callback = self.logs_select_callback
        self.add_item(self.logs_select)
    
    async def interaction_check(self, interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Solo la persona que ejecutó el comando puede usar estos controles.",
                ephemeral=True
            )
            return False
        return True
    
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        
        try:
            await self.message.edit(view=self)
        except:
            pass
    
    async def logs_select_callback(self, interaction):
        selection = self.logs_select.values[0]
        
        if selection == "back":
            from .configdata import ConfigDataMainView
            view = ConfigDataMainView(self.author_id, self.guild_data, interaction)
            await interaction.response.edit_message(
                content="Selecciona qué información quieres ver:",
                view=view,
                embeds=[]
            )
        elif selection == "cancel":
            for child in self.children:
                child.disabled = True
            
            await interaction.response.edit_message(
                content="Visualización de datos cancelada.",
                view=self,
                embeds=[]
            )
            self.stop()
        else:
            try:
                log_config = self.guild_data["audit_logs"][selection]

                detail_embed = await create_log_detail_embed(selection, log_config, interaction)

                preview_data = await create_preview(selection, log_config.get("message", {}), interaction.guild)
                
                embeds = []
                
                if preview_data.get("embed"):
                    embeds.append(preview_data["embed"])
                
                embeds.append(detail_embed)
                
                view = LogBackView(self.author_id, self.guild_data)
                
                content = None
                if not log_config.get("message", {}).get("embed", False) and log_config.get("message", {}).get("message"):
                    content = preview_data.get("content", "Vista previa del mensaje:")
                
                await interaction.response.edit_message(
                    content=content,
                    embeds=embeds,
                    view=view
                )
            except Exception as e:
                error_trace = traceback.format_exc()
                print(f"Error al mostrar la vista previa del log: {e}\n{error_trace}")
                
                error_embed = discord.Embed(
                    title="❌ Error al mostrar vista previa",
                    description=f"Se produjo un error al procesar la configuración del log:\n```\n{str(e)}\n```",
                    color=discord.Color.red()
                )
                
                await interaction.response.edit_message(
                    content="No se pudo generar la vista previa correctamente.",
                    embeds=[error_embed],
                    view=LogBackView(self.author_id, self.guild_data)
                )

class LogBackView(discord.ui.View):
    def __init__(self, author_id, guild_data):
        super().__init__(timeout=180)
        self.author_id = author_id
        self.guild_data = guild_data

        self.back_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Volver atrás",
            custom_id="back_log"
        )
        self.back_button.callback = self.back_callback
        self.add_item(self.back_button)

        self.cancel_button = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="Cancelar",
            custom_id="cancel_log"
        )
        self.cancel_button.callback = self.cancel_callback
        self.add_item(self.cancel_button)
    
    async def interaction_check(self, interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Solo la persona que ejecutó el comando puede usar estos controles.",
                ephemeral=True
            )
            return False
        return True
    
    async def back_callback(self, interaction):
        view = LogsListView(self.author_id, self.guild_data)
        await interaction.response.edit_message(
            content="Selecciona el tipo de log a visualizar:",
            view=view,
            embeds=[]
        )
    
    async def cancel_callback(self, interaction):
        for child in self.children:
            child.disabled = True
        
        await interaction.response.edit_message(
            content="Visualización de datos cancelada.",
            view=self,
            embeds=[]
        )
        self.stop()

async def create_log_detail_embed(log_type, log_config, interaction):
    log_names = {
        "ban": "Logs de baneos",
        "kick": "Logs de expulsiones",
        "unban": "Logs de desbaneos",
        "enter": "Logs de entradas",
        "leave": "Logs de salidas",
        "del_msg": "Logs de mensajes eliminados",
        "edited_msg": "Logs de mensajes editados",
        "warn": "Logs de advertencias",
        "unwarn": "Logs de eliminación de advertencias"
    }
    
    embed = discord.Embed(
        title=f"📋 Configuración de {log_names[log_type]}",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    is_activated = log_config.get("activated", False)
    embed.add_field(
        name="Estado",
        value="✅ Activado" if is_activated else "❌ Desactivado",
        inline=False
    )
    
    channel_id = log_config.get("log_channel", 0)
    channel = interaction.guild.get_channel(channel_id) if channel_id else None
    
    if channel:
        embed.add_field(
            name="Canal de logs",
            value=f"✅ Configurado: {channel.mention} (ID: {channel_id})",
            inline=False
        )
    else:
        embed.add_field(
            name="Canal de logs",
            value="❌ No configurado",
            inline=False
        )
    
    message_config = log_config.get("message", {})
    
    if not message_config:
        embed.add_field(
            name="Configuración de mensaje",
            value="❌ No hay configuración de mensaje",
            inline=False
        )
    else:
        if message_config.get("embed", False):
            embed.add_field(
                name="Tipo de mensaje",
                value="✅ Embed",
                inline=False
            )
            
            if message_config.get("title"):
                embed.add_field(
                    name="Título",
                    value=f"```{message_config['title']}```",
                    inline=False
                )
            
            if message_config.get("description"):
                embed.add_field(
                    name="Descripción",
                    value=f"```{message_config['description'][:500]}{'...' if len(message_config['description']) > 500 else ''}```",
                    inline=False
                )
            
            if message_config.get("footer"):
                embed.add_field(
                    name="Footer",
                    value=f"```{message_config['footer']}```",
                    inline=False
                )
            
            if message_config.get("color"):
                embed.add_field(
                    name="Color",
                    value=f"`{message_config['color'].capitalize()}`",
                    inline=True
                )
            
            if message_config.get("thumbnail", {}).get("has", False):
                embed.add_field(
                    name="Thumbnail",
                    value=f"✅ `{message_config['thumbnail']['param']}`",
                    inline=True
                )
            
            if message_config.get("image", {}).get("has", False):
                embed.add_field(
                    name="Imagen",
                    value=f"✅ `{message_config['image']['param']}`",
                    inline=True
                )
            
            fields = message_config.get("fields", {})
            field_count = 0
            if isinstance(fields, dict):
                field_count = len(fields)
            elif isinstance(fields, list):
                field_count = len([f for f in fields if f is not None and isinstance(f, dict)])
            
            if field_count > 0:
                embed.add_field(
                    name="Campos",
                    value=f"✅ `{field_count}` campos configurados",
                    inline=True
                )
        else:
            message = message_config.get("message", "")
            if message:
                embed.add_field(
                    name="Tipo de mensaje",
                    value="✅ Mensaje normal",
                    inline=False
                )
                embed.add_field(
                    name="Mensaje configurado",
                    value=f"```{message[:500]}{'...' if len(message) > 500 else ''}```",
                    inline=False
                )
            else:
                embed.add_field(
                    name="Configuración de mensaje",
                    value="❌ No hay mensaje configurado",
                    inline=False
                )
    
    is_configured = is_activated and channel and message_config and (
        (message_config.get("embed", False) and message_config.get("description")) or 
        (not message_config.get("embed", False) and message_config.get("message"))
    )
    
    embed.add_field(
        name="Estado general",
        value="✅ Completamente configurado" if is_configured else "⚠️ Configuración incompleta",
        inline=False
    )
    
    embed.set_footer(text=f"Solicitado por {interaction.user.name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
    return embed

async def show_logs_data(interaction, guild_data, author_id):
    try:
        view = LogsListView(author_id, guild_data)
        
        await interaction.response.edit_message(
            content="Selecciona el tipo de log a visualizar:",
            view=view,
            embeds=[]
        )
    except Exception as e:
        print(f"Error en show_logs_data: {e}")
        await interaction.response.send_message(
            f"Error al mostrar los datos de logs: {e}",
            ephemeral=True
        )