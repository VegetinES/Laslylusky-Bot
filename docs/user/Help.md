# Comandos de Laslylusky

Laslylusky tiene múltiples comandos y categorías para diferentes funciones. Aquí encontrarás toda la información sobre cada comando disponible.

## Información General

- El prefix del bot es `%`
- Puedes obtener ayuda específica escribiendo `%help <comando>` o `/help comando:<comando>`
- Para conocer la política de privacidad del bot, usa `%privacidad` o `/privacidad`

## Categorías de Comandos

### 🤖 Laslylusky

| Comando | Descripción | Uso | Permisos | Extra |
|---------|-------------|-----|----------|-------|
| `help` | Muestra todos los comandos disponibles | `%help [comando]` \| `/help` | Todos pueden utilizar este comando | |
| `invite` | Muestra el enlace de invitación del bot | `%invite` \| `/invite` | Todos pueden utilizar este comando | |
| `donate` | Manda al MD (mensaje privado) el enlace para hacer donaciones para contribuir en el desarrollo constante de Laslylusky | `%donate` | Todos pueden utilizar este comando | |
| `updates` | Comando para saber las actualizaciones del bot | `%updates` | Todos pueden utilizar este comando | |
| `info` | Comando que muestra información del bot | `%info` \| `/info` | Todos pueden usar este comando | |
| `privacidad` | Comando que envía la política de privacidad al utilizar el bot | `%privacidad` \| `/privacidad` | Todos pueden utilizar este comando | |
| `savedatachat` | Comando para descargar tu conversación que has tenido con la IA | `%savedatachat` \| `/savedatachat` | Todos pueden usar este comando | |
| `reset-chat` | Comando para restablecer la conversación de la IA | `%reset-chat` \| `/reset-chat` | Todos pueden usar este comando | |

### 😄 Diversión

| Comando | Descripción | Uso | Permisos | Extra |
|---------|-------------|-----|----------|-------|
| `kill` | Comando para intentar 'matar' a un jugador mencionado | `%kill {usuario.mencion}` | Todos pueden usar este comando | No escribas en el comando `{}`. `{usuario.mencion}` debe ser sustituido por la mención a un usuario al que quieres intentar 'matar' |
| `hug` | Comando para abrazar a alguien | `%hug {usuario}` | Todos pueden usar este comando | No escribas en el comando `{}`. `{usuario}` debe ser sustituido por la mención a un usuario al que quieres abrazar |

### 🛡️ Moderación

| Comando | Descripción | Uso | Permisos | Extra |
|---------|-------------|-----|----------|-------|
| `ban` | Comando para banear a los usuarios mencionados | `%ban {usuario} {razón}` | `ADMINISTRADOR`/`BANEAR USUARIOS` | No escribas en el comando `{}`. `{usuario}` tiene que ser sustituido por la mención al usuario o su ID, y `{razón}` por la razón del baneo |
| `unban` | Comando para desbanear al usuario pasándole su ID | `%unban {usuario.id}` | `ADMINISTRADOR`/`BANEAR USUARIOS` | No escribas en el comando `{}`. `{usuario.id}` tiene que ser sustituido por id del usuario baneado |
| `kick` | Comando para expulsar al usuario mencionado | `%kick {usuario} {razón}` | `ADMINISTRADOR`/`ESPULSAR USUARIOS` | No escribas en el comando `{}`. `{usuario}` tiene que ser sustituido por la mención al usuario o su ID, y `{razón}` por la razón de la expulsión |
| `clear` | Comando de de moderación para borrar la cantidad de mensajes que se escriba en el comando | `%clear {número}` | `ADMINISTRADOR`/`GESTIONAR MENSAJES` | No escribas en el comando `{}`. `{número}` tiene que ser sustituido por un número entre 1 a 100 que significa la cantidad de mensajes que quieres borrar |
| `warn` | Comando para mutear al usuario mencionado de forma definitiva hasta que se lo quite de forma manual | `%warn {usuario} {razón}` \| `/warn` | `ADVERTIR USUARIOS`/`ADMINISTRADOR` | No escribas en el comando `{}`. Sustituye `{usuario}` por la mención del usuario o la ID del usuario a quien se quiere poner una advertencia, y `{razón}` por la razón de la advertencia. Se recomienda utilizar `/warn`. Es necesario configurar el comando en config |
| `unwarn` | Comando para quitar el mute al usuario mencionado que ya esté silenciado | `%unwarn {warnid} {razón}` \| `</unwarn` | `MANEJAR ROLES`/`ADMINISTRADOR` | No escribas en el comando `{}`. Sustituye `{warnid}` por el ID de la advertencia (utilizar `/infracciones` para ver las infracciones del usuario), y `{razón}` por la razón de porqué se quita la advertencia. Se recomienda utilizar `/unwarn`. Es necesario configurar el comando en config |
| `infracciones` | Comando para ver las infracciones puestas al usuario mencionado | `%infracciones {usuario}` \| `/infracciones` | `ADVERTIR USUARIOS`/`ADMINISTRADOR`/`BANEAR USUARIOS`/`EXPULSAR USUARIOS`/`GESTIONAR ROLES`/`GESTIONAR SERVIDOR` | No escribas en el comando `{}`. Sustituye `{usuario}` por la mención del usuario que quieres ver sus infracciones |
| `moderador` | Comando para ver las sanciones puestas por el moderador que ejecutó el comando o el mencionado | `%moderador [usuario]` \| `/moderador` | `ADVERTIR USUARIOS`/`ADMINISTRADOR`/`BANEAR USUARIOS`/`EXPULSAR USUARIOS`/`GESTIONAR ROLES`/`GESTIONAR SERVIDOR` | No escribas en el comando `[]`. Sustituye `[usuario]` por la mención del usuario que quieres ver sanciones aplicadas |

