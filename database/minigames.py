from pymongo import MongoClient
import datetime

client = MongoClient('localhost', 27017)
db = client['minigames']

hangman_collection = db['hangman']
minesweeper_collection = db['minesweeper']
blackjack_collection = db['blackjack']

def get_user_stats(user_id, game_type='hangman'):
    if game_type == 'hangman':
        stats = hangman_collection.find_one({'user_id': user_id})
        if not stats:
            stats = {
                'user_id': user_id,
                'total_games': 0,
                'wins': 0,
                'losses': 0,
                'surrenders': 0,
                'points': 0,
                'words_guessed': [],
                'words_failed': [],
                'letters_used': {},
                'average_attempts': 0,
                'fastest_win': None,
                'longest_win': None,
                'last_played': None,
                'games_history': [],
                'challenges_sent': 0,
                'challenges_received': 0
            }
            hangman_collection.insert_one(stats)
        return stats
    elif game_type == 'minesweeper':
        stats = minesweeper_collection.find_one({'user_id': user_id})
        if not stats:
            stats = {
                'user_id': user_id,
                'total_games': 0,
                'wins': 0,
                'losses': 0,
                'abandoned': 0,
                'points': 0,
                'wins_easy': 0,
                'wins_normal': 0,
                'wins_hard': 0,
                'best_time': None,
                'average_time': 0,
                'total_cells_uncovered': 0,
                'total_flags_placed': 0,
                'correct_flags': 0,
                'current_streak': 0,
                'best_streak': 0,
                'last_played': None,
                'games_history': []
            }
            minesweeper_collection.insert_one(stats)
        return stats
    elif game_type == 'blackjack':
        stats = blackjack_collection.find_one({'user_id': user_id})
        if not stats:
            stats = {
                'user_id': user_id,
                'total_games': 0,
                'wins': 0,
                'losses': 0,
                'points': 0,
                'blackjacks': 0,
                'busts': 0,
                'cards_received': {},
                'final_values': [],
                'best_hand': 0,
                'average_cards': 0,
                'current_streak': 0,
                'best_streak': 0,
                'last_played': None,
                'games_history': []
            }
            blackjack_collection.insert_one(stats)
        return stats
    return None

def update_hangman_stats(user_id, game_data):
    current_stats = get_user_stats(user_id, 'hangman')
    
    current_stats['total_games'] += 1
    current_stats['last_played'] = datetime.datetime.now()
    
    if game_data.get('result') == 'win':
        current_stats['wins'] += 1
        current_stats['points'] += game_data.get('points', 0)
        current_stats['words_guessed'].append(game_data.get('word', '').lower())
        
        game_duration = game_data.get('duration')
        if game_duration:
            if not current_stats['fastest_win'] or game_duration < current_stats['fastest_win']:
                current_stats['fastest_win'] = game_duration
            if not current_stats['longest_win'] or game_duration > current_stats['longest_win']:
                current_stats['longest_win'] = game_duration
    
    elif game_data.get('result') == 'loss':
        current_stats['losses'] += 1
        current_stats['words_failed'].append(game_data.get('word', '').lower())
    
    elif game_data.get('result') == 'surrender':
        current_stats['surrenders'] += 1
        current_stats['words_failed'].append(game_data.get('word', '').lower())
        penalty = game_data.get('penalty', 0)
        current_stats['points'] = max(0, current_stats['points'] - penalty)
    
    for letter, count in game_data.get('letters_used', {}).items():
        if letter in current_stats['letters_used']:
            current_stats['letters_used'][letter] += count
        else:
            current_stats['letters_used'][letter] = count
    
    total_attempts = sum(game.get('attempts', 0) for game in current_stats['games_history'])
    if current_stats['total_games'] > 0:
        current_stats['average_attempts'] = total_attempts / current_stats['total_games']
    
    game_history_entry = {
        'date': datetime.datetime.now(),
        'word': game_data.get('word', '').lower(),
        'result': game_data.get('result'),
        'opponent': game_data.get('opponent'),
        'points': game_data.get('points', 0),
        'attempts': game_data.get('attempts', 0),
        'duration': game_data.get('duration')
    }
    current_stats['games_history'].append(game_history_entry)
    
    if game_data.get('is_challenge'):
        if game_data.get('is_challenger'):
            current_stats['challenges_sent'] += 1
        else:
            current_stats['challenges_received'] += 1
    
    hangman_collection.update_one(
        {'user_id': user_id},
        {'$set': current_stats}
    )
    
    return current_stats

