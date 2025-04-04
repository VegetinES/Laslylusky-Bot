import discord
from discord.ext import commands
import random
import string
import asyncio
from database.get import get_server_data, get_specific_field
from database.save import save_server_data
from datetime import datetime, timedelta
import time

class ConfirmView(discord.ui.View):
    def __init__(self, timeout=60.0):
        super().__init__(timeout=timeout)
        self.value = None
        self.confirm_button = None
        self.cancel_button = None
        self._setup_buttons()

    def _setup_buttons(self):
        self.confirm_button = discord.ui.Button(
            label="Confirmar", 
            style=discord.ButtonStyle.danger,
            disabled=True
        )
        self.confirm_button.callback = self.confirm_callback

        self.cancel_button = discord.ui.Button(
            label="Cancelar", 
            style=discord.ButtonStyle.secondary
        )
        self.cancel_button.callback = self.cancel_callback

        self.add_item(self.confirm_button)
        self.add_item(self.cancel_button)

    async def confirm_callback(self, interaction: discord.Interaction):
        self.value = True
        self.stop()
        self.confirm_button.disabled = True
        self.cancel_button.disabled = True
        await interaction.response.edit_message(view=self)

    async def cancel_callback(self, interaction: discord.Interaction):
        self.value = False
        self.stop()
        self.confirm_button.disabled = True
        self.cancel_button.disabled = True
        await interaction.response.edit_message(view=self)

    async def enable_confirm_button(self):
        await asyncio.sleep(15)
        self.confirm_button.disabled = False
        return self.confirm_button

