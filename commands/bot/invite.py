import discord
from discord.ext import commands
from discord import app_commands

class Invite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def create_invite_embed(self, interaction_or_ctx):
        if isinstance(interaction_or_ctx, discord.Interaction):
            user = interaction_or_ctx.user
        else:
            user = interaction_or_ctx.author
            
        embed_invite = discord.Embed(
            title="Invitar al bot",
            description=(
                f"Hola <@{user.id}>. Puedes invitarme de dos formas:\n\n"
                "- **Invitar al bot para utilizar solo los comandos de laslylusky, generales, diversión, información, utilidad, interacción, anime, minecraft y juegos** "
                "[invitación](https://discord.com/oauth2/authorize?client_id=784774864766500864&scope=bot%20applications.commands&permissions=3525697)\n\n"
                "- **Invitar al bot para utilizar todos los comandos (recomendable)** "
                "[invitación](https://discord.com/oauth2/authorize?client_id=784774864766500864&scope=bot%20applications.commands&permissions=8589803519)"
            ),
            color=discord.Color.random()
        )
        
        embed_invite.set_thumbnail(
            url="https://media.discordapp.net/attachments/818410022907412522/824373373185818704/1616616249024.png?width=593&height=593"
        )
        
        embed_invite.set_footer(
            text=f"Pedido por: {user.display_name}",
            icon_url=user.avatar.url
        )
        
        return embed_invite

    @commands.command(name="invite")
    async def invite_command(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            return
        
        embed_invite = self.create_invite_embed(ctx)
        
        try:
            await ctx.author.send(embed=embed_invite)
            await ctx.send("¡Te he enviado la invitación por MD! 📨")
        except discord.Forbidden:
            await ctx.send(
                f"No te lo he podido enviar por MD, pero aquí tienes la invitación al servidor:",
                embed=embed_invite
            )

    @app_commands.command(name="invite", description="Obtén los enlaces para invitar al bot a tu servidor")
    async def invite_slash(self, interaction: discord.Interaction):
        if isinstance(interaction.channel, discord.DMChannel):
            await interaction.response.send_message(
                "No puedo ejecutar comandos en mensajes directos.",
                ephemeral=True
            )
            return
        
        embed_invite = self.create_invite_embed(interaction)
        
        try:
            await interaction.user.send(embed=embed_invite)
            await interaction.response.send_message("¡Te he enviado la invitación por MD! 📨")
        except discord.Forbidden:
            await interaction.response.send_message(
                f"No te lo he podido enviar por MD, pero aquí tienes la invitación al servidor:",
                embed=embed_invite
            )

async def setup(bot):
    await bot.add_cog(Invite(bot))
    try:
        synced = await bot.tree.sync()
        print(f"Sincronizados {len(synced)} comandos de barra")
    except Exception as e:
        print(f"Error sincronizando comandos de barra: {e}")