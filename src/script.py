import os
import requests
import json
from googleapiclient.discovery import build

# Set up YouTube API client
youtube = build('youtube', 'v3', developerKey=os.environ['YOUTUBE_API_KEY'])

# Function to send Discord notification
def send_discord_notification(message):
    webhook_url = os.environ['DISCORD_WEBHOOK_URL']
    data = {"content": message}
    requests.post(webhook_url, json=data)

# Function to load last notified data
def load_last_notified():
    try:
        with open('last_notified.json', 'r') as f:
            data = json.load(f)
            print("Loaded last_notified.json:", data)
            return data
    except FileNotFoundError:
        print("last_notified.json not found, initializing with default values.")
        return {"last_video_id": None}

# Function to save last notified data
def save_last_notified(data):
    with open('last_notified.json', 'w') as f:
        json.dump(data, f)
        print("Saved last_notified.json:", data)

# Function to check if a video is public and not a Short
def is_public_video(video_id):
    try:
        request = youtube.videos().list(
            part="status,snippet",
            id=video_id
        )
        response = request.execute()
        if 'items' in response and response['items']:
            item = response['items'][0]
            is_public = item['status']['privacyStatus'] == 'public'
            is_excluded = bool(os.environ['EXCLUDE_PREFIX']) and item['snippet']['description'].startswith(os.environ['EXCLUDE_PREFIX'])
            return is_public and not is_excluded
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
        maxResults=1  # Check the last one video
    )
    response = request.execute()

    print("Response for new videos:", response)

    if 'items' in response:
        for video in response['items']:
            video_id = video['id']['videoId']
            video_description = video['snippet']['description']
            if is_public_video(video_id):
                video_title = video['snippet']['title']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                if video_id != last_notified['last_video_id']:
                    if bool(os.environ['LIVESTREAM_PREFIX']) and video_description.startswith(os.environ['LIVESTREAM_PREFIX']):
                        send_discord_notification(f"{os.environ['LIVESTREAM_MESSAGE']}\n\n{video_title}\n{video_url}")
                    else:
                        send_discord_notification(f"{os.environ['VIDEO_MESSAGE']}\n\n{video_title}\n{video_url}")
                    last_notified['last_video_id'] = video_id
                    print(f"Updated last_notified for video: {last_notified}")
                    return True
                return False  # We found the latest public non-Short video, but it was already notified
    return False

if __name__ == "__main__":
    last_notified = load_last_notified()
    print("Loaded last_notified:", last_notified)
    video_updated = check_new_videos(last_notified)
    if video_updated:
        save_last_notified(last_notified)
        print("Saved last_notified:", last_notified)
