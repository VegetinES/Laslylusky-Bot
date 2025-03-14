import discord

async def show_tickets_help(interaction: discord.Interaction):
    try:
        embed = discord.Embed(
            title="Ayuda del Sistema de Tickets",
            description=(
                "El sistema de tickets permite a los usuarios crear tickets para solicitar ayuda "
                "o reportar problemas. Sigue estos pasos para configurar el sistema de tickets:"
            ),
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="1️⃣ Configurar Canal",
            value=(
                "```/config tickets canal canal_abrir_ticket:<canal> canal_logs:<canal> nombre_ticket:<nombre>```\n"
                "- `canal_abrir_ticket`: El canal donde aparecerá el botón para abrir tickets\n"
                "- `canal_logs`: Canal donde se registrarán las acciones de tickets\n"
                "- `nombre_ticket`: Formato para nombrar los tickets (debe incluir {id})"
            ),
            inline=False
        )
        
        embed.add_field(
            name="2️⃣ Configurar Permisos (Obligatorio)",
            value=(
                "```/config tickets permisos canal:<id> permiso:Gestionar tickets accion:añadir roles:<roles>```\n"
                "- `canal`: ID del canal configurado\n"
                "- `permiso`: Tipo de permiso (Gestionar, Ver, Cerrar, Añadir/eliminar)\n"
                "- `accion`: añadir o eliminar\n"
                "- `roles`: Roles con permiso (requerido roles o usuarios)\n"
                "- `usuarios`: Usuarios con permiso (requerido roles o usuarios)"
            ),
            inline=False
        )
        
        embed.add_field(
            name="3️⃣ Configurar Mensajes (Obligatorio)",
            value=(
                "```/config tickets mensajes canal:<id> tipo:<tipo> título:<texto> descripción:<texto>```\n"
                "- `canal`: ID del canal configurado\n"
                "- `tipo`: Tipo de mensaje (ticket abierto o abrir ticket)\n"
                "- `título`: Título del mensaje\n"
                "- `descripción`: Descripción del mensaje\n"
                "- `imagen`: URL de imagen (opcional)\n"
                "- `footer`: Texto del footer (opcional)\n"
                "- `color`: Color del embed (opcional)\n"
                "- `mensaje`: Mensaje adicional para tickets abiertos (opcional)"
            ),
            inline=False
        )
        
        embed.add_field(
            name="4️⃣ Modificar o Eliminar",
            value=(
                "```/config tickets modificar canal:<id> accion:<accion>```\n"
                "- `canal`: ID del canal configurado\n"
                "- `accion`: restablecer (reestablece los permisos y mensajes) o eliminar (elimina la configuración)"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Variables Disponibles",
            value=(
                "Para personalizar mensajes puedes usar:\n"
                "- `{user}`: Mención del usuario\n"
                "- `{usertag}`: Nombre del usuario con discriminador\n"
                "- `{userid}`: ID del usuario\n"
                "- `{\\n}`: Salto de línea"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Tipos de Permisos",
            value=(
                "- **Gestionar tickets**: Acceso completo al sistema (requerido)\n"
                "- **Ver tickets**: Puede ver todos los tickets\n"
                "- **Cerrar tickets**: Puede cerrar tickets\n"
                "- **Añadir/eliminar usuarios**: Puede añadir o quitar personas de los tickets"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Orden de Configuración",
            value=(
                "1. Configura el canal\n"
                "2. Configura los permisos (al menos 'Gestionar tickets')\n"
                "3. Configura los mensajes (ambos tipos)\n"
                "4. ¡Listo! Tu sistema de tickets está operativo"
            ),
            inline=False
        )
        
        embed.add_field(
            name="📚 Documentación",
            value=(
                "[Documentación en línea]"
                "(https://github.com/VegetinES/Laslylusky-Bot/tree/main/docs/user/ConfigurationTickets.md)"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=False)
        
    except Exception as e:
        print(f"Error en show_tickets_help: {e}")
        await interaction.response.send_message(
            f"<:No:825734196256440340> Ocurrió un error al mostrar la ayuda: {str(e)}",
            ephemeral=True
        )