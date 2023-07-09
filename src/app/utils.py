import logging
import os
import requests
import contextlib
import urllib.request
import re
from pydub import AudioSegment
import random
import string
from settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
SEP = os.path.sep


def download_audio_from_url(audio_url, from_extension="ogg"):
    media_filename = audio_url.split(SEP)[-1]
    response = requests.get(audio_url)
    url = response.url
    # Download the OGG file
    input_filename = f"{settings.AUDIO_DIR}{SEP}{media_filename}.{from_extension}"
    urllib.request.urlretrieve(url, input_filename)
    return input_filename


def convert_audio_from_url(audio_url, from_extension="ogg", to_extension="pcm"):
    input_filename = download_audio_from_url(audio_url, from_extension="ogg")
    audio_file = AudioSegment.from_ogg(input_filename)
    # Export the file as MP3
    output_filename = f"{settings.AUDIO_DIR}{SEP}{input_filename}.{to_extension}"
    audio_file.export(output_filename, format=to_extension)
    return os.path.join(output_filename)


def convert_audio_to_pcm(
    audio_filepath, to_extension="pcm", format="s16le", bitrate="16k"
):
    print("convert_audio_to_pcm")
    print(f"audio_filepath {audio_filepath}")
    from_extension = audio_filepath.partition(f".")[-1]
    result = re.search(f".*\{SEP}(.*).{from_extension}", audio_filepath)
    if result is not None:
        media_filename = result.group(1)
    else:
        media_filename = audio_filepath.partition(f".{from_extension}")[0]
    print(f"media_filename {media_filename }")
    new_path = f"{settings.AUDIO_DIR}{SEP}{media_filename}.{to_extension}"
    print(f"new_pathe {new_path}")

    sound = AudioSegment.from_file(audio_filepath, format=format)
    sound.export(new_path, format=format)
    return new_path


def convert_audio_from_local_file(
    audio_filepath, from_extension="wav", to_extension="mp3"
):
    result = re.search(f".*\{SEP}(.*).{from_extension}", audio_filepath)
    if result is not None:
        media_filename = result.group(1)
    else:
        media_filename = audio_filepath.partition(f".{from_extension}")[0]
    output_filename = f"{settings.AUDIO_DIR}{SEP}{media_filename}.{to_extension}"
    AudioSegment.from_wav(audio_filepath).export(output_filename, format=to_extension)
    return f"{media_filename}.{to_extension}"


def random_string(length=25):
    pool = string.ascii_lowercase + string.ascii_uppercase
    return "".join(
        (random.choice(pool) for x in range(length))
    )  # run loop until the define length
