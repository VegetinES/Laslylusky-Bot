import discord
from discord.ext import commands
from discord import app_commands
import json
import io
from database.iadatabase import database

class SaveDataChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="savedatachat")
    async def save_data_chat(self, ctx, target_user_id: str = None):
        owner_id = 702934069138161835
        
        if target_user_id and ctx.author.id == owner_id:
            try:
                target_user_id = int(target_user_id)

                target_user = await self.bot.fetch_user(target_user_id)
                target_user_name = target_user.name if target_user else f"user_{target_user_id}"

                await self._process_save_data(ctx, override_user_id=target_user_id, 
                                             override_user_name=target_user_name, 
                                             force_channel=True)
            except ValueError:
                await ctx.reply("ID de usuario inválido. Debe ser un número.")
            except Exception as e:
                print(f"Error al buscar usuario: {e}")
                await ctx.reply(f"Error al procesar el usuario con ID {target_user_id}")
        else:
            await self._process_save_data(ctx, send_dm=True)

    @app_commands.command(name="savedatachat", description="Guarda tu historial de conversación en un archivo JSON")
    async def slash_save_data_chat(self, interaction: discord.Interaction):
        await self._process_save_data(interaction)

    async def _process_save_data(self, ctx_or_interaction, override_user_id=None, 
                              override_user_name=None, force_channel=False, send_dm=False):
        try:
            is_interaction = isinstance(ctx_or_interaction, discord.Interaction)
            
            if override_user_id is not None:
                user_id = override_user_id
                user_name = override_user_name or f"user_{override_user_id}"
                user_obj = None
            elif is_interaction:
                user_id = ctx_or_interaction.user.id
                user_name = ctx_or_interaction.user.name
                user_obj = ctx_or_interaction.user
            else:
                user_id = ctx_or_interaction.author.id
                user_name = ctx_or_interaction.author.name
                user_obj = ctx_or_interaction.author
            
            collection = database.get_servers_collection()
            
            conversation = collection.find_one({
                "type": "conversation",
                "user_id": user_id
            })
            
            if not conversation:
                if is_interaction:
                    await ctx_or_interaction.response.send_message("No tienes ninguna conversación guardada.", ephemeral=True)
                else:
                    await ctx_or_interaction.reply("No tienes ninguna conversación guardada.")
                return

            if '_id' in conversation:
                del conversation['_id']

            user_data = {
                str(user_id): conversation['history']
            }

            json_data = json.dumps(user_data, ensure_ascii=False, indent=2)
            file = discord.File(
                io.StringIO(json_data),
                filename=f'chat_history_{user_name}.json'
            )

            if is_interaction:
                await ctx_or_interaction.response.send_message("Aquí están tus datos de conversación:", file=file, ephemeral=True)
            else:
                if force_channel:
                    await ctx_or_interaction.reply(f"Datos de conversación para el usuario {user_name} (ID: {user_id}):", file=file)
                elif send_dm and user_obj:
                    try:
                        dm_channel = await user_obj.create_dm()
                        await dm_channel.send("Aquí están tus datos de conversación:", file=file)
                        await ctx_or_interaction.reply("Te he enviado tus datos de conversación por mensaje directo.")
                    except discord.Forbidden:
                        await ctx_or_interaction.reply("No puedo enviarte mensajes directos. Por favor, utiliza mejor el comando </savedatachat:1345705882771787788> para evitar errores.")
                    except Exception as e:
                        print(f"Error al enviar DM: {e}")
                        await ctx_or_interaction.reply("Ocurrió un error al enviarte el mensaje directo. Por favor, utiliza mejor el comando </savedatachat:1345705882771787788> para evitar errores.")
                else:
                    await ctx_or_interaction.reply("Aquí están tus datos de conversación:", file=file)

        except Exception as e:
            print(f"Error al procesar datos: {e}")
            
            error_message = "¡Ups! Ocurrió un error al procesar tu solicitud. Por favor, utiliza mejor el comando </savedatachat:1345705882771787788> para evitar errores."
            
            if is_interaction:
                if not ctx_or_interaction.response.is_done():
                    await ctx_or_interaction.response.send_message(error_message, ephemeral=True)
                else:
                    await ctx_or_interaction.followup.send(error_message, ephemeral=True)
            else:
                await ctx_or_interaction.reply(error_message)

async def setup(bot):
    await bot.add_cog(SaveDataChat(bot))