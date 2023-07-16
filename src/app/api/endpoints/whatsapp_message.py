import logging
import json

from fastapi import APIRouter, Request, Depends

from twilio.rest import Client as TwilioClient

# Internal imports
from utils import (
    download_audio_from_url,
    convert_audio_from_local_file,
    download_lex_audio_stream_to_filepath,
    delete_file,
    convert_audio_to_pcm,
)
from settings import settings

from dependencies import get_twilio_client, get_lex_client
from consts import WhatsappInputType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/message/whatsapp")
async def whatsapp_message(
    request: Request,
    twilio_client: TwilioClient = Depends(get_twilio_client),
    boto3_client=Depends(get_lex_client),
):
    # https://stackoverflow.com/questions/61872923/supporting-both-form-and-json-encoded-bodys-with-fastapi
    whatsapp_form_data = {**await request.form()}
    input_type = _get_input_type(form_data=whatsapp_form_data)
    whatsapp_user_number = whatsapp_form_data["From"].split("whatsapp:")[-1]

    lex_response = _send_input_to_lex2(boto3_client, whatsapp_form_data, input_type)

    if input_type == WhatsappInputType.TEXT:
        try:
            response_text = lex_response["messages"][0]["content"]
            _send_whatsapp_message(
                twilio_client=twilio_client,
                to_number=whatsapp_user_number,
                body_text=response_text,
            )
        except KeyError:
            # This is when Lex doesn't send messages bc it's done.
            # maybe if we add a finished message won't get KeyError?
            pass
    elif input_type == WhatsappInputType.AUDIO:
        audio_stream = lex_response["audioStream"].read()
        lex_data = {**lex_response}
        del lex_data["audioStream"]
        pprint_dict(lex_data["contentType"])

        lex_audio_stream_path_wav = download_lex_audio_stream_to_filepath(audio_stream)
        lex_audio_stream_filename_mp3 = convert_audio_from_local_file(
            audio_filepath=lex_audio_stream_path_wav, to_extension="mp3"
        )
        media_url = f"{settings.HOST_URL}/static/{lex_audio_stream_filename_mp3}"
        _send_whatsapp_message(
            twilio_client=twilio_client,
            to_number=whatsapp_user_number,
            media_url=media_url,
        )
        # Cleanup. Delete the wav after convert to mp3
        delete_file(lex_audio_stream_path_wav)
        # After the user plays media_filename_mp3 you can delete it, I guess they get it from whatsapp at that point.
        # or maybe it's saved locally after they download it.
        # But you can't delete here, you'll get a 404 when they try to get file.
        # TODO write a cron task or something.

    return


def _send_whatsapp_message(twilio_client, to_number, body_text=None, media_url=None):
    twilio_number = settings.TWILIO_NUMBER
    twilio_kwargs = {
        "from_": f"whatsapp:{twilio_number}",
        "to": f"whatsapp:{to_number}",
    }
    if all([body_text is not None, media_url is None]):
        message_type = "text"
        twilio_kwargs["body"] = body_text
    elif all([body_text is None, media_url is not None]):
        message_type = "audio"
        twilio_kwargs["media_url"] = [media_url]
    try:
        twilio_client.messages.create(**twilio_kwargs)
    except Exception as e:
        print(f"error sending {message_type} message {e}")


def _send_input_to_lex2(boto3_client, form_data, input_type):
    LOCALE_ID = _get_language()
    # TODO is this good enough, using phone number as session id?
    whatsapp_session_id = _build_session_from_whatsapp_from_value(form_data["From"])
    lex_kwargs = {
        "botId": settings.LEX2_BOT_ID,
        "botAliasId": settings.LEX2_BOT_ALIAS_ID,
        "localeId": LOCALE_ID,
        "sessionId": whatsapp_session_id,
    }

    if input_type == WhatsappInputType.TEXT:
        lex_kwargs["text"] = form_data["Body"]
        return boto3_client.recognize_text(**lex_kwargs)
    elif input_type == WhatsappInputType.AUDIO:
        media_url = form_data["MediaUrl0"]

        # first download the whhatsapp audio from the url in the form; it will be in ogg format
        input_filename = download_audio_from_url(media_url)
        # next convery it to pcm beore sending to Lex
        converted_audio_filepath = convert_audio_to_pcm(audio_filepath=input_filename)
        lex_kwargs["requestContentType"] = "audio/l16; rate=16000; channels=1"
        lex_kwargs["responseContentType"] = "audio/pcm"
        with open(converted_audio_filepath, "rb") as audio_file:
            lex_kwargs["inputStream"] = audio_file
            lex_response = boto3_client.recognize_utterance(**lex_kwargs)

        # Cleanup. Delete both ogg and pcm after I'm done with them
        delete_file(input_filename)
        delete_file(converted_audio_filepath)

        return lex_response


def _build_session_from_whatsapp_from_value(from_value):
    return from_value.replace("+", "")


def _get_input_type(form_data):
    body = form_data["Body"]
    if body != "":
        return WhatsappInputType.TEXT
    else:
        # ('MediaContentType0', 'audio/ogg'),  ('NumMedia', '1'),  ('Body', '')
        return WhatsappInputType.AUDIO


def _get_language():
    # TODO get it from user input
    return "en_US"


def pprint_dict(your_dict):
    print(json.dumps(your_dict, indent=4))
