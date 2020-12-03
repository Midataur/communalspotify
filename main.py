from flask import Flask, request, url_for, render_template, make_response, Markup
from flask_socketio import SocketIO, join_room, leave_room
from apscheduler.schedulers.background import BackgroundScheduler
from non_routes import *
import time
import json
import random
import redis
import requests
import os

app = Flask(__name__)
app.config['DEBUG'] = True if __name__ == '__main__' else False
socketio = SocketIO(app)

scheduler = BackgroundScheduler()
scheduler.start()

#this one is just for heroku
def create_app():
    global app
    return app

#all these functions should reallly be in a seperate file 
#eh, i'll do it later -mida

## API ROUTES

#this is a forwarder to the Spotify api so we don't give the authtokens to every client
@app.route('/api/search')
def spotify_search():
    params = {
        'type': 'track',
        'q': request.args['q'],
        'market': 'from_token',
        'limit': request.args['limit']
    }
    
    code = request.args['roomcode']
    r = redis_instance()
    token = r.hget(code,'access_token').decode('utf-8')

    headers = {'Authorization': f'Bearer {token}'}
    url = 'https://api.spotify.com/v1/search'

    return requests.get(url, headers=headers, params=params).json()

@app.route('/api/getPlayState')
def get_play_state():
    roomcode = request.args['roomcode']
    uid = request.args['uid']

    #we use this as a convenient way to track active users
    r = redis_instance()
    r.sadd(roomcode+'p', uid)

    return play_state(roomcode)

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

@socketio.on('vote-skip')
def vote_skip(code, id):
    r = redis_instance()
    pass

@socketio.on('vote-song')
def vote_song(code, uri, sign):
    #sign is +1 for upvote and -1 for downvote
    r = redis_instance()
    r.zincrby(str(code)+'q', sign, uri)

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

    #if user already made a room log them into that one
    if 'roomCode' in request.cookies and 'authCode' in request.cookies:
        try:
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
        auth_result = get_api_token(request.args['code'])
        roomcode = generate_roomcode()
        create_room(roomcode,auth_result)

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

    admin = False
    if 'authCode' in request.cookies:
        r = redis_instance()
        roomcode = request.cookies['roomCode']
        authCode = r.hget(roomcode,'access_token').decode('utf-8')
        if authCode == request.cookies['authCode']:
            admin = True

    resp = make_response(render_template('room.html',roomcode=roomcode, admin=admin))

    if 'id' not in request.cookies:
        unique_id = hex(random.randint(10**10,10**11))
        resp.set_cookie('id',unique_id)

    return resp

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
        0/0
    socketio.run(create_app(),host='0.0.0.0')