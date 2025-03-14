# Configuración del Sistema de Tickets

## Descripción General

El sistema de tickets permite a los usuarios crear tickets para solicitar ayuda o reportar problemas. Los administradores del servidor pueden configurar diferentes aspectos del sistema a través de los comandos `/config tickets`.

## Comandos disponibles

- `/config tickets help` - Muestra la ayuda para el sistema de tickets
- `/config tickets canal` - Configura los canales principales para el sistema de tickets
- `/config tickets mensajes` - Configura los mensajes que se mostrarán en los tickets
- `/config tickets permisos` - Configura los permisos para los tickets
- `/config tickets modificar` - Modifica o elimina la configuración de tickets existente

## Documentación de comandos

### Configurar Canal

Ejecución de </config tickets canal:1348216356918657089>

```
/config tickets canal canal_abrir_ticket:<canal> canal_logs:<canal> nombre_ticket:<nombre>
```

- `canal_abrir_ticket`: El canal donde aparecerá el botón para abrir tickets
- `canal_logs`: Canal donde se registrarán las acciones de tickets
- `nombre_ticket`: Formato para nombrar los tickets (debe incluir {id})

### Configurar Permisos

Ejecución de </config tickets permisos:1348216356918657089>

```
/config tickets permisos canal:<id> permiso:<tipo> accion:<acción> [roles:<roles>] [usuarios:<usuarios>]
```

- `canal`: ID del canal configurado
- `permiso`: Tipo de permiso (Gestionar, Ver, Cerrar, Añadir/eliminar)
- `accion`: añadir o eliminar
- `roles`: Roles con permiso (requerido roles o usuarios)
- `usuarios`: Usuarios con permiso (requerido roles o usuarios)

### Configurar Mensajes

Ejecución de </config tickets mensajes:1348216356918657089>

```
/config tickets mensajes canal:<id> tipo:<tipo> título:<texto> descripción:<texto> [imagen:<url>] [footer:<texto>] [color:<color>] [mensaje:<texto>]
```

- `canal`: ID del canal configurado
- `tipo`: Tipo de mensaje (ticket abierto o abrir ticket)
- `título`: Título del mensaje
- `descripción`: Descripción del mensaje
- `imagen`: URL de imagen (opcional)
- `footer`: Texto del footer (opcional)
- `color`: Color del embed (opcional)
- `mensaje`: Mensaje adicional para tickets abiertos (opcional)

### Modificar o Eliminar

Ejecución de </config tickets modificar:1348216356918657089>

```
/config tickets modificar canal:<id> accion:<accion>
```

- `canal`: ID del canal configurado
- `accion`: restablecer (reestablece los permisos y mensajes) o eliminar (elimina la configuración)

## Tipos de Permisos

- **Gestionar tickets**: Acceso completo al sistema (requerido)
- **Ver tickets**: Puede ver todos los tickets
- **Cerrar tickets**: Puede cerrar tickets
- **Añadir/eliminar usuarios**: Puede añadir o quitar personas de los tickets

## Variables Disponibles

Para personalizar mensajes puedes usar:
- `{user}`: Mención del usuario
- `{usertag}`: Nombre del usuario con discriminador
- `{userid}`: ID del usuario
- `{\n}`: Salto de línea

## Orden de Configuración

1. Configura el canal
2. Configura los permisos (al menos 'Gestionar tickets')
3. Configura los mensajes (ambos tipos)
4. ¡Listo! Tu sistema de tickets está operativo