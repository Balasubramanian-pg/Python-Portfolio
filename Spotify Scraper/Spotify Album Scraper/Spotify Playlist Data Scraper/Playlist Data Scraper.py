import spotipy
import csv
from spotipy.oauth2 import SpotifyClientCredentials

# Set up client credentials
client_id = 'Your Client ID'
client_secret = 'Your Client Secret'
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Get information about a playlist
playlist_id = 'Playlist_ID'
playlist = sp.playlist(playlist_id)

# Open a CSV file for writing
filename = 'playlist_data.csv'
with open(filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)

    # Write the header row to the CSV file
    writer.writerow(['Track Name', 'Artist', 'Album', 'Duration', 'Release Date', 'Streams'])

    # Write the data rows to the CSV file
    for item in playlist['tracks']['items']:
        track = item['track']
        name = track['name']
        artist = track['artists'][0]['name']
        album = track['album']['name']
        duration = track['duration_ms'] / 1000 # Convert duration to seconds
        release_date = track['album']['release_date']
        streams = track['popularity']
        writer.writerow([name, artist, album, duration, release_date, streams])
        
print(f"Playlist data saved to {filename}")
