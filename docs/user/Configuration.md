# Configuración del Bot

## Comandos disponibles

- `/config help` - Muestra esta ayuda
- `/config help tipo:logs` - Muestra ayuda específica sobre logs
- `/config help tipo:perms` - Muestra ayuda específica sobre permisos
- `/config help tipo:cmd` - Muestra ayuda específica sobre comandos
- `/config help tipo:update` - Muestra ayuda específica sobre actualización
- `/config help tipo:data` - Muestra ayuda específica sobre datos
- `/config data` - Muestra la configuración actual del servidor
- `/config update` - Restablece la configuración a los valores predeterminados
- `/config cmd comando estado` - Activa o desactiva comandos específicos
- `/config logs` - Configuración de registros de auditoría
- `/config perms` - Configuración de permisos

## Documentación de comandos

### Config perms

Ejecución de </config perms:1348216356918657089>

```
/config perms {permiso} {accion} ({roles}/{usuarios})
```

- `{permiso}`: el permiso que se quiere configurar
- `{accion}`: añadir o eliminar el permiso

Al menos uno de estos campos es obligatorio:

- `{roles}`: menciona o pon los roles que quieres añadir o eliminar, separados por espacios
- `{usuarios}`: menciona o pon los usuarios que quieres añadir o eliminar, separados por espacios

### Config cmd

Ejecución de </config cmd:1348216356918657089>

```
/config cmd {comando} {estado}
```

- `{comando}`: el comando que se quiere activar o desactivar
- `{estado}`: activar o desactivar el comando

### Config update

Ejecución de </config update:1348216356918657089>

```
/config update
```

Este comando restablece la configuración del servidor a los valores predeterminados.

### Config data

Ejecución de </config data:1348216356918657089>

```
/config data
```

Este comando muestra la configuración actual del servidor.

### Config logs

Ejecución de </config logs:1348216356918657089>:

```
/config logs {log} {estado} {canal} {tipoMensaje} ({mensaje}/<footer> {descripcion} <titulo>) ({limite})
```

- `{log}`: el log que se quiere configurar.
- `{estado}`: para activar o desactivar los logs
- `{canal}`: establecer el canal donde se mandarán los logs.
- `{tipoMensaje}`: poner el tipo de mensaje del log (embed o normal)

En caso de ser mensaje embed, solo se tendrán que poner los siguientes parámetros:
- `<titulo>`: establecer el título del embed.
- `{descripción}`: establecer la descripción del embed (obligatorio)
- `<footer>`: establecer el footer del embed.

En caso de ser mensaje normal, solo se tendrá que poner el siguiente parámetro:
- `{mensaje}`: establecer el mensaje del log.

En caso de que el log sea de mensajes editados o eliminados, este parámetro es obligatorio:
- `{límite}`: establecer el tiempo en el que saldrán logs de mensajes editados, mínimo 7 días, máximo 30 días, poner el número de días solo

## Parámetros para mensajes de logs

### Ban
**Mensaje y descripción:**
`{userid}` | `{usertag}` | `{mod}` | `{modid}` | `{modtag}` | `{reason}`

**Footer:**
`{userid}` | `{usertag}` | `{modid}` | `{modtag}`

### Kick
**Mensaje y descripción:**
`{userid}` | `{usertag}` | `{mod}` | `{modid}` | `{modtag}` | `{reason}`

**Footer:**
`{userid}` | `{usertag}` | `{modid}` | `{modtag}`

### Unban
**Mensaje y descripción:**
`{userid}` | `{usertag}` | `{mod}` | `{modid}` | `{modtag}`

**Footer:**
`{userid}` | `{usertag}` | `{modid}` | `{modtag}`

### Entradas
**Mensaje y descripción:**
`{userid}` | `{usertag}` | `{user}` | `{accage}`

**Footer:**
`{userid}` | `{usertag}` | `{user}`

### Salidas
**Mensaje y descripción:**
`{userid}` | `{usertag}`

**Footer:**
`{userid}` | `{usertag}`

### Mensajes eliminados
**Mensaje y descripción:**
`{del_msg}` | `{usertag}` | `{userid}` | `{user}` | `{channel}` | `{channelid}`

**Footer:**
`{usertag}` | `{userid}` | `{channelid}`

### Mensajes editados
**Mensaje y descripción:**
`{usertag}` | `{userid}` | `{user}` | `{channel}` | `{channelid}` | `{old_msg}` | `{new_msg}`

**Footer:**
`{usertag}` | `{userid}` | `{channelid}`

### Warns
**Mensaje y descripción:**
`{userid}` | `{usertag}` | `{mod}` | `{modid}` | `{modtag}` | `{reason}` | `{user}`

**Footer:**
`{userid}` | `{usertag}` | `{modid}` | `{modtag}`

### Unwarns
**Mensaje y descripción:**
`{userid}` | `{usertag}` | `{mod}` | `{modid}` | `{modtag}` | `{reason}` | `{user}`

**Footer:**
`{userid}` | `{usertag}` | `{modid}` | `{modtag}`

## Explicación de parámetros

- `{reason}`: razón de la sanción
- `{user}`: mención del usuario sancionado, que borra o edita el mensaje o que entra al servidor
- `{userid}`: id del usuario sancionado, que borra o edita el mensaje o que entra al servidor
- `{usertag}`: nombre de usuario normal del usuario sancionado, que borra o edita el mensaje o que entra al servidor
- `{mod}`: mención del mod que sanciona
- `{modid}`: id del mod que sanciona
- `{modtag}`: nombre de usuario normal del mod que sanciona
- `{channel}`: mención del canal
- `{channelid}`: id del canal
- `{del_msg}`: contenido del mensaje eliminado
- `{old_msg}`: contenido anterior del mensaje editado
- `{new_msg}`: contenido del nuevo mensaje editado
- `{accage}`: muetra la edad de la cuenta en Discord
- `{\n}`: para representar el salto de línea en los logs