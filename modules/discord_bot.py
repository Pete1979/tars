# modules/discord_bot.py
import discord

class DiscordBot:
    def __init__(self, bot_token, channel_id, char_greeting):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.char_greeting = char_greeting
        self.client = discord.Client(intents=discord.Intents.default())

        # Set up the events
        self.client.event(self.on_ready)
        self.client.event(self.on_message)

    async def on_ready(self):
        print(f'Logged in as {self.client.user}')
        # Send a greeting message to the specified channel
        channel = self.client.get_channel(self.channel_id)
        if channel:
            await channel.send(self.char_greeting)

    async def on_message(self, message):
        # Ignore messages from the bot itself
        if message.author == self.client.user:
            return

        # Check if the message starts with a mention of the bot
        if message.content.startswith(f'<@{self.client.user.id}>'):
            # Get the user's message
            user_message = message.content
            print(f"Received: {user_message}")

            # Process the message and generate a reply
            reply = self.process_completion(user_message)
            print(f"Reply: {reply}")

            # Send the reply in Discord
            await message.channel.send(reply)

    def process_completion(self, user_message):
        # Example: Add your custom logic here (TARS-specific logic)
        return f"Processing your message: {user_message}"

    def run(self):
        self.client.run(self.bot_token)