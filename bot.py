import discord
import feedparser
from flask import Flask, render_template

app = Flask(__name__)

# Define RSS feeds to monitor
feeds = [
    ("https://www.buzzfeed.com/world.xml", 123456789),  # Example
    # Add more feeds here
]

# Load or create pickle file for storing feed information
try:
    with open("feeds.pickle", "rb") as f:
        feed_info = pickle.load(f)
except FileNotFoundError:
    feed_info = {}

# Create a Discord client
client = discord.Client(intents=None)

# Discord event handlers
@client.event
async def on_ready():
    print(f"Logged in as {client.user.name} ({client.user.id})")

@client.event
async def on_member_join(member):
    # Send a welcome message to the member's default channel
    channel = member.guild.default_channel
    if channel:
        await channel.send(f"Welcome to the server, {member.mention}!")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Check if message contains any of the feed URLs
    for url, channel_id in feeds:
        if url in message.content:
            # Check if the feed has been posted recently
            if url not in feed_info or time.time() - feed_info[url]["last_post_time"] > 86400:
                # Fetch the latest feed entry
                feed = feedparser.parse(url)
                if feed.entries:
                    latest_entry = feed.entries[0]
                    # Post the entry to the specified channel
                    channel = client.get_channel(channel_id)
                    await channel.send(f"New post in {url}: {latest_entry.title}\n{latest_entry.link}")
                    # Update the last post time for the feed
                    feed_info[url] = {"last_post_time": time.time()}
                    with open("feeds.pickle", "wb") as f:
                        pickle.dump(feed_info, f)
                else:
                    await message.channel.send(f"No entries found for {url}")
            else:
                await message.channel.send(f"A post from {url} was already made today")

# Flask route for displaying monitored feeds
@app.route("/")
def index():
    return render_template("index.html", feeds=feeds)

# Start the bot and Flask app
client.run("YOUR_DISCORD_BOT_TOKEN")
app.run(port=8080, debug=True)
