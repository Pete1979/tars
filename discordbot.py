  # Set up intents (message_content intent is required to read message content)

intents = discord.Intents.default()

intents.message_content = True

    # Initialize the client

client = discord.Client(intents=intents)

    # Event: Bot has connected to Discord

@client.event

async def on_ready():

        print(f'Logged in as {client.user}')

        # Send a message to a specific channel after connecting

        #channel_id = 926676567663456306  # Replace with your channel ID

        channel = client.get_channel(channel_id)

        if channel:

            await channel.send(char_greeting)

    # Event: A new message is received

@client.event

async def on_message(message):

        # Ignore messages from the bot itself

        if message.author == client.user:

            return

        # Check if the message starts with a mention of the bot

        if message.content.startswith(f'<@{client.user.id}>'):

            #await message.channel.send('test complete')

            user_message = message.content

            global start_time, latest_text_to_read

            start_time = time.time() 

            print(user_message)

            reply = process_completion(user_message)

            print(reply)

            latest_text_to_read = reply

            await message.channel.send(latest_text_to_read)
