import openai
from twilio.rest import Client as TwilioClient
import boto3

from settings import settings


async def get_twilio_client() -> TwilioClient:
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    return TwilioClient(account_sid, auth_token)


async def get_openai() -> openai:
    openai.api_key = settings.OPENAI_API_KEY
    return openai

async def get_lex_client():
    # do I need aws_access_key_id and aws_secret_access_key ?
    client = boto3.client('lexv2-runtime', region = "eu-central-1")
    return client
