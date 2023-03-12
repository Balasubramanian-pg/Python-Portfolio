import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import csv

# Set up the Spotipy client
client_credentials_manager = SpotifyClientCredentials(client_id='Your Client ID', client_secret='Your client secret')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Get the artist's Spotify ID
artist_name = 'Artist_name_of_your_choice'
result = sp.search(artist_name, type='artist')
artist = result['artists']['items'][0]
artist_id = artist['id']

# Get all the albums of the artist
albums = []
results = sp.artist_albums(artist_id, album_type='album')
albums.extend(results['items'])
while results['next']:
    results = sp.next(results)
    albums.extend(results['items'])

# Write the track information to a CSV file
with open('Spotify_artist_data.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Track Name', 'Album Name', 'Album Release Date', 'Track Duration', 'Track Popularity', 'Track Streams'])
    
    # Loop through each album and get the track information
    for album in albums:
        album_name = album['name']
        album_release_date = album['release_date']
        tracks = sp.album_tracks(album['id'])
        for track in tracks['items']:
            track_name = track['name']
            track_duration = track['duration_ms']
            
            # Write the track information to the CSV file
            writer.writerow([track_name, album_name, album_release_date, track_duration])