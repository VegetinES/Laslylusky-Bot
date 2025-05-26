import discord
from discord.ext import commands
from discord import app_commands, ui
from .help_data import COMMAND_CATEGORIES
import asyncio
from database.get import get_server_data

class LinkView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
        self.add_item(ui.Button(label="Invitación", emoji="<:invite:1372151068426764370>", url="https://discord.com/oauth2/authorize?client_id=784774864766500864&scope=bot%20applications.commands&permissions=8589803519", style=discord.ButtonStyle.link, row=0))
        self.add_item(ui.Button(label="Discord", emoji="<:discord:1372872707837792336>", url="https://discord.gg/DN6PDKA7gf", style=discord.ButtonStyle.link, row=0))
        self.add_item(ui.Button(label="Top.gg", emoji="<:top_gg:1372873107945295932>", url="https://top.gg/bot/784774864766500864", style=discord.ButtonStyle.link, row=0))
        
        self.add_item(ui.Button(label="Valorar", emoji="<:form:1372873504499830895>", url="https://forms.gle/pqeiSo1n1d49jD7M9", style=discord.ButtonStyle.link, row=1))
        self.add_item(ui.Button(label="Donar", emoji="<:paypal:1372873732535615528>", url="https://paypal.me/VegetinES", style=discord.ButtonStyle.link, row=1))
        self.add_item(ui.Button(label="GitHub", emoji="<:github:1372873958105284658>", url="https://github.com/VegetinES/Laslylusky-Bot", style=discord.ButtonStyle.link, row=1))

class CategorySelect(ui.Select):
    def __init__(self, bot, guild_id, is_nsfw):
        self.bot = bot
        self.guild_id = guild_id
        self.is_nsfw = is_nsfw
        
        options = [
            discord.SelectOption(
                label="Laslylusky",
                value="Laslylusky",
                emoji="<:laslylusky:1372143928899534901>",
                description="Comandos que pertenecen al bot"
            ),
            discord.SelectOption(
                label="Diversión y juegos",
                value="Diversión y juegos",
                emoji="<:games:1372144428814307408>",
                description="Comandos de diversión y juegos"
            ),
            discord.SelectOption(
                label="Moderación",
                value="Moderación",
                emoji="<:moderation:1372144807023218759>",
                description="Comandos para la moderación del servidor"
            ),
            discord.SelectOption(
                label="Configuración",
                value="Configuración",
                emoji="<:configuration:1372145859361243216>",
                description="Comandos para configurar al bot en el servidor"
            ),
            discord.SelectOption(
                label="Información",
                value="Información",
                emoji="<:Information:1372146141994549349>",
                description="Comandos de información del servidor/usuarios"
            ),
            discord.SelectOption(
                label="Utilidad",
                value="Utilidad",
                emoji="<:utilities:1372146639963295764>",
                description="Comandos útiles"
            ),
            discord.SelectOption(
                label="Minecraft",
                value="Minecraft",
                emoji="<:minecraft:1372146869370880132>",
                description="Comandos de Minecraft"
            )
        ]
        
        if is_nsfw:
            options.append(discord.SelectOption(
                label="NSFW",
                value="NSFW",
                emoji="<:nsfw:1372147128545316964>",
                description="Comandos NSFW"
            ))
        
        super().__init__(
            placeholder="Selecciona una categoría",
            min_values=1,
            max_values=1,
            options=options,
            row=0
        )

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        category_data = COMMAND_CATEGORIES.get(category)
        
        if not category_data:
            await interaction.response.send_message("Categoría no encontrada.", ephemeral=True)
            return
            
        server_commands = self.bot.get_cog("Help").get_server_commands(self.guild_id)
        active_commands = set(server_commands["active"])
        deactivated_commands = set(server_commands["deactivated"])
        
        command_list = []
        for cmd_name, cmd_info in category_data['commands'].items():
            if cmd_name in active_commands or cmd_name in deactivated_commands:
                status = "<:activated:1372145083863928902>" if cmd_name in active_commands else "<:deactivated:1372145097017397318>"
                command_list.append(
                    f"- **Comando `{cmd_name}` | {status}:**\n"
                    f"{cmd_info['description']}\n"
                    f"-# Comandos/s: {cmd_info['usage']}"
                )

        pages = [command_list[i:i+5] for i in range(0, len(command_list), 5)]
        current_page = 0
        
        embed = discord.Embed(
            title=f"{category_data['emoji']} {category} (Página 1/{len(pages) or 1})",
            description="\n\n".join(pages[current_page]) if pages else "No hay comandos en esta categoría",
            color=63272
        )
        
        if isinstance(interaction.user, discord.Member) and interaction.user.avatar:
            embed.set_footer(text=f"Pedido por: {interaction.user.display_name}", icon_url=interaction.user.avatar.url)
        else:
            embed.set_footer(text=f"Pedido por: {interaction.user.display_name}")
        
        if len(pages) > 1:
            view = PaginatedView(
                self.bot, 
                self.guild_id, 
                self.is_nsfw,
                pages, 
                category, 
                category_data['emoji'],
                interaction.user
            )
            await interaction.response.edit_message(embed=embed, view=view)
            view.message = await interaction.original_response()
        else:
            view = CategoryView(self.bot, self.guild_id, self.is_nsfw)
            await interaction.response.edit_message(embed=embed, view=view)
            view.message = await interaction.original_response()

