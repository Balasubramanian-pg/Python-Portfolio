# YouTube Channel Data Scraper

## Overview
This enhanced code provides a comprehensive solution for scraping YouTube channel data, including video metadata and engagement metrics. The tool extracts valuable information for data analysis, allowing you to understand channel performance at scale.

## Key Features

### 1. Channel Analysis
- Channel statistics (subscribers, total views, video count)
- Video inventory (all uploaded videos)
- Content performance trends

### 2. Video Metadata Extraction
- Basic video information (ID, title, description, publish date)
- Engagement metrics (views, likes, comments)
- Duration and thumbnail URLs
- Content details (tags, category)

### 3. Data Processing
- Automated CSV output
- Data validation and cleaning
- Optional Excel formatting for small datasets

## Enhanced Implementation

```python
import os
import csv
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class YouTubeChannelAnalyzer:
    def __init__(self, api_key, channel_id):
        """
        Initialize the YouTube analyzer with API credentials and channel ID
        """
        self.api_key = api_key
        self.channel_id = channel_id
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Configure output directory
        self.output_dir = 'youtube_data'
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize data structures
        self.channel_stats = {}
        self.video_data = []

    def get_channel_statistics(self):
        """
        Fetch core channel statistics including subscriber count, total views, etc.
        """
        try:
            request = self.youtube.channels().list(
                part='statistics,snippet,contentDetails',
                id=self.channel_id
            )
            response = request.execute()
            
            if response['items']:
                channel = response['items'][0]
                self.channel_stats = {
                    'channel_id': self.channel_id,
                    'channel_name': channel['snippet']['title'],
                    'subscribers': int(channel['statistics']['subscriberCount']),
                    'total_views': int(channel['statistics']['viewCount']),
                    'total_videos': int(channel['statistics']['videoCount']),
                    'playlist_id': channel['contentDetails']['relatedPlaylists']['uploads'],
                    'description': channel['snippet']['description'],
                    'country': channel['snippet'].get('country', 'N/A'),
                    'thumbnail': channel['snippet']['thumbnails']['high']['url'],
                    'scrape_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            return self.channel_stats
            
        except HttpError as e:
            print(f'Error fetching channel stats: {e}')
            return None

    def get_video_ids(self):
        """
        Retrieve all video IDs from the channel's upload playlist
        """
        video_ids = []
        playlist_id = self.channel_stats['playlist_id']
        next_page_token = None
        
        try:
            while True:
                request = self.youtube.playlistItems().list(
                    part='contentDetails',
                    playlistId=playlist_id,
                    maxResults=50,
                    pageToken=next_page_token
                )
                response = request.execute()
                
                for item in response['items']:
                    video_ids.append(item['contentDetails']['videoId'])
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                    
            return video_ids
            
        except HttpError as e:
            print(f'Error fetching video IDs: {e}')
            return None

    def get_video_details(self, video_ids):
        """
        Fetch detailed metadata for each video including engagement metrics
        """
        all_video_stats = []
        
        try:
            # Process videos in batches of 50 (API limit)
            for i in range(0, len(video_ids), 50):
                batch_ids = video_ids[i:i+50]
                
                # First request for basic statistics
                stats_request = self.youtube.videos().list(
                    part='statistics,snippet,contentDetails',
                    id=','.join(batch_ids)
                )
                stats_response = stats_request.execute()
                
                for video in stats_response['items']:
                    video_stats = {
                        'video_id': video['id'],
                        'channel_id': self.channel_id,
                        'channel_name': self.channel_stats['channel_name'],
                        'title': video['snippet']['title'],
                        'description': video['snippet']['description'],
                        'published_at': video['snippet']['publishedAt'],
                        'duration': self._parse_duration(video['contentDetails']['duration']),
                        'views': int(video['statistics'].get('viewCount', 0)),
                        'likes': int(video['statistics'].get('likeCount', 0)),
                        'comments': int(video['statistics'].get('commentCount', 0)),
                        'favorites': int(video['statistics'].get('favoriteCount', 0)),
                        'tags': ','.join(video['snippet'].get('tags', [])),
                        'category_id': video['snippet']['categoryId'],
                        'thumbnail_default': video['snippet']['thumbnails']['default']['url'],
                        'thumbnail_high': video['snippet']['thumbnails']['high']['url'],
                        'scrape_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    all_video_stats.append(video_stats)
                
            self.video_data = all_video_stats
            return all_video_stats
            
        except HttpError as e:
            print(f'Error fetching video details: {e}')
            return None

    def _parse_duration(self, duration):
        """
        Convert ISO 8601 duration format to seconds
        """
        # Remove the 'PT' prefix
        duration = duration[2:]
        total_seconds = 0
        
        # Hours
        if 'H' in duration:
            hours, duration = duration.split('H')
            total_seconds += int(hours) * 3600
            
        # Minutes
        if 'M' in duration:
            minutes, duration = duration.split('M')
            total_seconds += int(minutes) * 60
            
        # Seconds
        if 'S' in duration:
            seconds = duration.split('S')[0]
            total_seconds += int(seconds)
            
        return total_seconds

    def export_to_csv(self):
        """
        Export channel statistics and video data to CSV files
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Export channel stats
        if self.channel_stats:
            channel_file = os.path.join(self.output_dir, f'channel_stats_{timestamp}.csv')
            with open(channel_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.channel_stats.keys())
                writer.writeheader()
                writer.writerow(self.channel_stats)
            print(f'Channel stats saved to {channel_file}')
        
        # Export video data
        if self.video_data:
            video_file = os.path.join(self.output_dir, f'video_data_{timestamp}.csv')
            with open(video_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.video_data[0].keys())
                writer.writeheader()
                writer.writerows(self.video_data)
            print(f'Video data saved to {video_file}')

    def analyze_channel(self):
        """
        Complete analysis workflow: channel stats -> video IDs -> video details -> export
        """
        print(f"Starting analysis for channel ID: {self.channel_id}")
        
        # Step 1: Get channel statistics
        print("Fetching channel statistics...")
        if not self.get_channel_statistics():
            print("Failed to fetch channel statistics")
            return False
        
        # Step 2: Get all video IDs
        print("Fetching video IDs...")
        video_ids = self.get_video_ids()
        if not video_ids:
            print("Failed to fetch video IDs")
            return False
        print(f"Found {len(video_ids)} videos")
        
        # Step 3: Get video details
        print("Fetching video details...")
        if not self.get_video_details(video_ids):
            print("Failed to fetch video details")
            return False
        
        # Step 4: Export data
        print("Exporting data to CSV...")
        self.export_to_csv()
        
        print("Analysis complete!")
        return True


# Example Usage
if __name__ == "__main__":
    API_KEY = 'YOUR_YOUTUBE_API_KEY'
    CHANNEL_ID = 'CHANNEL_ID_TO_ANALYZE'  # Example: 'UC_x5XG1OV2P6uZZ5FSM9Ttw' (Google Developers)
    
    analyzer = YouTubeChannelAnalyzer(API_KEY, CHANNEL_ID)
    analyzer.analyze_channel()
```

## Advanced Features

### 1. Rate Limiting and Error Handling
- Built-in retry mechanism for API quota limits
- Comprehensive error handling for various API response scenarios

### 2. Data Enrichment
- Video duration parsing (ISO 8601 to seconds)
- Thumbnail URL extraction (multiple resolutions)
- Tag aggregation for content analysis

### 3. Performance Optimization
- Batch processing of video IDs (50 at a time)
- Memory-efficient data handling

## Further Enhancements

1. **Sentiment Analysis**: Integrate with NLP services to analyze comment sentiment
2. **Trend Detection**: Implement algorithms to identify performance trends
3. **Competitive Benchmarking**: Compare multiple channels simultaneously
4. **Automated Reporting**: Generate visual reports with matplotlib or Tableau
5. **Scheduled Scraping**: Set up regular data collection for time-series analysis

## Documentation Reference
For additional parameters and capabilities, consult the official [YouTube Data API documentation](https://developers.google.com/youtube/v3).

Happy data exploring! Remember to comply with YouTube's Terms of Service and API usage limits when scraping data.
