import discord
from discord import ui
import aiohttp
import io

class ChannelSelectView(ui.View):
    def __init__(self, main_view):
        super().__init__(timeout=1800)
        self.main_view = main_view
        self.selected_channel = None
        
        self.add_item(ChannelSelect(self))
    
    async def show(self, interaction):
        embed = discord.Embed(
            title="Seleccionar Canal",
            description="Selecciona el canal donde quieres enviar el mensaje.",
            color=discord.Color.blue()
        )
        
        await interaction.response.edit_message(
            content="Selecciona un canal de texto para enviar el mensaje:",
            embed=embed,
            view=self
        )
    
    @ui.button(label="Volver atrás", style=discord.ButtonStyle.secondary)
    async def go_back(self, interaction: discord.Interaction, button: ui.Button):
        await self.main_view.update_message(interaction)
    
    @ui.button(label="Confirmar envío", style=discord.ButtonStyle.success, disabled=True)
    async def confirm_send(self, interaction: discord.Interaction, button: ui.Button):
        if not self.selected_channel:
            await interaction.response.send_message("Primero selecciona un canal.", ephemeral=True)
            return
        
        try:
            await interaction.response.defer(ephemeral=True)
            
            files = []
            if self.main_view.attachments and not self.main_view.message_id:
                async with aiohttp.ClientSession() as session:
                    for i, url in enumerate(self.main_view.attachments):
                        try:
                            async with session.get(url) as resp:
                                if resp.status == 200:
                                    data = await resp.read()
                                    filename = f"image_{i+1}.png"
                                    files.append(discord.File(io.BytesIO(data), filename=filename))
                        except Exception as e:
                            print(f"Error al descargar imagen {url}: {e}")
            
            if self.main_view.message_id:
                try:
                    message = await self.selected_channel.fetch_message(int(self.main_view.message_id))
                    if message.author.id == self.main_view.bot.user.id:
                        await message.edit(content=self.main_view.content, embeds=self.main_view.embeds)
                        await interaction.followup.send(f"Mensaje con ID {self.main_view.message_id} editado exitosamente en {self.selected_channel.mention}.", ephemeral=True)
                    else:
                        await interaction.followup.send("No puedo editar un mensaje que no fue enviado por mí.", ephemeral=True)
                except discord.NotFound:
                    await interaction.followup.send("No se encontró el mensaje especificado.", ephemeral=True)
                except Exception as e:
                    await interaction.followup.send(f"Error al editar el mensaje: {str(e)}", ephemeral=True)
            else:
                message = await self.selected_channel.send(content=self.main_view.content, embeds=self.main_view.embeds, files=files)
                await interaction.followup.send(f"Mensaje enviado exitosamente a {self.selected_channel.mention}. ID del mensaje: {message.id}", ephemeral=True)
            
            for file in files:
                file.close()
                
        except Exception as e:
            await interaction.followup.send(f"Error al enviar el mensaje: {str(e)}", ephemeral=True)

class ChannelSelect(ui.ChannelSelect):
    def __init__(self, view):
        super().__init__(
            placeholder="Selecciona un canal de texto...",
            channel_types=[discord.ChannelType.text]
        )
        self.channel_view = view
    
    async def callback(self, interaction: discord.Interaction):
        selected_channel_obj = self.values[0]
        real_channel = interaction.guild.get_channel(selected_channel_obj.id)
        
        if not real_channel:
            await interaction.response.send_message("No se pudo acceder al canal seleccionado.", ephemeral=True)
            return
        
        self.channel_view.selected_channel = real_channel
        
        for item in self.channel_view.children:
            if isinstance(item, ui.Button) and item.label == "Confirmar envío":
                item.disabled = False
                break
        
        embed = discord.Embed(
            title="Canal Seleccionado",
            description=f"El mensaje se enviará a {real_channel.mention}",
            color=discord.Color.green()
        )
        
        await interaction.response.edit_message(
            content=f"Canal seleccionado: {real_channel.mention}",
            embed=embed,
            view=self.channel_view
        )