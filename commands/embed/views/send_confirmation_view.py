import discord
from discord import ui
import aiohttp
import io

class WebhookConfirmationView(ui.View):
    def __init__(self, main_view):
        super().__init__(timeout=1800)
        self.main_view = main_view
    
    async def show(self, interaction):
        try:
            webhook_info = await self.get_webhook_info()
            
            embed = discord.Embed(
                title="Confirmar Envío por Webhook",
                color=discord.Color.blue()
            )
            
            if webhook_info:
                webhook_text = f"**Nombre:** {webhook_info['name']}"
                
                if webhook_info['channel_name'] != "desconocido":
                    webhook_text += f"\n**Canal:** #{webhook_info['channel_name']}"
                else:
                    webhook_text += f"\n**Canal ID:** {webhook_info['channel_id']}"
                
                if webhook_info['guild_name'] != "desconocido":
                    webhook_text += f"\n**Servidor:** {webhook_info['guild_name']}"
                else:
                    webhook_text += f"\n**Servidor ID:** {webhook_info['guild_id']}"
                
                embed.add_field(
                    name="Webhook",
                    value=webhook_text,
                    inline=False
                )
                
                if webhook_info['avatar']:
                    embed.set_thumbnail(url=webhook_info['avatar'])
            else:
                embed.add_field(
                    name="Webhook",
                    value="Webhook configurado (no se pudo obtener información detallada)",
                    inline=False
                )
            
            if self.main_view.webhook_name:
                embed.add_field(
                    name="Nombre personalizado",
                    value=self.main_view.webhook_name,
                    inline=True
                )
            
            if self.main_view.webhook_avatar:
                embed.add_field(
                    name="Avatar personalizado",
                    value="Configurado",
                    inline=True
                )
            
            if self.main_view.message_id:
                embed.add_field(
                    name="Acción",
                    value=f"Editar mensaje ID: {self.main_view.message_id}",
                    inline=False
                )
            else:
                embed.add_field(
                    name="Acción",
                    value="Enviar nuevo mensaje",
                    inline=False
                )
            
            await interaction.response.edit_message(
                content="¿Confirmas el envío del mensaje a través del webhook?",
                embed=embed,
                view=self
            )
            
        except Exception as e:
            print(f"Error al mostrar confirmación de webhook: {e}")
            embed = discord.Embed(
                title="Confirmar Envío por Webhook",
                description="¿Confirmas el envío del mensaje a través del webhook configurado?",
                color=discord.Color.blue()
            )
            
            await interaction.response.edit_message(
                content="¿Confirmas el envío del mensaje a través del webhook?",
                embed=embed,
                view=self
            )
    
    async def get_webhook_info(self):
        try:
            async with aiohttp.ClientSession() as session:
                webhook_id = self.main_view.webhook_url.split('/')[-2]
                webhook_token = self.main_view.webhook_url.split('/')[-1]
                
                headers = {'Authorization': f'Bot {self.main_view.bot.http.token}'}
                
                async with session.get(f'https://discord.com/api/v10/webhooks/{webhook_id}', headers=headers) as resp:
                    if resp.status == 200:
                        webhook_data = await resp.json()
                        
                        channel_id = webhook_data.get('channel_id')
                        guild_id = webhook_data.get('guild_id')
                        
                        channel_name = "desconocido"
                        guild_name = "desconocido"
                        
                        if channel_id:
                            channel = self.main_view.bot.get_channel(int(channel_id))
                            if channel:
                                channel_name = channel.name
                        
                        if guild_id:
                            guild = self.main_view.bot.get_guild(int(guild_id))
                            if guild:
                                guild_name = guild.name
                        
                        return {
                            'name': webhook_data.get('name', 'Webhook'),
                            'avatar': f"https://cdn.discordapp.com/avatars/{webhook_data['id']}/{webhook_data['avatar']}.png" if webhook_data.get('avatar') else None,
                            'channel_name': channel_name,
                            'guild_name': guild_name,
                            'channel_id': channel_id,
                            'guild_id': guild_id
                        }
                    else:
                        webhook = discord.Webhook.from_url(self.main_view.webhook_url, session=session)
                        webhook_data = await webhook.fetch()
                        
                        try:
                            async with session.get(f'https://discord.com/api/v10/webhooks/{webhook_id}/{webhook_token}') as resp:
                                if resp.status == 200:
                                    webhook_info = await resp.json()
                                    channel_id = webhook_info.get('channel_id')
                                    guild_id = webhook_info.get('guild_id')
                                else:
                                    channel_id = None
                                    guild_id = None
                        except:
                            channel_id = None
                            guild_id = None
                        
                        channel_name = "desconocido"
                        guild_name = "desconocido"
                        
                        if channel_id:
                            channel = self.main_view.bot.get_channel(int(channel_id))
                            if channel:
                                channel_name = channel.name
                        
                        if guild_id:
                            guild = self.main_view.bot.get_guild(int(guild_id))
                            if guild:
                                guild_name = guild.name
                        
                        return {
                            'name': webhook_data.name,
                            'avatar': webhook_data.display_avatar.url if webhook_data.display_avatar else None,
                            'channel_name': channel_name,
                            'guild_name': guild_name,
                            'channel_id': channel_id,
                            'guild_id': guild_id
                        }
        except Exception as e:
            print(f"Error al obtener información del webhook: {e}")
            return None
    
    @ui.button(label="Volver atrás", style=discord.ButtonStyle.secondary)
    async def go_back(self, interaction: discord.Interaction, button: ui.Button):
        await self.main_view.update_message(interaction)
    
    @ui.button(label="Confirmar envío", style=discord.ButtonStyle.success)
    async def confirm_send(self, interaction: discord.Interaction, button: ui.Button):
        try:
            await interaction.response.defer(ephemeral=True)
            
            async with aiohttp.ClientSession() as session:
                webhook = discord.Webhook.from_url(self.main_view.webhook_url, session=session)
                
                files = []
                if self.main_view.attachments and not self.main_view.message_id:
                    for i, url in enumerate(self.main_view.attachments):
                        try:
                            async with session.get(url) as resp:
                                if resp.status == 200:
                                    data = await resp.read()
                                    filename = f"image_{i+1}.png"
                                    files.append(discord.File(io.BytesIO(data), filename=filename))
                        except Exception as e:
                            print(f"Error al descargar imagen {url}: {e}")
                
                send_kwargs = {
                    'content': self.main_view.content,
                    'embeds': self.main_view.embeds
                }
                
                if self.main_view.webhook_name:
                    send_kwargs['username'] = self.main_view.webhook_name
                
                if self.main_view.webhook_avatar:
                    send_kwargs['avatar_url'] = self.main_view.webhook_avatar
                
                if not self.main_view.message_id:
                    send_kwargs['files'] = files
                
                if self.main_view.message_id:
                    await webhook.edit_message(self.main_view.message_id, **{k: v for k, v in send_kwargs.items() if k not in ['files', 'username', 'avatar_url']})
                    await interaction.followup.send(f"Mensaje con ID {self.main_view.message_id} editado exitosamente a través del webhook. Ten en cuenta que no se pueden modificar los adjuntos de un mensaje existente.", ephemeral=True)
                else:
                    send_kwargs['wait'] = True
                    message = await webhook.send(**send_kwargs)
                    await interaction.followup.send(f"Mensaje enviado exitosamente a través del webhook. ID del mensaje: {message.id}", ephemeral=True)
                
                for file in files:
                    file.close()
                
        except Exception as e:
            await interaction.followup.send(f"Error al enviar a través del webhook: {str(e)}", ephemeral=True)
    
    @ui.button(label="Cancelar", style=discord.ButtonStyle.danger)
    async def cancel_send(self, interaction: discord.Interaction, button: ui.Button):
        await self.main_view.update_message(interaction)