### ⚙️ Configuración

| Comando | Descripción | Uso | Permisos | Extra |
|---------|-------------|-----|----------|-------|
| `slowmode` | Comando de para cambiar el cooldown del canal donde se ejecuta el comando | `%slowmode {tiempo} [razón]` | `GESTIONAR CANALES` | |
| `config` | Comando para configurar al bot en el servidor donde se ejecute | `%config` | `ADMINISTRADOR` | Para utilizar la configuración de forma más detallada y fácil los comandos `/config help`, `/config data`, `/config update`, `/config perms`, `/config logs` o `/config cmd` |

### ℹ️ Información

| Comando | Descripción | Uso | Permisos | Extra |
|---------|-------------|-----|----------|-------|
| `userinfo` | Comando que envía la información del usuario mencionado, o del usuario que ejecutó el comando | `%userinfo` / `%userinfo {usuario}` | Todos pueden usar este comando | No escribas en el comando `{}`. `{usuario}` tiene que ser sustituido por la mención del usuario |
| `avatar` | Comando que envía la imagen de perfil tuya o del usuario mencionado | `%avatar` / `%avatar {usuario}` | Todos pueden usar este comando | No escribas en el comando `{}`. `{usuario}` tiene que ser sustituido por la mención del usuario |
| `servericon` | Comando que envía la imagen del servidor donde se ejecutó | `%servericon` | Todos pueden usar este comando | |
| `serverinfo` | Comando que envía la información del servidor donde se ha utilizado | `%serverinfo` | Todos pueden usar este comando | |

### 🔧 Utilidad

| Comando | Descripción | Uso | Permisos | Extra |
|---------|-------------|-----|----------|-------|
| `embed` | Comando simple de un embed | `%embed {mensaje}` | Todos pueden usar este comando | No escribas en el comando `{}`. `{mensaje}` tiene que ser sustituido por el mensaje que quieres que aparezca en el embed |
| `laslylusky` | Comando para tener una conversación con Laslylusky gracias a la IA | `@Laslylusky {texto}` | Todos pueden usar este comando | No escribas en el comando `{}`. `{texto}` debe ser sustituido por el mensaje que quieras decirle a la IA. La IA mantendrá un chat con el usuario siempre, recordando la conversación a no ser que el usuario la elimine. Para eliminar el chat con la IA de ese canal y empezar otro escribe `%reset-chat`. La AI solo podrá mantener conversación con solo 1 usuario |

### 🎮 Minecraft

