import pprint

import spotipy
from spotipy import util
from spotipy.oauth2 import SpotifyClientCredentials

client_credentials_manager = SpotifyClientCredentials(client_id='',
                                                      client_secret='')

sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_song(query):
    result = sp.search(query)
    if result["tracks"]["items"]:
        uri = str(result['tracks']['items'][0]['uri'])
        id = str(result['tracks']['items'][0]['id'])
        return (uri, id)
    else:
        return None


