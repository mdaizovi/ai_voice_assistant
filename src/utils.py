# Standard library import
import logging
import os
import requests
import urllib.request

# Third-party imports
from twilio.rest import Client
from decouple import config
from pydub import AudioSegment

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = config("TWILIO_ACCOUNT_SID")
auth_token = config("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)
twilio_number = config('TWILIO_NUMBER')

full_path = os.path.realpath(__file__)
this_file_dir = os.path.dirname(full_path)
AUDIO_IN_DIR = os.path.join(this_file_dir, "data", "input")
AUDIO_OUT_DIR = os.path.join(this_file_dir, "data", "output")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        print(f"media_filename {media_filename}")

        print(f"AUDIO_IN_DIR {AUDIO_IN_DIR }")
        print(f"AUDIO_OUT_DIR {AUDIO_OUT_DIR }")

        # Get the response of the OGG file
        response = requests.get(audio_url)
        # Get the redirect URL result
        url = response.url # `url` value something like this: "https://s3-external-1.amazonaws.com/media.twiliocdn.com/<some-hash>/<some-other-hash>"
        # Download the OGG file
        input_filename = f"{AUDIO_IN_DIR}/{media_filename}.ogg" 
        urllib.request.urlretrieve(url, input_filename)
        # Load the OGG file
        audio_file = AudioSegment.from_ogg(input_filename)
        # Export the file as MP3
        input_filename = f"{AUDIO_OUT_DIR}/{media_filename}.mp3" 
        audio_file.export(input_filename, format="mp3")
        return os.path.join(input_filename)