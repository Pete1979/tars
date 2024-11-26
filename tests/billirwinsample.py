import asyncio

async def test_voice():
    text = "Hello, I am TARS. What can I assist you with today?"
    communicate = Communicate(
        text=text, 
        voice="en-US-GuyNeural", 
        rate="-5%", 
        volume="+5%"
    )
    await communicate.save("test.mp3")

asyncio.run(test_voice())
