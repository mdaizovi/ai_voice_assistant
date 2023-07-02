import logging
import os
import requests
import urllib.request

from pydub import AudioSegment

from settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
SEP = os.path.sep

# TODO Split this into putting in S3 bucket and converting before or after.
def convert_audio(audio_url, from_extension="ogg", to_extension="mp3"):
    media_filename = audio_url.split(SEP)[-1]
    response = requests.get(audio_url)
    url = response.url
    # Download the OGG file
    input_filename = f"{settings.AUDIO_IN_DIR}{SEP}{media_filename}.{from_extension}"
    urllib.request.urlretrieve(url, input_filename)
    # Load the OGG file
    audio_file = AudioSegment.from_ogg(input_filename)
    # Export the file as MP3
    input_filename = f"{settings.AUDIO_OUT_DIR}{SEP}{media_filename}.{to_extension}"
    audio_file.export(input_filename, format=to_extension)
    return os.path.join(input_filename)
