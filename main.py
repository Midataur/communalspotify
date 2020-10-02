from flask import Flask, request, url_for, render_template, make_response, Markup
from flask_socketio import SocketIO, join_room, leave_room
from collections import defaultdict
import xml.sax.saxutils as saxutils
import hashlib
import json
import random
import redis
import requests
import os

app = Flask(__name__)
app.config['DEBUG'] = True if __name__ == '__main__' else False
socketio = SocketIO(app)

#this one is just for heroku
def create_app():
    global app
    return app

def redis_instance():
    #this wrapper exists for future proofing
    return redis.Redis()

def generate_roomcode():
    r = redis_instance()
    lower = 10**5
    upper = 10**6
    while True:
        code = str(random.randint(lower,upper))
        if not r.exists(code):
            r.set(code,'taken',ex=20)
            return code
        upper *= 10

def create_room(roomcode,tokens):
    r = redis_instance()
    data = {
        'access_token': tokens[0],
        'refresh_token': tokens[1]
    }
    r.delete(roomcode)
    r.hset(roomcode,mapping=data)

### SPOTIFY ###

def get_api_token(authCode):
    params = {
        'client_id': 'cb6e434f986247b7be00bba2ec03e9c0',
        'client_secret': 'c97a16c6d67f42bd836dbb67630877ed',
        'grant_type': 'authorization_code',
        'code': authCode,
        'redirect_uri': 'http://localhost:5000/create/actual'
    }

    url = 'https://accounts.spotify.com/api/token'

    response = requests.post(url, data=params).json()

    print('Expires in',response['expires_in'])

    return response['access_token'],response['refresh_token']

def play_state(code):
    r = redis_instance()
    token = r.hget(str(code),'access_token').decode('utf-8')

    headers = {'Authorization': f'Bearer {token}'}
    url = 'https://api.spotify.com/v1/me/player'

    resp = requests.get(url, headers=headers)
    return resp.json()

### SOCKETS ###

@socketio.on('room_connect')
def connect(code):
    join_room(code)
    print('New connection from',code)

@socketio.on('playpause')
def playpause(code):
    status = 'pause' if play_state(code)['is_playing'] else 'play'
    
    r = redis_instance()
    token = r.hget(str(code),'access_token').decode('utf-8')

    headers = {'Authorization': f'Bearer {token}'}
    url = f'https://api.spotify.com/v1/me/player/{status}'
    requests.put(url,headers=headers)

### ROUTES ###

@app.route('/')
def index():
    return render_template('index.html')

# i should prolly figure out a way to hide this route when published.
@app.route('/debug')
def debug_view():
    return render_template('debug.html')


@app.route('/create')
def create_user_facing():
    return render_template('create.html',client_id='cb6e434f986247b7be00bba2ec03e9c0')

@app.route('/create/actual')
def actual_create():
    if 'code' in request.args:
        tokens = get_api_token(request.args['code'])
        roomcode = generate_roomcode()
        create_room(roomcode,tokens)
        secret = (str(roomcode)+tokens[1]).encode('utf-8')
        secret = hashlib.sha256(secret).hexdigest()
        resp = make_response(f"""<script>window.location = '/room';</script>""")
        resp.set_cookie('roomCode',roomcode)
        resp.set_cookie('secret',secret)
        return resp
    return "You need to login for the webapp to work"

@app.route('/join', methods=['GET','POST'])
def join():
    if request.method == 'GET':
        return render_template('join.html')
    else:
        r = redis_instance()
        roomcode = request.form['code']
        if r.exists(str(roomcode)):
            resp = make_response(f"""<script>window.location = '/room';</script>""")
            resp.set_cookie('roomCode',roomcode)
            return resp
        else:
            return 'Room does not exist'

@app.route('/room')
def room():
    roomcode = request.cookies['roomCode']
    return render_template('room.html',roomcode="32039")

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

print(app.url_map)

### COMPONENTS ###

@app.context_processor
def component_processor():
    
    def component_import(*args):
        output_str = ""
        for i in args:
            f = open(f"./components/{i}.js", "r")
            f_str = f.read()
            output_str += f"{f_str}\n"
        return Markup(output_str)
     
    return dict(component_import=component_import)


if __name__ == '__main__':
    @app.route('/debug')
    def debug():
        global classrooms
        0/0
    socketio.run(create_app(),host='0.0.0.0')