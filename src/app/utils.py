import logging
import os
import requests
import urllib.request

from twilio.rest import Client
from pydub import AudioSegment

from settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AUDIO_IN_DIR = settings.AUDIO_IN_DIR
AUDIO_OUT_DIR = settings.AUDIO_OUT_DIR

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
twilio_number = settings.TWILIO_NUMBER
account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)


# Sending message logic through Twilio Messaging API
def send_message(to_number, body_text):
    try:
        message = client.messages.create(
            from_=f"whatsapp:{twilio_number}",
            body=body_text,
            to=f"whatsapp:{to_number}"
            )
        logger.info(f"Message sent to {to_number}: {message.body}")
    except Exception as e:
        logger.error(f"Error sending message to {to_number}: {e}")

def ogg2mp3(audio_url):
        media_filename = audio_url.split('/')[-1]
        response = requests.get(audio_url)
        url = response.url
        # Download the OGG file
        input_filename = f"{AUDIO_IN_DIR}/{media_filename}.ogg" 
        urllib.request.urlretrieve(url, input_filename)
        # Load the OGG file
        audio_file = AudioSegment.from_ogg(input_filename)
        # Export the file as MP3
        input_filename = f"{AUDIO_OUT_DIR}/{media_filename}.mp3" 
        audio_file.export(input_filename, format="mp3")
        return os.path.join(input_filename)