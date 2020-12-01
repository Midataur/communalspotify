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

REDIR_URI = os.environ.get('REDIRECT_URI')
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
REDIS_URL = os.environ.get('REDIS_URL')

#this one is just for heroku
def create_app():
    global app
    return app

def redis_instance():
    global REDIS_URL
    #this wrapper exists for future proofing
    return redis.Redis(host=REDIS_URL)

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
    global REDIR_URI, CLIENT_ID, CLIENT_SECRET
    params = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': authCode,
        'redirect_uri': REDIR_URI
    }

    url = 'https://accounts.spotify.com/api/token'

    response = requests.post(url, data=params).json()

    print(response)

    print('Expires in',response['expires_in'])

    return response['access_token'],response['refresh_token']

def play_state(code):
    r = redis_instance()
    token = r.hget(code,'access_token').decode('utf-8')

    headers = {'Authorization': f'Bearer {token}'}
    url = 'https://api.spotify.com/v1/me/player'

    resp = requests.get(url, headers=headers)
    print(resp.content)
    return resp.json()

## API ROUTES

#this is a forwarder to the Spotify api so we don't give the authtokens to every client
@app.route('/api/search')
def spotify_search():
    params = {
        'type': 'track',
        'q': request.args['q']
    }
    
    code = request.args['roomcode']
    r = redis_instance()
    token = r.hget(code,'access_token').decode('utf-8')

    headers = {'Authorization': f'Bearer {token}'}
    url = 'https://api.spotify.com/v1/search'

    return requests.get(url, headers=headers, params=params).json()

@app.route('/api/getPlayState')
def get_play_state():
    return play_state(request.args['roomcode'])

### SOCKETS ###

@socketio.on('room_connect')
def connect(code):
    join_room(code)
    print('New connection from',code)

@socketio.on('playpause')
def playpause(code):
    status = 'pause' if play_state(code)['is_playing'] else 'play'
    print(status)
    
    r = redis_instance()
    token = r.hget(str(code),'access_token').decode('utf-8')

    headers = {'Authorization': f'Bearer {token}'}
    url = f'https://api.spotify.com/v1/me/player/{status}'
    requests.put(url,headers=headers)

@socketio.on('skip')
def skip(code):
    r = redis_instance()
    token = r.hget(str(code),'access_token').decode('utf-8')

    headers = {'Authorization': f'Bearer {token}'}
    url = f'https://api.spotify.com/v1/me/player/next'
    requests.post(url,headers=headers)

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
    global CLIENT_ID, REDIR_URI
    if 'roomCode' in request.cookies and 'authCode' in request.cookies:
        try:
            print('Trying easy log')
            r = redis_instance()
            roomcode = request.cookies['roomCode']
            authCode = r.hget(roomcode,'access_token').decode('utf-8')
            if authCode == request.cookies['authCode']:
                return '<script>window.location = "/room"</script>'
        except AttributeError:
            pass
    return render_template('create.html',client_id=CLIENT_ID,redir_uri=REDIR_URI)

@app.route('/create/actual')
def actual_create():
    if 'code' in request.args:
        tokens = get_api_token(request.args['code'])
        roomcode = generate_roomcode()
        create_room(roomcode,tokens)

        r = redis_instance()
        authCode = r.hget(roomcode,'access_token')

        resp = make_response(f"""<script>window.location = '/room';</script>""")
        resp.set_cookie('roomCode',roomcode)
        resp.set_cookie('authCode',authCode)

        return resp
    return "You need to login for the webapp to work"

@app.route('/join', methods=['GET','POST'])
def join():
    if request.method == 'GET':
        return render_template('join.html')
    else:
        r = redis_instance()
        roomcode = request.form['code']
        if r.exists(roomcode):
            resp = make_response(f"""<script>window.location = '/room';</script>""")
            resp.set_cookie('roomCode',roomcode)
            return resp
        else:
            return 'Room does not exist'

@app.route('/room')
def room():
    roomcode = request.cookies['roomCode']
    return render_template('room.html',roomcode=roomcode)

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