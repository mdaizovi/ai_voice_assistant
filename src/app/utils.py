import logging
import os
import requests
import urllib.request
import re
from pydub import AudioSegment

from settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
SEP = os.path.sep


def convert_audio_from_url(audio_url, from_extension="ogg", to_extension="mp3"):
    media_filename = audio_url.split(SEP)[-1]
    response = requests.get(audio_url)
    url = response.url
    # Download the OGG file
    input_filename = f"{settings.AUDIO_IN_DIR}{SEP}{media_filename}.{from_extension}"
    urllib.request.urlretrieve(url, input_filename)
    # Load the OGG file
    audio_file = AudioSegment.from_ogg(input_filename)
    # Export the file as MP3
    output_filename = f"{settings.AUDIO_OUT_DIR}{SEP}{media_filename}.{to_extension}"
    audio_file.export(output_filename, format=to_extension)
    return os.path.join(output_filename)


def convert_audio_from_local_file(
    audio_filepath, from_extension="wav", to_extension="mp3"
):
    result = re.search(f".*\{SEP}(.*).{from_extension}", audio_filepath)
    if result is not None:
        media_filename = result.group(1)
    else:
        media_filename = audio_filepath.partition(f".{from_extension}")[0]
    output_filename = f"{settings.AUDIO_OUT_DIR}{SEP}{media_filename}.{to_extension}"
    AudioSegment.from_wav(audio_filepath).export(output_filename, format=to_extension)
    return f"{media_filename}.{to_extension}"
