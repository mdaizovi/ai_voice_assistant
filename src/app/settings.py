import os
from decouple import config
from pydantic import BaseSettings


class Settings(BaseSettings):
    full_path = os.path.realpath(__file__)
    this_file_dir = os.path.dirname(full_path)
    AUDIO_IN_DIR = os.path.join(this_file_dir, "data", "input")
    AUDIO_OUT_DIR = os.path.join(this_file_dir, "data", "output")

    OPENAI_API_KEY = config("OPENAI_API_KEY")
    TWILIO_ACCOUNT_SID = config("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = config("TWILIO_AUTH_TOKEN")
    TWILIO_NUMBER = config("TWILIO_NUMBER")

    LEX2_BOT_ID = config("LEX2_BOT_ID")
    LEX2_BOT_ALIAS_ID = config("LEX2_BOT_ALIAS_ID")

settings = Settings()