def update_minesweeper_stats(user_id, game_data):
    current_stats = get_user_stats(user_id, 'minesweeper')
    
    current_stats['total_games'] += 1
    current_stats['last_played'] = datetime.datetime.now()
    current_stats['total_cells_uncovered'] += game_data.get('cells_uncovered', 0)
    current_stats['total_flags_placed'] += game_data.get('flags_placed', 0)
    
    result = game_data.get('result')
    if result == 'win':
        current_stats['wins'] += 1
        current_stats['points'] += game_data.get('points', 0)
        current_stats['current_streak'] += 1
        
        if current_stats['current_streak'] > current_stats['best_streak']:
            current_stats['best_streak'] = current_stats['current_streak']
        
        difficulty = game_data.get('difficulty', '').lower()
        if difficulty == 'fácil':
            current_stats['wins_easy'] += 1
        elif difficulty == 'normal':
            current_stats['wins_normal'] += 1
        elif difficulty == 'difícil':
            current_stats['wins_hard'] += 1
        
        game_time = game_data.get('time')
        if game_time:
            if not current_stats['best_time'] or game_time < current_stats['best_time']:
                current_stats['best_time'] = game_time
    
    elif result == 'loss':
        current_stats['losses'] += 1
        current_stats['current_streak'] = 0
    
    elif result == 'abandoned':
        current_stats['abandoned'] += 1
        current_stats['current_streak'] = 0
    
    current_stats['correct_flags'] += game_data.get('correct_flags', 0)
    
    games_with_time = [game for game in current_stats['games_history'] if game.get('time')]
    if games_with_time:
        total_time = sum(game.get('time', 0) for game in games_with_time)
        current_stats['average_time'] = total_time / len(games_with_time)
    
    game_history_entry = {
        'date': datetime.datetime.now(),
        'difficulty': game_data.get('difficulty', ''),
        'result': result,
        'time': game_data.get('time', 0),
        'cells_uncovered': game_data.get('cells_uncovered', 0),
        'flags_placed': game_data.get('flags_placed', 0),
        'correct_flags': game_data.get('correct_flags', 0),
        'points': game_data.get('points', 0)
    }
    current_stats['games_history'].append(game_history_entry)
    
    minesweeper_collection.update_one(
        {'user_id': user_id},
        {'$set': current_stats}
    )
    
    return current_stats

def update_blackjack_stats(user_id, game_data):
    current_stats = get_user_stats(user_id, 'blackjack')
    
    current_stats['total_games'] += 1
    current_stats['last_played'] = datetime.datetime.now()
    
    result = game_data.get('result')
    final_value = game_data.get('final_value', 0)
    cards = game_data.get('cards', [])
    
    if final_value > 0:
        current_stats['final_values'].append(final_value)
    
    for card in cards:
        card_value = card[:-1]
        if card_value in current_stats['cards_received']:
            current_stats['cards_received'][card_value] += 1
        else:
            current_stats['cards_received'][card_value] = 1
    
    if result == 'win':
        current_stats['wins'] += 1
        current_stats['points'] += game_data.get('points', 0)
        current_stats['current_streak'] += 1
        
        if current_stats['current_streak'] > current_stats['best_streak']:
            current_stats['best_streak'] = current_stats['current_streak']
        
        if final_value > current_stats['best_hand']:
            current_stats['best_hand'] = final_value
            
        if final_value == 21 and len(cards) == 2:
            current_stats['blackjacks'] += 1
    
    elif result == 'loss':
        current_stats['losses'] += 1
        current_stats['current_streak'] = 0
    
    elif result == 'bust':
        current_stats['losses'] += 1
        current_stats['busts'] += 1
        current_stats['current_streak'] = 0
    
    total_cards = sum(len(game.get('cards', [])) for game in current_stats['games_history']) + len(cards)
    if current_stats['total_games'] > 0:
        current_stats['average_cards'] = total_cards / (current_stats['total_games'] + 1)
    
    game_history_entry = {
        'date': datetime.datetime.now(),
        'result': result,
        'final_value': final_value,
        'num_cards': len(cards),
        'cards': cards,
        'points': game_data.get('points', 0)
    }
    current_stats['games_history'].append(game_history_entry)
    
    blackjack_collection.update_one(
        {'user_id': user_id},
        {'$set': current_stats}
    )
    
    return current_stats

def get_top_players(game_type='hangman', limit=10, sort_by='points'):
    if game_type == 'hangman':
        return list(hangman_collection.find().sort(sort_by, -1).limit(limit))
    elif game_type == 'minesweeper':
        return list(minesweeper_collection.find().sort(sort_by, -1).limit(limit))
    elif game_type == 'blackjack':
        return list(blackjack_collection.find().sort(sort_by, -1).limit(limit))
    return []

def get_game_stats(game_type='hangman'):
    if game_type == 'hangman':
        total_games = hangman_collection.aggregate([
            {'$group': {'_id': None, 'total': {'$sum': '$total_games'}}}
        ])
        
        total_games_result = list(total_games)
        total_games_count = total_games_result[0]['total'] if total_games_result else 0
        
        return {
            'total_games': total_games_count,
            'total_players': hangman_collection.count_documents({}),
            'top_players': get_top_players(game_type)
        }
    elif game_type == 'minesweeper':
        total_games = minesweeper_collection.aggregate([
            {'$group': {'_id': None, 'total': {'$sum': '$total_games'}}}
        ])
        
        total_games_result = list(total_games)
        total_games_count = total_games_result[0]['total'] if total_games_result else 0
        
        return {
            'total_games': total_games_count,
            'total_players': minesweeper_collection.count_documents({}),
            'top_players': get_top_players(game_type)
        }
    elif game_type == 'blackjack':
        total_games = blackjack_collection.aggregate([
            {'$group': {'_id': None, 'total': {'$sum': '$total_games'}}}
        ])
        
        total_games_result = list(total_games)
        total_games_count = total_games_result[0]['total'] if total_games_result else 0
        
        return {
            'total_games': total_games_count,
            'total_players': blackjack_collection.count_documents({}),
            'top_players': get_top_players(game_type)
        }
    return {}