async def show_config_update(ctx, bot):
    is_interaction = isinstance(ctx, discord.Interaction)
    
    author = ctx.user if is_interaction else ctx.author
    guild = ctx.guild
    
    if not author.guild_permissions.administrator:
        if is_interaction:
            await ctx.response.send_message("No tienes permisos para ejecutar este comando. Se requieren permisos de administrador.", ephemeral=True)
        else:
            await ctx.reply("No tienes permisos para ejecutar este comando. Se requieren permisos de administrador.")
        return

    try:
        server_data = get_server_data(guild.id)
        
        if not server_data:
            data = {
                "guild_id": guild.id,
                "default_cdm": ["help", "donate", "info", "invite", "privacidad", "updates", "savedatachat", "bot-suggest", "bugreport", "laslylusky", "reset-chat", "config", "infracciones", "moderador"],
                "act_cmd": ["serverinfo", "slowmode", "kill", "meme", "avatar", "servericon", "userinfo", "ban", "unban", "clear", "kick", "warn", "unwarn", "4k", "anal", "ass", "blowjob", "boobs", "hanal", "hass", "hboobs", "pgif", "pussy", "mcstatus", "mcuser", "hypixel", "hug", "massban", "purgeban"],
                "deact_cmd": ["embed"],
                "mute_role": 0,
                "perms": {
                    "mg-ch-roles": [0],
                    "mg-ch-users": [0],
                    "admin-roles": [0],
                    "admin-users": [0],
                    "mg-rl-roles": [0],
                    "mg-rl-user": [0],
                    "mg-srv-roles": [0],
                    "mg-srv-users": [0],
                    "kick-roles": [0],
                    "kick-users": [0],
                    "ban-roles": [0],
                    "ban-users": [0],
                    "mute-roles": [0],
                    "mute-users": [0],
                    "deafen-roles": [0],
                    "deafen-users": [0],
                    "mg-msg-roles": [0],
                    "mg-msg-users": [0],
                    "warn-users": [0],
                    "warn-roles": [0],
                    "unwarn-users": [0],
                    "unwarn-roles": [0]
                },
                "audit_logs": {
                    "ban": {
                        "log_channel": 0,
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False
                    },
                    "kick": {
                        "log_channel": 0,
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False
                    },
                    "unban": {
                        "log_channel": 0,
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False
                    },
                    "enter": {
                        "log_channel": 0,
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False
                    },
                    "leave": {
                        "log_channel": 0,
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False
                    },
                    "del_msg": { 
                        "log_channel": 0, 
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False 
                    }, 
                    "edited_msg": { 
                        "log_channel": 0, 
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False 
                    },
                    "warn": {
                        "log_channel": 0,
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False
                    },
                    "unwarn": {
                        "log_channel": 0,
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False
                    },
                    "vc_enter": { 
                        "log_channel": 0, 
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False 
                    },
                    "vc_leave": { 
                        "log_channel": 0, 
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False 
                    },
                    "add_usr_rol": { 
                        "log_channel": 0, 
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False 
                    },
                    "rm_usr_rol": { 
                        "log_channel": 0, 
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False 
                    },
                    "add_ch": { 
                        "log_channel": 0, 
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False 
                    },
                    "del_ch": { 
                        "log_channel": 0, 
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False 
                    },
                    "changed_av": { 
                        "log_channel": 0, 
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False 
                    }
                },
                "tickets": {}
            }
            
            success = save_server_data(guild, data)
            if is_interaction:
                await ctx.response.send_message(
                    "¡Éxito! Se han creado los datos predeterminados para este servidor. Ya puedes utilizar y configurar el bot con normalidad." if success else "Ha ocurrido un error al crear los datos del servidor.",
                    ephemeral=True
                )
            else:
                await ctx.reply("¡Éxito! Se han creado los datos predeterminados para este servidor. Ya puedes utilizar y configurar el bot con normalidad." if success else "Ha ocurrido un error al crear los datos del servidor.")
            return

        future_timestamp = int(time.time()) + 15
        discord_timestamp = f"<t:{future_timestamp}:R>"

        embed = discord.Embed(
            title="Restablecer configuración",
            description=f"**¿Estás seguro que quieres restablecer la configuración?**\n\nEspera {discord_timestamp} para confirmar. En caso contrario, pulsa el botón cancelar.\n\n:warning: **Esto no se podrá revertir** :warning:",
            colour=0xf53100,
            timestamp=datetime.now()
        )
        embed.set_footer(text=f'Servidor de "{guild.name}" | ID: {guild.id}')

        view = ConfirmView(timeout=60.0)
        
        if is_interaction:
            await ctx.response.defer(ephemeral=False)
            message = await ctx.followup.send(embed=embed, view=view)
        else:
            message = await ctx.send(embed=embed, view=view)
        
        bot.loop.create_task(enable_confirm_button_and_update(message, view, bot))

        await view.wait()
        
        if view.value is None:
            embed.description = "⏰ **Tiempo excedido**\n\nHan pasado 60 segundos sin respuesta. Si deseas restablecer la configuración, vuelve a ejecutar el comando."
            embed.colour = discord.Colour.light_grey()

            if is_interaction:
                await message.edit(embed=embed, view=None)
            else:
                await message.edit(embed=embed, view=None)
                
        elif view.value:
            data = {
                "guild_id": guild.id,
                "default_cdm": ["help", "donate", "info", "invite", "privacidad", "updates", "savedatachat", "bot-suggest", "bugreport", "laslylusky", "reset-chat", "config", "infracciones", "moderador"],
                "act_cmd": ["serverinfo", "slowmode", "kill", "meme", "avatar", "servericon", "userinfo", "ban", "unban", "clear", "kick", "warn", "unwarn", "4k", "anal", "ass", "blowjob", "boobs", "hanal", "hass", "hboobs", "pgif", "pussy", "mcstatus", "mcuser", "hypixel", "hug", "massban", "purgeban"],
                "deact_cmd": ["embed"],
                "mute_role": 0,
                "perms": {
                    "mg-ch-roles": [0],
                    "mg-ch-users": [0],
                    "admin-roles": [0],
                    "admin-users": [0],
                    "mg-rl-roles": [0],
                    "mg-rl-user": [0],
                    "mg-srv-roles": [0],
                    "mg-srv-users": [0],
                    "kick-roles": [0],
                    "kick-users": [0],
                    "ban-roles": [0],
                    "ban-users": [0],
                    "mute-roles": [0],
                    "mute-users": [0],
                    "deafen-roles": [0],
                    "deafen-users": [0],
                    "mg-msg-roles": [0],
                    "mg-msg-users": [0],
                    "warn-users": [0],
                    "warn-roles": [0],
                    "unwarn-users": [0],
                    "unwarn-roles": [0]
                },
                "audit_logs": {
                    "ban": {
                        "log_channel": 0,
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False
                    },
                    "kick": {
                        "log_channel": 0,
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False
                    },
                    "unban": {
                        "log_channel": 0,
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False
                    },
                    "enter": {
                        "log_channel": 0,
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False
                    },
                    "leave": {
                        "log_channel": 0,
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False
                    },
                    "del_msg": { 
                        "log_channel": 0, 
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False 
                    }, 
                    "edited_msg": { 
                        "log_channel": 0, 
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False 
                    },
                    "warn": {
                        "log_channel": 0,
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False
                    },
                    "unwarn": {
                        "log_channel": 0,
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False
                    },
                    "vc_enter": { 
                        "log_channel": 0, 
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False 
                    },
                    "vc_leave": { 
                        "log_channel": 0, 
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False 
                    },
                    "add_usr_rol": { 
                        "log_channel": 0, 
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False 
                    },
                    "rm_usr_rol": { 
                        "log_channel": 0, 
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False 
                    },
                    "add_ch": { 
                        "log_channel": 0, 
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False 
                    },
                    "del_ch": { 
                        "log_channel": 0, 
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False 
                    },
                    "changed_av": { 
                        "log_channel": 0, 
                        "message": {
                            "embed": False,
                            "title": "",
                            "description": "",
                            "footer": "",
                            "color": "", 
                            "image": {
                                "has": False,
                                "param": ""
                            },
                            "thumbnail": {
                                "has": False,
                                "param": ""
                            },
                            "fields": {},
                            "message": ""
                        },
                        "activated": False 
                    }
                },
                "tickets": {}
            }
            
            success = save_server_data(guild, data)
            
            embed.description = "<:Si:825734135116070962> **¡Configuración restablecida con éxito!**\n\nTodos los ajustes han sido reconfigurados a los valores predeterminados."
            embed.colour = discord.Colour.green()
            
            if is_interaction:
                await message.edit(embed=embed, view=None)
            else:
                await message.edit(embed=embed, view=None)
        else:
            embed.description = "<:No:825734196256440340> **Operación cancelada**\n\nNo se ha realizado ningún cambio en la configuración del servidor."
            embed.colour = discord.Colour.red()
            
            if is_interaction:
                await message.edit(embed=embed, view=None)
            else:
                await message.edit(embed=embed, view=None)
                
    except Exception as e:
        print(f"Error en show_config_update: {str(e)}")
        if is_interaction:
            await ctx.followup.send("Ha ocurrido un error al procesar el comando.", ephemeral=True)
        else:
            await ctx.send("Ha ocurrido un error al procesar el comando.")

async def enable_confirm_button_and_update(message, view, bot):
    try:
        await asyncio.sleep(15)
        if not view.is_finished():
            view.confirm_button.disabled = False
            await message.edit(view=view)
    except Exception as e:
        print(f"Error habilitando el botón de confirmar: {str(e)}")