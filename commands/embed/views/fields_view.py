import discord
from discord import ui
from ..modals.embed_modals import EmbedFieldModal
from ..constants import MAX_FIELDS

class FieldsView(ui.View):
    def __init__(self, edit_view):
        super().__init__(timeout=1800)
        self.edit_view = edit_view
        self.embed = edit_view.embed
        
        if len(self.embed.fields) > 0:
            self.add_item(FieldSelector(self))
    
    async def show(self, interaction):
        try:
            await interaction.response.edit_message(
                content=f"Gestión de campos - Embed {self.edit_view.embed_index + 1}",
                embed=discord.Embed(
                    title="Campos del Embed",
                    description=f"Campos actuales: {len(self.embed.fields)}/{MAX_FIELDS}",
                    color=discord.Color.blue()
                ),
                view=self
            )
        except discord.errors.InteractionResponded:
            print("FieldsView.show: Interacción ya respondida, intentando followup")
            try:
                await interaction.followup.edit_message(
                    message_id=interaction.message.id,
                    content=f"Gestión de campos - Embed {self.edit_view.embed_index + 1}",
                    embed=discord.Embed(
                        title="Campos del Embed",
                        description=f"Campos actuales: {len(self.embed.fields)}/{MAX_FIELDS}",
                        color=discord.Color.blue()
                    ),
                    view=self
                )
            except Exception as e:
                print(f"FieldsView.show: Error en followup: {e}")
                await interaction.followup.send(
                    "Hubo un problema al mostrar la gestión de campos. Intenta nuevamente.",
                    ephemeral=True
                )
    
    @ui.button(label="Volver atrás", style=discord.ButtonStyle.secondary)
    async def go_back(self, interaction: discord.Interaction, button: ui.Button):
        await self.edit_view.show(interaction)
    
    @ui.button(label="Añadir campo", style=discord.ButtonStyle.success)
    async def add_field(self, interaction: discord.Interaction, button: ui.Button):
        if len(self.embed.fields) >= MAX_FIELDS:
            await interaction.response.send_message(
                f"Has alcanzado el límite máximo de {MAX_FIELDS} campos.",
                ephemeral=True
            )
            return
        
        modal = EmbedFieldModal(self.edit_view, -1)
        await interaction.response.send_modal(modal)
    
    @ui.button(label="Eliminar todos", style=discord.ButtonStyle.danger)
    async def clear_fields(self, interaction: discord.Interaction, button: ui.Button):
        self.embed.clear_fields()
        await self.show(interaction)

class FieldSelector(ui.Select):
    def __init__(self, fields_view):
        self.fields_view = fields_view
        self.embed = fields_view.embed
        
        options = []
        for i, field in enumerate(self.embed.fields):
            name = field.name if len(field.name) <= 25 else field.name[:22] + "..."
            value = field.value[:50] if len(field.value) <= 50 else field.value[:47] + "..."
            
            options.append(discord.SelectOption(
                label=f"Campo {i+1}: {name}",
                value=str(i),
                description=value
            ))
        
        super().__init__(placeholder="Selecciona un campo para editar", options=options)
    
    async def callback(self, interaction: discord.Interaction):
        field_index = int(self.values[0])
        edit_field_view = EditFieldView(self.fields_view, field_index)
        await edit_field_view.show(interaction)

class EditFieldView(ui.View):
    def __init__(self, fields_view, field_index):
        super().__init__(timeout=1800)
        self.fields_view = fields_view
        self.field_index = field_index
        self.field = fields_view.embed.fields[field_index]
    
    async def show(self, interaction):
        field_info = discord.Embed(
            title=f"Campo {self.field_index + 1}",
            color=discord.Color.blue()
        )
        field_info.add_field(name="Nombre", value=self.field.name, inline=False)
        field_info.add_field(name="Valor", value=self.field.value, inline=False)
        field_info.add_field(name="Inline", value="Sí" if self.field.inline else "No", inline=False)
        
        await interaction.response.edit_message(
            content=None,
            embed=field_info,
            view=self
        )
    
    @ui.button(label="Volver", style=discord.ButtonStyle.secondary)
    async def go_back(self, interaction: discord.Interaction, button: ui.Button):
        await self.fields_view.show(interaction)
    
    @ui.button(label="Editar", style=discord.ButtonStyle.primary)
    async def edit_field(self, interaction: discord.Interaction, button: ui.Button):
        modal = EmbedFieldModal(self.fields_view.edit_view, self.field_index)
        await interaction.response.send_modal(modal)
    
    @ui.button(label="Eliminar", style=discord.ButtonStyle.danger)
    async def delete_field(self, interaction: discord.Interaction, button: ui.Button):
        self.fields_view.embed.remove_field(self.field_index)
        await self.fields_view.show(interaction)