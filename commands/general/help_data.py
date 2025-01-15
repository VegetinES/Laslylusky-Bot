COMMAND_CATEGORIES = {
    "General": {
        "emoji": "<:General:838015864455299082>",
        "commands": {
            "help": {
                "description": "Muestra todos los comandos disponibles",
                "usage": "%help [comando]",
                "permissions": "Todos pueden usar este comando"
            },
            "invite": {
                "description": "Muestra el enlace de invitación del bot",
                "usage": "%invite",
                "permissions": "Todos pueden usar este comando"
            },
            "discord": {
                "description": "Comando que envía el enlace del servidor oficial del bot",
                "usage": "%discord",
                "permissions": "Todos pueden utilizar este comando"
            },
            "soon": {
                "description": "Comando que muestra que es lo que puede ser que añadan proximamente al bot",
                "usage": "%soon",
                "permissions": "Todos pueden utilizar este comando"
            },
            "vote": {
                "description": "Comando que envía el enlace para votar al bot en top.gg",
                "usage": "%vote",
                "permissions": "Todos pueden utilizar este comando"
            },
            "updates": {
                "description": "Comando para saber las actualizaciones del bot",
                "usage": "%updates",
                "permissions": "Todos pueden utilizar este comando"
            },
            "uptime": {
                "description": "Comando que envía la cantidad de tiempo que lleva online el bot",
                "usage": "%uptime",
                "permissions": "Todos pueden utilizar este comando"
            },
            "steam": {
                "description": "Comando que envía sobre un juego de Steam",
                "usage": "%steam {juego.steam}",
                "permissions": "Todos pueden utilizar este comando"
            },
            "instagram": {
                "description": "Comando que envía información del usuario de instagram que se puso",
                "usage": "%instagram {ig.usuario}",
                "permissions": "Todos pueden utilizar este comando"
            },
            "privacidad": {
                "description": "Comando que envía la política de privacidad al utilizar el bot",
                "usage": "%privacidad",
                "permissions": "Todos pueden utilizar este comando"
            }
        }
    },
    "Diversión": {
        "emoji": "<:Diversion:838016251787345930>",
        "commands": {
            "8ball": {
                "description": "Comando que responde con Sí o No a la pregunta",
                "usage": "%8ball {pregunta}",
                "permissions": "Todos pueden usar este comando",
                "extra": "No escribas en el comando `{}`. La `{pregunta}` debe ser una que se pueda responder con Sí o No"
            },
            "confession": {
                "description": "Comando parecido al del bot Chocolat, solo que este se puede utilizar en cualquier canal",
                "usage": "%confession {mensaje}",
                "permissions": "Todos pueden usar este comando",
                "extra": "No escribas en el comando `{}`. `{mensaje}` tiene que ser sustituido por el mensaje que quieres que aparezca"
            },
            "impostor": {
                "description": "Comando de diversión que al mencionar a un usuario (o el que ejecuta el comando), dirá si es o no un impostor",
                "usage": "%impostor` | `%impostor {usuario}",
                "permissions": "Todos pueden usar este comando",
                "extra": "No escribas en el comando `{}`. `{usuario}` tiene que ser sustituido por la mención de un usuario"
            },
            "love": {
                "description": "Comando de diversión que al mencionar a un usuario, el bot mandará un porcentaje aleatorio de como sería el amor entre el usuario mencionado y el que ejecutó el comando",
                "usage": "%love {usuario}",
                "permissions": "Todos pueden utilizar el comando",
                "extra": "No escribas en el comando `{}`. `{usuario}` tiene que ser sustituido por el usuario mencionado"
            },
            "hack": {
                "description": "Comando para hackear de broma al usuario mencionado",
                "usage": "%hack {usuario.mencion}",
                "permissions": "Todos pueden utilizar este comando",
                "extra": "No escribas en el comando `{}`. Sustituye `{usuario.mencion}` por la mención de un usuario"
            },
            "presentacion": {
                "description": "Comando de diversión que envía una imagen con las palabras que hayas puesto en el comando",
                "usage": "%presentacion {texto}",
                "permissions": "Todos pueden utilizar este comando",
                "extra": "No escribas `{}`. `{texto}` se sustituye por el texto que quieres que aparezca en el comando"
            },
            "meme": {
                "description": "Comando que envía un meme aleatorio",
                "usage": "%meme",
                "permissions": "Todos pueden utilizar este comando"
            },
            "captcha": {
                "description": "No hay información",
                "usage": "No hay información",
                "permissions": "No hay información",
                "extra": "No hay información"
            },
            "dm": {
                "description": "Comando que envía un mensaje por privado a la id del usuario o al usuario que se mencionó",
                "usage": "%dm {usuario.id} [mensaje]`/`%dm {usuario.mencion} [mensaje]",
                "permissions": "Todos pueden utilizar este comando",
                "extra": "No escribas en el comando `{}` ni `[]`. Sustituye `{usuario.id}` por la id del usuario que quieres que le llegue el mensaje | Sustituye `{usuario.mencion}` por la mención del usuario que quieras enviar el mensaje | Sustituye `[mensaje]` por el mensaje que quieras enviar al usuario"
            }
        }
    },
    "Moderación": {
        "emoji": "<:Moderacion:838015484032057384>",
        "commands": {
            "ban": {
                "description": "Comando para banear a los usuarios mencionados",
                "usage": "%ban {usuario.mención} [razón]",
                "permissions": "`ADMINISTRADOR`/`BANEAR USUARIOS`",
                "extra": "No escribas en el comando `[]` ni `{}`. `{usuario.mención}` tiene que ser sustituido por la mención del usuario a quien quieres banear"
            },
            "kick": {
                "description": "Comando para expulsar al usuario mencionado",
                "usage": "%kick {usuario.mención} [razón]",
                "permissions": "`ADMINISTRADOR`/`ESPULSAR USUARIOS`",
                "extra": "No escribas en el comando `[]` ni `{}`. `{usuario.mención}` tiene que ser sustituido por la mención del usuario a quien quieres expulsar"
            },
            "clear": {
                "description": "Comando de de moderación para borrar la cantidad de mensajes que se escriba en el comando",
                "usage": "%clear {número}",
                "permissions": "Necesitas tener el permiso de gestionar mensajes",
                "extra": "No escribas en el comando `{}`. `{número}` tiene que ser sustituido por un número entre 1 a 100 que significa la cantidad de mensajes que quieres borrar"
            },
            "mute": {
                "description": "Comando para mutear al usuario mencionado",
                "usage": "%mute {usuario} [razón]",
                "permissions": "`MANEJAR ROLES`/`ADMINISTRADOR`",
                "extra": "No escribas en el comando `{}` ni `[]`. `{usuario}` tiene que ser sustituido por el usuario mencionado que quieras mutear | `[razón]` tiene que ser sustituido por la razón del mute"
            },
            "idban": {
                "description": "Comando para banear al usuario de la ID del usuario que has puesto en el comando",
                "usage": "%idban {id} [razón]",
                "permissions": "`ADMINISTRADOR`/`BANEAR USUARIOS`",
                "extra": "No escribas en el comando `[]` ni `{}`. `{id}` tiene que ser sustituido por la id del usuario que quieres banear | `[razón]` tiene que ser sustituido por la razón del ban"
            },
            "unmute": {
                "description": "Comando para quitar el mute al usuario mencionado que ya esté silenciado",
                "usage": "%unmute {usuario.mencion}",
                "permissions": "`MANEJAR ROLES`/`ADMINISTRADOR`",
                "extra": "No escribas en el comando `{}`. Sustituye `{usuario.mencion}` por la mención del usuario a quien quieres quitar el mute"
            },
            "config": {
                "description": "Comando para configurar opciones de moderación, logs y comandos del bot en el servidor donde se utiliza",
                "usage": "%config` (para mostrar los comandos a configurar) / `%config {comando}",
                "permissions": "`ADMINISTRADOR`",
                "extra": "No escribas en el comando `{}`. Sustituye `{comando}` por el comando que quieras configurar en tu servidor"
            }
        }
    },
    "Información": {
        "emoji": "<:Info:837631728368746548>",
        "commands": {
            "user": {
                "description": "Comando que envía la información del usuario mencionado, o del usuario que ejecutó el comando",
                "usage": "%user` / `%user {usuario}",
                "permissions": "Todos pueden usar este comando",
                "extra": "No escribas en el comando `{}`. `{usuario}` tiene que ser sustituido por la mención del usuario"
            },
            "ping": {
                "description": "Comando que envía el ping que tiene el bot",
                "usage": "%ping",
                "permissions": "Todos pueden usar este comando"
            },
            "avatar": {
                "description": "Comando que envía la imagen de perfil tuya o del usuario mencionado",
                "usage": "%avatar` / `%avatar {usuario}",
                "permissions": "Todos pueden usar este comando",
                "extra": "No escribas en el comando `{}`. `{usuario}` tiene que ser sustituido por la mención del usuario"
            },
            "about": {
                "description": "Comando que envía una breve descripción del bot",
                "usage": "`%about",
                "permissions": "Todos pueden usar este comando"
            },
            "guild": {
                "description": "Comando que dice en cuantos servidores está",
                "usage": "%guild",
                "permissions": "Todos pueden usar este comando"
            },
            "servericon": {
                "description": "Comando que envía la imagen del servidor donde se ejecutó",
                "usage": "%servericon",
                "permissions": "Todos pueden usar este comando"
            },
            "stats": {
                "description": "Comando que envía la información del servidor donde se ha utilizado (puede tener algunos bugs)",
                "usage": "%stats",
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
            "iembed": {
                "description": "Comando que envía un embed con la imagen del enlace que le has escrito",
                "usage": "%iembed {enlace.imagen}",
                "permissions": "Todos pueden usar este comando",
                "extra": "No escribas en el comando `{}`. `{enlace.imagen}` tiene que ser sustituido por el enlace de la imagen que quieres que aparezca en el embed"
            },
            "say": {
                "description": "Comando que hace que el bot envíe el mensaje que tu le escribes",
                "usage": "%say {mensaje}",
                "permissions": "Todos pueden usar este comando",
                "extra": "No escribas en el comando `{}`. `{mensaje}` tiene que ser sustituido por el mensaje que quieres que envíe el bot. Si el mensaje contiene `@everyone` o `@here`, el bot no enviará el mensaje"
            },
            "slowmode": {
                "description": "Comando de para cambiar el cooldown del canal donde se ejecuta el comando",
                "usage": "%slowmode {tiempo} [razón]",
                "permissions": "`GESTIONAR CANALES`",
                "extra": ""
            },
            "jumbo": {
                "description": "",
                "usage": "",
                "permissions": "Todos pueden usar este comando",
                "extra": "No escribas en el comando `{}` ni `[]`. `{tiempo}` tiene que ser sustituido por el número del tiempo que quieres que sea el cooldown en el canal (el tiempo viene en segundos) | `[razón]` tiene que ser sustituido por el mensaje de la razón por la que se va a cambiar el cooldown (esto es obligatorio)"
            },
            "calculadora": {
                "description": "Comando que calcula una fórmula matemática",
                "usage": "%calculadora {fórmula}",
                "permissions": "Todos pueden usar este comando",
                "extra": "No escribas en el comando `{}`. Sustituye `{fórmula}` por la fórmula que quieres que te calcule el bot"
            }
        }
    },
    "Interacción": {
        "emoji": "<:Interaccion:839105758566154340>",
        "commands": {
            "pop": {
                "description": "Comando que envía un mensaje que contiene pop (prueba a ejecutar el comando)",
                "usage": "%pop",
                "permissions": "Todos pueden utilizar este comando"
            },
            "hi": {
                "description": "No hay información",
                "usage": "No hay información",
                "permissions": "Todos pueden utilizar este comando",
                "extra": "No hay información"
            }
        }
    },
    "Anime": {
        "emoji": "<:Laslylusky:833614887547699221>",
        "commands": {
            "animesearch": {
                "description": "Comando que envía información del anime que se ha escrito al ejecutar el comando",
                "usage": "%animesearch {nombre.anime}",
                "permissions": "Todos pueden utilizar este comando",
                "extra": "No escribas en el comando `{}`. Sustituye `{nombre.anime}` por el nombre del anime del que quieres saber la información"
            },
            "waifu": {
                "description": "Comando que envía la imagen de una waifu",
                "usage": "%waifu",
                "permissions": "Todos pueden utilizar este comando"
            }
        }
    },
    "Minecraft": {
        "emoji": "<:Minecraft:837706204079194123>",
        "commands": {
            "mcuser": {
                "description": "Comando que envía información del jugador de Minecraft Premium",
                "usage": "%mcuser {jugador.premium}",
                "permissions": "Todos pueden utilizar este comando",
                "extra": "No escribas en el comando `{}`. Sustituye `{jugador.premium}` por el nombre del jugador de Minecraft Premium para saber su información"
            },
            "mcserver": {
                "description": "Comando que envía información del servidor de Minecraft",
                "usage": "%mcserver {ip.servidor}",
                "permissions": "Todos pueden utilizar este comando",
                "extra": "No escribas en el comando `{}`. Sustituye `{ip.servidor}` por la ip del servidor de Minecraft que quieras saber información"
            }
        }
    },
    "Juegos": {
        "emoji": "<:Juegos:838012718631616512>",
        "commands": {
            "waterdrop": {
                "description": "Comando para jugar. El comando es BETA <:Beta:838012413193486356>",
                "usage": "%waterdrop",
                "permissions": "Todos pueden utilizar este comando",
                "extra": "Consejo: Jugar en un canal donde solo pueda enviar mensajes el que vaya a jugar"
            },
            "aki": {
                "description": "No hay información",
                "usage": "No hay información",
                "permissions": "Todos pueden utilizar este comando"
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
                "description": "Comando que envía culos de mujeres (por ahora)",
                "usage": "",
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
            "hentai": {
                "description": "Comando que envía imágenes hentai",
                "usage": "%hentai",
                "permissions": "Todos pueden utilizar este comando. **Solo se puede utilizar en un canal NSFW**"
            },
            "slut": {
                "description": "Comando que envía *putas*",
                "usage": "%slut",
                "permissions": "Todos pueden utilizar este comando. **Solo se puede utilizar en un canal NSFW**"
            }
        }
    },
    "Reportar bug | Enviar sugerencia :incoming_envelope:": {
        "emoji": ":pushpin:",
        "commands": {
            "bugreport": {
                "description": "Comando para reportar un bug/error de un comando",
                "usage": "%bugreport {mensaje}",
                "permissions": "Todos pueden usar este comando",
                "extra": "No escribas en el comando `{}`. `{mensaje}` tiene que ser sustituido por el mensaje del reporte del bug/error de un comando"
            },
            "suggest": {
                "description": "Comando para enviar una sugerencia de lo que quieres que se añada al bot",
                "usage": "%suggest {sugerencia}",
                "permissions": "Todos pueden utilizar este comando",
                "extra": "No escribas en el comando `{}`. `{sugerencia}` tiene que ser sustituido por la sugerencia que quieres que añadan al bot"
            }
        }
    }
}