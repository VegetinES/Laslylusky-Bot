import discord
from discord import app_commands
from discord.ext import commands
import datetime
from typing import Union
import asyncio

from database.oracle import Oracle
from database.get import get_specific_field

class Infracciones(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Oracle()
    
    async def get_user_obj(self, ctx_or_interaction, user_id):
        try:
            user = self.bot.get_user(user_id)
            
            if user is None:
                try:
                    user = await self.bot.fetch_user(user_id)
                except discord.NotFound:
                    user = None
            
            return user
        except Exception as e:
            print(f"Error al obtener usuario: {e}")
            return None
    
    def create_paginated_embeds(self, base_embed, all_fields, fields_per_page=6):
        embeds = []
        total_fields = len(all_fields)
        total_pages = (total_fields + fields_per_page - 1) // fields_per_page
        
        for page in range(total_pages):
            embed = discord.Embed(
                title=base_embed.title,
                description=base_embed.description,
                color=base_embed.color,
                timestamp=base_embed.timestamp
            )
            
            if base_embed.thumbnail:
                embed.set_thumbnail(url=base_embed.thumbnail.url)
            if base_embed.footer:
                embed.set_footer(text=f"{base_embed.footer.text} • Página {page+1}/{total_pages}")
            
            start_idx = page * fields_per_page
            end_idx = min(start_idx + fields_per_page, total_fields)
            
            for i in range(start_idx, end_idx):
                field = all_fields[i]
                embed.add_field(name=field["name"], value=field["value"], inline=field["inline"])
            
            embeds.append(embed)
        
        return embeds

    async def create_infractions_embed(self, ctx_or_interaction, user, infractions_data):
        embed = discord.Embed(
            title=f"Infracciones de {user.display_name}",
            color=discord.Color.red(),
            timestamp=datetime.datetime.now()
        )
        
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"ID: {user.id}")
        
        if "error" in infractions_data:
            error_msg = infractions_data["error"]
            if f"No se encontraron infracciones para el usuario {user.id}" in error_msg:
                embed.description = f"No se encontraron infracciones para el usuario <@{user.id}>"
            else:
                embed.description = error_msg
            return [embed]
        
        all_fields = []
        
        if "warns" in infractions_data and infractions_data["warns"]:
            all_fields.append({
                "name": f"Advertencias ({len(infractions_data['warns'])})",
                "value": "",
                "inline": False
            })
            
            for warn in infractions_data["warns"]:
                mod_id = warn.get("mod")
                mod_user = await self.get_user_obj(ctx_or_interaction, int(mod_id)) if mod_id else None
                mod_name = mod_user.display_name if mod_user else f"Desconocido"
                
                warn_date = datetime.datetime.fromtimestamp(warn.get("fecha", 0))
                discord_timestamp = f"<t:{int(warn_date.timestamp())}:F>"
                
                warn_text = f"**Moderador:** <@{mod_id}> [{mod_id}]\n"
                warn_text += f"**Fecha sanción:** {discord_timestamp}\n"
                warn_text += f"**Razón:**\n```\n{warn.get('razón', 'No especificada')}\n```"
                
                all_fields.append({
                    "name": f"<:ID:839428824189763604> ID: {warn.get('id')}",
                    "value": warn_text,
                    "inline": True
                })
        else:
            all_fields.append({
                "name": "Advertencias",
                "value": "No tiene advertencias",
                "inline": False
            })
        
        if "bans" in infractions_data and infractions_data["bans"]:
            all_fields.append({
                "name": "<:ban:1344768257646661684> Ban Activo",
                "value": "",
                "inline": False
            })
            
            ban = infractions_data["bans"]
            mod_id = ban.get("mod")
            mod_user = await self.get_user_obj(ctx_or_interaction, int(mod_id)) if mod_id else None
            mod_name = mod_user.display_name if mod_user else f"Desconocido"
            
            ban_date = datetime.datetime.fromtimestamp(ban.get("fecha", 0))
            discord_timestamp = f"<t:{int(ban_date.timestamp())}:F>"
            
            ban_text = f"Moderador: <@{mod_id}> {mod_name} [{mod_id}]\n"
            ban_text += f"Fecha sanción: {discord_timestamp}\n"
            ban_text += f"Razón:\n```\n{ban.get('razón', 'No especificada')}\n```"
            
            all_fields.append({
                "name": "Ban",
                "value": ban_text,
                "inline": True
            })
        else:
            all_fields.append({
                "name": "Ban",
                "value": "No está baneado",
                "inline": False
            })
        
        if len(all_fields) > 6:
            return self.create_paginated_embeds(embed, all_fields)
        
        for field in all_fields:
            embed.add_field(name=field["name"], value=field["value"], inline=field["inline"])
        
        return [embed]
        
    @commands.command(name="infracciones", aliases=["infrs", "warns"])
    async def infracciones_prefix(self, ctx, usuario: Union[discord.Member, discord.User, str] = None):
        if isinstance(ctx.channel, discord.DMChannel):
            return
            
        act_commands = get_specific_field(ctx.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando </config update:1348059363834859584> si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if "infracciones" not in act_commands:
            await ctx.reply("El comando no está activado en este servidor.")
            return
        
        if usuario is None:
            await ctx.send("<:No:825734196256440340> Debes especificar un usuario.")
            return
        
        if isinstance(usuario, str):
            try:
                if usuario.startswith('<@') and usuario.endswith('>'):
                    usuario = usuario.replace('<@', '').replace('>', '').replace('!', '')
                
                user_id = int(usuario)
                user = await self.get_user_obj(ctx, user_id)
                
                if user is None:
                    await ctx.send("<:No:825734196256440340> No se pudo encontrar al usuario.")
                    return
            except ValueError:
                await ctx.send("<:No:825734196256440340> ID de usuario inválido.")
                return
        else:
            user = usuario
        
        guild_id = str(ctx.guild.id)
        user_id = str(user.id)
        
        try:
            self.db.connect()
            try:
                infractions = self.db.get(guild_id, user_id)
                embeds = await self.create_infractions_embed(ctx, user, infractions)
            finally:
                self.db.close()

            if len(embeds) == 1:
                await ctx.send(embed=embeds[0])
                return

            current_page = 0
            message = await ctx.send(embed=embeds[current_page])

            page_reactions = ['<:Flecha_izquierda:838688078758543360>', '<:Flecha_derecha:838687977948839966>']
            for reaction in page_reactions:
                await message.add_reaction(reaction)
            
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in page_reactions and reaction.message.id == message.id

            while True:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                    
                    if str(reaction.emoji) == '<:Flecha_izquierda:838688078758543360>':
                        if current_page > 0:
                            current_page -= 1
                            await message.edit(embed=embeds[current_page])
                    elif str(reaction.emoji) == '<:Flecha_derecha:838687977948839966>':
                        if current_page < len(embeds) - 1:
                            current_page += 1
                            await message.edit(embed=embeds[current_page])

                    try:
                        await message.remove_reaction(reaction.emoji, user)
                    except:
                        pass
                    
                except asyncio.TimeoutError:
                    try:
                        await message.clear_reactions()
                    except:
                        pass
                    break
        except Exception as e:
            await ctx.send(f"<:No:825734196256440340> Error al obtener infracciones: {str(e)}")
    
    @app_commands.command(name="infracciones", description="Muestra las infracciones de un usuario")
    @app_commands.describe(user="El usuario del que quieres ver las infracciones")
    async def infracciones_slash(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.defer()

        guild_id = str(interaction.guild.id)
        user_id = str(user.id)
        
        try:
            self.db.connect()
            try:
                infractions = self.db.get(guild_id, user_id)
                embeds = await self.create_infractions_embed(interaction, user, infractions)
            finally:
                self.db.close()

            if len(embeds) == 1:
                await interaction.followup.send(embed=embeds[0])
                return

            class InfractionsPagination(discord.ui.View):
                def __init__(self, embeds, *, timeout=60):
                    super().__init__(timeout=timeout)
                    self.embeds = embeds
                    self.current_page = 0
                    self.total_pages = len(embeds)

                    self.update_buttons()
                
                def update_buttons(self):
                    self.previous.disabled = self.current_page == 0
                    self.next.disabled = self.current_page == self.total_pages - 1
                
                @discord.ui.button(label="Anterior", style=discord.ButtonStyle.secondary, emoji="<:Flecha_izquierda:838688078758543360>")
                async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if self.current_page > 0:
                        self.current_page -= 1
                        self.update_buttons()
                        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
                    else:
                        await interaction.response.defer()
                
                @discord.ui.button(label="Siguiente", style=discord.ButtonStyle.primary, emoji="<:Flecha_derecha:838687977948839966>")
                async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if self.current_page < len(self.embeds) - 1:
                        self.current_page += 1
                        self.update_buttons()
                        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
                    else:
                        await interaction.response.defer()
                
                async def on_timeout(self):
                    self.previous.disabled = True
                    self.next.disabled = True

                    try:
                        await self.message.edit(view=self)
                    except:
                        pass

            view = InfractionsPagination(embeds)

            message = await interaction.followup.send(embed=embeds[0], view=view)

            view.message = message
            
        except Exception as e:
            await interaction.followup.send(f"<:No:825734196256440340> Error al obtener infracciones: {str(e)}")

async def setup(bot):
    await bot.add_cog(Infracciones(bot))