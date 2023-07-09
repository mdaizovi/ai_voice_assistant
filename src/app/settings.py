import os
from decouple import config
from pydantic import BaseSettings


class Settings(BaseSettings):
    full_path = os.path.realpath(__file__)
    this_file_dir = os.path.dirname(full_path)
    AUDIO_IN_DIR = os.path.join(this_file_dir, "data", "input")
    AUDIO_OUT_DIR = os.path.join(this_file_dir, "data", "output")

    TWILIO_ACCOUNT_SID = config("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = config("TWILIO_AUTH_TOKEN")
    TWILIO_NUMBER = config("TWILIO_NUMBER")

    LEX2_BOT_ID = config("LEX2_BOT_ID")
    LEX2_BOT_ALIAS_ID = config("LEX2_BOT_ALIAS_ID")

    HOST_URL = "https://9505-62-27-218-107.ngrok-free.app"


settings = Settings()
