# Assuming you have installed googleapiclient in your terminal or environment else use pip install googleapiclient
## To find the individual video ID from a channel

from googleapiclient.discovery import build

# Replace API_KEY with your own API key
api_key = "API_KEY"
youtube = build('youtube', 'v3', developerKey=api_key)

# Channel ID of the YouTube channel to retrieve video IDs for
channel_id = "CHANNEL_ID"

# Retrieve the playlist ID of the channel's uploaded videos
playlist_response = youtube.channels().list(part='contentDetails',
                                            id=channel_id).execute()
playlist_id = playlist_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

# Retrieve the video IDs of all the videos in the channel
video_ids = []
next_page_token = None

while True:
    # Use the playlistItems().list() method to retrieve videos in the playlist
    playlistitems_response = youtube.playlistItems().list(part='contentDetails',
                                                          playlistId=playlist_id,
                                                          pageToken=next_page_token).execute()

    # Retrieve the video IDs from the playlistItemsResponse
    for item in playlistitems_response['items']:
        video_ids.append(item['contentDetails']['videoId'])

    # Check if there are more pages of results to retrieve
    next_page_token = playlistitems_response.get('nextPageToken')

    if not next_page_token:
        break

# Print the video IDs to the console
print(video_ids)

# After you get the individual video IDs you can scrap any necessary informtion using youtube API

import csv
from googleapiclient.discovery import build

# Replace API_KEY with your own API key
api_key = 'YOUR_API_KEY'
youtube = build('youtube', 'v3', developerKey=api_key)

# List of video IDs to retrieve information for
video_ids = [VIDEO_IDS]

# Open a new CSV file for writing
with open('the_weeknd.csv', mode='w', newline='', encoding='utf-8') as csv_file:
    fieldnames = ['title', 'upload_date', 'views', 'likes', 'comments']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    # Write header row to CSV file
    writer.writeheader()

    # Iterate through each video ID and retrieve information
    for video_id in video_ids:
        video_response = youtube.videos().list(part='snippet,statistics',
                                                id=video_id).execute()
        video_title = video_response['items'][0]['snippet']['title']
        upload_date = video_response['items'][0]['snippet']['publishedAt']
        views = video_response['items'][0]['statistics']['viewCount']
        likes = video_response['items'][0]['statistics']['likeCount']
        comments = video_response['items'][0]['statistics']['commentCount']

        # Write video information to CSV file
        writer.writerow({'title': video_title,
                         'upload_date': upload_date,
                         'views': views,
                         'likes': likes,
                         'comments': comments})
        
# This writes the information to a csv file which you can use for other data analysis or visualizations
## happy explorations!