import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# PROXIMAMENTE:

"""
    - EL BOT CONTARÁ CON TODOS LOS COMANDOS ANTERIORES MÁS MUCHOS NUEVOS
    - LOS COMANDOS ESTARÁN ORGANIZADOS EN UNA CARPETA A PARTE
    - SERÁ MÁS EFICIENTE Y SEGURO
    - HOST 24/7
    - CONTARÁ CON BASES DE DATOS
    - SE HARÁ EN PYTHON (INICIALMENTE HECHO EN JAVASCRIPT)
    - TRATARÁ DE TENER IA (NO ES SEGURO 100% QUE VAYA A TENER)
"""

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='%', intents=intents)

@bot.command(name='ayuda')
async def ayuda(ctx, *args):
    if isinstance(ctx.channel, discord.DMChannel):
        return

    embed_general = discord.Embed(
        title="Todos los comandos de Laslylusky",
        description=(
            f"Hola {ctx.author.mention}, mi prefix es `%` y tengo **56 comandos** y **11 categorías (ACTUALMENTE NO DISPONIBLE NINGUNA EXCEPTO `%ayuda`)**.\n"
            f"Escribe `%ayuda <comando>` para obtener más información sobre un comando.\n\n"
            "__Escribe__ `%privacidad` __para conocer la política de privacidad del bot__."
        ),
        color=discord.Color.random()
    )
    embed_general.set_thumbnail(url="https://media.discordapp.net/attachments/818410022907412522/824373373185818704/1616616249024.png?width=593&height=593")
    embed_general.add_field(name="<:General:838015864455299082> General [10]", value="`ayuda` `invite` `discord` `soon` `vote` `update` `uptime` `steam` `instagram` `privacidad`", inline=True)
    embed_general.add_field(name="<:Diversion:838016251787345930> Diversión [9]", value="`8ball` `confession` `impostor` `love` `hack` `presentacion` `meme` `captcha` `dm`", inline=True)
    embed_general.add_field(name="<:Moderacion:838015484032057384> Moderación [6]", value="`ban` `kick` `clear` `mute` `idban` `unmute`", inline=True)
    embed_general.add_field(name="<:Info:837631728368746548> Información [8]", value="`user` `ping` `avatar` `about` `guild` `servericon` `stats`", inline=True)
    embed_general.add_field(name="<:Utilidad:838016540246147133> Utilidad [6]", value="`embed` `iembed` `say` `slowmode` `jumbo` `calculadora`", inline=True)
    embed_general.add_field(name="<:Interaccion:839105758566154340> Interacción [3]", value="`pop` `hi` `covid`", inline=True)
    embed_general.add_field(name="<:Laslylusky:833614887547699221> Anime [2]", value="`animesearch` `waifu`", inline=True)
    embed_general.add_field(name="<:Minecraft:837706204079194123> Minecraft [2]", value="`mcuser` `mcserver`", inline=True)
    embed_general.add_field(name="<:Juegos:838012718631616512> Juegos [2]", value="`waterdrop` `aki`", inline=True)
    embed_general.add_field(name="<:NSFW:838014363893366785> NSFW [8]", value="||`boobs` `anal` `ass` `pgif` `4k` `pussy` `hentai` `slut`||", inline=True)

    embed_general.add_field(
        name=":pushpin: Reportar bug | Enviar sugerencia :incoming_envelope:",
        value="`bugreport` `sugerir`",
        inline=True
    )

    embed_general.add_field(
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

    embed_general.set_footer(
        text=f"Pedido por: {ctx.author.display_name}",
        icon_url=ctx.author.avatar.url
    )

    embed_general.color = discord.Color.random()

    if args:
        command = args[0].lower()
        if command == 'ban':
            embed_command = discord.Embed(
                title="Información del comando 'ban'",
                description=(
                    "__Información:__ Comando para banear a los usuarios mencionados.\n"
                    "__Uso:__ `%ban <usuario> [razón]`\n"
                    "__Permisos:__ `ADMINISTRADOR` o `BANEAR USUARIOS`."
                ),
                color=discord.Color.blue()
            )
            embed_command.set_footer(text=f"Pedido por: {ctx.author.display_name}", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed_command)

            # AÑADIR CONDICIONES COMANDOS
        else:
            await ctx.send(f"El comando `{command}` no se encuentra en la lista de ayuda.")
    else:
        await ctx.send(embed=embed_general)

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.idle,
        activity=discord.Game(name="En mantenimiento, se vienen cosas")
    )
    print(f"Estamos dentro! {bot.user}")

bot.run(os.getenv('DISCORD_TOKEN'))