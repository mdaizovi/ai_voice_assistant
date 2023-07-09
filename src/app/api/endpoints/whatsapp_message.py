import logging
import json
import os
import wave
from pydub import AudioSegment
from fastapi import APIRouter, Request, Depends

from twilio.rest import Client as TwilioClient

# Internal imports
from utils import convert_audio_from_url, convert_audio_from_local_file
from settings import settings

from dependencies import get_twilio_client, get_lex_client
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
):
    # https://stackoverflow.com/questions/61872923/supporting-both-form-and-json-encoded-bodys-with-fastapi
    # form_data = await request.form()
    form_data = {**await request.form()}
    input_type = _get_input_type(form_data=form_data)
    whatsapp_user_number = form_data["From"].split("whatsapp:")[-1]

    lex_response = _send_input_to_lex2(boto3_client, form_data, input_type)
    if input_type == WhatsappInputType.TEXT:
        # prettified = json.dumps(lex_response, indent=4)
        # print(f"\n\lex_response\n{prettified}\n")
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
    elif input_type == WhatsappInputType.AUDIO:
        print("input type is audio")
        # audio_stream = lex_response["ResponseMetadata"]["audioStream"]

        audio_data = {**lex_response}
        del audio_data["audioStream"]
        prettified = json.dumps(audio_data, indent=4)
        print(f"\n\lex_response\n{prettified}\n")

        audio_stream = lex_response["audioStream"].read()
        # lex_response['audioStream'].close()
        print("got audio stream")
        print(type(audio_stream))
        media_path = _download_lex_audio_stream_to_filepath(audio_stream)

        media_filename = convert_audio_from_local_file(
            audio_filepath=media_path, from_extension="wav", to_extension="mp3"
        )
        print(f"media_filename {media_filename}")

        media_url = f"{settings.HOST_URL}/static/{media_filename}"
        print(f"media url is {media_url}")
        _send_whatsapp_message(
            twilio_client=twilio_client,
            to_number=whatsapp_user_number,
            media_url=media_url,
        )
        print(f"media path is {media_path}")
        if os.path.isfile(media_path):
            print(f"deleting {media_path}")
            # os.remove(media_path)
        else:
            print("not a file")

    return


def _download_lex_audio_stream_to_filepath(audio_stream):
    # 'content-type': 'audio/pcm',
    # has example of lex response: https://stackoverflow.com/questions/34570226/how-to-use-botocore-response-streamingbody-as-stdin-pipe

    output_format = "wav"
    filename = "audiofile"
    output_file_path = f"{settings.AUDIO_IN_DIR}/{filename}.{output_format}"

    f = wave.open(output_file_path, "wb")
    f.setnchannels(2)
    f.setsampwidth(2)
    f.setframerate(16000)  # sounds like a chipmunk
    f.setframerate(8000)  # acceptable
    f.setnframes(0)

    f.writeframesraw(audio_stream)
    f.close()

    media_path = f"{filename}.{output_format}"
    print(f"starting media_path is {media_path}")
    return media_path

    # audio_bytes = audio_stream.read()
    # audio_stream.close()
    # audio_segment = AudioSegment.from_file_using_temporary_files(audio_bytes)
    # output_format = 'mp3'
    # #TODO filename from audio_stream ?
    # filename = "audiofile"
    # output_file_path = f"{settings.AUDIO_OUT_DIR}/{filename}.{output_format}"
    # audio_segment.export(output_file_path, format=output_format)
    # return f"{filename}.{output_format}"


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
        # TODO remember to delete audio file after
        media_url = form_data["MediaUrl0"]
        mp3_file_path = convert_audio_from_url(audio_url=media_url)
        with open(mp3_file_path, "rb") as audio_file:
            lex_kwargs["requestContentType"] = "audio/l16; rate=16000; channels=1"
            lex_kwargs["responseContentType"] = "audio/pcm"
            lex_kwargs["inputStream"] = audio_file
            return boto3_client.recognize_utterance(**lex_kwargs)


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
