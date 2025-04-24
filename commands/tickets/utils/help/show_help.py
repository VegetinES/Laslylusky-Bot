import discord

async def show_tickets_help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Sistema de Tickets - Guía Completa",
        description="El sistema de tickets permite a tus usuarios crear conversaciones privadas con el equipo de soporte de tu servidor de manera organizada y eficiente.",
        color=0x3498db
    )
    
    embed.add_field(
        name="✨ Características Principales",
        value=(
            "• **Hilos privados:** Tickets organizados como hilos Discord\n"
            "• **Personalización completa:** Múltiples tipos de tickets con mensajes personalizados\n"
            "• **Control de acceso:** Sistema de permisos para roles y usuarios específicos\n"
            "• **Registros detallados:** Seguimiento de todas las acciones realizadas\n"
            "• **Interfaz intuitiva:** Fácil de usar tanto para administradores como usuarios"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🔧 Pasos de Configuración",
        value=(
            "1️⃣ **Selecciona canales:** Configura un canal para crear tickets y otro para logs\n"
            "2️⃣ **Define permisos:** Asigna roles y usuarios que podrán gestionar tickets\n"
            "3️⃣ **Personaliza mensajes:** Configura los mensajes de apertura y respuesta\n"
            "4️⃣ **Añade botones:** Crea botones personalizados para diferentes tipos de tickets\n"
            "5️⃣ **Guarda y despliega:** El sistema creará automáticamente el mensaje con los botones"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🔒 Tipos de Permisos",
        value=(
            "**Gestionar tickets:** Permite visualizar, escribir, añadir/eliminar usuarios y archivar tickets\n"
            "**Ver tickets:** Permite solamente ver los tickets sin interactuar con ellos"
        ),
        inline=False
    )
    
    embed.add_field(
        name="📝 Formato de Nombres",
        value=(
            "Personaliza el formato de nombres de tickets usando estas variables:\n"
            "`{id}` - Número único autoincremental por tipo de ticket\n"
            "`{userid}` - ID del usuario que abre el ticket\n"
            "`{usertag}` - Nombre de usuario en Discord\n"
            "Ejemplo: `soporte-{id}-{usertag}`"
        ),
        inline=False
    )
    
    embed.add_field(
        name="👥 Interacción con Tickets",
        value=(
            "• **Crear ticket:** Los usuarios hacen clic en el botón correspondiente\n"
            "• **Añadir miembros:** El equipo puede añadir más usuarios al ticket\n"
            "• **Eliminar miembros:** También puede remover usuarios del ticket\n"
            "• **Archivar ticket:** Al finalizar, se pueden archivar los tickets\n"
            "• **Reabrir ticket:** Se pueden reabrir tickets respondiendo en ellos"
        ),
        inline=False
    )
    
    embed.set_footer(text="Sistema de Tickets • Configura múltiples tipos para diferentes necesidades (soporte, reportes, sugerencias, etc.)")
    
    await interaction.response.edit_message(
        embed=embed,
        view=TicketsHelpView()
    )

class TicketsHelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        
        back_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Volver al Menú Principal",
            emoji="⬅️",
            custom_id="back_to_main"
        )
        back_button.callback = self.back_callback
        self.add_item(back_button)
    
    async def back_callback(self, interaction: discord.Interaction):
        from ...views.main_view import TicketsMainView
        
        view = TicketsMainView(interaction.client)
        embed = discord.Embed(
            title="Configuración del Sistema de Tickets",
            description="Configura el sistema de tickets para tu servidor",
            color=0x3498db
        )
        
        embed.add_field(
            name="❓ Ayuda",
            value="Muestra información detallada sobre cómo configurar y usar el sistema de tickets.",
            inline=False
        )
        
        embed.add_field(
            name="🎫 Gestionar Tickets",
            value="Configura, modifica o elimina los tickets de tu servidor.",
            inline=False
        )
        
        embed.add_field(
            name="❌ Cancelar",
            value="Cancela la configuración de tickets.",
            inline=False
        )
        
        await interaction.response.edit_message(
            embed=embed,
            view=view
        )