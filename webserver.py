from flask import Flask, render_template, redirect, url_for, request, send_from_directory, Response, session, jsonify
from threading import Thread
import logging
import requests
import os
from urllib.parse import urlencode
from web.permissions import create_permission_checker
from web.server_management import ServerManager
from web.tickets_management import TicketsManager
from web.logs_management import LogsManager
from web.permissions_management import PermissionsManager
import asyncio
import base64
import json

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask('', template_folder='web/templates', static_folder='web/static')
app.secret_key = os.getenv('FLASK_SECRET_KEY')

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
DISCORD_API_BASE = os.getenv('DISCORD_API_BASE')
DISCORD_OAUTH2_URL = os.getenv('DISCORD_OAUTH2_URL')

bot_instance = None
permission_checker = None
server_manager = None
tickets_manager = None
logs_manager = None
permissions_manager = None

def set_bot_instance(bot):
    global bot_instance, permission_checker, server_manager, tickets_manager, logs_manager, permissions_manager
    bot_instance = bot
    permission_checker = create_permission_checker(bot)
    server_manager = ServerManager(bot)
    tickets_manager = TicketsManager(bot)
    logs_manager = LogsManager(bot)
    permissions_manager = PermissionsManager(bot)

def get_bot_guilds():
    if bot_instance:
        return [{'id': str(guild.id), 'name': guild.name, 'icon': guild.icon} for guild in bot_instance.guilds]
    return []

def create_oauth_state(language='es', redirect_path='dashboard'):
    state_data = {
        'lang': language,
        'redirect': redirect_path
    }
    state_json = json.dumps(state_data)
    state_encoded = base64.urlsafe_b64encode(state_json.encode()).decode()
    return state_encoded

def decode_oauth_state(state):
    try:
        state_json = base64.urlsafe_b64decode(state.encode()).decode()
        return json.loads(state_json)
    except:
        return {'lang': 'es', 'redirect': 'dashboard'}

@app.route('/')
def root():
    return redirect('/es/')

@app.route('/es/')
def index_es():
    session['preferred_language'] = 'es'
    return render_template('es/home.html', lang='es')

@app.route('/en/')
def index_en():
    session['preferred_language'] = 'en'
    return render_template('en/home.html', lang='en')

@app.route('/es/privacidad')
def privacy_es():
    session['preferred_language'] = 'es'
    return render_template('es/privacidad.html', lang='es')

@app.route('/en/privacy')
def privacy_en():
    session['preferred_language'] = 'en'
    return render_template('en/privacy.html', lang='en')

@app.route('/es/tos')
def terms_es():
    session['preferred_language'] = 'es'
    return render_template('es/tos.html', lang='es')

@app.route('/en/tos')
def terms_en():
    session['preferred_language'] = 'en'
    return render_template('en/tos.html', lang='en')

@app.route('/es/documentacion/help')
def doc_help_es():
    session['preferred_language'] = 'es'
    return render_template('es/documentacion/help.html', lang='es')

@app.route('/en/documentation/help')
def doc_help_en():
    session['preferred_language'] = 'en'
    return render_template('en/documentation/help.html', lang='en')

@app.route('/es/documentacion/configuracion')
def doc_config_es():
    session['preferred_language'] = 'es'
    return render_template('es/documentacion/configuracion.html', lang='es')

@app.route('/en/documentation/configuration')
def doc_config_en():
    session['preferred_language'] = 'en'
    return render_template('en/documentation/configuration.html', lang='en')

@app.route('/es/documentacion/tickets')
def tickets_documentation_es():
    session['preferred_language'] = 'es'
    return render_template('es/documentacion/tickets.html', lang='es')

@app.route('/en/documentation/tickets')
def tickets_documentation_en():
    session['preferred_language'] = 'en'
    return render_template('en/documentation/tickets.html', lang='en')

@app.route('/es/vegetines')
def vegetines_es():
    session['preferred_language'] = 'es'
    return render_template('es/vegetines/vegetines.html', lang='es')

@app.route('/en/vegetines')
def vegetines_en():
    session['preferred_language'] = 'en'
    return render_template('en/vegetines/vegetines.html', lang='en')

