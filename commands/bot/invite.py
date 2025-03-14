import discord
from discord.ext import commands
from discord import app_commands

class Invite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.imagen_path = "/home/ubuntu/Laslylusky/web/static/resources/laslylusky.png"
    
    def create_invite_embed(self, interaction_or_ctx):
        if isinstance(interaction_or_ctx, discord.Interaction):
            user = interaction_or_ctx.user
        else:
            user = interaction_or_ctx.author
            
        embed_invite = discord.Embed(
            title="Invitar al bot",
            description=(
                f"Hola <@{user.id}>. Aquí tienes el enlace para invitarme:\n\n"
                "- [Enlace de invitación](https://laslylusky.es/invite)"
            ),
            color=discord.Color.blue()
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
        
        archivo = discord.File(self.imagen_path, filename="laslylusky.png")
        embed_invite.set_thumbnail(url="attachment://laslylusky.png")
        
        try:
            await ctx.author.send(embed=embed_invite, file=archivo)
            await ctx.send("¡Te he enviado la invitación por MD! 📨")
        except discord.Forbidden:
            await ctx.send(
                f"No te lo he podido enviar por MD, pero aquí tienes la invitación al servidor:",
                embed=embed_invite,
                file=archivo
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
        
        archivo = discord.File(self.imagen_path, filename="laslylusky.png")
        embed_invite.set_thumbnail(url="attachment://laslylusky.png")
        
        try:
            await interaction.user.send(embed=embed_invite, file=archivo)
            await interaction.response.send_message("¡Te he enviado la invitación por MD! 📨")
        except discord.Forbidden:
            await interaction.response.send_message(
                f"No te lo he podido enviar por MD, pero aquí tienes la invitación al servidor:",
                embed=embed_invite,
                file=archivo
            )

async def setup(bot):
    await bot.add_cog(Invite(bot))