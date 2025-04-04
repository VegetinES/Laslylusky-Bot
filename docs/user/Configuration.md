# Configuración del Bot

## Comandos disponibles

- `/config help` - Muestra esta ayuda
- `/config data` - Muestra la configuración actual del servidor
- `/config update` - Restablece la configuración a los valores predeterminados
- `/config cmd` - Activa o desactiva comandos específicos
- `/config logs` - Configuración de registros de auditoría
- `/config perms` - Configuración de permisos
- `/config tickets help` - Muestra la ayuda de configuración de los tickets

## Documentación de comandos

### Config perms

Ejecución de `/config perms`

```
/config perms {permiso} {accion} ({roles}/{usuarios})
```

- `{permiso}`: el permiso que se quiere configurar
- `{accion}`: añadir o eliminar el permiso

Al menos uno de estos campos es obligatorio:

- `{roles}`: menciona o pon los roles que quieres añadir o eliminar, separados por espacios
- `{usuarios}`: menciona o pon los usuarios que quieres añadir o eliminar, separados por espacios

### Config cmd

Ejecución de `/config cmd`

```
/config cmd {comando} {estado}
```

- `{comando}`: el comando que se quiere activar o desactivar
- `{estado}`: activar o desactivar el comando

### Config update

Ejecución de `/config update`

```
/config update
```

Este comando restablece la configuración del servidor a los valores predeterminados.

### Config data

Ejecución de `/config data`

```
/config data
```

Este comando muestra la configuración actual del servidor.

### Config logs

Ejecución de `/config logs`:

```
/config logs {log}
```

- `{log}`: el log que se quiere configurar.

### Config tickets help

Ejecución de `/config tickets help`

```
/config tickets help
```

Este comando muestra la ayuda específica para configurar el sistema de tickets.

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
`{userid}` | `{usertag}` | `{user}` | `{accage}` | `{acc_age}`

**Footer:**
`{userid}` | `{usertag}` | `{user}`

### Salidas
**Mensaje y descripción:**
`{userid}` | `{usertag}` | `{acc_age}` | `{server_age}`

**Footer:**
`{userid}` | `{usertag}`

### Mensajes eliminados
**Mensaje y descripción:**
`{del_msg}` | `{usertag}` | `{userid}` | `{user}` | `{channel}` | `{channelid}` | `{attached}`

**Footer:**
`{usertag}` | `{userid}` | `{channelid}`

### Mensajes editados
**Mensaje y descripción:**
`{usertag}` | `{userid}` | `{user}` | `{channel}` | `{channelid}` | `{old_msg}` | `{new_msg}` | `{attached}`

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

### Entrada a canales de voz
**Mensaje y descripción:**
`{user}` | `{usertag}` | `{userid}` | `{channel}` | `{channelid}`

**Footer:**
`{usertag}` | `{userid}` | `{channelid}`

### Salida de canales de voz
**Mensaje y descripción:**
`{user}` | `{usertag}` | `{userid}` | `{channel}` | `{channelid}`

**Footer:**
`{usertag}` | `{userid}` | `{channelid}`

### Roles añadidos a usuarios
**Mensaje y descripción:**
`{user}` | `{usertag}` | `{userid}` | `{role}` | `{roleid}`

**Footer:**
`{usertag}` | `{userid}` | `{roleid}`

### Roles removidos de usuarios
**Mensaje y descripción:**
`{user}` | `{usertag}` | `{userid}` | `{role}` | `{roleid}`

**Footer:**
`{usertag}` | `{userid}` | `{roleid}`

### Canales creados
**Mensaje y descripción:**
`{channel}` | `{channelid}` | `{category}`

**Footer:**
`{channelid}`

### Canales eliminados
**Mensaje y descripción:**
`{channel}` | `{channelid}` | `{category}`

**Footer:**
`{channelid}`

### Actualización de avatar o nombre
**Mensaje y descripción:**
`{user}` | `{usertag}` | `{userid}` | `{old_avatar_link}` | `{new_avatar_link}` | `{old_name}` | `{new_name}`

**Footer:**
`{usertag}` | `{userid}`

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
- `{attached}`: contenido de archivos adjuntos en caso de haberlos
- `{acc_age}`: edad de la cuenta de Discord
- `{server_age}`: tiempo que lleva el usuario en el servidor
- `{\n}`: para representar el salto de línea en los logs
- `{role}`: mención del rol que se añade o quita
- `{roleid}`: id del rol que se añade o quita
- `{category}`: nombre de la categoría del canal (o "sin categoría")
- `{old_avatar_link}`: link del antiguo avatar del usuario, formato [antiguo avatar](link)
- `{new_avatar_link}`: link del nuevo avatar del usuario, formato [nuevo avatar](link)
- `{old_name}`: antiguo nombre del usuario (o "el nombre no cambió")
- `{new_name}`: nuevo nombre del usuario (o "el nombre no cambió")