@app.route('/es/vegetines/portafolio')
def vegetines_portfolio_es():
    session['preferred_language'] = 'es'
    return render_template('es/vegetines/portafolio.html', lang='es')

@app.route('/en/vegetines/portfolio')
def vegetines_portfolio_en():
    session['preferred_language'] = 'en'
    return render_template('en/vegetines/portfolio.html', lang='en')

@app.route('/es/vegetines/servicios')
def vegetines_services_es():
    session['preferred_language'] = 'es'
    return render_template('es/vegetines/servicios.html', lang='es')

@app.route('/en/vegetines/services')
def vegetines_services_en():
    session['preferred_language'] = 'en'
    return render_template('en/vegetines/services.html', lang='en')

@app.route('/dashboard')
def dashboard_redirect():
    preferred_lang = session.get('preferred_language', 'es')
    
    if 'access_token' in session:
        return redirect(f'/{preferred_lang}/dashboard')
    
    state = create_oauth_state(preferred_lang, 'dashboard')
    oauth_url = f"{DISCORD_OAUTH2_URL}?{urlencode({'client_id': CLIENT_ID, 'redirect_uri': REDIRECT_URI, 'response_type': 'code', 'scope': 'identify guilds', 'state': state})}"
    return redirect(oauth_url)

@app.route('/login')
def login():
    preferred_lang = session.get('preferred_language', 'es')
    state = create_oauth_state(preferred_lang, 'dashboard')
    oauth_url = f"{DISCORD_OAUTH2_URL}?{urlencode({'client_id': CLIENT_ID, 'redirect_uri': REDIRECT_URI, 'response_type': 'code', 'scope': 'identify guilds', 'state': state})}"
    return redirect(oauth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    
    if not code:
        return redirect('/es/')
    
    state_data = decode_oauth_state(state) if state else {'lang': 'es', 'redirect': 'dashboard'}
    preferred_lang = state_data.get('lang', 'es')
    redirect_path = state_data.get('redirect', 'dashboard')
    
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        response = requests.post(f'{DISCORD_API_BASE}/oauth2/token', data=data, headers=headers)
        
        if response.status_code == 200:
            token_data = response.json()
            session['access_token'] = token_data['access_token']
            session['refresh_token'] = token_data['refresh_token']
            session['preferred_language'] = preferred_lang
            
            if redirect_path.startswith('dashboard'):
                return redirect(f'/{preferred_lang}/dashboard')
            else:
                return redirect(f'/{preferred_lang}/{redirect_path}')
        else:
            print(f"Error en OAuth2: {response.status_code} - {response.text}")
            return redirect(f'/{preferred_lang}/')
    except Exception as e:
        print(f"Error en callback: {e}")
        return redirect(f'/{preferred_lang}/')

@app.route('/es/dashboard')
def dashboard_es():
    session['preferred_language'] = 'es'
    
    if 'access_token' not in session:
        state = create_oauth_state('es', 'dashboard')
        oauth_url = f"{DISCORD_OAUTH2_URL}?{urlencode({'client_id': CLIENT_ID, 'redirect_uri': REDIRECT_URI, 'response_type': 'code', 'scope': 'identify guilds', 'state': state})}"
        return redirect(oauth_url)
    
    if not permission_checker:
        return redirect('/es/')
    
    access_token = session['access_token']
    
    user_headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        user_response = requests.get(f'{DISCORD_API_BASE}/users/@me', headers=user_headers)
        guilds_response = requests.get(f'{DISCORD_API_BASE}/users/@me/guilds', headers=user_headers)
        
        if user_response.status_code != 200 or guilds_response.status_code != 200:
            session.clear()
            session['preferred_language'] = 'es'
            state = create_oauth_state('es', 'dashboard')
            oauth_url = f"{DISCORD_OAUTH2_URL}?{urlencode({'client_id': CLIENT_ID, 'redirect_uri': REDIRECT_URI, 'response_type': 'code', 'scope': 'identify guilds', 'state': state})}"
            return redirect(oauth_url)
        
        user_data = user_response.json()
        user_guilds = guilds_response.json()
        
        user_avatar = f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png" if user_data['avatar'] else "https://cdn.discordapp.com/embed/avatars/0.png"
        
        user = {
            'id': user_data['id'],
            'username': user_data['username'],
            'discriminator': user_data['discriminator'] if user_data['discriminator'] != '0' else '',
            'avatar': user_avatar
        }
        
        manageable_servers = permission_checker.get_all_manageable_servers(user_guilds, user_data['id'])
        
        return render_template('es/dashboard.html', user=user, servers=manageable_servers, lang='es')
        
    except Exception as e:
        print(f"Error en dashboard: {e}")
        session.clear()
        session['preferred_language'] = 'es'
        state = create_oauth_state('es', 'dashboard')
        oauth_url = f"{DISCORD_OAUTH2_URL}?{urlencode({'client_id': CLIENT_ID, 'redirect_uri': REDIRECT_URI, 'response_type': 'code', 'scope': 'identify guilds', 'state': state})}"
        return redirect(oauth_url)

@app.route('/en/dashboard')
def dashboard_en():
    session['preferred_language'] = 'en'
    
    if 'access_token' not in session:
        state = create_oauth_state('en', 'dashboard')
        oauth_url = f"{DISCORD_OAUTH2_URL}?{urlencode({'client_id': CLIENT_ID, 'redirect_uri': REDIRECT_URI, 'response_type': 'code', 'scope': 'identify guilds', 'state': state})}"
        return redirect(oauth_url)
    
    if not permission_checker:
        return redirect('/en/')
    
    access_token = session['access_token']
    
    user_headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        user_response = requests.get(f'{DISCORD_API_BASE}/users/@me', headers=user_headers)
        guilds_response = requests.get(f'{DISCORD_API_BASE}/users/@me/guilds', headers=user_headers)
        
        if user_response.status_code != 200 or guilds_response.status_code != 200:
            session.clear()
            session['preferred_language'] = 'en'
            state = create_oauth_state('en', 'dashboard')
            oauth_url = f"{DISCORD_OAUTH2_URL}?{urlencode({'client_id': CLIENT_ID, 'redirect_uri': REDIRECT_URI, 'response_type': 'code', 'scope': 'identify guilds', 'state': state})}"
            return redirect(oauth_url)
        
        user_data = user_response.json()
        user_guilds = guilds_response.json()
        
        user_avatar = f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png" if user_data['avatar'] else "https://cdn.discordapp.com/embed/avatars/0.png"
        
        user = {
            'id': user_data['id'],
            'username': user_data['username'],
            'discriminator': user_data['discriminator'] if user_data['discriminator'] != '0' else '',
            'avatar': user_avatar
        }
        
        manageable_servers = permission_checker.get_all_manageable_servers(user_guilds, user_data['id'])
        
        return render_template('en/dashboard.html', user=user, servers=manageable_servers, lang='en')
        
    except Exception as e:
        print(f"Error en dashboard: {e}")
        session.clear()
        session['preferred_language'] = 'en'
        state = create_oauth_state('en', 'dashboard')
        oauth_url = f"{DISCORD_OAUTH2_URL}?{urlencode({'client_id': CLIENT_ID, 'redirect_uri': REDIRECT_URI, 'response_type': 'code', 'scope': 'identify guilds', 'state': state})}"
        return redirect(oauth_url)

@app.route('/es/dashboard/<server_id>')
def server_management_es(server_id):
    session['preferred_language'] = 'es'
    
    if 'access_token' not in session:
        state = create_oauth_state('es', f'dashboard/{server_id}')
        oauth_url = f"{DISCORD_OAUTH2_URL}?{urlencode({'client_id': CLIENT_ID, 'redirect_uri': REDIRECT_URI, 'response_type': 'code', 'scope': 'identify guilds', 'state': state})}"
        return redirect(oauth_url)
    
    if not permission_checker or not server_manager:
        return redirect('/es/dashboard')
    
    access_token = session['access_token']
    user_headers = {'Authorization': f'Bearer {access_token}'}
    
    try:
        user_response = requests.get(f'{DISCORD_API_BASE}/users/@me', headers=user_headers)
        guilds_response = requests.get(f'{DISCORD_API_BASE}/users/@me/guilds', headers=user_headers)
        
        if user_response.status_code != 200 or guilds_response.status_code != 200:
            session.clear()
            session['preferred_language'] = 'es'
            state = create_oauth_state('es', f'dashboard/{server_id}')
            oauth_url = f"{DISCORD_OAUTH2_URL}?{urlencode({'client_id': CLIENT_ID, 'redirect_uri': REDIRECT_URI, 'response_type': 'code', 'scope': 'identify guilds', 'state': state})}"
            return redirect(oauth_url)
        
        user_data = user_response.json()
        user_guilds = guilds_response.json()
        
        manageable_servers = permission_checker.get_all_manageable_servers(user_guilds, user_data['id'])
        
        target_server = None
        for server in manageable_servers:
            if str(server['id']) == str(server_id):
                target_server = server
                break
        
        if not target_server or not target_server.get('bot_present', False):
            return redirect('/es/dashboard')
        
        server_data = server_manager.get_server_config(server_id)
        
        user_avatar = f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png" if user_data['avatar'] else "https://cdn.discordapp.com/embed/avatars/0.png"
        
        user = {
            'id': user_data['id'],
            'username': user_data['username'],
            'discriminator': user_data['discriminator'] if user_data['discriminator'] != '0' else '',
            'avatar': user_avatar
        }
        
        return render_template('es/server_management.html', 
                             user=user, 
                             server=target_server, 
                             server_data=server_data, 
                             lang='es')
        
    except Exception as e:
        print(f"Error en server management: {e}")
        return redirect('/es/dashboard')

@app.route('/en/dashboard/<server_id>')
def server_management_en(server_id):
    session['preferred_language'] = 'en'
    
    if 'access_token' not in session:
        state = create_oauth_state('en', f'dashboard/{server_id}')
        oauth_url = f"{DISCORD_OAUTH2_URL}?{urlencode({'client_id': CLIENT_ID, 'redirect_uri': REDIRECT_URI, 'response_type': 'code', 'scope': 'identify guilds', 'state': state})}"
        return redirect(oauth_url)
    
    if not permission_checker or not server_manager:
        return redirect('/en/dashboard')
    
    access_token = session['access_token']
    user_headers = {'Authorization': f'Bearer {access_token}'}
    
    try:
        user_response = requests.get(f'{DISCORD_API_BASE}/users/@me', headers=user_headers)
        guilds_response = requests.get(f'{DISCORD_API_BASE}/users/@me/guilds', headers=user_headers)
        
        if user_response.status_code != 200 or guilds_response.status_code != 200:
            session.clear()
            session['preferred_language'] = 'en'
            state = create_oauth_state('en', f'dashboard/{server_id}')
            oauth_url = f"{DISCORD_OAUTH2_URL}?{urlencode({'client_id': CLIENT_ID, 'redirect_uri': REDIRECT_URI, 'response_type': 'code', 'scope': 'identify guilds', 'state': state})}"
            return redirect(oauth_url)
        
        user_data = user_response.json()
        user_guilds = guilds_response.json()
        
        manageable_servers = permission_checker.get_all_manageable_servers(user_guilds, user_data['id'])
        
        target_server = None
        for server in manageable_servers:
            if str(server['id']) == str(server_id):
                target_server = server
                break
        
        if not target_server or not target_server.get('bot_present', False):
            return redirect('/en/dashboard')
        
        server_data = server_manager.get_server_config(server_id)
        
        user_avatar = f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png" if user_data['avatar'] else "https://cdn.discordapp.com/embed/avatars/0.png"
        
        user = {
            'id': user_data['id'],
            'username': user_data['username'],
            'discriminator': user_data['discriminator'] if user_data['discriminator'] != '0' else '',
            'avatar': user_avatar
        }
        
        return render_template('en/server_management.html', 
                             user=user, 
                             server=target_server, 
                             server_data=server_data, 
                             lang='en')
        
    except Exception as e:
        print(f"Error en server management: {e}")
        return redirect('/en/dashboard')

@app.route('/api/server/<server_id>/commands', methods=['GET', 'POST'])
def api_server_commands(server_id):
    if 'access_token' not in session or not server_manager:
        return jsonify({'error': 'No autorizado'}), 401
    
    if request.method == 'GET':
        try:
            commands_data = server_manager.get_commands_config(server_id)
            return jsonify(commands_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            success = server_manager.update_commands_config(server_id, data)
            if success:
                return jsonify({'success': True})
            else:
                return jsonify({'error': 'Error al actualizar'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/api/server/<server_id>/permissions', methods=['GET'])
def api_server_permissions(server_id):
    if 'access_token' not in session or not permissions_manager:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        permissions = permissions_manager.get_all_permissions(server_id)
        return jsonify({'permissions': permissions})
    except Exception as e:
        print(f"Error en API permissions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/server/<server_id>/permissions/<permission_key>', methods=['GET'])
def api_server_permission_details(server_id, permission_key):
    if 'access_token' not in session or not permissions_manager:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        permission_details = permissions_manager.get_permission_details(server_id, permission_key)
        if permission_details:
            return jsonify(permission_details)
        else:
            return jsonify({'error': 'Permiso no encontrado'}), 404
    except Exception as e:
        print(f"Error obteniendo detalles del permiso: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/server/<server_id>/permissions/<permission_key>/add', methods=['POST'])
def api_server_permission_add(server_id, permission_key):
    if 'access_token' not in session or not permissions_manager:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        item_id = data.get('item_id')
        item_type = data.get('item_type')
        
        if not item_id or not item_type:
            return jsonify({'error': 'Faltan datos requeridos'}), 400
        
        success, message = permissions_manager.add_permission_item(server_id, permission_key, item_id, item_type)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'error': message}), 400
    except Exception as e:
        print(f"Error añadiendo elemento al permiso: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/server/<server_id>/permissions/<permission_key>/remove', methods=['POST'])
def api_server_permission_remove(server_id, permission_key):
    if 'access_token' not in session or not permissions_manager:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        item_id = data.get('item_id')
        
        if not item_id:
            return jsonify({'error': 'Falta el ID del elemento'}), 400
        
        success, message = permissions_manager.remove_permission_item(server_id, permission_key, item_id)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'error': message}), 400
    except Exception as e:
        print(f"Error eliminando elemento del permiso: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/server/<server_id>/permissions/custom', methods=['POST'])
def api_server_permission_create_custom(server_id):
    if 'access_token' not in session or not permissions_manager:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        permission_name = data.get('permission_name')
        
        if not permission_name:
            return jsonify({'error': 'Falta el nombre del permiso'}), 400
        
        success, message = permissions_manager.create_custom_permission(server_id, permission_name)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'error': message}), 400
    except Exception as e:
        print(f"Error creando permiso personalizado: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/server/<server_id>/permissions/custom/<permission_name>', methods=['DELETE'])
def api_server_permission_delete_custom(server_id, permission_name):
    if 'access_token' not in session or not permissions_manager:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        success, message = permissions_manager.delete_custom_permission(server_id, permission_name)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'error': message}), 400
    except Exception as e:
        print(f"Error eliminando permiso personalizado: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/server/<server_id>/logs', methods=['GET'])
def api_server_logs(server_id):
    if 'access_token' not in session or not logs_manager:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        logs = logs_manager.get_all_logs(server_id)
        return jsonify({'logs': logs})
    except Exception as e:
        print(f"Error en API logs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/server/<server_id>/logs/<log_type>', methods=['GET', 'POST'])
def api_server_log(server_id, log_type):
    if 'access_token' not in session or not logs_manager:
        return jsonify({'error': 'No autorizado'}), 401
    
    if request.method == 'GET':
        try:
            log_data = logs_manager.get_log_config(server_id, log_type)
            if log_data:
                return jsonify(log_data)
            else:
                return jsonify({'error': 'Log no encontrado'}), 404
        except Exception as e:
            print(f"Error obteniendo log: {e}")
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            config = request.get_json()
            
            if not config:
                return jsonify({'error': 'Configuración inválida'}), 400
            
            success = logs_manager.save_log_config(server_id, log_type, config)
            
            if success:
                return jsonify({'success': True})
            else:
                return jsonify({'error': 'Error al guardar configuración'}), 500
        except Exception as e:
            print(f"Error guardando log: {e}")
            return jsonify({'error': str(e)}), 500

@app.route('/api/server/<server_id>/logs/preview', methods=['POST'])
def api_logs_preview(server_id):
    if 'access_token' not in session or not logs_manager:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        log_type = data.get('log_type')
        message_config = data.get('message_config')
        
        if not log_type or not message_config:
            return jsonify({'error': 'Datos incompletos'}), 400
        
        preview = logs_manager.generate_preview_data(log_type, message_config, server_id)
        if preview:
            return jsonify(preview)
        else:
            return jsonify({'error': 'Error generando preview'}), 500
    except Exception as e:
        print(f"Error generando preview: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/server/<server_id>/tickets', methods=['GET'])
def api_server_tickets(server_id):
    if 'access_token' not in session or not tickets_manager:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        tickets = tickets_manager.get_all_tickets(server_id)
        return jsonify({'tickets': tickets})
    except Exception as e:
        print(f"Error en API tickets: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/server/<server_id>/tickets/<channel_id>', methods=['GET', 'POST', 'DELETE'])
def api_server_ticket(server_id, channel_id):
    if 'access_token' not in session or not tickets_manager:
        return jsonify({'error': 'No autorizado'}), 401
    
    if request.method == 'GET':
        try:
            ticket_data = tickets_manager.get_ticket_config(server_id, channel_id)
            if ticket_data:
                return jsonify(ticket_data)
            else:
                return jsonify({'error': 'Ticket no encontrado'}), 404
        except Exception as e:
            print(f"Error obteniendo ticket: {e}")
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            config = request.get_json()
            
            if not config:
                return jsonify({'error': 'Configuración inválida'}), 400
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                success = loop.run_until_complete(tickets_manager.save_ticket_config(server_id, channel_id, config))
            finally:
                loop.close()
            
            if success:
                return jsonify({'success': True})
            else:
                return jsonify({'error': 'Error al guardar configuración'}), 500
        except Exception as e:
            print(f"Error guardando ticket: {e}")
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                success = loop.run_until_complete(tickets_manager.delete_ticket(server_id, channel_id))
            finally:
                loop.close()
            
            if success:
                return jsonify({'success': True})
            else:
                return jsonify({'error': 'Error al eliminar ticket'}), 500
        except Exception as e:
            print(f"Error eliminando ticket: {e}")
            return jsonify({'error': str(e)}), 500

@app.route('/api/server/<server_id>/channels', methods=['GET'])
def api_server_channels(server_id):
    if 'access_token' not in session or not logs_manager:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        channels = logs_manager.get_guild_channels(server_id)
        return jsonify({'channels': channels})
    except Exception as e:
        print(f"Error obteniendo canales: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/server/<server_id>/roles', methods=['GET'])
def api_server_roles(server_id):
    if 'access_token' not in session or not permissions_manager:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        roles = permissions_manager.get_guild_roles(server_id)
        return jsonify({'roles': roles})
    except Exception as e:
        print(f"Error obteniendo roles: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/server/<server_id>/tickets/preview', methods=['POST'])
def api_tickets_preview(server_id):
    if 'access_token' not in session or not tickets_manager:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        config = request.get_json()
        
        if not config:
            return jsonify({'error': 'Configuración inválida'}), 400
        
        preview = tickets_manager.generate_preview_data(config, server_id)
        if preview:
            return jsonify(preview)
        else:
            return jsonify({'error': 'Error generando preview'}), 500
    except Exception as e:
        print(f"Error generando preview: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
def logout():
    preferred_lang = session.get('preferred_language', 'es')
    session.clear()
    return redirect(f'/{preferred_lang}/')

@app.route('/invite')
def invite():
    discord_invite_link = "https://discord.com/oauth2/authorize?client_id=784774864766500864&scope=bot&permissions=8"
    return redirect(discord_invite_link)

@app.route('/sitemap.xml')
def sitemap():
    sitemap_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
    <url>
        <loc>https://laslylusky.es/</loc>
        <xhtml:link rel="alternate" hreflang="es" href="https://laslylusky.es/es/" />
        <xhtml:link rel="alternate" hreflang="en" href="https://laslylusky.es/en/" />
        <xhtml:link rel="alternate" hreflang="x-default" href="https://laslylusky.es/es/" />
        <lastmod>2025-05-31</lastmod>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://laslylusky.es/es/</loc>
        <xhtml:link rel="alternate" hreflang="es" href="https://laslylusky.es/es/" />
        <xhtml:link rel="alternate" hreflang="en" href="https://laslylusky.es/en/" />
        <xhtml:link rel="alternate" hreflang="x-default" href="https://laslylusky.es/es/" />
        <lastmod>2025-05-31</lastmod>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://laslylusky.es/en/</loc>
        <xhtml:link rel="alternate" hreflang="es" href="https://laslylusky.es/es/" />
        <xhtml:link rel="alternate" hreflang="en" href="https://laslylusky.es/en/" />
        <xhtml:link rel="alternate" hreflang="x-default" href="https://laslylusky.es/es/" />
        <lastmod>2025-05-31</lastmod>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://laslylusky.es/es/documentacion/help</loc>
        <xhtml:link rel="alternate" hreflang="es" href="https://laslylusky.es/es/documentacion/help" />
        <xhtml:link rel="alternate" hreflang="en" href="https://laslylusky.es/en/documentation/help" />
        <lastmod>2025-05-31</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.9</priority>
    </url>
    <url>
        <loc>https://laslylusky.es/es/documentacion/configuracion</loc>
        <xhtml:link rel="alternate" hreflang="es" href="https://laslylusky.es/es/documentacion/configuracion" />
        <xhtml:link rel="alternate" hreflang="en" href="https://laslylusky.es/en/documentation/configuration" />
        <lastmod>2025-05-31</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://laslylusky.es/es/documentacion/tickets</loc>
        <xhtml:link rel="alternate" hreflang="es" href="https://laslylusky.es/es/documentacion/tickets" />
        <xhtml:link rel="alternate" hreflang="en" href="https://laslylusky.es/en/documentation/tickets" />
        <lastmod>2025-05-31</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://laslylusky.es/en/documentation/help</loc>
        <xhtml:link rel="alternate" hreflang="es" href="https://laslylusky.es/es/documentacion/help" />
        <xhtml:link rel="alternate" hreflang="en" href="https://laslylusky.es/en/documentation/help" />
        <lastmod>2025-05-31</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.9</priority>
    </url>
    <url>
        <loc>https://laslylusky.es/en/documentation/configuration</loc>
        <xhtml:link rel="alternate" hreflang="es" href="https://laslylusky.es/es/documentacion/configuracion" />
        <xhtml:link rel="alternate" hreflang="en" href="https://laslylusky.es/en/documentation/configuration" />
        <lastmod>2025-05-31</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://laslylusky.es/en/documentation/tickets</loc>
        <xhtml:link rel="alternate" hreflang="es" href="https://laslylusky.es/es/documentacion/tickets" />
        <xhtml:link rel="alternate" hreflang="en" href="https://laslylusky.es/en/documentation/tickets" />
        <lastmod>2025-05-31</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://laslylusky.es/es/vegetines</loc>
        <xhtml:link rel="alternate" hreflang="es" href="https://laslylusky.es/es/vegetines" />
        <xhtml:link rel="alternate" hreflang="en" href="https://laslylusky.es/en/vegetines" />
        <lastmod>2025-05-31</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
    <url>
        <loc>https://laslylusky.es/es/vegetines/portafolio</loc>
        <xhtml:link rel="alternate" hreflang="es" href="https://laslylusky.es/es/vegetines/portafolio" />
        <xhtml:link rel="alternate" hreflang="en" href="https://laslylusky.es/en/vegetines/portfolio" />
        <lastmod>2025-05-31</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.6</priority>
    </url>
    <url>
        <loc>https://laslylusky.es/es/vegetines/servicios</loc>
        <xhtml:link rel="alternate" hreflang="es" href="https://laslylusky.es/es/vegetines/servicios" />
        <xhtml:link rel="alternate" hreflang="en" href="https://laslylusky.es/en/vegetines/services" />
        <lastmod>2025-05-31</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.6</priority>
    </url>
    <url>
        <loc>https://laslylusky.es/en/vegetines</loc>
        <xhtml:link rel="alternate" hreflang="es" href="https://laslylusky.es/es/vegetines" />
        <xhtml:link rel="alternate" hreflang="en" href="https://laslylusky.es/en/vegetines" />
        <lastmod>2025-05-31</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
    <url>
        <loc>https://laslylusky.es/en/vegetines/portfolio</loc>
        <xhtml:link rel="alternate" hreflang="es" href="https://laslylusky.es/es/vegetines/portafolio" />
        <xhtml:link rel="alternate" hreflang="en" href="https://laslylusky.es/en/vegetines/portfolio" />
        <lastmod>2025-05-31</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.6</priority>
    </url>
    <url>
        <loc>https://laslylusky.es/en/vegetines/services</loc>
        <xhtml:link rel="alternate" hreflang="es" href="https://laslylusky.es/es/vegetines/servicios" />
        <xhtml:link rel="alternate" hreflang="en" href="https://laslylusky.es/en/vegetines/services" />
        <lastmod>2025-05-31</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.6</priority>
    </url>
    <url>
        <loc>https://laslylusky.es/es/privacidad</loc>
        <xhtml:link rel="alternate" hreflang="es" href="https://laslylusky.es/es/privacidad" />
        <xhtml:link rel="alternate" hreflang="en" href="https://laslylusky.es/en/privacy" />
        <lastmod>2025-05-26</lastmod>
        <changefreq>yearly</changefreq>
        <priority>0.5</priority>
    </url>
    <url>
        <loc>https://laslylusky.es/es/tos</loc>
        <xhtml:link rel="alternate" hreflang="es" href="https://laslylusky.es/es/tos" />
        <xhtml:link rel="alternate" hreflang="en" href="https://laslylusky.es/en/tos" />
        <lastmod>2025-05-26</lastmod>
        <changefreq>yearly</changefreq>
        <priority>0.5</priority>
    </url>
    <url>
        <loc>https://laslylusky.es/en/privacy</loc>
        <xhtml:link rel="alternate" hreflang="es" href="https://laslylusky.es/es/privacidad" />
        <xhtml:link rel="alternate" hreflang="en" href="https://laslylusky.es/en/privacy" />
        <lastmod>2025-05-26</lastmod>
        <changefreq>yearly</changefreq>
        <priority>0.5</priority>
    </url>
    <url>
        <loc>https://laslylusky.es/en/tos</loc>
        <xhtml:link rel="alternate" hreflang="es" href="https://laslylusky.es/es/tos" />
        <xhtml:link rel="alternate" hreflang="en" href="https://laslylusky.es/en/tos" />
        <lastmod>2025-05-26</lastmod>
        <changefreq>yearly</changefreq>
        <priority>0.5</priority>
    </url>
    <url>
        <loc>https://laslylusky.es/invite</loc>
        <lastmod>2025-05-31</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.9</priority>
    </url>
</urlset>'''
    return Response(sitemap_xml, mimetype='application/xml')

@app.route('/robots.txt')
def robots():
    robots_txt = '''User-agent: *
Allow: /

Sitemap: https://laslylusky.es/sitemap.xml

Crawl-delay: 1

User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: Slurp
Allow: /

User-agent: DuckDuckBot
Allow: /

User-agent: Baiduspider
Allow: /

User-agent: YandexBot
Allow: /

User-agent: AhrefsBot
Disallow: /

User-agent: MJ12bot
Disallow: /

User-agent: DotBot
Disallow: /

User-agent: SemrushBot
Disallow: /

User-agent: facebookexternalhit
Allow: /

User-agent: Twitterbot
Allow: /

User-agent: LinkedInBot
Allow: /

User-agent: WhatsApp
Allow: /

User-agent: DiscordBot
Allow: /

User-agent: TelegramBot
Allow: /'''
    return Response(robots_txt, mimetype='text/plain')

def run():
    app.run(host='0.0.0.0', port=8080, debug=False)

def keep_alive():
    server = Thread(target=run, daemon=True)
    server.start()
    return server