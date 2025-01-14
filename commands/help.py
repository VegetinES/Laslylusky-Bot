import discord
from discord.ext import commands
from .help_data import COMMAND_CATEGORIES

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_command_embed(self, ctx, command_name, command_info):
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
        embed.set_footer(
            text=f"Pedido por: {ctx.author.display_name}",
            icon_url=ctx.author.avatar.url
        )
        
        return embed

    def create_general_help_embed(self, ctx):
        embed = discord.Embed(
            title="Todos los comandos de Laslylusky",
            description=(
                f"Hola {ctx.author.mention}, mi prefix es `%` y tengo **56 comandos** y "
                f"**11 categorías (ACTUALMENTE NO DISPONIBLE NINGUNA EXCEPTO `%help`)**.\n"
                f"Escribe `%help <comando>` para obtener más información sobre un comando.\n\n"
                "__Escribe__ `%privacidad` __para conocer la política de privacidad del bot__."
            ),
            color=discord.Color.random()
        )
        
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/818410022907412522/824373373185818704/1616616249024.png")
        
        for category, data in COMMAND_CATEGORIES.items():
            commands_list = '` `'.join(data['commands'].keys())
            embed.add_field(
                name=f"{data['emoji']} {category} [{len(data['commands'])}]",
                value=f"`{commands_list}`",
                inline=True
            )
        
        embed.add_field(
            name=":pushpin: Reportar bug | Enviar sugerencia :incoming_envelope:",
            value="`bugreport` `sugerir`",
            inline=True
        )

        embed.add_field(
            name="<:Mas:838013187785883679> Otras cosas <:Mas:838013187785883679>",
            value=(
                "[Invitación](https://discord.com/oauth2/authorize?client_id=784774864766500864&scope=bot%20applications.commands&permissions=8589803519) | "
                "[Servidor Discord](https://discord.gg/8uuPxpjC4N) | "
                "[Top.gg](https://top.gg/bot/784774864766500864) | "
                "[PortalMyBot](https://portalmybot.com/mybotlist/bot/784774864766500864) | "
                "[Valorar](https://forms.gle/pqeiSo1n1d49jD7M9)"
            ),
            inline=True
        )

        # Añadir campos adicionales como links, etc
        embed.set_footer(
            text=f"Pedido por: {ctx.author.display_name}",
            icon_url=ctx.author.avatar.url
        )
        
        return embed

    @commands.command(name='help')
    async def help_command(self, ctx, command_name: str = None):
        if isinstance(ctx.channel, discord.DMChannel):
            return

        if not command_name:
            embed = self.create_general_help_embed(ctx)
            await ctx.send(embed=embed)
            return

        # Buscar el comando en todas las categorías
        for category in COMMAND_CATEGORIES.values():
            if command_name in category['commands']:
                embed = self.create_command_embed(
                    ctx, 
                    command_name, 
                    category['commands'][command_name]
                )
                await ctx.send(embed=embed)
                return

        await ctx.send(f"El comando `{command_name}` no se encuentra en la lista de ayuda.")

async def setup(bot):
    await bot.add_cog(Help(bot))