import openai
from pydub import AudioSegment
from decouple import config


# from decouple import Config, RepositoryEnv

# DOTENV_FILE = '/opt/envs/my-project/.env'
# env_config = Config(RepositoryEnv(DOTENV_FILE))

# use the Config().get() method as you normally would since 
# decouple.config uses that internally. 
# i.e. config('SECRET_KEY') = env_config.get('SECRET_KEY')
# OPENAI_API_KEY = env_config.get('SECRET_KEY')
# openai.api_key = OPENAI_API_KEY
OPENAI_API_KEY = config("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY
input_file = 'data/input/sample_audio.ogg'
# Load the audio file
audio_file = AudioSegment.from_ogg(input_file)

mp3_file = "data/output/sample_audio.mp3"
# Export the audio file in MP3 format
audio_file.export(mp3_file, format="mp3")
audio_file = open(mp3_file, "rb")

whisper_response = openai.Audio.transcribe(
        file=audio_file,
        model="whisper-1",
        language="en",
        temperature=0.5,
        )
audio_file.close()
print(whisper_response)