COMMAND_CATEGORIES = {
    "Laslylusky": {
        "emoji": "<:laslylusky:1338239823441563718>",
        "commands": {
            "help": {
                "description": "Muestra todos los comandos disponibles",
                "usage": "%help [comando]` | </help:1346858629889790063>",
                "permissions": "Todos pueden utilizar este comando"
            },
            "invite": {
                "description": "Muestra el enlace de invitación del bot",
                "usage": "%invite` | </invite:1348016312235982941>",
                "permissions": "Todos pueden utilizar este comando"
            },
            "donate": {
                "description": "Manda al MD (mensaje privado) el enlace para hacer donaciones para contribuir en el desarrollo constante de Laslylusky",
                "usage": "%donate",
                "permissions": "Todos pueden utilizar este comando"
            },
            "updates": {
                "description": "Comando para saber las actualizaciones del bot",
                "usage": "%updates",
                "permissions": "Todos pueden utilizar este comando"
            },
            "info": {
                "description": "Comando que muestra información del bot",
                "usage": "%info` | </info:1348248452080996404>",
                "permissions": "Todos pueden usar este comando"
            },
            "privacidad": {
                "description": "Comando que envía la política de privacidad al utilizar el bot",
                "usage": "%privacidad` | </privacidad:1348016059499810860>",
                "permissions": "Todos pueden utilizar este comando"
            },
            "savedatachat": {
                "description": "Comando para descargar tu conversación que has tenido con la IA",
                "usage": "%savedatachat` | </savedatachat:1348248452080996408>",
                "permissions": "Todos pueden usar este comando"
            },
            "reset-chat": {
                "description": "Comando para restablecer la conversación de la IA",
                "usage": "%reset-chat` | </reset-chat:1348248452080996409>",
                "permissions": "Todos pueden usar este comando"
            }
        }
    },
    "Diversión": {
        "emoji": "<:Diversion:838016251787345930>",
        "commands": {
            "kill": {
                "description": "Comando para intentar 'matar' a un jugador mencionado",
                "usage": "%kill {usuario.mencion}",
                "permissions": "Todos pueden usar este comando",
                "extra": "No escribas en el comando `{}`. `{usuario.mencion}` debe ser sustituido por la mención a un usuario al que quieres intentar 'matar'"
            },
            "hug": {
                "description": "Comando para abrazar a alguien",
                "usage": "%hug {usuario}",
                "permissions": "Todos pueden usar este comando",
                "extra": "No escribas en el comando `{}`. `{usuario}` debe ser sustituido por la mención a un usuario al que quieres abrazar"
            }
        }
    },
    "Moderación": {
        "emoji": "<:Moderacion:838015484032057384>",
        "commands": {
            "ban": {
                "description": "Comando para banear a los usuarios mencionados",
                "usage": "%ban {usuario} {razón}",
                "permissions": "`ADMINISTRADOR`/`BANEAR USUARIOS`",
                "extra": "No escribas en el comando `{}`. `{usuario}` tiene que ser sustituido por la mención al usuario o su ID, y `{razón}` por la razón del baneo"
            },
            "unban": {
                "description": "Comando para desbanear al usuario pasándole su ID",
                "usage": "%unban {usuario.id}",
                "permissions": "`ADMINISTRADOR`/`BANEAR USUARIOS`",
                "extra": "No escribas en el comando `{}`. `{usuario.id}` tiene que ser sustituido por id del usuario baneado"
            },
            "kick": {
                "description": "Comando para expulsar al usuario mencionado",
                "usage": "%kick {usuario} {razón}",
                "permissions": "`ADMINISTRADOR`/`ESPULSAR USUARIOS`",
                "extra": "No escribas en el comando `{}`. `{usuario}` tiene que ser sustituido por la mención al usuario o su ID, y `{razón}` por la razón de la expulsión"
            },
            "clear": {
                "description": "Comando de de moderación para borrar la cantidad de mensajes que se escriba en el comando",
                "usage": "%clear {número}",
                "permissions": "`ADMINISTRADOR`/`GESTIONAR MENSAJES`",
                "extra": "No escribas en el comando `{}`. `{número}` tiene que ser sustituido por un número entre 1 a 100 que significa la cantidad de mensajes que quieres borrar"
            },
            "warn": {
                "description": "Comando para mutear al usuario mencionado de forma definitiva hasta que se lo quite de forma manual",
                "usage": "%warn {usuario} {razón}` | </warn:1348248454610161749>",
                "permissions": "`ADVERTIR USUARIOS`/`ADMINISTRADOR`",
                "extra": "No escribas en el comando `{}`. Sustituye `{usuario}` por la mención del usuario o la ID del usuario a quien se quiere poner una advertencia, y `{razón}` por la razón de la advertencia. \nSe recomienda utilizar </warn:1345790007666806928>. Es necesario configurar el comando en config"
            },
            "unwarn": {
                "description": "Comando para quitar el mute al usuario mencionado que ya esté silenciado",
                "usage": "%unwarn {warnid} {razón}` | </unwarn:1348248454610161750>",
                "permissions": "`MANEJAR ROLES`/`ADMINISTRADOR`",
                "extra": "No escribas en el comando `{}`. Sustituye `{ID.warn}` por el ID de la advertencia (utilizar </infracciones:1345790007666806926> para ver las infracciones del usuario), y `{razón}` por la razón de porqué se quita la advertencia. \nSe recomienda utilizar </unwarn:1345790007666806929>. Es necesario configurar el comando en config"
            },
            "infracciones": {
                "description": "Comando para ver las infracciones puestas al usuario mencionado",
                "usage": "%infracciones {usuario}` | </infracciones:1348248454610161746>",
                "permissions": "`ADVERTIR USUARIOS`/`ADMINISTRADOR`/`BANEAR USUARIOS`/`EXPULSAR USUARIOS`/`GESTIONAR ROLES`/`GESTIONAR SERVIDOR`",
                "extra": "No escribas en el comando `{}`. Sustituye `{usuario}` por la mención del usuario que quieres ver sus infracciones"
            },
            "moderador": {
                "description": "Comando para ver las sanciones puestas por el moderador que ejecutó el comando o el mencionado",
                "usage": "%moderador [usuario]` | </moderador:1348248454610161748>",
                "permissions": "`ADVERTIR USUARIOS`/`ADMINISTRADOR`/`BANEAR USUARIOS`/`EXPULSAR USUARIOS`/`GESTIONAR ROLES`/`GESTIONAR SERVIDOR`",
                "extra": "No escribas en el comando `[]`. Sustituye `[usuario]` por la mención del usuario que quieres ver sanciones aplicadas"
            }
        }
    },
    "Configuración": {
        "emoji": "<:Configurar:842423920850370580>",
        "commands": {
            "slowmode": {
                "description": "Comando de para cambiar el cooldown del canal donde se ejecuta el comando",
                "usage": "%slowmode {tiempo} [razón]",
                "permissions": "`GESTIONAR CANALES`",
                "extra": ""
            },
            "config": {
                "description": "Comando para configurar al bot en el servidor donde se ejecute",
                "usage": "%config",
                "permissions": "`ADMINISTRADOR`",
                "extra": "Para utilizar la configuración de forma más detallada y fácil los comandos </config help:1348248454610161751>, </config data:1348248454610161751>, </config update:1348248454610161751>, </config perms:1348248454610161751>, </config logs:1348248454610161751> o </config cmd:1348248454610161751>"
            }
        }
    },
    "Información": {
        "emoji": "<:Info:837631728368746548>",
        "commands": {
            "userinfo": {
                "description": "Comando que envía la información del usuario mencionado, o del usuario que ejecutó el comando",
                "usage": "%userinfo` / `%userinfo {usuario}",
                "permissions": "Todos pueden usar este comando",
                "extra": "No escribas en el comando `{}`. `{usuario}` tiene que ser sustituido por la mención del usuario"
            },
            "avatar": {
                "description": "Comando que envía la imagen de perfil tuya o del usuario mencionado",
                "usage": "%avatar` / `%avatar {usuario}",
                "permissions": "Todos pueden usar este comando",
                "extra": "No escribas en el comando `{}`. `{usuario}` tiene que ser sustituido por la mención del usuario"
            },
            "servericon": {
                "description": "Comando que envía la imagen del servidor donde se ejecutó",
                "usage": "%servericon",
                "permissions": "Todos pueden usar este comando"
            },
            "serverinfo": {
                "description": "Comando que envía la información del servidor donde se ha utilizado",
                "usage": "%serverinfo",
                "permissions": "Todos pueden usar este comando"
            }
        }
    },
    "Utilidad": {
        "emoji": "<:Utilidad:838016540246147133>",
        "commands": {
            "embed": {
                "description": "Comando simple de un embed",
                "usage": "%embed {mensaje}",
                "permissions": "Todos pueden usar este comando",
                "extra": "No escribas en el comando `{}`. `{mensaje}` tiene que ser sustituido por el mensaje que quieres que aparezca en el embed"
            },
            "laslylusky": {
                "description": "Comando para tener una conversación con Laslylusky gracias a la IA",
                "usage": "@Laslylusky {texto}",
                "permissions": "Todos pueden usar este comando",
                "extra": "No escribas en el comando `{}`. `{texto}` debe ser sustituido por el mensaje que quieras decirle a la IA. La IA mantendrá un chat con el usuario siempre, recordando la conversación a no ser que el usuario la elimine. Para eliminar el chat con la IA de ese canal y empezar otro escribe `%reset-chat`. La AI solo podrá mantener conversación con solo 1 usuario"
            }
        }
    },
    "Minecraft": {
        "emoji": "<:Minecraft:837706204079194123>",
        "commands": {
            "mcstatus": {
                "description": "Comando que muestra el estado de un servidor de Minecraft, ya sea de Java o Bedrock",
                "usage": "%mcstatus {serverip} {plataforma}",
                "permissions": "Todos pueden usar este comando",
                "extra": "No escribas en el comando `{}`. `{serverip}` tiene que ser sustituido por la IP del servidor y `{plataforma}` por la plataforma de Minecraft (poner `java` o `bedrock`)"
            },
            "mcuser": {
                "description": "Comando que muestra información de la cuenta de Minecraft que se ha pasado",
                "usage": "%mcuser {usuario}",
                "permissions": "Todos pueden usar este comando",
                "extra": "No escribas en el comando `{}`. `{usuario}` tiene que ser sustituido por el nombre del jugador"
            },
            "hypixel": {
                "description": "Comando que muestra las estadísticas de un jugador en hypixel",
                "usage": "%hypixel {usuario}",
                "permissions": "Todos pueden usar este comando",
                "extra": "No escribas en el comando `{}`. `{usuario}` tiene que ser sustituido por el nombre del jugador"
            }
        }
    },
    "NSFW": {
        "emoji": "<:NSFW:838014363893366785>",
        "commands": {
            "boobs": {
                "description": "Comando que envía tetas de mujeres (por ahora)(el diablo)",
                "usage": "%boobs",
                "permissions": "Todos pueden utilizar este comando. **Solo se puede utilizar en un canal NSFW**"
            },
            "anal": {
                "description": "Comando que envía sexo anal",
                "usage": "%anal",
                "permissions": "Todos pueden utilizar este comando. **Solo se puede utilizar en un canal NSFW**"
            },
            "ass": {
                "description": "Comando que envía culos de mujeres",
                "usage": "%ass",
                "permissions": "Todos pueden utilizar este comando. **Solo se puede utilizar en un canal NSFW**"
            },
            "pgif": {
                "description": "Comando que envía gifs porno",
                "usage": "%pgif",
                "permissions": "Todos pueden utilizar este comando. **Solo se puede utilizar en un canal NSFW**"
            },
            "4k": {
                "description": "Comando que envía contenido porno en 4k",
                "usage": "%4k",
                "permissions": "Todos pueden utilizar este comando. **Solo se puede utilizar en un canal NSFW**"
            },
            "pussy": {
                "description": "Comando que envía coños de mujeres",
                "usage": "%pussy",
                "permissions": "Todos pueden utilizar este comando. **Solo se puede utilizar en un canal NSFW**"
            },
            "hboobs": {
                "description": "Comando que envía tetas de hentai",
                "usage": "%hboobs",
                "permissions": "Todos pueden utilizar este comando. **Solo se puede utilizar en un canal NSFW**"
            },
            "hass": {
                "description": "Comando que envía culos de hentai",
                "usage": "%hass",
                "permissions": "Todos pueden utilizar este comando. **Solo se puede utilizar en un canal NSFW**"
            },
            "hanal": {
                "description": "Comando que envía anal de hentai",
                "usage": "%hanal",
                "permissions": "Todos pueden utilizar este comando. **Solo se puede utilizar en un canal NSFW**"
            },
            "blowjob": {
                "description": "Comando que envía mamadas",
                "usage": "%blowjob",
                "permissions": "Todos pueden utilizar este comando. **Solo se puede utilizar en un canal NSFW**"
            }
        }
    },
    "Reportar bug | Enviar sugerencia :incoming_envelope:": {
        "emoji": ":pushpin:",
        "commands": {
            "bugreport": {
                "description": "Comando para reportar un bug/error de un comando",
                "usage": "%bugreport {mensaje}` | </bugreport:1348248452080996406>",
                "permissions": "Todos pueden usar este comando",
                "extra": "No escribas en el comando `{}`. `{mensaje}` tiene que ser sustituido por el mensaje del reporte del bug/error de un comando. \nSe recomienda usar </bugreport:1342426095617708145>"
            },
            "bot-suggest": {
                "description": "Comando para enviar una sugerencia de lo que quieres que se añada al bot",
                "usage": "%bot-suggest {sugerencia}` | </botsuggest:1348248452080996407>",
                "permissions": "Todos pueden utilizar este comando",
                "extra": "No escribas en el comando `{}`. `{sugerencia}` tiene que ser sustituido por la sugerencia que quieres que añadan al bot"
            }
        }
    }
}