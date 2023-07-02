import logging

from fastapi import APIRouter, Request, Depends

from twilio.rest import Client as TwilioClient

# Internal imports
from utils import convert_audio
from settings import settings

from app.dependencies import get_twilio_client, get_openai


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/message/whatsapp")
async def whatsapp_message(request: Request, twilio_client: TwilioClient = Depends(get_twilio_client), 
                           openai = Depends(get_openai)):
    form_data = await request.form()
    whatsapp_number = form_data['From'].split("whatsapp:")[-1]
    
    # TODO convert audio with AWS, not locally.
    media_url = form_data['MediaUrl0']
    text = _get_text_from_audio_url(openai, media_url)

    #TODO
    # send text to lex
    # return to user audio and/or text from lex

    chat_response = f"I think you said: {text}"
    _send_echo_message(twilio_client, to_number=whatsapp_number, body_text=chat_response)
    return ""


def _send_echo_message(twilio_client, to_number, body_text):
    twilio_number = settings.TWILIO_NUMBER
    try:
        message = twilio_client.messages.create(
            from_=f"whatsapp:{twilio_number}",
            body=body_text,
            to=f"whatsapp:{to_number}"
            )
        logger.info(f"Message sent to {to_number}: {message.body}")
    except Exception as e:
        logger.error(f"Error sending message to {to_number}: {e}")


def _get_text_from_audio_url(openai, media_url):
    mp3_file_path = convert_audio(audio_url=media_url)

    with open(mp3_file_path, "rb") as audio_file:
    # Call the OpenAI API to transcribe the audio using Whisper API
        whisper_response = openai.Audio.transcribe(
            file=audio_file,
            model="whisper-1",
            language="en",
            temperature=0.5,
        )
    return whisper_response.get("text")