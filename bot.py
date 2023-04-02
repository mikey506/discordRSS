import discord
import feedparser
import pickle
from flask import Flask, render_template

app = Flask(__name__)

# Define the RSS feed URLs and the corresponding Discord channels
feeds = {
    "https://nbmediacoop.org/feed/": 123456789012345678,
    "http://feeds.feedburner.com/TourismNewBrunswick": 234567890123456789,
    # ... other feeds ...
    "https://www.iheartradio.ca/feed/podcast-1/pure-country-weekends-1.9209392": 678901234567890123
}

# Load the stored feed information from a file, if it exists
try:
    with open("feeds.pickle", "rb") as f:
        stored_feeds = pickle.load(f)
except FileNotFoundError:
    stored_feeds = {}

# Create a Discord client
client = discord.Client()

@app.route('/')
def index():
    feed_info = [(url, channel_id) for url, channel_id in feeds.items()]
    return render_template('index.html', feeds=feed_info)

@client.event
async def on_ready():
    print("Logged in as {0.user}.".format(client))

@client.event
async def on_error(event, *args, **kwargs):
    print("Error:", args[0])

@client.event
async def on_disconnect():
    print("Disconnected.")

@client.event
async def on_message(message):
    if message.content == "!listfeeds":
        # Show a list of all the monitored feeds and their corresponding channels
        feed_list = "\n".join([f"{url}: {channel_id}" for url, channel_id in feeds.items()])
        await message.channel.send("Monitored feeds:\n" + feed_list)

# Monitor the RSS feeds and post updates to Discord
async def monitor_feeds():
    await client.wait_until_ready()

    while not client.is_closed():
        for url, channel_id in feeds.items():
            # Check if the feed has been updated since the last time it was checked
            last_checked = stored_feeds.get(url, None)
            feed = feedparser.parse(url)
            latest_entry = feed.entries[0]
            if last_checked is None or latest_entry.published_parsed > last_checked:
                # Post the update to the Discord channel
                channel = client.get_channel(channel_id)
                await channel.send(f"**{feed.feed.title}**\n{latest_entry.title}\n{latest_entry.link}")

                # Update the stored feed information
                stored_feeds[url] = latest_entry.published_parsed
                with open("feeds.pickle", "wb") as f:
                    pickle.dump(stored_feeds, f)

        # Wait for 10 minutes before checking the feeds again
        await asyncio.sleep(600)

# Start the Discord client and the feed monitor loop
client.loop.create_task(monitor_feeds())
client.run("<your_bot_token>")
