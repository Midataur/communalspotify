from apscheduler.schedulers.background import BackgroundScheduler
import time
import json
import random
import redis
import requests
import os

#enviro vars
REDIR_URI = os.environ.get('REDIRECT_URI')
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
REDIS_URL = os.environ.get('REDIS_URL')

#constants
ALLOWED_IDLE_TIME = 60*60*3 #measured in seconds

scheduler = BackgroundScheduler()
scheduler.start()

def redis_instance():
    global REDIS_URL
    if REDIS_URL:
        return redis.from_url(REDIS_URL)
    else:
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

def create_room(roomcode,auth_result):
    global scheduler

    r = redis_instance()
    data = {
        'access_token': auth_result[0],
        'refresh_token': auth_result[1],
    }

    r.delete(roomcode)
    r.hset(roomcode,mapping=data)

    renewer = scheduler.add_job(
        func=room_checkup, 
        trigger="interval", 
        seconds=auth_result[2], 
        args=(roomcode,)
    )

    #remember the id of this job so we can delete it later
    r.hset(roomcode, 'job_id', renewer.id)

### SCHEDULED WORKERS ###

def room_checkup(roomcode):
    global ALLOWED_IDLE_TIME, scheduler
    r = redis_instance()

    #first, check if we should kill the room
    queue_key = roomcode+'q'
    idle_time = r.object("idletime", queue_key)

    # idle time is in seconds
    if not idle_time or idle_time > ALLOWED_IDLE_TIME:
        job_id = r.hget(roomcode, 'job_id')

        r.delete(roomcode)
        r.delete(queue_key)

        #seppuku
        print('goodbye room',roomcode)
        scheduler.remove_job('job_id')

    else:
        renew_token(roomcode)

    #refresh active users
    r.delete(roomcode+'p')
    print('room checkup done on', roomcode)

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

    return response['access_token'],response['refresh_token'],response['expires_in']

def renew_token(roomcode):
    global CLIENT_ID, CLIENT_SECRET

    r = redis_instance()
    refresh_token = r.hget(roomcode,'access_token').decode('utf-8')

    params = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }

    url = 'https://accounts.spotify.com/api/token'

    headers = {'Authorization': f'Basic {CLIENT_ID}:{CLIENT_SECRET}'}
    response = requests.post(url, data=params, headers=headers).json()

    r.hset(roomcode,'access_token', response['access_token'])

def play_state(code):
    r = redis_instance()
    
    token = r.hget(code,'access_token').decode('utf-8')

    headers = {'Authorization': f'Bearer {token}'}
    url = 'https://api.spotify.com/v1/me/player'

    resp = requests.get(url, headers=headers)

    return resp.json()

def queue_song(code, uri):
    params = {
        'uri': uri
    }
    
    r = redis_instance()
    token = r.hget(code,'access_token').decode('utf-8')

    headers = {'Authorization': f'Bearer {token}'}
    url = 'https://api.spotify.com/v1/me/player/queue'

    resp = requests.post(url, headers=headers, params=params)

    return str(resp.status_code)

def skip_song(code):
    r = redis_instance()
    token = r.hget(str(code),'access_token').decode('utf-8')

    headers = {'Authorization': f'Bearer {token}'}
    url = f'https://api.spotify.com/v1/me/player/next'
    requests.post(url,headers=headers)

def get_tracks_info(uris, roomcode):
    #chop off the resource type to get the spotify ids
    spot_ids = [x[14:] for x in uris]

    r = redis_instance()
    token = r.hget(str(roomcode),'access_token').decode('utf-8')

    params = {
        'ids': ','.join(spot_ids)
    }

    headers = {'Authorization': f'Bearer {token}'}
    url = f'https://api.spotify.com/v1/tracks'

    resp = requests.get(url,params=params, headers=headers).json()
    return resp['tracks']

def proccess_tracks(tracks):

    new_tracks = []

    for track, score in tracks:
        data = {
            'score': score,
            'image': track['album']['images'][0]['url'],
            'uri': track['uri'],
            'name': track['name'],
            'artist': track['artists'][0]['name']
        }
        new_tracks.append(data)
    
    return new_tracks