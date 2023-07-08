from twilio.rest import Client as TwilioClient
import boto3
import logging

from settings import settings


async def get_twilio_client() -> TwilioClient:
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    client = TwilioClient(account_sid, auth_token)
    # Logging happens here automaticlly, to make it shut up do
    logging.basicConfig()
    client.http_client.logger.setLevel(logging.WARNING)
    # DEBUG INFO WARNING ERROR CRITICAL
    return client


async def get_lex_client():
    """
    Will work locally if you have  ~/.aws/credentials configured.
    Else you'll need to provide aws_access_key_id and aws_secret_access_key
    """
    client = boto3.client("lexv2-runtime", region_name="eu-central-1")
    return client
