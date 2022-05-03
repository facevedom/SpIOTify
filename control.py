import paho.mqtt.client as mqtt

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

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))



def on_connect(client, userdata, flags, rc):
    print('Connected to MQTT!')
    client.subscribe(mqtt_topic)
    
def on_message(client, userdata, msg):
    action = str(msg.payload.decode())
    execute(action)

def execute(action):
    if action == 'toggle':
        is_playing = sp.current_user_playing_track()['is_playing']
        if is_playing:
            print('> Pausing')
            sp.pause_playback()
        else:
            print('> Playing')
            sp.start_playback()
    
    elif action == 'next':
        print('> Next song')
        sp.next_track()

    elif action == 'previous':
        print('> Previous song')
        sp.previous_track()

    elif action == 'save':
        song = sp.current_user_playing_track()
        print('> Added ' + song['item']['name'] + ' to saved tracks 💚')
        sp.current_user_saved_tracks_add(tracks=[song['item']['id']])

client.on_connect = on_connect
client.on_message = on_message

client.connect('broker.hivemq.com', 1883)

client.loop_forever()
client.disconnect()