| Comando | Descripción | Uso | Permisos | Extra |
|---------|-------------|-----|----------|-------|
| `mcstatus` | Comando que muestra el estado de un servidor de Minecraft, ya sea de Java o Bedrock | `%mcstatus {serverip} {plataforma}` | Todos pueden usar este comando | No escribas en el comando `{}`. `{serverip}` tiene que ser sustituido por la IP del servidor y `{plataforma}` por la plataforma de Minecraft (poner `java` o `bedrock`) |
| `mcuser` | Comando que muestra información de la cuenta de Minecraft que se ha pasado | `%mcuser {usuario}` | Todos pueden usar este comando | No escribas en el comando `{}`. `{usuario}` tiene que ser sustituido por el nombre del jugador |
| `hypixel` | Comando que muestra las estadísticas de un jugador en hypixel | `%hypixel {usuario}` | Todos pueden usar este comando | No escribas en el comando `{}`. `{usuario}` tiene que ser sustituido por el nombre del jugador |

### 🔞 NSFW

> Nota: Estos comandos solo pueden utilizarse en canales NSFW

| Comando | Descripción | Uso | Permisos |
|---------|-------------|-----|----------|
| `boobs` | Comando que envía tetas de mujeres (por ahora)(el diablo) | `%boobs` | Todos pueden utilizar este comando. **Solo se puede utilizar en un canal NSFW** |
| `anal` | Comando que envía sexo anal | `%anal` | Todos pueden utilizar este comando. **Solo se puede utilizar en un canal NSFW** |
| `ass` | Comando que envía culos de mujeres | `%ass` | Todos pueden utilizar este comando. **Solo se puede utilizar en un canal NSFW** |
| `pgif` | Comando que envía gifs porno | `%pgif` | Todos pueden utilizar este comando. **Solo se puede utilizar en un canal NSFW** |
| `4k` | Comando que envía contenido porno en 4k | `%4k` | Todos pueden utilizar este comando. **Solo se puede utilizar en un canal NSFW** |
| `pussy` | Comando que envía coños de mujeres | `%pussy` | Todos pueden utilizar este comando. **Solo se puede utilizar en un canal NSFW** |
| `hboobs` | Comando que envía tetas de hentai | `%hboobs` | Todos pueden utilizar este comando. **Solo se puede utilizar en un canal NSFW** |
| `hass` | Comando que envía culos de hentai | `%hass` | Todos pueden utilizar este comando. **Solo se puede utilizar en un canal NSFW** |
| `hanal` | Comando que envía anal de hentai | `%hanal` | Todos pueden utilizar este comando. **Solo se puede utilizar en un canal NSFW** |
| `blowjob` | Comando que envía mamadas | `%blowjob` | Todos pueden utilizar este comando. **Solo se puede utilizar en un canal NSFW** |

### 📌 Reportar bug | Enviar sugerencia 📨

| Comando | Descripción | Uso | Permisos | Extra |
|---------|-------------|-----|----------|-------|
| `bugreport` | Comando para reportar un bug/error de un comando | `%bugreport {mensaje}` \| `/bugreport` | Todos pueden usar este comando | No escribas en el comando `{}`. `{mensaje}` tiene que ser sustituido por el mensaje del reporte del bug/error de un comando. Se recomienda usar </bugreport:1342426095617708145> |
| `bot-suggest` | Comando para enviar una sugerencia de lo que quieres que se añada al bot | `%bot-suggest {sugerencia}` \| `/botsuggest` | Todos pueden utilizar este comando | No escribas en el comando `{}`. `{sugerencia}` tiene que ser sustituido por la sugerencia que quieres que añadan al bot |

## Enlaces Útiles

- **Invitación**: [Invitar a Laslylusky a tu servidor](https://laslylusky.es/invite)
- **Servidor Discord**: [Unirse al servidor de soporte](https://discord.gg/8uuPxpjC4N)
- **Top.gg**: [Perfil en Top.gg](https://top.gg/bot/784774864766500864)
- **Valorar**: [Formulario para valorar al bot](https://forms.gle/pqeiSo1n1d49jD7M9)
- **Donar**: [Apoyar el desarrollo vía PayPal](https://paypal.me/VegetinES)
- **GitHub**: [Repositorio del bot](https://github.com/VegetinES/Laslylusky-Bot)
- **Página Web**: [Sitio web oficial](https://laslylusky.es)

## Notas Importantes

- Los comandos predeterminados que no pueden desactivarse son: "help", "donate", "info", "invite", "privacidad", "updates", "savedatachat", "bot-suggest", "bugreport", "laslylusky", "reset-chat", "config", "infracciones", "moderador"
- El bot proporciona información detallada sobre cada comando cuando se solicita con `%help <comando>` o `/help comando:<comando>`
- Para ver los comandos NSFW, debes ejecutar los comandos de ayuda en un canal marcado como NSFW