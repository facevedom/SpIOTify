from set_tokens import *

import paho.mqtt.client as mqtt
import paho.mqtt.publish as paho

import spotipy
from spotipy.oauth2 import SpotifyOAuth

mqtt_topic = "spiotify/control"

client = mqtt.Client()


scope = "user-library-read,\
        user-modify-playback-state,\
        user-read-playback-state,\
        user-read-currently-playing,\
        user-read-recently-played,\
        user-read-playback-position,\
        user-library-modify,\
        user-library-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(cache_path='/home/pi/Code/SpIOTify/.cache',scope=scope, client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET,redirect_uri=SPOTIPY_REDIRECT_URI), requests_timeout=10, retries=10)



def on_connect(client, userdata, flags, rc):
    print('Connected to MQTT!')
    client.subscribe(mqtt_topic)
    
def on_message(client, userdata, msg):
    action = str(msg.payload.decode())
    execute(action)

def execute(action):
    if action == 'toggle':
        try:
            is_playing = sp.current_user_playing_track()['is_playing']
            if is_playing:
                print('> Pausing')
                sp.pause_playback()
            else:
                print('> Playing')
                sp.start_playback()
        except:
            print('No active device')
    
    elif action == 'next':
        print('> Next song')
        sp.next_track()

    elif action == 'previous':
        print('> Previous song')
        sp.previous_track()

    elif action == 'shuffle':
        shuffle = bool(sp.current_playback()['shuffle_state'])
        if shuffle:
            print('> Shuffle off')
        else:
            print('> Shuffle on')
        sp.shuffle(not shuffle)

    elif action == 'save':
        song = sp.current_user_playing_track()
        print('> Added ' + song['item']['name'] + ' to saved tracks 💚')
        sp.current_user_saved_tracks_add(tracks=[song['item']['id']])

    elif action == 'initialize':
        # repeated but necessary so the display doesn't start empty
        # TODO find a better way
        current_track = sp.current_user_playing_track()
        if current_track is not None:
            paho.single("spiotify/now_playing", current_track['item']['name'], qos=1, hostname="broker.hivemq.com")

client.on_connect = on_connect
client.on_message = on_message

client.connect('broker.hivemq.com', 1883)

client.loop_forever()
client.disconnect()
