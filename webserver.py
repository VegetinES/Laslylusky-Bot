from flask import Flask, render_template, redirect
from threading import Thread
import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask('', template_folder='web/templates', static_folder='web/static')

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/privacidad')
def privacy():
    return render_template('privacidad.html')

@app.route('/tos')
def terms():
    return render_template('tos.html')

@app.route('/documentacion/help')
def doc_help():
    return render_template('documentacion/help.html')

@app.route('/documentacion/configuracion')
def doc_config():
    return render_template('documentacion/configuracion.html')

@app.route('/documentacion/tickets')
def tickets_documentation():
    return render_template('documentacion/tickets.html')

@app.route('/invite')
def invite():
    discord_invite_link = "https://discord.com/oauth2/authorize?client_id=784774864766500864&scope=bot&permissions=8"
    return redirect(discord_invite_link)

def run():
    app.run(host='0.0.0.0', port=8080, debug=False)

def keep_alive():
    server = Thread(target=run, daemon=True)
    server.start()
    return server