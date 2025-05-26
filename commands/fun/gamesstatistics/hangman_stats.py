import discord
from datetime import datetime
from database.minigames import get_user_stats

def get_hangman_stats_embed(user, stats, page=0):
    embed = discord.Embed(
        title=f"Estadísticas del Ahorcado - {user.display_name}",
        color=0x00BFFF
    )
    
    if page == 0:
        total_games = stats.get('total_games', 0)
        wins = stats.get('wins', 0)
        losses = stats.get('losses', 0)
        surrenders = stats.get('surrenders', 0)
        points = stats.get('points', 0)
        
        win_rate = (wins / total_games * 100) if total_games > 0 else 0
        
        embed.add_field(name="Total de partidas", value=str(total_games), inline=True)
        embed.add_field(name="Victorias", value=str(wins), inline=True)
        embed.add_field(name="Derrotas", value=str(losses), inline=True)
        embed.add_field(name="Abandonos", value=str(surrenders), inline=True)
        embed.add_field(name="Puntos", value=str(points), inline=True)
        embed.add_field(name="Porcentaje de victorias", value=f"{win_rate:.1f}%", inline=True)
        
        average_attempts = stats.get('average_attempts', 0)
        embed.add_field(name="Promedio de intentos", value=f"{average_attempts:.1f}", inline=True)
        
        last_played = stats.get('last_played')
        if last_played:
            last_played_str = last_played.strftime("%d/%m/%Y %H:%M")
            embed.add_field(name="Última partida", value=last_played_str, inline=True)
        
        challenges_sent = stats.get('challenges_sent', 0)
        challenges_received = stats.get('challenges_received', 0)
        embed.add_field(name="Desafíos enviados", value=str(challenges_sent), inline=True)
        embed.add_field(name="Desafíos recibidos", value=str(challenges_received), inline=True)
        
        embed.set_footer(text="Página 1/3 - Usa los botones para navegar")
    
    elif page == 1:
        words_guessed = stats.get('words_guessed', [])
        if words_guessed:
            recent_words = words_guessed[-10:]
            embed.add_field(
                name=f"Últimas palabras adivinadas ({len(words_guessed)} total)",
                value="• " + "\n• ".join(recent_words),
                inline=False
            )
        else:
            embed.add_field(name="Palabras adivinadas", value="Ninguna todavía", inline=False)
        
        words_failed = stats.get('words_failed', [])
        if words_failed:
            recent_failed = words_failed[-10:]
            embed.add_field(
                name=f"Últimas palabras fallidas ({len(words_failed)} total)",
                value="• " + "\n• ".join(recent_failed),
                inline=False
            )
        else:
            embed.add_field(name="Palabras fallidas", value="Ninguna todavía", inline=False)
        
        letters_used = stats.get('letters_used', {})
        if letters_used:
            sorted_letters = sorted(letters_used.items(), key=lambda x: x[1], reverse=True)
            top_letters = sorted_letters[:10]
            
            letter_stats = "\n".join([f"• {letter}: {count} veces" for letter, count in top_letters])
            embed.add_field(
                name="Letras más usadas",
                value=letter_stats,
                inline=False
            )
        
        embed.set_footer(text="Página 2/3 - Usa los botones para navegar")
    
    elif page == 2:
        games_history = stats.get('games_history', [])
        
        if games_history:
            recent_games = games_history[-5:]
            
            for i, game in enumerate(reversed(recent_games)):
                date = game.get('date')
                word = game.get('word', 'desconocida')
                result = game.get('result', 'desconocido')
                points = game.get('points', 0)
                
                result_text = {
                    'win': '✅ Victoria',
                    'loss': '❌ Derrota',
                    'surrender': '🏳️ Abandono'
                }.get(result, result)
                
                date_str = date.strftime("%d/%m/%Y %H:%M") if date else "Desconocida"
                
                embed.add_field(
                    name=f"Partida {i+1}",
                    value=f"Fecha: {date_str}\nPalabra: {word}\nResultado: {result_text}\nPuntos: {points}",
                    inline=True
                )
        else:
            embed.add_field(name="Historial de partidas", value="No hay partidas registradas", inline=False)
        
        embed.set_footer(text="Página 3/3 - Usa los botones para navegar")
    
    return embed

def get_hangman_stats_view(parent_view):
    class HangmanStatsView(discord.ui.View):
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
            stats = get_user_stats(parent_view.user.id, 'hangman')
            embed = get_hangman_stats_embed(parent_view.user, stats, parent_view.current_page)
            
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
            stats = get_user_stats(parent_view.user.id, 'hangman')
            embed = get_hangman_stats_embed(parent_view.user, stats, parent_view.current_page)
            
            for item in parent_view.children:
                if item.custom_id == "prev_page":
                    item.disabled = parent_view.current_page == 0
                elif item.custom_id == "next_page":
                    item.disabled = parent_view.current_page == 2
            
            await interaction.response.edit_message(embed=embed, view=parent_view)
    
    return HangmanStatsView()