# Comandos de Laslylusky

Laslylusky tiene múltiples comandos y categorías para diferentes funciones. Aquí encontrarás toda la información sobre cada comando disponible.

## Información General

- El prefix del bot es `%`
- Puedes obtener ayuda específica escribiendo `%help <comando>` o `/help comando:<comando>`
- Para conocer la política de privacidad del bot, usa `%privacidad` o `/privacidad`

## Categorías de Comandos

### Laslylusky

| Comando | Descripción | Uso | Permisos | Opciones | Extra |
|---------|-------------|-----|----------|----------|-------|
| `help` | Muestra todos los comandos disponibles | `%help <comando>` \| `/help comando:<comando>` | Todos pueden utilizar este comando | `<comando>`: nombre del comando que quieres ver la ayuda | |
| `invite` | Muestra el enlace de invitación del bot | `%invite` \| `/invite` | Todos pueden utilizar este comando | | |
| `donate` | Manda al MD (mensaje privado) el enlace para hacer donaciones para contribuir en el desarrollo constante de Laslylusky | `%donate` | Todos pueden utilizar este comando | | |
| `updates` | Comando para saber las actualizaciones del bot | `%updates <actualización>` \| `/updates versión:<actualización>` | Todos pueden utilizar este comando | `<actualización>`: versión que quieres saber las actualizaciones | |
| `info` | Comando que muestra información del bot | `%info` \| `/info` | Todos pueden usar este comando | | |
| `privacidad` | Comando que envía la política de privacidad al utilizar el bot | `%privacidad` \| `/privacidad` | Todos pueden utilizar este comando | | |
| `savedatachat` | Comando para descargar tu conversación que has tenido con la IA | `%savedatachat` \| `/savedatachat` | Todos pueden usar este comando | | |
| `reset-chat` | Comando para restablecer la conversación de la IA | `%reset-chat` \| `/reset-chat` | Todos pueden usar este comando | | |
| `bugreport` | Comando para reportar un bug/error de un comando | `%bugreport {mensaje}` \| `/bugreport razonbug:{mensaje} error:<error> comando_ejecutado:<comando>` | Todos pueden usar este comando | `{mensaje}`: mensaje del reporte del bug/error de un comando<br>`<error>`: mensaje de error si es que existe<br>`<comando_ejecutado>`: comando que causó el error | |
| `botsuggest` | Comando para enviar una sugerencia de lo que quieres que se añada al bot | `%botsuggest {sugerencia}` \| `/botsuggest sugerencia:{sugerencia}` | Todos pueden utilizar este comando | `{sugerencia}`: sugerencia que quieres que añadan al bot | |

### Diversión y juegos

