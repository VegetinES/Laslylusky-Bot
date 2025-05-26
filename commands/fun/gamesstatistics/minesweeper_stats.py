import discord
from datetime import datetime

def get_minesweeper_stats_embed(user, stats, page=0):
    embed = discord.Embed(
        title=f"Estadísticas del Buscaminas - {user.display_name}",
        color=0x00BFFF
    )
    
    if page == 0:
        total_games = stats.get('total_games', 0)
        wins = stats.get('wins', 0)
        losses = stats.get('losses', 0)
        abandoned = stats.get('abandoned', 0)
        points = stats.get('points', 0)
        
        win_rate = (wins / total_games * 100) if total_games > 0 else 0
        
        embed.add_field(name="Total de partidas", value=str(total_games), inline=True)
        embed.add_field(name="Victorias", value=str(wins), inline=True)
        embed.add_field(name="Derrotas", value=str(losses), inline=True)
        embed.add_field(name="Abandonos", value=str(abandoned), inline=True)
        embed.add_field(name="Puntos", value=str(points), inline=True)
        embed.add_field(name="Porcentaje de victorias", value=f"{win_rate:.1f}%", inline=True)
        
        embed.add_field(name="Victorias en fácil", value=str(stats.get('wins_easy', 0)), inline=True)
        embed.add_field(name="Victorias en normal", value=str(stats.get('wins_normal', 0)), inline=True)
        embed.add_field(name="Victorias en difícil", value=str(stats.get('wins_hard', 0)), inline=True)
        
        last_played = stats.get('last_played')
        if last_played:
            last_played_str = last_played.strftime("%d/%m/%Y %H:%M")
            embed.add_field(name="Última partida", value=last_played_str, inline=True)
        
        embed.set_footer(text="Página 1/3 - Usa los botones para navegar")
    
    elif page == 1:
        best_time = stats.get('best_time')
        if best_time:
            embed.add_field(name="Mejor tiempo (victoria)", value=f"{best_time:.1f} segundos", inline=True)
        
        avg_time = stats.get('average_time')
        if avg_time:
            embed.add_field(name="Tiempo promedio", value=f"{avg_time:.1f} segundos", inline=True)
        
        total_cells_uncovered = stats.get('total_cells_uncovered', 0)
        embed.add_field(name="Total celdas descubiertas", value=str(total_cells_uncovered), inline=True)
        
        total_flags_placed = stats.get('total_flags_placed', 0)
        embed.add_field(name="Total banderas colocadas", value=str(total_flags_placed), inline=True)
        
        correct_flags = stats.get('correct_flags', 0)
        if total_flags_placed > 0:
            flag_accuracy = (correct_flags / total_flags_placed * 100)
            embed.add_field(name="Precisión de banderas", value=f"{flag_accuracy:.1f}%", inline=True)
        
        current_streak = stats.get('current_streak', 0)
        best_streak = stats.get('best_streak', 0)
        embed.add_field(name="Racha actual", value=str(current_streak), inline=True)
        embed.add_field(name="Mejor racha", value=str(best_streak), inline=True)
        
        embed.set_footer(text="Página 2/3 - Usa los botones para navegar")
    
    elif page == 2:
        games_history = stats.get('games_history', [])
        
        if games_history:
            recent_games = games_history[-5:]
            
            for i, game in enumerate(reversed(recent_games)):
                date = game.get('date')
                difficulty = game.get('difficulty', 'desconocida')
                result = game.get('result', 'desconocido')
                time = game.get('time', 0)
                cells_uncovered = game.get('cells_uncovered', 0)
                
                result_text = {
                    'win': '✅ Victoria',
                    'loss': '💣 Derrota',
                    'abandoned': '🏳️ Abandono'
                }.get(result, result)
                
                date_str = date.strftime("%d/%m/%Y %H:%M") if date else "Desconocida"
                
                embed.add_field(
                    name=f"Partida {i+1}",
                    value=f"Fecha: {date_str}\nDificultad: {difficulty}\nResultado: {result_text}\nTiempo: {time:.1f}s\nCeldas descubiertas: {cells_uncovered}",
                    inline=True
                )
        else:
            embed.add_field(name="Historial de partidas", value="No hay partidas registradas", inline=False)
        
        embed.set_footer(text="Página 3/3 - Usa los botones para navegar")
    
    return embed

def get_minesweeper_stats_view(parent_view):
    class MinesweeperStatsView(discord.ui.View):
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
            stats = get_user_stats(parent_view.user.id, 'minesweeper')
            embed = get_minesweeper_stats_embed(parent_view.user, stats, parent_view.current_page)
            
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
            stats = get_user_stats(parent_view.user.id, 'minesweeper')
            embed = get_minesweeper_stats_embed(parent_view.user, stats, parent_view.current_page)
            
            for item in parent_view.children:
                if item.custom_id == "prev_page":
                    item.disabled = parent_view.current_page == 0
                elif item.custom_id == "next_page":
                    item.disabled = parent_view.current_page == 2
            
            await interaction.response.edit_message(embed=embed, view=parent_view)
    
    return MinesweeperStatsView()