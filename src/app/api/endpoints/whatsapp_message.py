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

# get_session
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lexv2-runtime/client/get_session.html

# recognize_utterance - can be text or speech
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lexv2-runtime/client/recognize_utterance.html

# recognize_text
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lexv2-runtime/client/recognize_text.html


@router.post("/message/whatsapp")
async def whatsapp_message(
    request: Request,
    twilio_client: TwilioClient = Depends(get_twilio_client),
    openai=Depends(get_openai),
):
    form_data = await request.form()
    #TODO I guess i can keep track of convrsation by whatsapp_number
    # Can I connect lex session id to that?
    whatsapp_user_number = form_data["From"].split("whatsapp:")[-1]
    whatsapp_session_id = form_data["From"]
    print(f"whatsapp_session_id  {whatsapp_session_id }")
    
    body = form_data["Body"]
    input_type = _get_input_type(input=form_data["Body"])

    if input_type == WhatsappInputType.TEXT:
        text = body
    elif input_type == WhatsappInputType.AUDIO:
        # No body means it's an audio message (well could be img but lets not worry about that)
        # TODO convert audio with AWS, not locally.
        # or can i jsut send to AWS?
        media_url = form_data["MediaUrl0"]
        text = _get_text_from_audio_url(openai, media_url)

    #TODO placeholder, does nothing
    _send_input_to_lex2()

    # TODO currently only sends text
    _send_whatsapp_response(twilio_client, whatsapp_user_number, text)

    return


def _send_echo_message(twilio_client, to_number, body_text):
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

def _get_language():
    #TODO get it from user input
    return "en_US"

def _send_input_to_lex2():
    """
    The following request fields must be compressed with gzip 
    and then base64 encoded before you send them to Amazon Lex V2.
        - requestAttributes
        - sessionState
    The following response fields are compressed using gzip 
    and then base64 encoded by Amazon Lex V2. 
    Before you can use these fields, you must decode and decompress them.
        - inputTranscript
        - interpretations
        - messages
        - requestAttributes
        - sessionState
    """
#     LOCALE_ID = _get_language()
#     response = client.recognize_text(
#     botId=botId,
#     botAliasId=botAliasId,
#     localeId=localeId,
#     sessionId=sessionId,
#     text='Book hotel')

# send to user 
# response['messages'][0]['content']


def _send_whatsapp_response(twilio_client, whatsapp_number, text):
    chat_response = f"I think you said: {text}"
    _send_echo_message(
        twilio_client, to_number=whatsapp_number, body_text=chat_response
    ) 
    
def _get_input_type(input):
    if (isinstance(input, str)):
        return WhatsappInputType.TEXT
    else:
        return WhatsappInputType.AUDIO

