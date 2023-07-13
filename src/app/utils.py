import logging
import os
import requests

import urllib.request
import re
import wave
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


def convert_audio_from_url(audio_url, to_extension="mp3"):
    input_filename = download_audio_from_url(audio_url)
    audio_file = AudioSegment.from_ogg(input_filename)
    # Export the file as MP3
    media_filename, __ = _parse_filename_and_extension_from_full_path(input_filename)
    output_filename = f"{settings.AUDIO_DIR}{SEP}{media_filename}.{to_extension}"
    audio_file.export(output_filename, format=to_extension)
    return os.path.join(output_filename)


def convert_audio_to_pcm(
    audio_filepath, to_extension="pcm", format="s16le", bitrate="16k"
):
    media_filename, __ = _parse_filename_and_extension_from_full_path(audio_filepath)
    new_path = f"{settings.AUDIO_DIR}{SEP}{media_filename}.{to_extension}"
    # This creates a pcm file that audacity recognizes, but when i send it to aws it thinks it's text
    audio_file = AudioSegment.from_file(audio_filepath)
    pcm_audio = audio_file.set_frame_rate(44100).set_sample_width(2).set_channels(1)
    # pcm_audio.export(new_path, format=format, bitrate=bitrate)
    # Raw works for "book hotel" but that's it
    pcm_audio.export(out_f=new_path, format="raw")
    return new_path


def convert_audio_from_local_file(audio_filepath, to_extension="mp3"):
    media_filename, __ = _parse_filename_and_extension_from_full_path(audio_filepath)
    output_filename = f"{settings.AUDIO_DIR}{SEP}{media_filename}.{to_extension}"
    AudioSegment.from_wav(audio_filepath).export(output_filename, format=to_extension)
    return f"{media_filename}.{to_extension}"


def _parse_filename_and_extension_from_full_path(full_path):
    extension = full_path.partition(f".")[-1]
    result = re.search(f".*\{SEP}(.*).{extension}", full_path)
    if result is not None:
        filename = result.group(1)
    else:
        filename = full_path.partition(f".{extension}")[0]
    return filename, extension


def random_string(length=25):
    pool = string.ascii_lowercase + string.ascii_uppercase
    return "".join(
        (random.choice(pool) for x in range(length))
    )  # run loop until the define length
