import requests
from bs4 import BeautifulSoup
from spotipy import SpotifyOAuth, Spotify
import spotipy.oauth2
import os
from pprint import pprint


CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET')
REDIRECT_URI = os.environ.get('SPOTIPY_REDIRECT_URI')
OAUTH_AUTHORIZE_URL = 'https://accounts.spotify.com/authorize'
OAUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SCOPE = 'playlist-modify-private'

# Scraping Billboard 100
date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
response = requests.get('https://www.billboard.com/charts/hot-100/' + date)
billboard_html = response.text
soup = BeautifulSoup(billboard_html, 'html.parser')
# Adding song name to a list
song_name_tag = soup.select(selector='h3.a-no-trucate')
song_name_list = [name.getText().strip() for name in song_name_tag]
# Adding song artists to a list
song_artist_tag = soup.select(selector='span.a-no-trucate')
song_artist_list = [artist.getText().strip() for artist in song_artist_tag]

# Spotify Authentication
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_path="token.txt"
    )
)
user_id = sp.current_user()['id']

# Searching Spotify for songs by title and artists
new_playlist_songs_uri = []
skipped_songs = []
for i in range(len(song_name_list) - 1):
    search_query = sp.search(q=f"artist:{song_artist_list[i]} track:{song_name_list[i]}", type='track')
    try:
        track = search_query['tracks']['items'][0]['uri']
        new_playlist_songs_uri.append(track)

    except IndexError:
        skipped_songs.append(song_name_list[i])
        print(f"{song_name_list[i]} doesn't exist in spotify. Skipped")

# Creating playlist
new_playlist = sp.user_playlist_create(user=user_id, name=f'{date} Billboard 100',
                                       public=False, description=f"Billboard hits {date}")
playlist_id = new_playlist['id']

# Adding song into the new playlist
sp.playlist_add_items(playlist_id=playlist_id, items=new_playlist_songs_uri)





