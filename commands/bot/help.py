import discord
from discord.ext import commands
from discord import app_commands, ui
from .help_data import COMMAND_CATEGORIES
import asyncio
from database.get import get_server_data

class LinkView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
        self.add_item(ui.Button(label="Invitación", emoji="<:laslylusky:1338239823441563718>", url="https://discord.com/oauth2/authorize?client_id=784774864766500864&scope=bot%20applications.commands&permissions=8589803519", style=discord.ButtonStyle.link, row=0))
        self.add_item(ui.Button(label="Servidor Discord", emoji="<:DiscordLogoColor:850013816640110593>", url="https://discord.gg/8uuPxpjC4N", style=discord.ButtonStyle.link, row=0))
        self.add_item(ui.Button(label="Top.gg", emoji="<:TopGG:1348313617879007335>", url="https://top.gg/bot/784774864766500864", style=discord.ButtonStyle.link, row=0))
        
        self.add_item(ui.Button(label="Valorar", emoji="<:BlackStar:1348312410460524736>", url="https://forms.gle/pqeiSo1n1d49jD7M9", style=discord.ButtonStyle.link, row=1))
        self.add_item(ui.Button(label="Donar", emoji="<:Paypal:1348200347348369449>", url="https://paypal.me/VegetinES", style=discord.ButtonStyle.link, row=1))
        self.add_item(ui.Button(label="GitHub", emoji="<:GitHub:1348277206870261820>", url="https://github.com/VegetinES/Laslylusky-Bot", style=discord.ButtonStyle.link, row=1))

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.default_cmd = ["help", "donate", "info", "invite", "privacidad", "updates", "savedatachat", "bot-suggest", "bugreport", "laslylusky", "reset-chat", "config", "infracciones", "moderador"]
        self.imagen_path = "/home/ubuntu/Laslylusky/web/resources/laslylusky 1.png"

    def get_server_commands(self, guild_id):
        server_data = get_server_data(guild_id)
        if not server_data:
            return {"active": self.default_cmd, "deactivated": []}
            
        active_commands = list(set(server_data.get("act_cmd", []) + self.default_cmd))
        deactivated_commands = server_data.get("deact_cmd", [])
        return {"active": active_commands, "deactivated": deactivated_commands}

    def create_command_embed(self, interaction_or_ctx, command_name, command_info):
        embed = discord.Embed(
            title=f"Información del comando '{command_name}'",
            color=discord.Color.blue()
        )
        
        description = []
        description.append(f"__Información:__ {command_info['description']}")
        description.append(f"__Uso:__ `{command_info['usage']}`")
        description.append(f"__Permisos:__ {command_info['permissions']}")
        if 'extra' in command_info:
            description.append(f"__Más:__ {command_info['extra']}")
        
        if isinstance(interaction_or_ctx, discord.Interaction):
            guild_id = interaction_or_ctx.guild.id
            user = interaction_or_ctx.user
        else:
            guild_id = interaction_or_ctx.guild.id
            user = interaction_or_ctx.author
            
        server_commands = self.get_server_commands(guild_id)
        if command_name in server_commands["deactivated"]:
            description.append("\n<:Info:837631728368746548> **Este comando está actualmente desactivado en este servidor**")
        
        embed.description = "\n\n".join(description)
        
        footer_kwargs = {
            'text': f"Pedido por: {user.display_name}"
        }
        
        if user.avatar and user.avatar.url:
            footer_kwargs['icon_url'] = user.avatar.url
            
        embed.set_footer(**footer_kwargs)
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
            title="Todos los comandos de Laslylusky",
            description=(
                f"Hola {user.mention}, mi prefix es `%` y tengo **{total_commands} comandos** y "
                f"**{total_categories} categorías**.\n\n"
                f"Escribe `%help <comando>` o `/help comando:<comando>` para obtener más información sobre un comando.\n\n"
                f"__Escribe__ `%privacidad` o </privacidad:1348016059499810860> **para conocer la política de privacidad del bot**.\n\n"
                "**Leyenda:**\n"
                "<:Si:825734135116070962> Comando activo\n"
                "<:No:825734196256440340> Comando desactivado"
            ),
            color=discord.Color.blue()
        )
        
        embed.set_image(url="attachment://laslylusky.png")
        
        for category, data in COMMAND_CATEGORIES.items():
            if category == "NSFW" and not include_nsfw:
                continue
                
            formatted_commands = []
            for cmd_name in data['commands'].keys():
                if cmd_name in active_commands:
                    formatted_commands.append(f"<:Si:825734135116070962>`{cmd_name}`")
                elif cmd_name in deactivated_commands:
                    formatted_commands.append(f"<:No:825734196256440340>`{cmd_name}`")
                    
            if formatted_commands:
                embed.add_field(
                    name=f"{data['emoji']} {category} [{len(formatted_commands)}]",
                    value=" ".join(formatted_commands),
                    inline=True
                )
            
        if not include_nsfw:
            embed.add_field(
                name="<:Prohibido:839877689154469928> Comandos NSFW",
                value="`Para ver los comandos NSFW, ejecuta` **%help** `o` **/help** `en un canal NSFW`",
                inline=True
            )
            
        embed.add_field(
            name="<:Mas:838013187785883679> Otras cosas <:Mas:838013187785883679>",
            value="Utiliza los botones de abajo para acceder a los enlaces",
            inline=False
        )
        
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
            file = discord.File(self.imagen_path, filename="laslylusky.png")
            await ctx.send(file=file, embed=embed, view=LinkView())
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
            file = discord.File(self.imagen_path, filename="laslylusky.png")
            await interaction.response.send_message(file=file, embed=embed, view=LinkView())
        except Exception as e:
            await interaction.response.send_message(f"Ha ocurrido un error al mostrar la ayuda: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Help(bot))