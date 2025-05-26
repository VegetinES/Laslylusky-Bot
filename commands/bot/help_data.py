COMMAND_CATEGORIES = {
    "Laslylusky": {
        "emoji": "<:laslylusky:1338239823441563718>",
        "commands": {
            "help": {
                "description": "Muestra todos los comandos disponibles",
                "usage": "`%help <comando>` | `/help comando:<comando>`",
                "options": {
                    "<comando>": "nombre del comando que quieres ver la ayuda"
                },
                "permissions": "Todos pueden utilizar este comando"
            },
            "invite": {
                "description": "Muestra el enlace de invitación del bot",
                "usage": "`%invite` | `/invite`",
                "permissions": "Todos pueden utilizar este comando",
            },
            "donate": {
                "description": "Manda al MD (mensaje privado) el enlace para hacer donaciones para contribuir en el desarrollo constante de Laslylusky",
                "usage": "`%donate`",
                "permissions": "Todos pueden utilizar este comando",
            },
            "updates": {
                "description": "Comando para saber las actualizaciones del bot",
                "usage": "`%updates <actualización>` | `/updates versión:<actualización>`",
                "options": {
                    "<actualización>": "versión que quieres saber las actualizaciones"
                },
                "permissions": "Todos pueden utilizar este comando"
            },
            "info": {
                "description": "Comando que muestra información del bot",
                "usage": "`%info` | `/info`",
                "permissions": "Todos pueden usar este comando"
            },
            "privacidad": {
                "description": "Comando que envía la política de privacidad al utilizar el bot",
                "usage": "`%privacidad` | `/privacidad`",
                "permissions": "Todos pueden utilizar este comando"
            },
            "savedatachat": {
                "description": "Comando para descargar tu conversación que has tenido con la IA",
                "usage": "`%savedatachat` | `/savedatachat`",
                "permissions": "Todos pueden usar este comando"
            },
            "reset-chat": {
                "description": "Comando para restablecer la conversación de la IA",
                "usage": "`%reset-chat` | `/reset-chat`",
                "permissions": "Todos pueden usar este comando"
            },
            "bugreport": {
                "description": "Comando para reportar un bug/error de un comando",
                "usage": "`%bugreport {mensaje}` | `/bugreport razonbug:{mensaje} error:<error> comando_ejecutado:<comando>`",
                "options": {
                    "{mensaje}": "mensaje del reporte del bug/error de un comando",
                    "<error>": "mensaje de error si es que existe",
                    "<comando_ejecutado>": "comando que causó el error"
                },
                "permissions": "Todos pueden usar este comando"
            },
            "botsuggest": {
                "description": "Comando para enviar una sugerencia de lo que quieres que se añada al bot",
                "usage": "`%botsuggest {sugerencia}` | `/botsuggest sugerencia:{sugerencia}`",
                "options": {
                    "{sugerencia}": "sugerencia que quieres que añadan al bot"
                },
                "permissions": "Todos pueden utilizar este comando"
            },
            "tos": {
                "description": "Comando para ver los términos de servicio del bot",
                "usage": "`%tos` | `/tos`",
                "permissions": "Todos pueden utilizar este comando"
            }
        }
    },
    "Diversión y juegos": {
        "emoji": "<:Diversion:838016251787345930>",
        "commands": {
            "kill": {
                "description": "Comando para intentar 'matar' a un jugador mencionado",
                "usage": "`%kill {usuario}`",
                "options": {
                    "{usuario}": "mención del usuario"
                },
                "permissions": "Todos pueden usar este comando"
            },
            "hug": {
                "description": "Comando para abrazar a alguien",
                "usage": "`%hug {usuario}`",
                "options": {
                    "{usuario}": "mención del usuario"
                },
                "permissions": "Todos pueden usar este comando"
            },
            "8ball": {
                "description": "Comando para consultar la bola mágica 8",
                "usage": "`%8ball {pregunta}` | `/8ball pregunta:{pregunta}`",
                "options": {
                    "{pregunta}": "pregunta que quieres hacerle a la bola mágica"
                },
                "permissions": "Todos pueden usar este comando"
            },
            "meme": {
                "description": "Comando que muestra un meme aleatorio en español",
                "usage": "`%meme` | `/meme`",
                "permissions": "Todos pueden usar este comando"
            },
            "morse": {
                "description": "Comando para convertir texto a código morse o viceversa",
                "usage": "`%morse {texto}` | `/morse texto_a_morse:<texto_a_morse> morse_a_texto:<morse_a_texto>`",
                "options": {
                    "{texto}": "texto que quieres convertir a morse",
                    "<texto_a_morse>": "texto que quieres convertir a morse",
                    "<morse_a_texto>": "texto en morse que quieres convertir a texto"
                },
                "permissions": "Todos pueden usar este comando",
                "extra": "Con `/morse` se puede convertir un texto a morse o al revés. Es obligatorio poner uno de los 2 argumentos"
            },
            "trivia": {
                "description": "Comando para jugar a trivia",
                "usage": "`%trivia` | `/trivia`",
                "permissions": "Todos pueden usar este comando"
            },
            "ahorcado": {
                "description": "Comando para jugar al ahorcado por lo menos 2 jugadores",
                "usage": "`%ahorcado` | `/ahorcado`",
                "permissions": "Todos pueden usar este comando"
            },
            "blackjack": {
                "description": "Comando para jugar al blackjack 2 o más jugadores",
                "usage": "`%blackjack` | `/blackjack`",
                "permissions": "Todos pueden usar este comando"
            },
            "insulto": {
                "description": "Comando para insultar a alguien de forma graciosa",
                "usage": "`%insulto <usuario>` | `/insulto usuario:<usuario>`",
                "options": {
                    "<usuario>": "mención del usuario al que quieres insultar"
                },
                "permissions": "Todos pueden usar este comando"
            },
            "buscaminas": {
                "description": "Comando para jugar al buscaminas",
                "usage": "`/buscaminas dificultad:{dificultad}`",
                "options": {
                    "{dificultad}": "dificultad del buscaminas (fácil, medio o difícil)"
                },
                "permissions": "Todos pueden usar este comando"
            },
            "piedrapapeltijera": {
                "description": "Comando para jugar al piedra papel o tijera 2 jugadores",
                "usage": "`%piedrapapeltijera` | `/piedrapapeltijera`",
                "permissions": "Todos pueden usar este comando"
            },
            "ruletarusa": {
                "description": "Comando para jugar a la ruleta rusa de 2 a 6 jugadores",
                "usage": "`%ruletarusa` | `/ruletarusa`",
                "permissions": "Todos pueden usar este comando"
            },
            "tictactoe": {
                "description": "Comando para jugar al tres en raya 2 jugadores",
                "usage": "`%tictactoe` | `/tictactoe`",
                "permissions": "Todos pueden usar este comando"
            },
            "conecta4": {
                "description": "Comando para jugar al conecta4 2 jugadores",
                "usage": "`%conecta4` | `/conecta4`",
                "permissions": "Todos pueden usar este comando"
            },
            "halago": {
                "description": "Comando para enviar un halago a un usuario",
                "usage": "`%halago <usuario>` | `/halago usuario:<usuario>`",
                "options": {
                    "<usuario>": "mención del usuario al que quieres mandarle un halago"
                },
                "permissions": "Todos pueden usar este comando"
            },
            "moneda": {
                "description": "Comando para lanzar una moneda y ver si sale cara o cruz",
                "usage": "`%moneda` | `/moneda`",
                "permissions": "Todos pueden usar este comando",
            },
            "dado": {
                "description": "Comando para lanzar un dado y ver el número que ha salido",
                "usage": "`%dado <caras>` | `/dado caras:<caras>`",
                "options": {
                    "<caras>": "número de caras del dado (por defecto 6)"
                },
                "permissions": "Todos pueden usar este comando"
            },
            "2048": {
                "description": "Comando para jugar al 2048 hasta llegar al número 8192 (por ahora)",
                "usage": "`%2048` | `/2048`",
                "permissions": "Todos pueden usar este comando"
            },
            "estadisticas-juegos": {
                "description": "Comando para ver estadisticas de minijuegos",
                "usage": "`%estadisticas-juegos` | `/estadisticas-juegos`",
                "permissions": "Todos pueden usar este comando",
            }
        }
    },
    "Moderación": {
        "emoji": "<:Moderacion:838015484032057384>",
        "commands": {
            "ban": {
                "description": "Comando para banear a un usuario, temporal o permanentemente",
                "usage": "`%ban {usuario} <razón>` | `/ban usuario:{usuario} razón:<razón> tiempo:<tiempo>`",
                "options": {
                    "{usuario}": "mención del usuario o su ID",
                    "<razón>": "razón del baneo",
                    "<tiempo>": "tiempo del baneo"
                },
                "permissions": "`ADMINISTRADOR`/`BANEAR USUARIOS`",
                "extra": "El tiempo se ha de poner en segundos (s), minutos (m), horas (h) o días (d), siendo 15 días el máximo del ban temporal"
            },
            "massban": {
                "description": "Comando para hacer un baneo masivo a varios usuarios",
                "usage": "`%massban {usuarios.coma} {razón}` | `/massban ids:{usuarios} razón:{razón}`",
                "options": {
                    "{usuarios.coma}": "IDs o mención de los usuarios a banear separados por comas",
                    "{usuarios}": "IDs de los usuarios a banear separados por espacios",
                    "{razón}": "razón del baneo masivo"
                },
                "permissions": "`ADMINISTRADOR`/`BANEAR USUARIOS`"
            },
            "unban": {
                "description": "Comando para desbanear al usuario pasándole su ID",
                "usage": "`%unban {usuario.id}` | `/unban usuario_id:{usuario.id}`",
                "options": {
                    "{usuario.id}": "ID del usuario a desbanear"
                },
                "permissions": "`ADMINISTRADOR`/`BANEAR USUARIOS`"
            },
            "kick": {
                "description": "Comando para expulsar al usuario mencionado",
                "usage": "`%kick {usuario} <razón>` | `/kick usuario:{usuario} razón:<razón>`",
                "options": {
                    "{usuario}": "mención del usuario o su ID",
                    "<razón>": "razón de la expulsión"
                },
                "permissions": "`ADMINISTRADOR`/`ESPULSAR USUARIOS`"
            },
            "clear": {
                "description": "Comando borrar la cantidad de mensajes que se escriba en el comando",
                "usage": "`%clear {número}` | `/clear cantidad:{número} usuarios:<usuarios> canal:<canal> excluir_usuarios:<excluir_usuarios>`",
                "options": {
                    "{número}": "número de mensajes a borrar",
                    "<usuarios>": "ID de los usuarios que quieres borrar los mensajes, separados por espacios",
                    "<canal>": "mención del canal donde quieres borrar los mensajes, por defecto el canal donde se ejecuta el comando",
                    "<excluir_usuarios>": "ID de los usuarios que quieres excluir de la eliminación de mensajes, separados por espacios"
                },
                "permissions": "`ADMINISTRADOR`/`GESTIONAR MENSAJES`"
            },
            "warn": {
                "description": "Comando para warnear al usuario mencionado",
                "usage": "`%warn {usuario} {razón}` | `/warn user:{usuario} reason:{razón}`",
                "options": {
                    "{usuario}": "mención del usuario o su ID",
                    "{razón}": "razón de la advertencia"
                },
                "permissions": "`ADVERTIR USUARIOS`/`ADMINISTRADOR`"
            },
            "unwarn": {
                "description": "Comando para quitar el warn al usuario mencionado que ya esté warneado",
                "usage": "`%unwarn {warnid} {razón}` | `/unwarn warn_id:{ID.warn} reason:{razón}`",
                "options": {
                    "{warnid}": "ID de la advertencia que quieres quitar",
                    "{razón}": "razón de la desadvertencia"
                },
                "permissions": "`MANEJAR ROLES`/`ADMINISTRADOR`",
                "extra": "Utiliza `/infracciones para ver las infracciones del usuario)"
            },
            "infracciones": {
                "description": "Comando para ver las infracciones puestas al usuario mencionado",
                "usage": "`%infracciones {usuario}` | `/infracciones user:{usuario}`",
                "options": {
                    "{usuario}": "mención del usuario o su ID"
                },
                "permissions": "`ADVERTIR USUARIOS`/`ADMINISTRADOR`/`BANEAR USUARIOS`/`EXPULSAR USUARIOS`/`GESTIONAR ROLES`/`GESTIONAR SERVIDOR`"
            },
            "moderador": {
                "description": "Comando para ver las sanciones puestas por el moderador que ejecutó el comando o el mencionado",
                "usage": "`%moderador <usuario>` | `/moderador moderador:<usuario>`",
                "options": {
                    "<usuario>": "mención del usuario o su ID"
                },
                "permissions": "`ADVERTIR USUARIOS`/`ADMINISTRADOR`/`BANEAR USUARIOS`/`EXPULSAR USUARIOS`/`GESTIONAR ROLES`/`GESTIONAR SERVIDOR`"
            },
            "mute": {
                "description": "Comando para aislar temporalmente a un usuario en el servidor",
                "usage": "`%mute {usuario} {tiempo} <razón>` | `/mute usuario:{usuario} tiempo:{tiempo} razón:<razón>`",
                "options": {
                    "{usuario}": "mención del usuario o su ID",
                    "{tiempo}": "tiempo del aislamiento",
                    "<razón>": "razón del aislamiento"
                },
                "permissions": "`ADMINISTRADOR`/`MUTEAR USUARIOS`/`MODERAR MIEMBROS`",
                "extra": "El tiempo se ha de poner en segundos (s), minutos (m), horas (h) o días (d), siendo 7 días el máximo del aislamiento"
            },
            "unmute": {
                "description": "Comando para aislar temporalmente a un usuario en el servidor",
                "usage": "`%unmute {usuario} <razón>` | `/unmute usuario:{usuario} razón:<razón>`",
                "options": {
                    "{usuario}": "mención del usuario o su ID",
                    "<razón>": "razón del des-aislamiento"
                },
                "permissions": "`ADMINISTRADOR`/`MUTEAR USUARIOS`/`MODERAR MIEMBROS`"
            }
        }
    },
    "Configuración": {
        "emoji": "<:Configurar:842423920850370580>",
        "commands": {
            "slowmode": {
                "description": "Comando de para cambiar el cooldown del canal donde se ejecuta el comando",
                "usage": "`%slowmode {tiempo} <razón>`",
                "options": {
                    "{tiempo}": "tiempo del cooldown",
                    "<razón>": "razón del cooldown"
                },
                "permissions": "`GESTIONAR CANALES`"
            },
            "config": {
                "description": "Comando para configurar al bot en el servidor donde se ejecute",
                "usage": "`/config {opción}`",
                "options": {
                    "{opción}": "opción que quieres configurar: \n> - `/config cmd comando:{comando} estado:{estado}` -> activar/desactivar comandos\n>   - `{comando}`: nombre del comando que quieres activar o desactivar\n>   - `{estado}`: estado del comando (activado/desactivado)\n> - `/config data` -> ver datos de configuración del bot en el servidor \n> - `/config update` -> restablecer configuración del bot en el servidor\n> - `/config help` -> muestra ayuda de la configuración \n> - `/config logs tipo:{tipo}` -> configurar logs del servidor\n>   - `{tipo}`: tipo de logs a configurar \n>  `/config perms permiso:{permiso} acción:{acción} roles:<roles> usuarios:<usuarios>` -> establecer/quitar permisos de comandos del bot a usuarios o roles\n>   - `{permiso}`: nombre del permiso que quieres establecer o quitar\n>   - `{acción}`: acción a realizar (añadir/quitar)\n>   - `<roles>`: ID de los roles a los que quieres añadir o quitar el permiso, separados por espacios\n>   - `<usuarios>`: ID de los usuarios a los que quieres añadir o quitar el permiso, separados por espacios\n> - `/config tickets` -> gestionar tickets del servidor",
                },
                "permissions": "`ADMINISTRADOR`"
            },
            "voicesetup": {
                "description": "Comando para gestionar canales de voz temporales en un servidor",
                "usage": "`/voicesetup`",
                "permissions": "ADMINISTRADOR"
            }
        }
    },
    "Información": {
        "emoji": "<:Info:837631728368746548>",
        "commands": {
            "userinfo": {
                "description": "Comando que envía la información del usuario mencionado, o del usuario que ejecutó el comando",
                "usage": "`%userinfo <usuario>` | `/userinfo usuario:<usuario>`",
                "options": {
                    "<usuario>": "mención del usuario o su ID"
                },
                "permissions": "Todos pueden usar este comando"
            },
            "avatar": {
                "description": "Comando que envía la imagen de perfil tuya o del usuario mencionado",
                "usage": "`%avatar <usuario>` | `/avatar usuario:<usuario>`",
                "options": {
                    "<usuario>": "mención del usuario o su ID"
                },
                "permissions": "Todos pueden usar este comando"
            },
            "servericon": {
                "description": "Comando que envía la imagen del servidor donde se ejecutó",
                "usage": "`%servericon` | `/servericon`",
                "permissions": "Todos pueden usar este comando"
            },
            "serverinfo": {
                "description": "Comando que envía la información del servidor donde se ha utilizado",
                "usage": "`%serverinfo` | `/serverinfo`",
                "permissions": "Todos pueden usar este comando"
            }
        }
    },
    "Utilidad": {
        "emoji": "<:Utilidad:838016540246147133>",
        "commands": {
            "embed": {
                "description": "Comando para crear y enviar embed a través del bot o un webhook",
                "usage": "`/embed cargar:<cargar> mensaje_id:<mensaje_id>`",
                "options": {
                    "<cargar>": "archivo JSON que quieres cargar para crear el embed",
                    "<mensaje_id>": "ID del mensaje al que quieres actualizar el embed"
                },
                "permissions": "ADMINISTRADOR"
            },
            "laslylusky": {
                "description": "Comando para tener una conversación con Laslylusky gracias a la IA",
                "usage": "<@784774864766500864> {texto}",
                "options": {
                    "{texto}": "mensaje que quieres decirle a la IA"
                },
                "permissions": "Todos pueden usar este comando",
                "extra": "La IA mantendrá un chat con el usuario siempre, recordando la conversación a no ser que el usuario la elimine. Para eliminar el chat con la IA de ese canal y empezar otro escribe `%reset-chat`. La AI solo podrá mantener conversación con solo 1 usuario"
            },
            "id": {
                "description": "Comando que muestra información de IDs de emojis, usuarios, canales o roles",
                "usage": "`/id tipo:{tipo} {opción}`",
                "options": {
                    "{tipo}": "tipo de ID que quieres ver (emoji, usuario, canal o rol)",
                    "{opción}": "`emoji`, `usuario`, `canal` o `rol`"
                },
                "permissions": "Todos pueden usar este comando"
            },
            "recordatorio": {
                "description": "Comando para crear recordatorios que el bot te enviará por MD",
                "usage": "`/recordatorio {opción}`",
                "options": {
                    "{opción}": "`ver`, `crear` o `gestionar`"
                },
                "permissions": "Todos pueden usar este comando",
                "extra": "Para la zona horaria en GMT mira tu ubicación en [este enlace](https://greenwichmeantime.com/time-zone/)"
            },
            "cumpleaños": {
                "description": "Comando para gestionar los cumpleaños en un servidor",
                "usage": "`/cumpleaños {opción}`",
                "options": {
                    "{opción}": "`ver`, `establecer`, `eliminar` o `configurar`"
                },
                "permissions": "Todos pueden usar este comando / ADMINISTRADOR",
                "extra": "Para la zona horaria en GMT mira la ubicación en [este eºnlace](https://greenwichmeantime.com/time-zone/)"
            },
            "nivel": {
                "description": "Comando para gestionar los niveles en un servidor",
                "usage": "`/nivel {opción}`",
                "options": {
                    "{opción}": "`ver`, `gestionar`, `top` o `configurar`"
                },
                "permissions": "Todos pueden usar este comando / ADMINISTRADOR"
            },
            "comprobar-virus": {
                "description": "Comando para comprobar si un archivo o enlace tiene virus",
                "usage": "`/comprobar-virus archivo:<archivo> enlace:<enlace>`",
                "options": {
                    "<archivo>": "archivo que quieres comprobar",
                    "<enlace>": "enlace que quieres comprobar"
                },
                "permissions": "Todos pueden usar este comando",
                "extra": "Es obligatorio poner uno de los 2 argumentos, y no se pueden poner los 2 a la vez."
            }
        }
    },
    "Minecraft": {
        "emoji": "<:Minecraft:837706204079194123>",
        "commands": {
            "mcstatus": {
                "description": "Comando que muestra el estado de un servidor de Minecraft, ya sea de Java o Bedrock",
                "usage": "`%mcstatus {serverip} {plataforma}` | `/mcstatus ip:{serverip} plataforma:{plataforma}`",
                "options": {
                    "{serverip}": "IP del servidor de Minecraft",
                    "{plataforma}": "plataforma del servidor de Minecraft (java o bedrock)"
                },
                "permissions": "Todos pueden usar este comando"
            },
            "mcuser": {
                "description": "Comando que muestra información de la cuenta de Minecraft que se ha pasado",
                "usage": "`%mcuser {usuario}`",
                "options": {
                    "{usuario}": "nombre de usuario de Minecraft"
                },
                "permissions": "Todos pueden usar este comando"
            },
            "hypixel": {
                "description": "Comando que muestra las estadísticas de un jugador en hypixel",
                "usage": "`%hypixel {usuario}`",
                "options": {
                    "{usuario}": "nombre de usuario de Minecraft"
                },
                "permissions": "Todos pueden usar este comando"
            }
        }
    },
    "NSFW": {
        "emoji": "<:NSFW:838014363893366785>",
        "commands": {
            "boobs": {
                "description": "Comando que envía tetas de mujeres (por ahora)(el diablo)",
                "usage": "`%boobs`",
                "permissions": "Todos pueden utilizar este comando",
                "extra": "**Solo se puede utilizar en un canal NSFW**"
            },
            "anal": {
                "description": "Comando que envía sexo anal",
                "usage": "`%anal`",
                "permissions": "Todos pueden utilizar este comando",
                "extra": "**Solo se puede utilizar en un canal NSFW**"
            },
            "ass": {
                "description": "Comando que envía culos de mujeres",
                "usage": "`%ass`",
                "permissions": "Todos pueden utilizar este comando",
                "extra": "**Solo se puede utilizar en un canal NSFW**"
            },
            "pgif": {
                "description": "Comando que envía gifs porno",
                "usage": "`%pgif`",
                "permissions": "Todos pueden utilizar este comando",
                "extra": "**Solo se puede utilizar en un canal NSFW**"
            },
            "4k": {
                "description": "Comando que envía contenido porno en 4k",
                "usage": "`%4k`",
                "permissions": "Todos pueden utilizar este comando",
                "extra": "**Solo se puede utilizar en un canal NSFW**"
            },
            "pussy": {
                "description": "Comando que envía coños de mujeres",
                "usage": "`%pussy`",
                "permissions": "Todos pueden utilizar este comando",
                "extra": "**Solo se puede utilizar en un canal NSFW**"
            },
            "hboobs": {
                "description": "Comando que envía tetas de hentai",
                "usage": "`%hboobs`",
                "permissions": "Todos pueden utilizar este comando",
                "extra": "**Solo se puede utilizar en un canal NSFW**"
            },
            "hass": {
                "description": "Comando que envía culos de hentai",
                "usage": "`%hass`",
                "permissions": "Todos pueden utilizar este comando",
                "extra": "**Solo se puede utilizar en un canal NSFW**"
            },
            "hanal": {
                "description": "Comando que envía anal de hentai",
                "usage": "`%hanal`",
                "permissions": "Todos pueden utilizar este comando",
                "extra": "**Solo se puede utilizar en un canal NSFW**"
            },
            "blowjob": {
                "description": "Comando que envía mamadas",
                "usage": "`%blowjob`",
                "permissions": "Todos pueden utilizar este comando",
                "extra": "**Solo se puede utilizar en un canal NSFW**"
            }
        }
    }
}