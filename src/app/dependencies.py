import openai
from twilio.rest import Client as TwilioClient

from settings import settings


async def get_twilio_client() -> TwilioClient:
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    return TwilioClient(account_sid, auth_token)


async def get_openai() -> openai:
    openai.api_key = settings.OPENAI_API_KEY
    return openai
