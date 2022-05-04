from requests.exceptions import ReadTimeout

import time

import spotipy
from spotipy.oauth2 import SpotifyOAuth

import paho.mqtt.publish as paho

MQTT_BROKER = "broker.hivemq.com"
MQTT_NOW_PLAYING_TOPIC = "spiotify/now_playing"

scope = "user-library-read,\
        user-modify-playback-state,\
        user-read-playback-state,\
        user-read-currently-playing,\
        user-read-recently-played,\
        user-read-playback-position,\
        user-library-modify,\
        user-library-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope), requests_timeout=10, retries=10)

def publish(message):
    paho.single(MQTT_NOW_PLAYING_TOPIC, message, qos=1, hostname=MQTT_BROKER)


last_played = {'item': {'id': ''}}

while True:
    current_track = sp.current_user_playing_track()
    if current_track is None:
        continue

    try:
        if last_played['item']['id'] != current_track['item']['id']:
            current_track['saved'] = sp.current_user_saved_tracks_contains(tracks=[current_track['item']['id']])
            print("New song playing: " + current_track['item']['name'])
            
            publish(current_track['item']['name'])
            last_played = current_track
    except:
        print('Something went wrong while fetching song')

    time.sleep(1)