| Comando | Descripción | Uso | Permisos | Opciones | Extra |
|---------|-------------|-----|----------|----------|-------|
| `kill` | Comando para intentar 'matar' a un jugador mencionado | `%kill {usuario}` | Todos pueden usar este comando | `{usuario}`: mención del usuario | |
| `hug` | Comando para abrazar a alguien | `%hug {usuario}` | Todos pueden usar este comando | `{usuario}`: mención del usuario | |
| `8ball` | Comando para consultar la bola mágica 8 | `%8ball {pregunta}` \| `/8ball pregunta:{pregunta}` | Todos pueden usar este comando | `{pregunta}`: pregunta que quieres hacerle a la bola mágica | |
| `meme` | Comando que muestra un meme aleatorio en español | `%meme` \| `/meme` | Todos pueden usar este comando | | |
| `morse` | Comando para convertir texto a código morse o viceversa | `%morse {texto}` \| `/morse texto_a_morse:<texto_a_morse> morse_a_texto:<morse_a_texto>` | Todos pueden usar este comando | `{texto}`: texto que quieres convertir a morse<br>`<texto_a_morse>`: texto que quieres convertir a morse<br>`<morse_a_texto>`: texto en morse que quieres convertir a texto | Con `/morse` se puede convertir un texto a morse o al revés. Es obligatorio poner uno de los 2 argumentos |
| `trivia` | Comando para jugar a trivia | `%trivia` \| `/trivia` | Todos pueden usar este comando | | |
| `ahorcado` | Comando para jugar al ahorcado por lo menos 2 jugadores | `%ahorcado` \| `/ahorcado` | Todos pueden usar este comando | | |
| `blackjack` | Comando para jugar al blackjack 2 o más jugadores | `%blackjack` \| `/blackjack` | Todos pueden usar este comando | | |
| `insulto` | Comando para insultar a alguien de forma graciosa | `%insulto <usuario>` \| `/insulto usuario:<usuario>` | Todos pueden usar este comando | `<usuario>`: mención del usuario al que quieres insultar | |
| `buscaminas` | Comando para jugar al buscaminas | `/buscaminas dificultad:{dificultad}` | Todos pueden usar este comando | `{dificultad}`: dificultad del buscaminas (fácil, medio o difícil) | |
| `piedrapapeltijera` | Comando para jugar al piedra papel o tijera 2 jugadores | `%piedrapapeltijera` \| `/piedrapapeltijera` | Todos pueden usar este comando | | |
| `ruletarusa` | Comando para jugar a la ruleta rusa de 2 a 6 jugadores | `%ruletarusa` \| `/ruletarusa` | Todos pueden usar este comando | | |
| `tictactoe` | Comando para jugar al tres en raya 2 jugadores | `%tictactoe` \| `/tictactoe` | Todos pueden usar este comando | | |
| `conecta4` | Comando para jugar al conecta4 2 jugadores | `%conecta4` \| `/conecta4` | Todos pueden usar este comando | | |
| `halago` | Comando para enviar un halago a un usuario | `%halago <usuario>` \| `/halago usuario:<usuario>` | Todos pueden usar este comando | `<usuario>`: mención del usuario al que quieres mandarle un halago | |
| `moneda` | Comando para lanzar una moneda y ver si sale cara o cruz | `%moneda` \| `/moneda` | Todos pueden usar este comando | | |
| `dado` | Comando para lanzar un dado y ver el número que ha salido | `%dado <caras>` \| `/dado caras:<caras>` | Todos pueden usar este comando | `<caras>`: número de caras del dado (por defecto 6) | |
| `estadisticas-juegos` | Comando para ver estadisticas de minijuegos | `%estadisticas-juegos` \| `/estadisticas-juegos` | Todos pueden usar este comando | | |
| `2048` | Comando para jugar al 2048 hasta llegar al número 8192 (por ahora) | `%2048` \| `/2048` | Todos pueden usar este comando | | |

### Moderación

