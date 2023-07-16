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
    input_filename = build_path_to_media_dir(
        filename=f"{media_filename}.{from_extension}"
    )
    urllib.request.urlretrieve(url, input_filename)
    return input_filename


def convert_audio_to_pcm(
    audio_filepath, to_extension="pcm", format="s16le", bitrate="16k"
):
    media_filename, from_extension = _parse_filename_and_extension_from_full_path(
        audio_filepath
    )
    new_path = build_path_to_media_dir(filename=f"{media_filename}.{to_extension}")
    # This creates a pcm file that audacity recognizes, but when i send it to aws it thinks it's text
    audio_file = AudioSegment.from_file(audio_filepath, format=from_extension)
    # Set the desired settings
    pcm_audio = audio_file.set_frame_rate(16000).set_sample_width(2).set_channels(1)
    pcm_data = pcm_audio.raw_data

    # Save the PCM data to a file
    new_path = f"{settings.AUDIO_DIR}{SEP}{media_filename}.{to_extension}"
    with open(new_path, "wb") as f:
        f.write(pcm_data)
    return new_path


def convert_audio_from_local_file(audio_filepath, to_extension="mp3"):
    media_filename, __ = _parse_filename_and_extension_from_full_path(audio_filepath)
    output_filename = build_path_to_media_dir(
        filename=f"{media_filename}.{to_extension}"
    )
    AudioSegment.from_wav(audio_filepath).export(output_filename, format=to_extension)
    return f"{media_filename}.{to_extension}"


def download_lex_audio_stream_to_filepath(audio_stream, to_extension="wav"):
    # I'm only using wav bc wave library is only thing i got to work with saving lex audio. can replace later.
    media_filename = random_string()
    output_file_path = build_path_to_media_dir(
        filename=f"{media_filename}.{to_extension}"
    )
    f = wave.open(output_file_path, "wb")
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(16000)
    f.writeframesraw(audio_stream)
    f.close()
    return output_file_path


def _parse_filename_and_extension_from_full_path(full_path):
    extension = full_path.partition(f".")[-1]
    result = re.search(f".*\{SEP}(.*).{extension}", full_path)
    if result is not None:
        filename = result.group(1)
    else:
        filename = full_path.partition(f".{extension}")[0]
    return filename, extension


def build_path_to_media_dir(filename):
    return f"{settings.AUDIO_DIR}{SEP}{filename}"


def delete_file(media_path):
    if os.path.isfile(media_path):
        os.remove(media_path)


def random_string(length=25):
    pool = string.ascii_lowercase + string.ascii_uppercase
    return "".join(
        (random.choice(pool) for x in range(length))
    )  # run loop until the define length
