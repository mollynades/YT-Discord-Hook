import os
import requests
import json
from googleapiclient.discovery import build

# Set up YouTube API client
youtube = build('youtube', 'v3', developerKey=os.environ['YOUTUBE_API_KEY'])

# Function to send Discord notification
def send_discord_notification(message):
    webhook_url = os.environ['DISCORD_WEBHOOK']
    data = {"content": message}
    requests.post(webhook_url, json=data)

# Function to check if a video is public and not a Short
def is_public_full_video(video_id):
    try:
        request = youtube.videos().list(
            part="status,snippet",
            id=video_id
        )
        response = request.execute()
        if 'items' in response and response['items']:
            item = response['items'][0]
            is_public = item['status']['privacyStatus'] == 'public'
            is_not_short = item['snippet'].get('description') != '#Shorts'
            return is_public and is_not_short
    except Exception as e:
        print(f"Error checking video status: {e}")
    return False

# Check for new public videos (excluding Shorts)
def check_new_videos(last_notified):
    request = youtube.search().list(
        part="snippet",
        channelId=os.environ['CHANNEL_ID'],
        type="video",
        order="date",
        maxResults=10
    )
    response = request.execute()

    if 'items' in response:
        for video in response['items']:
            video_id = video['id']['videoId']
            if is_public_full_video(video_id):
                video_title = video['snippet']['title']
                video_url = f"https://www.youtube.com/watch?v={video_id}"

                if video_id != last_notified['video']:
                    send_discord_notification(f"New public video uploaded: {video_title}\n{video_url}")
                    last_notified['video'] = video_id
                    return True
    return False

# Main execution
if __name__ == "__main__":
    last_notified = {'video': None, 'livestream': None}
    check_new_videos(last_notified)
    # Add check_live_streams() function if needed