| Comando | Descripción | Uso | Permisos | Opciones | Extra |
|---------|-------------|-----|----------|----------|-------|
| `ban` | Comando para banear a un usuario, temporal o permanentemente | `%ban {usuario} <razón>` \| `/ban usuario:{usuario} razón:<razón> tiempo:<tiempo>` | `ADMINISTRADOR`/`BANEAR USUARIOS` | `{usuario}`: mención del usuario o su ID<br>`<razón>`: razón del baneo<br>`<tiempo>`: tiempo del baneo | El tiempo se ha de poner en segundos (s), minutos (m), horas (h) o días (d), siendo 15 días el máximo del ban temporal |
| `massban` | Comando para hacer un baneo masivo a varios usuarios | `%massban {usuarios.coma} {razón}` \| `/massban ids:{usuarios} razón:{razón}` | `ADMINISTRADOR`/`BANEAR USUARIOS` | `{usuarios.coma}`: IDs de los usuarios a banear separados por comas<br>`{usuarios}`: IDs de los usuarios a banear separados por espacios<br>`{razón}`: razón del baneo masivo | |
| `unban` | Comando para desbanear al usuario pasándole su ID | `%unban {usuario.id}` \| `/unban usuario_id:{usuario.id}` | `ADMINISTRADOR`/`BANEAR USUARIOS` | `{usuario.id}`: ID del usuario a desbanear | |
| `kick` | Comando para expulsar al usuario mencionado | `%kick {usuario} <razón>` \| `/kick usuario:{usuario} razón:<razón>` | `ADMINISTRADOR`/`EXPULSAR USUARIOS` | `{usuario}`: mención del usuario o su ID<br>`<razón>`: razón de la expulsión | |
| `clear` | Comando de de moderación para borrar la cantidad de mensajes que se escriba en el comando | `%clear {número}` \| `/clear cantidad:{número} usuarios:<usuarios> canal:<canal> excluir_usuarios:<excluir_usuarios>` | `ADMINISTRADOR`/`GESTIONAR MENSAJES` | `{número}`: número de mensajes a borrar<br>`<usuarios>`: ID de los usuarios que quieres borrar los mensajes, separados por espacios<br>`<canal>`: mención del canal donde quieres borrar los mensajes, por defecto el canal donde se ejecuta el comando<br>`<excluir_usuarios>`: ID de los usuarios que quieres excluir de la eliminación de mensajes, separados por espacios | |
| `warn` | Comando para advertir al usuario mencionado | `%warn {usuario} {razón}` \| `/warn user:{usuario} reason:{razón}` | `ADVERTIR USUARIOS`/`ADMINISTRADOR` | `{usuario}`: mención del usuario o su ID<br>`{razón}`: razón de la advertencia | |
| `unwarn` | Comando para quitar la advertencia al usuario mencionado | `%unwarn {warnid} {razón}` \| `/unwarn warn_id:{ID.warn} reason:{razón}` | `MANEJAR ROLES`/`ADMINISTRADOR` | `{warnid}`: ID de la advertencia que quieres quitar<br>`{razón}`: razón de la desadvertencia | Utiliza `/infracciones` para ver las infracciones del usuario |
| `infracciones` | Comando para ver las infracciones puestas al usuario mencionado | `%infracciones {usuario}` \| `/infracciones user:{usuario}` | `ADVERTIR USUARIOS`/`ADMINISTRADOR`/`BANEAR USUARIOS`/`EXPULSAR USUARIOS`/`GESTIONAR ROLES`/`GESTIONAR SERVIDOR` | `{usuario}`: mención del usuario o su ID | |
| `moderador` | Comando para ver las sanciones puestas por el moderador que ejecutó el comando o el mencionado | `%moderador <usuario>` \| `/moderador moderador:<usuario>` | `ADVERTIR USUARIOS`/`ADMINISTRADOR`/`BANEAR USUARIOS`/`EXPULSAR USUARIOS`/`GESTIONAR ROLES`/`GESTIONAR SERVIDOR` | `<usuario>`: mención del usuario o su ID | |
| `aislar` | Comando para aislar temporalmente a un usuario en el servidor | `%aislar {usuario} {tiempo} <razón>` \| `/aislar usuario:{usuario} tiempo:{tiempo} razón:<razón>` | `ADMINISTRADOR`/`MUTEAR USUARIOS`/`MODERAR MIEMBROS` | `{usuario}`: mención del usuario o su ID<br>`{tiempo}`: tiempo del aislamiento<br>`<razón>`: razón del aislamiento | El tiempo se ha de poner en segundos (s), minutos (m), horas (h) o días (d), siendo 7 días el máximo del aislamiento |
| `desaislar` | Comando para quitar el aislamiento a un usuario en el servidor | `%desaislar {usuario} <razón>` \| `/desaislar usuario:{usuario} razón:<razón>` | `ADMINISTRADOR`/`MUTEAR USUARIOS`/`MODERAR MIEMBROS` | `{usuario}`: mención del usuario o su ID<br>`<razón>`: razón del desaislamiento | |

### Configuración

| Comando | Descripción | Uso | Permisos | Opciones | Extra |
|---------|-------------|-----|----------|----------|-------|
| `slowmode` | Comando de para cambiar el cooldown del canal donde se ejecuta el comando | `%slowmode {tiempo} <razón>` | `GESTIONAR CANALES` | `{tiempo}`: tiempo del cooldown<br>`<razón>`: razón del cooldown | |
| `config` | Comando para configurar al bot en el servidor donde se ejecute | `/config {opción}` | `ADMINISTRADOR` | `{opción}`: opción que quieres configurar: <br>- `/config cmd comando:{comando} estado:{estado}` -> activar/desactivar comandos<br>  - `{comando}`: nombre del comando que quieres activar o desactivar<br>  - `{estado}`: estado del comando (activado/desactivado)<br>- `/config data` -> ver datos de configuración del bot en el servidor <br>- `/config update` -> restablecer configuración del bot en el servidor<br>- `/config help` -> muestra ayuda de la configuración <br>- `/config logs tipo:{tipo}` -> configurar logs del servidor<br>  - `{tipo}`: tipo de logs a configurar <br> `/config perms permiso:{permiso} acción:{acción} roles:<roles> usuarios:<usuarios>` -> establecer/quitar permisos de comandos del bot a usuarios o roles<br>  - `{permiso}`: nombre del permiso que quieres establecer o quitar<br>  - `{acción}`: acción a realizar (añadir/quitar)<br>  - `<roles>`: ID de los roles a los que quieres añadir o quitar el permiso, separados por espacios<br>  - `<usuarios>`: ID de los usuarios a los que quieres añadir o quitar el permiso, separados por espacios<br>- `/config tickets` -> gestionar tickets del servidor | |
| `voicesetup` | Comando para gestionar canales de voz temporales en un servidor | `/voicesetup` | `ADMINISTRADOR` | | |

