# youtube-discord-notify

## Introduction

Most of social media automation tools I found out there requires me to pay, regularly, even for a simple Discord message notification using webhooks and API keys I manage, and also still need some coding for very simple two step logics.\
I wrote this so we don't have to spend 20 bucks a month just to send a message to Discord on videos we rarely upload as a casual content creator.

## Features

- Send Discord message via webhook on new videos
- Exclude videos with custom prefix in the description
- Different message for livestream videos

## Setup

1. Fork this repo
2. Set the repository secrets in your forked repo settings

```
CHANNEL_ID // your youtube channel id
DISCORD_WEBHOOK_URL // webhook to your discord server channel
GIT_EMAIL
GIT_USERNAME
YOUTUBE_API_KEY
```

- You can get your youtube channel ID from your channel URL: `https://www.youtube.com/channel/<CHANNEL_ID>`\
  If you use handle for your channel, you can get it in the channel customization page
- You can create your webhook in your Discord channel `Settings > Integration`
- For Youtube API key, read this [Youtube Data API Guide](https://developers.google.com/youtube/registering_an_application)

3. Set the repository variables (Optional)

```
// message text for the notification, defaults to "New video:"
VIDEO_MESSAGE
// put the same text at the beginning of your video description which you want to exclude
EXCLUDE_PREFIX
// just like EXCLUDE_PREFIX but for custom message (you can use this for non-live videos also)
LIVESTREAM_PREFIX
// message text for videos with LIVESTREAM_PREFIX, defaults to "Live:"
LIVESTREAM_MESSAGE
```

4. It's pretty much done. Run `Youtube Discord Notify` workflow in Github Actions, or just wait for about 10 minutes for it to run by itself.\
   By default it will run every 10 minutes, you can change this in `.github/workflow/deploy.yml`

## Improvements and Contribution

Currently this will only check for one latest public video you have, and will save that only one video notification state in `last-notified.json`.\
So if you delete that one latest video, the previous video which already notified will get duplicate notification. I plan to improve this using SQLite or more reliable JSON structure.\
\
Contributions are welcome! Feel free to submit your PR, and I'm open to other improvement ideas.

## Contact

Please open an issue if you have questions or feedbacks.
