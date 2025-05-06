from database.get import get_specific_field
import discord
from discord import app_commands
from discord.ext import commands
import re

class Morse(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.text_to_morse = {
            'a': '.-', 'b': '-...', 'c': '-.-.', 'd': '-..', 'e': '.', 'f': '..-.', 
            'g': '--.', 'h': '....', 'i': '..', 'j': '.---', 'k': '-.-', 'l': '.-..', 
            'm': '--', 'n': '-.', 'o': '---', 'p': '.--.', 'q': '--.-', 'r': '.-.', 
            's': '...', 't': '-', 'u': '..-', 'v': '...-', 'w': '.--', 'x': '-..-', 
            'y': '-.--', 'z': '--..', 
            'ñ': '--.--',
            'á': '.--.-', 'é': '..-..', 'í': '..', 'ó': '---.', 'ú': '..--',
            '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-', 
            '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.', 
            '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.', '!': '-.-.--', 
            '/': '-..-.', '(': '-.--.', ')': '-.--.-', '&': '.-...', ':': '---...', 
            ';': '-.-.-.', '=': '-...-', '+': '.-.-.', '-': '-....-', '"': '.-..-.', 
            '$': '...-..-', '@': '.--.-.', ' ': '/'
        }
        
        self.morse_to_text = {v: k for k, v in self.text_to_morse.items()}

    @commands.command(name="morse")
    async def morse_text_command(self, ctx, *, text=None):
        if isinstance(ctx.channel, discord.DMChannel):
            return
        
        act_commands = get_specific_field(ctx.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if "morse" not in act_commands:
            await ctx.reply("El comando no está activado en este servidor.")
            return
        
        if not text:
            await ctx.send("Debes proporcionar un texto para convertir a código morse.")
            return
        
        morse_text = self.convert_to_morse(text)
        
        if len(morse_text) > 2000:
            await ctx.send("El texto convertido es demasiado largo para mostrarlo.")
            return
        
        await ctx.send(f"```{morse_text}```")
    
    @app_commands.command(name="morse", description="Convierte texto a morse o morse a texto")
    @app_commands.describe(
        texto_a_morse="Texto para convertir a código morse",
        morse_a_texto="Código morse para convertir a texto (usa . para punto, - para raya, / para espacio)"
    )
    async def morse_slash_command(self, interaction: discord.Interaction, texto_a_morse: str = None, morse_a_texto: str = None):
        act_commands = get_specific_field(interaction.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if "morse" not in act_commands:
            await interaction.response.send_message("El comando no está activado en este servidor.", ephemeral=True)
            return
        
        if not texto_a_morse and not morse_a_texto:
            await interaction.response.send_message("Debes proporcionar un texto para convertir a morse o un código morse para convertir a texto.", ephemeral=True)
            return
        
        if texto_a_morse and morse_a_texto:
            await interaction.response.send_message("Solo puedes usar uno de los parámetros a la vez.", ephemeral=True)
            return
        
        if texto_a_morse:
            result = self.convert_to_morse(texto_a_morse)
            if len(result) > 2000:
                await interaction.response.send_message("El texto convertido es demasiado largo para mostrarlo.", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="Texto a Morse",
                description=f"```{result}```",
                color=discord.Color.blue()
            )
            embed.add_field(name="Texto original", value=texto_a_morse[:1000])
            
            await interaction.response.send_message(embed=embed)
        
        elif morse_a_texto:
            result = self.convert_from_morse(morse_a_texto)
            if not result:
                await interaction.response.send_message("No se pudo convertir el código morse. Asegúrate de usar '.' para punto, '-' para raya y '/' para espacios entre palabras.", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="Morse a Texto",
                description=f"```{result}```",
                color=discord.Color.green()
            )
            embed.add_field(name="Morse original", value=morse_a_texto[:1000])
            
            await interaction.response.send_message(embed=embed)
    
    def convert_to_morse(self, text):
        text = text.lower()
        morse_text = []
        
        for char in text:
            if char in self.text_to_morse:
                morse_text.append(self.text_to_morse[char])
            else:
                morse_text.append(char)
        
        return ' '.join(morse_text)
    
    def convert_from_morse(self, morse_code):
        morse_code = morse_code.strip()
        words = morse_code.split(' / ')
        result = []
        
        for word in words:
            morse_chars = word.split()
            decoded_word = ''
            
            for morse_char in morse_chars:
                if morse_char in self.morse_to_text:
                    decoded_word += self.morse_to_text[morse_char]
                else:
                    decoded_word += '?'
            
            result.append(decoded_word)
        
        return ' '.join(result)

async def setup(bot):
    await bot.add_cog(Morse(bot))