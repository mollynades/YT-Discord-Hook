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

# Function to load last notified data
def load_last_notified():
    try:
        with open('last_notified.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"video": None, "livestream": None}

# Function to save last notified data
def save_last_notified(data):
    with open('last_notified.json', 'w') as f:
        json.dump(data, f)

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
        maxResults=10  # Check the last 10 videos to find the latest public non-Short
    )
    response = request.execute()

    if 'items' in response:
        for video in response['items']:
            video_id = video['id']['videoId']
            if is_public_full_video(video_id):
                video_title = video['snippet']['title']
                video_url = f"https://www.youtube.com/watch?v={video_id}"

                if video_id != last_notified['video']:
                    send_discord_notification(f"@everyone cekidot video baru ges :fire:\n\n{video_title}\n{video_url}")
                    last_notified['video'] = video_id
                    return True
                return False  # We found the latest public non-Short video, but it was already notified
    return False

# Check for public live streams
def check_live_streams(last_notified):
    request = youtube.search().list(
        part="snippet",
        channelId=os.environ['CHANNEL_ID'],
        type="video",
        eventType="live",
        maxResults=1
    )
    response = request.execute()

    if 'items' in response:
        stream = response['items'][0]
        stream_id = stream['id']['videoId']
        if is_public_full_video(stream_id):  # Livestreams are not Shorts, but we'll use the same check for consistency
            stream_title = stream['snippet']['title']
            stream_url = f"https://www.youtube.com/watch?v={stream_id}"

            if stream_id != last_notified['livestream']:
                send_discord_notification(f"@everyone nonton live ges yak :v\n\n{stream_title}\n{stream_url}")
                last_notified['livestream'] = stream_id
                return True
    return False

if __name__ == "__main__":
    last_notified = load_last_notified()
    video_updated = check_new_videos(last_notified)
    livestream_updated = check_live_streams(last_notified)
    if video_updated or livestream_updated:
        save_last_notified(last_notified)