class CategoryView(ui.View):
    def __init__(self, bot, guild_id, is_nsfw):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
        self.is_nsfw = is_nsfw
        self.message = None
        
        self.add_item(CategorySelect(bot, guild_id, is_nsfw))
        
        self.add_item(ui.Button(label="Invitación", emoji="<:invite:1372151068426764370>", url="https://discord.com/oauth2/authorize?client_id=784774864766500864&scope=bot%20applications.commands&permissions=8589803519", style=discord.ButtonStyle.link, row=1))
        self.add_item(ui.Button(label="Discord", emoji="<:discord:1372872707837792336>", url="https://discord.gg/DN6PDKA7gf", style=discord.ButtonStyle.link, row=1))
        self.add_item(ui.Button(label="Top.gg", emoji="<:top_gg:1372873107945295932>", url="https://top.gg/bot/784774864766500864", style=discord.ButtonStyle.link, row=1))
        
        self.add_item(ui.Button(label="Valorar", emoji="<:form:1372873504499830895>", url="https://forms.gle/pqeiSo1n1d49jD7M9", style=discord.ButtonStyle.link, row=2))
        self.add_item(ui.Button(label="Donar", emoji="<:paypal:1372873732535615528>", url="https://paypal.me/VegetinES", style=discord.ButtonStyle.link, row=2))
        self.add_item(ui.Button(label="GitHub", emoji="<:github:1372873958105284658>", url="https://github.com/VegetinES/Laslylusky-Bot", style=discord.ButtonStyle.link, row=2))
        
    async def on_timeout(self):
        if hasattr(self, 'message') and self.message is not None:
            for item in self.children:
                if not isinstance(item, ui.Button) or item.style != discord.ButtonStyle.link:
                    item.disabled = True
            try:
                await self.message.edit(view=self)
            except:
                pass

