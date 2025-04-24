# Sistema de Tickets - Guía Completa

## Descripción General

El sistema de tickets ofrece una solución avanzada para que los usuarios de tu servidor puedan crear conversaciones privadas con tu equipo de soporte. Utilizando hilos privados de Discord, proporciona una experiencia organizada y personalizable que mejora la comunicación y la gestión de solicitudes.

## Características Principales

- **Hilos privados:** Tickets organizados como hilos Discord
- **Personalización completa:** Múltiples tipos de tickets con mensajes personalizados
- **Control de acceso:** Sistema de permisos para roles y usuarios específicos
- **Registros detallados:** Seguimiento de todas las acciones realizadas
- **Interfaz intuitiva:** Fácil de usar tanto para administradores como usuarios

## Pasos de Configuración

### 1. Crear y Configurar Ticket

Para comenzar, utiliza el menú principal de tickets:

```
/config tickets
```

Selecciona "Gestionar Tickets" y luego "Crear Nuevo Ticket". El asistente de configuración te guiará a través de los siguientes pasos:

1. Seleccionar el canal donde aparecerá el botón de tickets
2. Seleccionar el canal donde se registrarán las acciones (logs)

### 2. Configurar Permisos

Es necesario configurar quién tendrá acceso a la gestión de tickets:

- **Permisos de Gestión:** Permite control total sobre tickets
  - Añadir roles: Asigna permisos a roles enteros
  - Añadir usuarios: Asigna permisos a usuarios específicos
- **Permisos de Visualización:** Permite solo ver tickets sin interactuar

### 3. Personalizar Mensajes

Configura dos tipos de mensajes principales:

- **Mensaje para abrir tickets:** El mensaje con botones visible para todos
  - Título y descripción personalizables
  - Imágenes, colores y campos adicionales
  - Botones de diferentes estilos
- **Mensaje de ticket abierto:** El que se muestra dentro del ticket cuando se crea
  - Puede ser diferente para cada tipo de ticket
  - Totalmente personalizable con embeds

### 4. Configurar Botones

Añade hasta 5 botones para diferentes tipos de solicitudes:
- Personaliza texto, emoji y estilo visual
- Define formato de nombre único para cada tipo
- Configura mensajes de respuesta específicos

### 5. Guardar y Desplegar

Al guardar, el sistema automáticamente:
- Configura los permisos del canal
- Envía el mensaje con botones
- Activa el sistema para uso inmediato

## Formato de Nombres de Tickets

Personaliza el formato usando estas variables:
- `{id}`: Número único autoincremental por tipo de ticket
- `{userid}`: ID del usuario que abre el ticket
- `{usertag}`: Nombre de usuario en Discord

Ejemplo: `soporte-{id}-{usertag}` resultaría en "soporte-1-Usuario#1234"

## Interacción con el Sistema

### Para Usuarios
- Hacer clic en el botón correspondiente al tipo de ayuda que necesitan
- El ticket se crea como hilo privado donde solo pueden ver/participar ellos y el equipo
- Reciben notificaciones cuando el personal responde

### Para el Equipo de Soporte
- **Añadir miembros:** Añadir usuarios adicionales al ticket
- **Eliminar miembros:** Remover usuarios del ticket
- **Archivar tickets:** Cerrar tickets resueltos
- **Reabrir tickets:** Continuar conversaciones en tickets archivados

## Consejos para el Uso Óptimo

- Configura diferentes tipos de tickets para distintas necesidades
- Utiliza colores distintos para identificar fácilmente cada categoría
- Configura mensajes claros que expliquen el propósito de cada tipo
- Revisa los logs periódicamente para monitorear la actividad
- Asigna permisos de gestión solo a miembros de confianza

## Solución de Problemas

Si encuentras algún problema durante la configuración:
- Verifica que los canales seleccionados tengan los permisos correctos
- Asegúrate de haber asignado al menos un rol o usuario a los permisos de gestión
- Comprueba que el formato de nombre incluya al menos la variable `{id}`
- Confirma que los mensajes contengan información clara sobre el propósito de cada ticket