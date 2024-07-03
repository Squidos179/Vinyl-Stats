import sounddevice as sd
from scipy.io.wavfile import write
import asyncio
from shazamio import Shazam

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from time import sleep

from IDs import *

sp_oauth = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE)  

sp = spotipy.Spotify(auth_manager=sp_oauth)

devices = sp.devices()
device_id = devices['devices'][0]['id'] if devices['devices'] else None

freq = 44100

duration = 5  # seconds

print(sp.current_playback())

while True:

    current_song = ""
    artist = ""

    async def main():
        shazam = Shazam()
        song = await shazam.recognize("./currentSong.wav")
        global current_song 
        current_song = song['track']['title']
        global artist
        artist = song['track']['subtitle']

    found = False

    while not found:

        try:
            print("Listenning the song")

            recording = sd.rec(int(duration * 44100), samplerate=freq, channels=2, dtype='int16')

            sd.wait()

            write("currentSong.wav", freq, recording)

            asyncio.run(main())
        except:
            print("Song not found, trying again")
            continue
        finally:
            if current_song != "":
                found = True
        
    print(f"Song found by : {current_song}")

    results = sp.search(q=current_song + artist, limit=1, type='track')

    print(f"Song found by Spotify : {results['tracks']['items'][0]['name']}")

    if results['tracks']['items']:
        track_id = results['tracks']['items'][0]['id']
        print(f"Track ID: {track_id}")
    else:
        print("No tracks found.")

    if device_id:
        sp.start_playback(device_id=device_id, uris=['spotify:track:' + track_id])
    else:
        print("No device found")

    stop = False

    while not stop:
        sleep(5)
        print(sp.current_playback()['is_playing'])
        if sp.current_playback():
            if sp.current_playback()['is_playing'] == False:
                stop = True