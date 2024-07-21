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
    response = requests.post(webhook_url, json=data)
    print(f"Discord notification sent. Status code: {response.status_code}")

# Function to check video details
def get_video_details(video_id):
    try:
        request = youtube.videos().list(
            part="status,snippet",
            id=video_id
        )
        response = request.execute()
        if 'items' in response and response['items']:
            item = response['items'][0]
            privacy_status = item['status']['privacyStatus']
            is_short = '#Shorts' in item['snippet'].get('tags', []) or item['snippet'].get('description', '').startswith('#Shorts')
            return privacy_status, is_short
    except Exception as e:
        print(f"Error checking video status: {e}")
    return None, None

# Check for new videos (including private and Shorts)
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
            print(f"Checking video: {video_id}")
            privacy_status, is_short = get_video_details(video_id)

            if privacy_status is not None:
                video_title = video['snippet']['title']
                video_url = f"https://www.youtube.com/watch?v={video_id}"

                if is_short and video_id != last_notified['short']:
                    send_discord_notification(f"New {privacy_status} Short uploaded: {video_title}\n{video_url}")
                    last_notified['short'] = video_id
                    return True
                elif not is_short and video_id != last_notified['video']:
                    send_discord_notification(f"New {privacy_status} video uploaded: {video_title}\n{video_url}")
                    last_notified['video'] = video_id
                    return True
                else:
                    print(f"Video {video_id} already notified or not relevant")
    return False

# Main execution
if __name__ == "__main__":
    last_notified = {'video': None, 'livestream': None, 'short': None}
    check_new_videos(last_notified)
    # Add check_live_streams() function if needed
