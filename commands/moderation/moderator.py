import discord
from discord import app_commands
from discord.ext import commands
import datetime
from typing import Union
import asyncio
from database.oracle import Oracle
from database.get import get_specific_field

class Moderador(commands.Cog):
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
    
    def create_paginated_embeds(self, base_embed, all_fields, fields_per_page=4):
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

    async def create_mod_stats_embed(self, ctx_or_interaction, moderator, guild_id):
        embed = discord.Embed(
            title=f"Estadísticas de Moderación - {moderator.display_name}",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        
        embed.set_thumbnail(url=moderator.display_avatar.url)
        embed.set_footer(text=f"ID: {moderator.id}")

        try:
            self.db.connect()
            try:
                guild_data = self.db._get_data()
            finally:
                self.db.close()
            
            if guild_id not in guild_data.get("guilds", {}):
                embed.description = "<:No:825734196256440340> No hay datos de moderación para este servidor." 
                return [embed]
            
            server_data = guild_data["guilds"].get(guild_id, {})
            mod_id = str(moderator.id)

            warn_count = 0
            ban_count = 0

            all_fields = []

            mod_warns = []
            mod_bans = []

            if "warns" in server_data:
                for user_id, warns in server_data["warns"].items():
                    for warn in warns:
                        if warn.get("mod") == mod_id:
                            warn_count += 1
                            target_user = await self.get_user_obj(ctx_or_interaction, int(user_id))
                            target_name = target_user.display_name if target_user else f"Usuario {user_id}"
                            
                            mod_warns.append({
                                "id": warn.get("id"),
                                "user_id": user_id,
                                "user_name": target_name,
                                "reason": warn.get("razón", "No especificada"),
                                "date": warn.get("fecha", 0)
                            })

            if "bans" in server_data:
                for user_id, ban in server_data["bans"].items():
                    if ban.get("mod") == mod_id:
                        ban_count += 1
                        target_user = await self.get_user_obj(ctx_or_interaction, int(user_id))
                        target_name = target_user.display_name if target_user else f"Usuario {user_id}"
                        
                        mod_bans.append({
                            "user_id": user_id,
                            "user_name": target_name,
                            "reason": ban.get("razón", "No especificada"),
                            "date": ban.get("fecha", 0)
                        })

            total_actions = warn_count + ban_count

            all_fields.append({
                "name": "Total de Acciones",
                "value": f"`{total_actions}` acciones aplicadas",
                "inline": False
            })
            
            all_fields.append({
                "name": "<:warn:1344814055713406977> Advertencias",
                "value": f"`{warn_count}` warns aplicados",
                "inline": True
            })
            
            all_fields.append({
                "name": "<:ban:1344768257646661684> Baneos",
                "value": f"`{ban_count}` baneos aplicados",
                "inline": True
            })

            if mod_warns or mod_bans:
                all_fields.append({
                    "name": "Infracciones Aplicadas",
                    "value": "A continuación se muestran las infracciones aplicadas por este moderador:",
                    "inline": False
                })

            mod_warns.sort(key=lambda x: x["date"], reverse=True)

            if mod_warns:
                all_fields.append({
                    "name": f"Advertencias Aplicadas ({len(mod_warns)})",
                    "value": "Lista de advertencias aplicadas por este moderador:",
                    "inline": False
                })
                
                for warn in mod_warns:
                    warn_date = datetime.datetime.fromtimestamp(warn["date"])
                    discord_timestamp = f"<t:{int(warn_date.timestamp())}:F>"
                    
                    warn_text = f"**Usuario:** <@{warn['user_id']}> [{warn['user_id']}]\n"
                    warn_text += f"**Fecha:** {discord_timestamp}\n"
                    warn_text += f"**Razón:**\n```\n{warn['reason']}\n```"
                    
                    all_fields.append({
                        "name": f"<:ID:839428824189763604> ID Warn: {warn['id']}",
                        "value": warn_text,
                        "inline": False
                    })

            mod_bans.sort(key=lambda x: x["date"], reverse=True)
            
            if mod_bans:
                all_fields.append({
                    "name": f"Baneos Aplicados ({len(mod_bans)})",
                    "value": "Lista de baneos aplicados por este moderador:",
                    "inline": False
                })
                
                for ban in mod_bans:
                    ban_date = datetime.datetime.fromtimestamp(ban["date"])
                    discord_timestamp = f"<t:{int(ban_date.timestamp())}:F>"
                    
                    ban_text = f"**Usuario:** <@{ban['user_id']}> [{ban['user_id']}]\n"
                    ban_text += f"**Fecha:** {discord_timestamp}\n"
                    ban_text += f"**Razón:**\n```\n{ban['reason']}\n```"
                    
                    all_fields.append({
                        "name": f"<:ban:1344768257646661684> Ban a {ban['user_name']}",
                        "value": ban_text,
                        "inline": False
                    })
            
            if not mod_warns and not mod_bans:
                all_fields.append({
                    "name": "Sin Infracciones",
                    "value": "Este moderador no ha aplicado ninguna infracción todavía.",
                    "inline": False
                })

            if len(all_fields) > 4:
                summary_fields = all_fields[:3]

                if len(all_fields) > 3 and "Infracciones Aplicadas" in all_fields[3]["name"]:
                    summary_fields.append(all_fields[3])
                    infractions_fields = all_fields[4:]
                else:
                    infractions_fields = all_fields[3:]

                base_embed = discord.Embed(
                    title=embed.title,
                    color=embed.color,
                    timestamp=embed.timestamp
                )
                base_embed.set_thumbnail(url=embed.thumbnail.url)
                base_embed.set_footer(text=f"ID: {moderator.id}")
                
                for field in summary_fields:
                    base_embed.add_field(name=field["name"], value=field["value"], inline=field["inline"])

                return self.create_paginated_embeds(base_embed, infractions_fields, fields_per_page=4)

            for field in all_fields:
                embed.add_field(name=field["name"], value=field["value"], inline=field["inline"])
            
            return [embed]
            
        except Exception as e:
            embed.description = f"<:No:825734196256440340> Error al obtener estadísticas: {str(e)}"
            return [embed]

    async def check_moderator_permissions(self, ctx):
        perms_data = get_specific_field(ctx.guild.id, "perms")
        if not perms_data:
            return False

        user_id = str(ctx.author.id)
        if (user_id in perms_data.get("admin-users", []) or
            user_id in perms_data.get("mg-rl-user", []) or
            user_id in perms_data.get("mg-srv-users", []) or
            user_id in perms_data.get("kick-users", []) or
            user_id in perms_data.get("ban-users", []) or
            user_id in perms_data.get("mute-users", []) or
            user_id in perms_data.get("warn-users", [])):
            return True

        author_role_ids = [str(role.id) for role in ctx.author.roles]
        
        allowed_roles = []
        allowed_roles.extend(perms_data.get("admin-roles", []))
        allowed_roles.extend(perms_data.get("mg-rl-roles", []))
        allowed_roles.extend(perms_data.get("mg-srv-roles", []))
        allowed_roles.extend(perms_data.get("kick-roles", []))
        allowed_roles.extend(perms_data.get("ban-roles", []))
        allowed_roles.extend(perms_data.get("mute-roles", []))
        allowed_roles.extend(perms_data.get("warn-roles", []))
        
        return any(role_id in allowed_roles for role_id in author_role_ids)

    async def check_moderator_permissions_interaction(self, interaction):
        perms_data = get_specific_field(interaction.guild.id, "perms")
        if not perms_data:
            return False

        user_id = str(interaction.user.id)
        if (user_id in perms_data.get("admin-users", []) or
            user_id in perms_data.get("mg-rl-user", []) or
            user_id in perms_data.get("mg-srv-users", []) or
            user_id in perms_data.get("kick-users", []) or
            user_id in perms_data.get("ban-users", []) or
            user_id in perms_data.get("mute-users", []) or
            user_id in perms_data.get("unwarn-users", []) or
            user_id in perms_data.get("warn-users", [])):
            return True

        author_role_ids = [str(role.id) for role in interaction.user.roles]
        
        allowed_roles = []
        allowed_roles.extend(perms_data.get("admin-roles", []))
        allowed_roles.extend(perms_data.get("mg-rl-roles", []))
        allowed_roles.extend(perms_data.get("mg-srv-roles", []))
        allowed_roles.extend(perms_data.get("kick-roles", []))
        allowed_roles.extend(perms_data.get("ban-roles", []))
        allowed_roles.extend(perms_data.get("mute-roles", []))
        allowed_roles.extend(perms_data.get("unwarn-roles", []))
        allowed_roles.extend(perms_data.get("warn-roles", []))
        
        return any(role_id in allowed_roles for role_id in author_role_ids)
    
    @commands.command(name="moderador", aliases=["mod", "modstats"])
    async def moderador_prefix(self, ctx, moderador: Union[discord.Member, discord.User, str] = None):
        if isinstance(ctx.channel, discord.DMChannel):
            return

        has_permission = (
            ctx.author.guild_permissions.administrator or
            ctx.author.guild_permissions.ban_members or
            ctx.author.guild_permissions.kick_members or
            ctx.author.guild_permissions.manage_roles or
            ctx.author.guild_permissions.moderate_members or
            ctx.author.guild_permissions.manage_guild or
            await self.check_moderator_permissions(ctx)
        )
        
        if not has_permission:
            embed = discord.Embed(
                title="**No tienes permiso para usar este comando**",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if moderador is None:
            moderador = ctx.author
        
        if isinstance(moderador, str):
            try:
                if moderador.startswith('<@') and moderador.endswith('>'):
                    moderador = moderador.replace('<@', '').replace('>', '').replace('!', '')
                
                user_id = int(moderador)
                user = await self.get_user_obj(ctx, user_id)
                
                if user is None:
                    await ctx.send("<:No:825734196256440340> No se pudo encontrar al usuario.")
                    return
            except ValueError:
                await ctx.send("<:No:825734196256440340> ID de usuario inválido.")
                return
        else:
            user = moderador
        
        guild_id = str(ctx.guild.id)
        
        try:
            embeds = await self.create_mod_stats_embed(ctx, user, guild_id)
            
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
            await ctx.send(f"<:No:825734196256440340> Error al obtener estadísticas: {str(e)}") 
    
    @app_commands.command(name="moderador", description="Muestra las estadísticas de moderación de un usuario")
    @app_commands.describe(moderator="El moderador del que quieres ver las estadísticas")
    async def moderador_slash(self, interaction: discord.Interaction, moderator: discord.User = None):
        has_permission = (
            interaction.user.guild_permissions.administrator or
            interaction.user.guild_permissions.ban_members or
            interaction.user.guild_permissions.kick_members or
            interaction.user.guild_permissions.manage_roles or
            interaction.user.guild_permissions.moderate_members or
            interaction.user.guild_permissions.manage_guild or
            await self.check_moderator_permissions_interaction(interaction)
        )
        
        if not has_permission:
            await interaction.response.send_message("No tienes permisos para usar este comando.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        if moderator is None:
            moderator = interaction.user

        guild_id = str(interaction.guild.id)
        
        try:
            embeds = await self.create_mod_stats_embed(interaction, moderator, guild_id)

            if len(embeds) == 1:
                await interaction.followup.send(embed=embeds[0])
                return

            class ModeratorPagination(discord.ui.View):
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
            
            view = ModeratorPagination(embeds)
            
            message = await interaction.followup.send(embed=embeds[0], view=view)
            
            view.message = message
            
        except Exception as e:
            await interaction.followup.send(f"<:No:825734196256440340> Error al obtener estadísticas: {str(e)}")

async def setup(bot):
    await bot.add_cog(Moderador(bot))