class PaginatedView(ui.View):
    def __init__(self, bot, guild_id, is_nsfw, pages, category, emoji, user):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
        self.is_nsfw = is_nsfw
        self.pages = pages
        self.category = category
        self.emoji = emoji
        self.user = user
        self.current_page = 0
        self.message = None
        self.has_navigation_buttons = False
        
        self.add_item(CategorySelect(self.bot, self.guild_id, self.is_nsfw))
        
        self.update_buttons()
        
        self.add_item(ui.Button(label="Invitación", emoji="<:invite:1372151068426764370>", url="https://discord.com/oauth2/authorize?client_id=784774864766500864&scope=bot%20applications.commands&permissions=8589803519", style=discord.ButtonStyle.link, row=2))
        self.add_item(ui.Button(label="Discord", emoji="<:discord:1372872707837792336>", url="https://discord.gg/DN6PDKA7gf", style=discord.ButtonStyle.link, row=2))
        self.add_item(ui.Button(label="Top.gg", emoji="<:top_gg:1372873107945295932>", url="https://top.gg/bot/784774864766500864", style=discord.ButtonStyle.link, row=2))
        
        self.add_item(ui.Button(label="Valorar", emoji="<:form:1372873504499830895>", url="https://forms.gle/pqeiSo1n1d49jD7M9", style=discord.ButtonStyle.link, row=3))
        self.add_item(ui.Button(label="Donar", emoji="<:paypal:1372873732535615528>", url="https://paypal.me/VegetinES", style=discord.ButtonStyle.link, row=3))
        self.add_item(ui.Button(label="GitHub", emoji="<:github:1372873958105284658>", url="https://github.com/VegetinES/Laslylusky-Bot", style=discord.ButtonStyle.link, row=3))

    def update_buttons(self):
        nav_buttons = [item for item in self.children 
                      if isinstance(item, ui.Button) and 
                         item.style == discord.ButtonStyle.blurple and
                         item.row == 1]
        
        for button in nav_buttons:
            self.remove_item(button)
        
        prev_button = ui.Button(
            emoji="⬅️", 
            style=discord.ButtonStyle.blurple, 
            disabled=self.current_page == 0,
            row=1
        )
        prev_button.callback = self.previous_page
        self.add_item(prev_button)
        
        next_button = ui.Button(
            emoji="➡️", 
            style=discord.ButtonStyle.blurple, 
            disabled=self.current_page == len(self.pages)-1,
            row=1
        )
        next_button.callback = self.next_page
        self.add_item(next_button)

    async def previous_page(self, interaction: discord.Interaction):
        self.current_page -= 1
        await self.update_embed(interaction)

    async def next_page(self, interaction: discord.Interaction):
        self.current_page += 1
        await self.update_embed(interaction)

    async def update_embed(self, interaction: discord.Interaction):
        self.update_buttons()
        embed = discord.Embed(
            title=f"{self.emoji} {self.category} (Página {self.current_page + 1}/{len(self.pages)})",
            description="\n\n".join(self.pages[self.current_page]),
            color=63272
        )
        
        if self.user.avatar:
            embed.set_footer(text=f"Pedido por: {self.user.display_name}", icon_url=self.user.avatar.url)
        else:
            embed.set_footer(text=f"Pedido por: {self.user.display_name}")
        
        await interaction.response.edit_message(embed=embed, view=self)
        self.message = await interaction.original_response()

    async def on_timeout(self):
        if hasattr(self, 'message') and self.message is not None:
            for item in self.children:
                if not isinstance(item, ui.Button) or item.style != discord.ButtonStyle.link:
                    item.disabled = True
            try:
                await self.message.edit(view=self)
            except:
                pass

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.default_cmd = ["help", "donate", "info", "invite", "privacidad", "updates", "savedatachat", "botsuggest", "bugreport", "laslylusky", "reset-chat", "config", "infracciones", "moderador", "recordatorio", "nivel", "voicesetup", "cumpleaños", "estadisticas-juegos", "comprobar-virus", "tos"]

    def get_server_commands(self, guild_id):
        server_data = get_server_data(guild_id)
        if not server_data:
            return {"active": self.default_cmd, "deactivated": []}
            
        active_commands = list(set(server_data.get("act_cmd", []) + self.default_cmd))
        deactivated_commands = server_data.get("deact_cmd", [])
        return {"active": active_commands, "deactivated": deactivated_commands}

    def parse_options_from_usage(self, usage):
        options = []
        if '<' in usage or '{' in usage:
            parts = usage.replace('`', '').split()
            for part in parts:
                if part.startswith('<') or part.startswith('{'):
                    option_name = part.strip('<>{}')
                    if ':' in option_name:
                        option_name = option_name.split(':')[0]
                    options.append(option_name)
        return options

    def create_command_embed(self, interaction_or_ctx, command_name, command_info):
        embed = discord.Embed(
            color=40695
        )
        
        description = []
        description.append(f"# <:faq:1372879060329435147> Información del comando `{command_name}`")
        description.append(f"### <:flecha:1372877292899926107> Información\n> {command_info['description']}")
        description.append(f"### <:flecha:1372877292899926107> Uso\n> {command_info['usage']}")
        
        options_text = []
        if 'options' in command_info and command_info['options']:
            for option in command_info['options']:
                options_text.append(f"- `{option}`: {command_info['options'][option]}")
        else:
            options = self.parse_options_from_usage(command_info['usage'])
            if options:
                for option in options:
                    options_text.append(f"- `{option}`: nombre del comando que quieres ver la ayuda")
                
        if options_text:
            description.append(f"### <:flecha:1372877292899926107> Opciones\n> {chr(10).join(options_text)}")
            
        description.append(f"### <:flecha:1372877292899926107> Permisos\n> {command_info['permissions']}")
        
        if 'extra' in command_info and command_info['extra']:
            description.append(f"### <:flecha:1372877292899926107> Extra \n> {command_info['extra']}")
        
        description.append("\n-# No pongas en los comandos `<>` ni `{}`.")
        description.append("-# - `<>`: opcional")
        description.append("-# - `{}`: obligatorio")
        
        embed.description = "\n".join(description)
        embed.set_image(url="https://i.imgur.com/dSHF16t.png")
        
        return embed

    def create_general_help_embed(self, interaction_or_ctx, include_nsfw=False):
        if isinstance(interaction_or_ctx, discord.Interaction):
            user = interaction_or_ctx.user
            guild_id = interaction_or_ctx.guild.id
        else:
            user = interaction_or_ctx.author
            guild_id = interaction_or_ctx.guild.id
        
        server_commands = self.get_server_commands(guild_id)
        
        active_commands = set(server_commands["active"])
        deactivated_commands = set(server_commands["deactivated"])
        
        total_commands = sum(
            len([cmd for cmd in category["commands"].keys() 
                if cmd in active_commands or cmd in deactivated_commands])
            for category in COMMAND_CATEGORIES.values()
        )
        
        total_categories = len(COMMAND_CATEGORIES)
        
        embed = discord.Embed(
            title="Ayuda de Laslylusky",
            description=(
                f"Hola {user.mention}, mi prefix es `%` y tengo **{total_commands} comandos** y **{total_categories} categorías**\n\n"
                f"Escribe `%help <comando>` o `/help comando:<comando>` para obtener más información sobre un comando.\n\n"
                f"Escribe `%privacidad` o `/privacidad` *para conocer la política de privacidad del bot.\n\n"
                "### Categorías\n"
                "- <:laslylusky:1372143928899534901> Laslylusky\n"
                "- <:games:1372144428814307408> Juegos\n"
                "- <:moderation:1372144807023218759> Moderación\n"
                "- <:configuration:1372145859361243216> Configuración\n"
                "- <:Information:1372146141994549349> Información\n"
                "- <:utilities:1372146639963295764> Utilidad\n"
                "- <:minecraft:1372146869370880132> Minecraft\n"
                "- <:nsfw:1372147128545316964> NSFW"
            ),
            color=63272
        )
        
        embed.set_image(url="https://i.imgur.com/Jhaa71e.png")
        
        footer_kwargs = {
            'text': f"Pedido por: {user.display_name}"
        }
        
        if user.avatar and user.avatar.url:
            footer_kwargs['icon_url'] = user.avatar.url
            
        embed.set_footer(**footer_kwargs)
        return embed

    def is_nsfw_command(self, command_name):
        return any(command_name in data['commands'] 
                  for category, data in COMMAND_CATEGORIES.items() 
                  if category == "NSFW")

    def get_available_commands(self, guild_id, include_nsfw=False):
        server_commands = self.get_server_commands(guild_id)
        all_available_commands = set(server_commands["active"] + server_commands["deactivated"])
        
        command_list = []
        for category, data in COMMAND_CATEGORIES.items():
            if category == "NSFW" and not include_nsfw:
                continue
            
            for cmd_name in data['commands'].keys():
                if cmd_name in all_available_commands:
                    command_list.append(cmd_name)
        
        return sorted(command_list)

    @commands.command(name='help')
    async def help_command(self, ctx, command_name: str = None):
        if isinstance(ctx.channel, discord.DMChannel):
            return

        if command_name:
            server_commands = self.get_server_commands(ctx.guild.id)
            all_available_commands = set(server_commands["active"] + server_commands["deactivated"])
            
            if command_name not in all_available_commands:
                await ctx.send(f"El comando `{command_name}` no está disponible en este servidor.")
                return

            if self.is_nsfw_command(command_name) and not ctx.channel.is_nsfw():
                try:
                    await ctx.message.delete()
                except:
                    pass
                temp_msg = await ctx.send("Este comando no se puede ejecutar aquí, se debe hacer en un canal NSFW")
                await asyncio.sleep(10)
                try:
                    await temp_msg.delete()
                except:
                    pass
                return

            for category in COMMAND_CATEGORIES.values():
                if command_name in category['commands']:
                    embed = self.create_command_embed(
                        ctx, command_name, category['commands'][command_name]
                    )
                    await ctx.send(embed=embed)
                    return

        try:
            embed = self.create_general_help_embed(ctx, include_nsfw=ctx.channel.is_nsfw())
            view = CategoryView(self.bot, ctx.guild.id, ctx.channel.is_nsfw())
            message = await ctx.send(embed=embed, view=view)
            view.message = message
        except Exception as e:
            await ctx.send(f"Ha ocurrido un error al mostrar la ayuda: {e}")

    @app_commands.command(name="help", description="Muestra la lista de comandos disponibles")
    @app_commands.describe(comando="Nombre del comando del que quieres obtener información")
    async def help_slash(self, interaction: discord.Interaction, comando: str = None):
        if isinstance(interaction.channel, discord.DMChannel):
            await interaction.response.send_message("No puedo ejecutar comandos en mensajes directos.", ephemeral=True)
            return

        if comando:
            server_commands = self.get_server_commands(interaction.guild.id)
            all_available_commands = set(server_commands["active"] + server_commands["deactivated"])
            
            if comando not in all_available_commands:
                await interaction.response.send_message(
                    f"El comando `{comando}` no está disponible en este servidor.",
                    ephemeral=True
                )
                return

            if self.is_nsfw_command(comando) and not interaction.channel.is_nsfw():
                await interaction.response.send_message(
                    "Este comando no se puede ejecutar aquí, se debe hacer en un canal NSFW",
                    ephemeral=True
                )
                return

            for category in COMMAND_CATEGORIES.values():
                if comando in category['commands']:
                    embed = self.create_command_embed(
                        interaction, comando, category['commands'][comando]
                    )
                    await interaction.response.send_message(embed=embed)
                    return

        try:
            embed = self.create_general_help_embed(interaction, include_nsfw=interaction.channel.is_nsfw())
            view = CategoryView(self.bot, interaction.guild.id, interaction.channel.is_nsfw())
            await interaction.response.send_message(embed=embed, view=view)
            view.message = await interaction.original_response()
        except Exception as e:
            await interaction.response.send_message(f"Ha ocurrido un error al mostrar la ayuda: {e}", ephemeral=True)

    @help_slash.autocomplete('comando')
    async def command_autocomplete(self, interaction: discord.Interaction, current: str):
        is_nsfw = interaction.channel.is_nsfw() if hasattr(interaction.channel, 'is_nsfw') else False
        commands = self.get_available_commands(interaction.guild.id, include_nsfw=is_nsfw)
        
        if current:
            commands = [cmd for cmd in commands if current.lower() in cmd.lower()]
        
        commands = commands[:25]
        
        return [
            app_commands.Choice(name=cmd, value=cmd)
            for cmd in commands
        ]

async def setup(bot):
    await bot.add_cog(Help(bot))