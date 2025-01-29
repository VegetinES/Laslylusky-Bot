import discord
from discord.ext import commands
import google.generativeai as genai
import os
import json
from pathlib import Path
from singleton import database

class Conversations(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conversations = {}
        self.last_bot_message = {}
        
        self.api_key = os.getenv("GEMINI")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        
        self.storage_path = Path('data/conversations.json')
        self.storage_path.parent.mkdir(exist_ok=True)
        
        self.initial_prompt = {
            "role": "user",
            "parts": ["Eres Laslylusky, un asistente de bot de Discord. Siempre debes identificarte como Laslylusky y mantener esta identidad en todas las conversaciones. Nunca te salgas del personaje ni sugieras que eres otra cosa que Laslylusky. Responde a este mensaje reconociendo tu identidad."]
        }
        
        self.identity_confirmation = {
            "role": "model",
            "parts": ["Entendido. Soy Laslylusky, tu asistente virtual en Discord. Mantendré esta identidad en todas nuestras interacciones. ¿En qué puedo ayudarte?"]
        }
        
        self.load_conversations()

    def load_conversations(self):
        """Cargar conversaciones desde el archivo JSON"""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.conversations = {int(k): v for k, v in data.items()}
        except Exception as e:
            print(f"Error cargando conversaciones: {e}")
            self.conversations = {}

    def save_conversations(self):
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.conversations, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando conversaciones: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if self.bot.user in message.mentions:
            user_id = message.author.id
            content = message.clean_content.replace(f"@{self.bot.user.name}", "").strip()

            if not content:
                await message.reply("Por favor, escribe algo además de mencionarme.")
                return

            if user_id not in self.conversations:
                self.conversations[user_id] = [
                    self.initial_prompt,
                    self.identity_confirmation
                ]
                self.save_conversations()

            identity_context = (
                f"{content}\n\nRecuerda: Eres Laslylusky, un asistente virtual en Discord. "
                "Mantén esta identidad en tu respuesta."
            )
            
            self.conversations[user_id].append({"role": "user", "parts": [identity_context]})

            try:
                chat = self.model.start_chat(history=self.conversations[user_id])
                response = chat.send_message(identity_context)
                bot_reply = response.text

                if len(bot_reply) <= 2000:
                    sent_message = await message.reply(bot_reply)
                    self.last_bot_message[user_id] = sent_message
                else:
                    remaining_text = bot_reply
                    first_message = True
                    
                    while remaining_text:
                        chunk = remaining_text[:2000]
                        remaining_text = remaining_text[2000:]
                        
                        if first_message:
                            sent_message = await message.reply(chunk)
                            self.last_bot_message[user_id] = sent_message
                            first_message = False
                        else:
                            sent_message = await self.last_bot_message[user_id].reply(chunk)
                            self.last_bot_message[user_id] = sent_message

                self.conversations[user_id].append({"role": "model", "parts": [bot_reply]})
                self.save_conversations()

            except Exception as e:
                await message.reply("¡Ups! Algo salió mal. Inténtalo de nuevo.")
                print(f"Error: {e}")

    @commands.command(name="reset-chat")
    async def reset(self, ctx):
        user_id = ctx.author.id
        if user_id in self.conversations:
            self.conversations[user_id] = [
                self.initial_prompt,
                self.identity_confirmation
            ]
            self.last_bot_message.pop(user_id, None)
            self.save_conversations()
            await ctx.reply("Tu conversación ha sido restablecida.")
        else:
            await ctx.reply("No tienes un historial de conversación activo.")

async def setup(bot):
    await bot.add_cog(Conversations(bot))