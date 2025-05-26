import discord
from datetime import datetime

def get_blackjack_stats_embed(user, stats, page=0):
    embed = discord.Embed(
        title=f"Estadísticas del Blackjack - {user.display_name}",
        color=0x00BFFF
    )
    
    if page == 0:
        total_games = stats.get('total_games', 0)
        wins = stats.get('wins', 0)
        losses = stats.get('losses', 0)
        points = stats.get('points', 0)
        
        win_rate = (wins / total_games * 100) if total_games > 0 else 0
        
        embed.add_field(name="Total de partidas", value=str(total_games), inline=True)
        embed.add_field(name="Victorias", value=str(wins), inline=True)
        embed.add_field(name="Derrotas", value=str(losses), inline=True)
        embed.add_field(name="Puntos", value=str(points), inline=True)
        embed.add_field(name="Porcentaje de victorias", value=f"{win_rate:.1f}%", inline=True)
        
        blackjacks = stats.get('blackjacks', 0)
        busts = stats.get('busts', 0)
        embed.add_field(name="Blackjacks", value=str(blackjacks), inline=True)
        embed.add_field(name="Veces pasado de 21", value=str(busts), inline=True)
        
        last_played = stats.get('last_played')
        if last_played:
            last_played_str = last_played.strftime("%d/%m/%Y %H:%M")
            embed.add_field(name="Última partida", value=last_played_str, inline=True)
        
        embed.set_footer(text="Página 1/3 - Usa los botones para navegar")
    
    elif page == 1:
        cards_received = stats.get('cards_received', {})
        if cards_received:
            sorted_cards = sorted(cards_received.items(), key=lambda x: x[1], reverse=True)
            cards_text = "\n".join([f"• {card}: {count} veces" for card, count in sorted_cards[:10]])
            embed.add_field(name="Cartas más recibidas", value=cards_text or "Sin datos", inline=False)
        
        final_values = stats.get('final_values', [])
        if final_values:
            value_counts = {}
            for value in final_values:
                if value in value_counts:
                    value_counts[value] += 1
                else:
                    value_counts[value] = 1
            
            sorted_values = sorted(value_counts.items())
            values_text = "\n".join([f"• {value}: {count} veces" for value, count in sorted_values[:10]])
            embed.add_field(name="Valores finales más comunes", value=values_text or "Sin datos", inline=False)
        
        avg_cards = stats.get('average_cards', 0)
        embed.add_field(name="Promedio de cartas por mano", value=f"{avg_cards:.1f}", inline=True)
        
        best_hand = stats.get('best_hand', 0)
        embed.add_field(name="Mejor mano", value=str(best_hand), inline=True)
        
        embed.set_footer(text="Página 2/3 - Usa los botones para navegar")
    
    elif page == 2:
        games_history = stats.get('games_history', [])
        
        if games_history:
            recent_games = games_history[-5:]
            
            for i, game in enumerate(reversed(recent_games)):
                date = game.get('date')
                result = game.get('result', 'desconocido')
                final_value = game.get('final_value', 0)
                num_cards = game.get('num_cards', 0)
                
                result_text = {
                    'win': '✅ Victoria',
                    'loss': '❌ Derrota',
                    'bust': '💥 Pasado de 21'
                }.get(result, result)
                
                date_str = date.strftime("%d/%m/%Y %H:%M") if date else "Desconocida"
                
                embed.add_field(
                    name=f"Partida {i+1}",
                    value=f"Fecha: {date_str}\nResultado: {result_text}\nValor final: {final_value}\nNúmero de cartas: {num_cards}",
                    inline=True
                )
        else:
            embed.add_field(name="Historial de partidas", value="No hay partidas registradas", inline=False)
        
        embed.set_footer(text="Página 3/3 - Usa los botones para navegar")
    
    return embed

def get_blackjack_stats_view(parent_view):
    class BlackjackStatsView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)
            
            prev_button = discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label="◀️ Anterior",
                custom_id="prev_page",
                disabled=parent_view.current_page == 0
            )
            prev_button.callback = self.prev_page_callback
            self.add_item(prev_button)
            
            next_button = discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label="Siguiente ▶️",
                custom_id="next_page",
                disabled=parent_view.current_page == 2
            )
            next_button.callback = self.next_page_callback
            self.add_item(next_button)
        
        async def prev_page_callback(self, interaction: discord.Interaction):
            if interaction.user.id != parent_view.user.id:
                await interaction.response.send_message("Esta no es tu estadística.", ephemeral=True)
                return
            
            parent_view.current_page = max(0, parent_view.current_page - 1)
            from database.minigames import get_user_stats
            stats = get_user_stats(parent_view.user.id, 'blackjack')
            embed = get_blackjack_stats_embed(parent_view.user, stats, parent_view.current_page)
            
            for item in parent_view.children:
                if item.custom_id == "prev_page":
                    item.disabled = parent_view.current_page == 0
                elif item.custom_id == "next_page":
                    item.disabled = parent_view.current_page == 2
            
            await interaction.response.edit_message(embed=embed, view=parent_view)
        
        async def next_page_callback(self, interaction: discord.Interaction):
            if interaction.user.id != parent_view.user.id:
                await interaction.response.send_message("Esta no es tu estadística.", ephemeral=True)
                return
            
            parent_view.current_page = min(2, parent_view.current_page + 1)
            from database.minigames import get_user_stats
            stats = get_user_stats(parent_view.user.id, 'blackjack')
            embed = get_blackjack_stats_embed(parent_view.user, stats, parent_view.current_page)
            
            for item in parent_view.children:
                if item.custom_id == "prev_page":
                    item.disabled = parent_view.current_page == 0
                elif item.custom_id == "next_page":
                    item.disabled = parent_view.current_page == 2
            
            await interaction.response.edit_message(embed=embed, view=parent_view)
    
    return BlackjackStatsView()