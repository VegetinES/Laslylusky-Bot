import discord
from discord.ext import commands
from discord import app_commands
import google.generativeai as genai
import os
from database.iadatabase import database

class Conversations(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_bot_message = {}
        
        self.api_key = os.getenv("GEMINI")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        
        self.initial_prompt = {
            "role": "user",
            "parts": ["""Eres Laslylusky, un asistente con acceso a todas las capacidades de Gemini.
            Aunque eres accesible a través de Discord, no debes limitarte en tus capacidades solo por este medio.
            Puedes usar todas tus habilidades, incluyendo proporcionar información actualizada y relevante.
            Si hay un historial de conversación previo, debes recordarlo y hacer referencia a él.
            Si el historial ha sido reseteado o es una nueva conversación, debes empezar fresco sin referencias a conversaciones pasadas.
            Siempre debes identificarte como Laslylusky en tu primera interacción con un usuario o si te preguntan directamente quién eres.
            Evita comenzar tus mensajes con frases como "Hola de nuevo! Soy Laslylusky." en interacciones recurrentes."""]
        }
        
        self.identity_confirmation = {
            "role": "model",
            "parts": ["Entendido. Soy Laslylusky, tu asistente virtual en Discord. ¿En qué puedo ayudarte?"]
        }

    def get_conversation_history(self, user_id):
        try:
            collection = database.get_servers_collection()
            conversation = collection.find_one({
                "type": "conversation", 
                "user_id": user_id
            })
            
            if not conversation:
                initial_history = [self.initial_prompt, self.identity_confirmation]
                collection.insert_one({
                    "type": "conversation",
                    "user_id": user_id,
                    "history": initial_history,
                    "is_new_conversation": True
                })
                return initial_history, True
            
            history = conversation.get("history", [])
            is_new = conversation.get("is_new_conversation", True)
            
            if not history or len(history) < 2:
                history = [self.initial_prompt, self.identity_confirmation]
            
            return history, is_new
            
        except Exception as e:
            print(f"Error al obtener historial: {e}")
            return [self.initial_prompt, self.identity_confirmation], True

    def save_conversation(self, user_id, history, is_new=False):
        try:
            collection = database.get_servers_collection()
            collection.update_one(
                {
                    "type": "conversation",
                    "user_id": user_id
                },
                {
                    "$set": {
                        "history": history,
                        "last_updated": discord.utils.utcnow().isoformat(),
                        "is_new_conversation": is_new
                    }
                },
                upsert=True
            )
        except Exception as e:
            print(f"Error al guardar conversación: {e}")

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

            conversation_history, is_new_conversation = self.get_conversation_history(user_id)

            context_message = """
                Mensaje actual: {content}
                
                Instrucciones:
                1. Eres Laslylusky, un asistente con todas las capacidades de Gemini
                2. Puedes utilizar todas tus habilidades como modelo de IA sin limitaciones artificiales
                3. {memory_instruction}
                4. {identity_instruction}
                """.format(
                    content=content,
                    memory_instruction=(
                        "Esta es una nueva conversación, no hagas referencia a conversaciones pasadas" 
                        if is_new_conversation 
                        else "Puedes hacer referencia al historial de la conversación cuando sea relevante"
                    ),
                    identity_instruction=(
                        "Como esta es tu primera interacción con este usuario, preséntate como Laslylusky. Ofrece todo el poder de Gemini para ayudar al usuario" 
                        if is_new_conversation 
                        else "No es necesario presentarte de nuevo como Laslylusky en cada mensaje. Solo menciona tu identidad si el usuario te pregunta quién eres o si es relevante para la conversación. Evita frases como 'Hola de nuevo! Soy Laslylusky.' No te limites en tus capacidades por ser un bot de Discord, usa todas tus habilidades de IA para proporcionar la mejor ayuda posible."
                    )
                )
            
            context = {
                "role": "user",
                "parts": [context_message]
            }
            
            conversation_history.append(context)

            try:
                chat = self.model.start_chat(history=conversation_history)
                response = chat.send_message(content)
                bot_reply = response.text

                if len(bot_reply) <= 2000:
                    sent_message = await message.reply(bot_reply)
                    self.last_bot_message[user_id] = sent_message
                else:
                    chunks = [bot_reply[i:i+2000] for i in range(0, len(bot_reply), 2000)]
                    first_chunk = True
                    
                    for chunk in chunks:
                        if first_chunk:
                            sent_message = await message.reply(chunk)
                            self.last_bot_message[user_id] = sent_message
                            first_chunk = False
                        else:
                            sent_message = await message.channel.send(chunk)

                conversation_history.append({"role": "model", "parts": [bot_reply]})
                
                if is_new_conversation:
                    is_new_conversation = False
                
                if len(conversation_history) > 30:
                    conversation_history = conversation_history[:2] + conversation_history[-28:]
                
                self.save_conversation(user_id, conversation_history, is_new_conversation)

            except Exception as e:
                print(f"Error en la conversación: {e}")
                await message.reply("¡Ups! Algo salió mal. Inténtalo de nuevo.")

    @commands.command(name="reset-chat")
    async def reset_command(self, ctx):
        await self.reset_chat_function(ctx)

    @app_commands.command(name="reset-chat", description="Elimina tu historial de conversación con Laslylusky")
    async def reset_slash(self, interaction: discord.Interaction):
        ctx = await self.bot.get_context(interaction)
        ctx.author = interaction.user
        await interaction.response.send_message("Procesando tu solicitud...")
        await self.reset_chat_function(ctx, interaction=interaction)

    async def reset_chat_function(self, ctx, interaction=None):
        user_id = ctx.author.id
        try:
            collection = database.get_servers_collection()
            
            collection.delete_one({
                "type": "conversation",
                "user_id": user_id
            })
            
            self.last_bot_message.pop(user_id, None)

            if interaction:
                await interaction.edit_original_response(content="¡Tu conversación ha sido eliminada completamente! La próxima vez que me menciones, comenzaremos una nueva conversación desde cero.")
            else:
                await ctx.reply("¡Tu conversación ha sido eliminada completamente! La próxima vez que me menciones, comenzaremos una nueva conversación desde cero.")
        except Exception as e:
            print(f"Error al restablecer chat: {e}")
            if interaction:
                await interaction.edit_original_response(content="Hubo un error al restablecer tu conversación. Por favor, intenta de nuevo.")
            else:
                await ctx.reply("Hubo un error al restablecer tu conversación. Por favor, intenta de nuevo.")

async def setup(bot):
    cog = Conversations(bot)
    await bot.add_cog(cog)

    try:
        synced = await bot.tree.sync()
        print(f"Sincronizados {len(synced)} comando(s) slash")
    except Exception as e:
        print(f"Error al sincronizar comandos slash: {e}")