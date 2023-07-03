import logging

from fastapi import APIRouter, Request, Depends

from twilio.rest import Client as TwilioClient

# Internal imports
from utils import convert_audio
from settings import settings

from dependencies import get_twilio_client, get_openai, get_lex_client
from consts import WhatsappInputType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# TODO: change to
# recognize_utterance - can be text or speech
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lexv2-runtime/client/recognize_utterance.html


@router.post("/message/whatsapp")
async def whatsapp_message(
    request: Request,
    twilio_client: TwilioClient = Depends(get_twilio_client),
    boto3_client=Depends(get_lex_client),
    openai=Depends(get_openai),
):
    form_data = await request.form()
    # TODO I guess i can keep track of convrsation by whatsapp_number
    # Can I connect lex session id to that?
    whatsapp_user_number = form_data["From"].split("whatsapp:")[-1]
    whatsapp_session_id = _build_session_from_whatsapp_from_value(form_data["From"])
    input_type = _get_input_type(form_data=form_data)

    if input_type == WhatsappInputType.TEXT:
        text = form_data["Body"]
    elif input_type == WhatsappInputType.AUDIO:
        # No body means it's an audio message (well could be img but lets not worry about that)
        # TODO convert audio with AWS, not locally.
        # or can i jsut send to AWS?
        media_url = form_data["MediaUrl0"]
        text = _get_text_from_audio_url(openai, media_url)

    lex_response = _send_input_to_lex2(
        boto3_client=boto3_client, session_id=whatsapp_session_id, text=text
    )
    try:
        response_text = lex_response["messages"][0]["content"]
        _send_whatsapp_message(
            twilio_client=twilio_client,
            to_number=whatsapp_user_number,
            body_text=response_text,
        )
    except KeyError:
        # This is when Lex doesn't send messages bc it's done.
        # maybe if we add a finsihed message won't get KeyError?
        pass

    return


def _send_whatsapp_message(twilio_client, to_number, body_text):
    twilio_number = settings.TWILIO_NUMBER
    try:
        message = twilio_client.messages.create(
            from_=f"whatsapp:{twilio_number}",
            body=body_text,
            to=f"whatsapp:{to_number}",
        )
        logger.info(f"Message sent to {to_number}: {message.body}")
    except Exception as e:
        logger.error(f"Error sending message to {to_number}: {e}")


def _get_text_from_audio_url(openai, media_url):
    mp3_file_path = convert_audio(audio_url=media_url)

    with open(mp3_file_path, "rb") as audio_file:
        # Call the OpenAI API to transcribe the audio using Whisper API
        whisper_response = openai.Audio.transcribe(
            file=audio_file, model="whisper-1", language="en", temperature=0.5,
        )
    return whisper_response.get("text")


def _build_session_from_whatsapp_from_value(from_value):
    return from_value.replace("+", "")


def _get_language():
    # TODO get it from user input
    return "en_US"


def _send_input_to_lex2(boto3_client, session_id, text):
    LOCALE_ID = _get_language()
    # TODO handle both text and audio
    return boto3_client.recognize_text(
        botId=settings.LEX2_BOT_ID,
        botAliasId=settings.LEX2_BOT_ALIAS_ID,
        localeId=LOCALE_ID,
        sessionId=session_id,
        text=text,
    )


def _get_input_type(form_data):
    body = form_data["Body"]
    if body != "":
        return WhatsappInputType.TEXT
    else:
        # ('MediaContentType0', 'audio/ogg'),  ('NumMedia', '1'),  ('Body', '')
        return WhatsappInputType.AUDIO