### Información

| Comando | Descripción | Uso | Permisos | Opciones | Extra |
|---------|-------------|-----|----------|----------|-------|
| `userinfo` | Comando que envía la información del usuario mencionado, o del usuario que ejecutó el comando | `%userinfo <usuario>` \| `/userinfo usuario:<usuario>` | Todos pueden usar este comando | `<usuario>`: mención del usuario o su ID | |
| `avatar` | Comando que envía la imagen de perfil tuya o del usuario mencionado | `%avatar <usuario>` \| `/avatar usuario:<usuario>` | Todos pueden usar este comando | `<usuario>`: mención del usuario o su ID | |
| `servericon` | Comando que envía la imagen del servidor donde se ejecutó | `%servericon` \| `/servericon` | Todos pueden usar este comando | | |
| `serverinfo` | Comando que envía la información del servidor donde se ha utilizado | `%serverinfo` \| `/serverinfo` | Todos pueden usar este comando | | |

### Utilidad

| Comando | Descripción | Uso | Permisos | Opciones | Extra |
|---------|-------------|-----|----------|----------|-------|
| `embed` | Comando para crear y enviar embed a través del bot o un webhook | `/embed` | `ADMINISTRADOR` | | |
| `laslylusky` | Comando para tener una conversación con Laslylusky gracias a la IA | `@Laslylusky {texto}` | Todos pueden usar este comando | `{texto}`: mensaje que quieres decirle a la IA | La IA mantendrá un chat con el usuario siempre, recordando la conversación a no ser que el usuario la elimine. Para eliminar el chat con la IA de ese canal y empezar otro escribe `%reset-chat`. La AI solo podrá mantener conversación con solo 1 usuario |
| `id` | Comando que muestra información de IDs de emojis, usuarios, canales o roles | `/id tipo:{tipo} {opción}` | Todos pueden usar este comando | `{tipo}`: tipo de ID que quieres ver (emoji, usuario, canal o rol)<br>`{opción}`: `emoji`, `usuario`, `canal` o `rol` | |
| `recordatorio` | Comando para crear recordatorios que el bot te enviará por MD | `/recordatorio {opción}` | Todos pueden usar este comando | `{opción}`: `ver`, `crear` o `gestionar` | Para la zona horaria en GMT mira tu ubicación en [este enlace](https://greenwichmeantime.com/time-zone/) |
| `cumpleaños` | Comando para gestionar los cumpleaños en un servidor | `/cumpleaños {opción}` | Todos pueden usar este comando / ADMINISTRADOR | `{opción}`: `ver`, `establecer`, `eliminar` o `configurar` | Para la zona horaria en GMT mira la ubicación en [este enlace](https://greenwichmeantime.com/time-zone/) |
| `nivel` | Comando para gestionar los niveles en un servidor | `/nivel {opción}` | Todos pueden usar este comando / ADMINISTRADOR | `{opción}`: `ver`, `gestionar`, `top` o `configurar` | |
| `comprobar-virus` | omando para comprobar si un archivo o enlace tiene virus | `/comprobar-virus archivo:<archivo> enlace:<enlace>` | Todos pueden usar este comando | `<archivo>`: archivo que quieres comprobar<br>`<enlace>`: "enlace que quieres comprobar | Es obligatorio poner uno de los 2 argumentos, y no se pueden poner los 2 a la vez. |

### Minecraft

| Comando | Descripción | Uso | Permisos | Opciones | Extra |
|---------|-------------|-----|----------|----------|-------|
| `mcstatus` | Comando que muestra el estado de un servidor de Minecraft, ya sea de Java o Bedrock | `%mcstatus {serverip} {plataforma}` \| `/mcstatus ip:{serverip} plataforma:{plataforma}` | Todos pueden usar este comando | `{serverip}`: IP del servidor de Minecraft<br>`{plataforma}`: plataforma del servidor de Minecraft (java o bedrock) | |
| `mcuser` | Comando que muestra información de la cuenta de Minecraft que se ha pasado | `%mcuser {usuario}` | Todos pueden usar este comando | `{usuario}`: nombre de usuario de Minecraft | |
| `hypixel` | Comando que muestra las estadísticas de un jugador en hypixel | `%hypixel {usuario}` | Todos pueden usar este comando | `{usuario}`: nombre de usuario de Minecraft | |

### NSFW

> Nota: Estos comandos solo pueden utilizarse en canales NSFW

| Comando | Descripción | Uso | Permisos | Extra |
|---------|-------------|-----|----------|-------|
| `boobs` | Comando que envía tetas de mujeres (por ahora)(el diablo) | `%boobs` | Todos pueden utilizar este comando | **Solo se puede utilizar en un canal NSFW** |
| `anal` | Comando que envía sexo anal | `%anal` | Todos pueden utilizar este comando | **Solo se puede utilizar en un canal NSFW** |
| `ass` | Comando que envía culos de mujeres | `%ass` | Todos pueden utilizar este comando | **Solo se puede utilizar en un canal NSFW** |
| `pgif` | Comando que envía gifs porno | `%pgif` | Todos pueden utilizar este comando | **Solo se puede utilizar en un canal NSFW** |
| `4k` | Comando que envía contenido porno en 4k | `%4k` | Todos pueden utilizar este comando | **Solo se puede utilizar en un canal NSFW** |
| `pussy` | Comando que envía coños de mujeres | `%pussy` | Todos pueden utilizar este comando | **Solo se puede utilizar en un canal NSFW** |
| `hboobs` | Comando que envía tetas de hentai | `%hboobs` | Todos pueden utilizar este comando | **Solo se puede utilizar en un canal NSFW** |
| `hass` | Comando que envía culos de hentai | `%hass` | Todos pueden utilizar este comando | **Solo se puede utilizar en un canal NSFW** |
| `hanal` | Comando que envía anal de hentai | `%hanal` | Todos pueden utilizar este comando | **Solo se puede utilizar en un canal NSFW** |
| `blowjob` | Comando que envía mamadas | `%blowjob` | Todos pueden utilizar este comando | **Solo se puede utilizar en un canal NSFW** |

## Enlaces Útiles

- **Invitación**: [Invitar a Laslylusky a tu servidor](https://discord.com/oauth2/authorize?client_id=784774864766500864&scope=bot%20applications.commands&permissions=8589803519)
- **Servidor Discord**: [Unirse al servidor de soporte](https://discord.gg/DN6PDKA7gf)
- **Top.gg**: [Perfil en Top.gg](https://top.gg/bot/784774864766500864)
- **Valorar**: [Formulario para valorar al bot](https://forms.gle/pqeiSo1n1d49jD7M9)
- **Donar**: [Apoyar el desarrollo vía PayPal](https://paypal.me/VegetinES)
- **GitHub**: [Repositorio del bot](https://github.com/VegetinES/Laslylusky-Bot)
- **Página Web**: [Sitio web oficial](https://laslylusky.es)

## Notas Importantes

- Los comandos predeterminados que no pueden desactivarse son: "help", "donate", "info", "invite", "privacidad", "updates", "savedatachat", "botsuggest", "bugreport", "laslylusky", "reset-chat", "config", "infracciones", "moderador", "recordatorio", "nivel", "voicesetup", "cumpleaños", "estadisticas-juegos"
- El bot proporciona información detallada sobre cada comando cuando se solicita con `%help <comando>` o `/help comando:<comando>`
- Para ver los comandos NSFW, debes ejecutar los comandos de ayuda en un canal marcado como NSFW

### Notas sobre el formato de comandos:
- No pongas en los comandos `<>` ni `{}`
- `<>`: parámetro opcional
- `{}`: parámetro obligatorio