# Third-party imports
import openai
from fastapi import FastAPI, Request
from decouple import config
from sqlalchemy.orm import Session

# Internal imports
from utils import send_message, logger, ogg2mp3

openai.api_key = config("OPENAI_API_KEY")
app = FastAPI()


@app.post("/message/whatsapp")
async def reply(request: Request):
    # Await for the incoming webhook request to extract information
    # like phone number and the media URL of the voice note
    form_data = await request.form()
    whatsapp_number = form_data['From'].split("whatsapp:")[-1]
    body = form_data['Body']
    print(f"body {body}")

    media_url = form_data['MediaUrl0']
    media_type = form_data['MediaContentType0']
    print(f"Media URL: {media_url}\nMedia Content type: {media_type}")

    # Convert the OGG audio to MP3 using ogg2mp3() function
    mp3_file_path = ogg2mp3(media_url)

    with open(mp3_file_path, "rb") as audio_file:
    # Call the OpenAI API to transcribe the audio using Whisper API
        whisper_response = openai.Audio.transcribe(
            file=audio_file,
            model="whisper-1",
            language="en",
            temperature=0.5,
        )
        print(f"""
        Transcribed the voice note to the following text: {whisper_response}.
            Now it's being sent to ChatGPT API to reply...
        """)

    text = whisper_response.get("text")
    chat_response = f"I think you said: {text}"
    send_message(whatsapp_number, chat_response)
    return ""