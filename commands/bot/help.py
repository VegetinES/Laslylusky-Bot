import discord
from discord.ext import commands
from discord import app_commands
from .help_data import COMMAND_CATEGORIES
import asyncio

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
        
        embed.description = "\n\n".join(description)
        
        if isinstance(interaction_or_ctx, discord.Interaction):
            user = interaction_or_ctx.user
        else:
            user = interaction_or_ctx.author
            
        embed.set_footer(
            text=f"Pedido por: {user.display_name}",
            icon_url=user.avatar.url
        )
        return embed

    def create_general_help_embed(self, interaction_or_ctx, include_nsfw=False):
        if isinstance(interaction_or_ctx, discord.Interaction):
            user = interaction_or_ctx.user
        else:
            user = interaction_or_ctx.author
        
        total_commands = sum(len(category["commands"]) for category in COMMAND_CATEGORIES.values())
        total_categories = len(COMMAND_CATEGORIES)
        
        embed = discord.Embed(
            title="Todos los comandos de Laslylusky",
            description=(
                f"Hola {user.mention}, mi prefix es `%` y tengo **{total_commands} comandos** y "
                f"**{total_categories} categorías**.\n\n**Disponibles actualmente: `help (/help)` | `invite (/invite)` | `bugreport` | `bot-suggest` | `updates` | `embed` | `clear` | `slowmode` | `donate` | `serverinfo` | `info` | `servericon` | `userinfo` | `privacidad (/privacidad)` | `avatar`** \n\n"
                f"Escribe `%help <comando>` o `/help comando:<comando>` para obtener más información sobre un comando.\n\n"
                "__Escribe__ `%privacidad` o `/privacidad` **para conocer la política de privacidad del bot**."
            ),
            color=discord.Color.random()
        )
        
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/772803956379222016/1329014967239839744/2cef87cccba0f00826a16740ac049231.png?ex=6788cd24&is=67877ba4&hm=72e8520e7b4654280d6cadf0ac23cec37de06f70eaaa647cc6a87883401569c0&=&format=webp&quality=lossless")
        
        for category, data in COMMAND_CATEGORIES.items():
            if category == "NSFW" and not include_nsfw:
                continue
                
            commands_list = '` `'.join(data['commands'].keys())
            embed.add_field(
                name=f"{data['emoji']} {category} [{len(data['commands'])}]",
                value=f"`{commands_list}`",
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
            value=(
                "[Invitación](https://discord.com/oauth2/authorize?client_id=784774864766500864&scope=bot%20applications.commands&permissions=8589803519) | "
                "[Servidor Discord](https://discord.gg/8uuPxpjC4N) | "
                "[Top.gg](https://top.gg/bot/784774864766500864) | "
                "[PortalMyBot](https://portalmybot.com/mybotlist/bot/784774864766500864) | "
                "[Valorar](https://forms.gle/pqeiSo1n1d49jD7M9) | "
                "[Donar](https://paypal.me/VegetinES)"
            ),
            inline=True
        )
        
        embed.set_footer(
            text=f"Pedido por: {user.display_name}",
            icon_url=user.avatar.url
        )
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
            if self.is_nsfw_command(command_name):
                if not ctx.channel.is_nsfw():
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
                    
            await ctx.send(f"El comando `{command_name}` no se encuentra en la lista de ayuda.")
            return

        embed = self.create_general_help_embed(ctx, include_nsfw=ctx.channel.is_nsfw())
        await ctx.send(embed=embed)

    @app_commands.command(name="help", description="Muestra la lista de comandos disponibles")
    @app_commands.describe(comando="Nombre del comando del que quieres obtener información")
    async def help_slash(self, interaction: discord.Interaction, comando: str = None):
        if isinstance(interaction.channel, discord.DMChannel):
            await interaction.response.send_message("No puedo ejecutar comandos en mensajes directos.", ephemeral=True)
            return

        if comando:
            if self.is_nsfw_command(comando):
                if not interaction.channel.is_nsfw():
                    await interaction.response.send_message(
                        "Este comando no se puede ejecutar aquí, se debe hacer en un canal NSFW",
                        ephemeral=True,
                        delete_after=10
                    )
                    return

            for category in COMMAND_CATEGORIES.values():
                if comando in category['commands']:
                    embed = self.create_command_embed(
                        interaction, comando, category['commands'][comando]
                    )
                    await interaction.response.send_message(embed=embed)
                    return
                    
            await interaction.response.send_message(
                f"El comando `{comando}` no se encuentra en la lista de ayuda.",
                ephemeral=True
            )
            return

        embed = self.create_general_help_embed(interaction, include_nsfw=interaction.channel.is_nsfw())
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
    try:
        synced = await bot.tree.sync()
        print(f"Sincronizados {len(synced)} comandos de barra")
    except Exception as e:
        print(f"Error sincronizando comandos de barra: {e}")