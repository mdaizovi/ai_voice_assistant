# AWS Lex Whatsapp Voice BFF
whatsapp voice message -> twillio -> EP -> AWS Lex 

## Why?
The reason for this chain is that the Lex-> Twillio -> Whatsapp integration doesn't support audio messages out-of-the box. If you set up a Whatsapp conversation between you and your twillio number/Lex bot, and you send it an audio message, you will get "Input message cannot be empty". If you set up an AWS lambda, it won't even be triggered. I don't know exactly where the chain breaks, but it breaks somewhere.

This BFF serves as an intermediary to catch the audio file from Whatsapp and then send it to Lex.

This is just a toy project to get to know Lex. It works locally for me (*famous last words*) but it is not production ready. Most of all because I never set up a cron task too delete the mp3 audio fil safter you send them to whatsapp. If you were to use this for any reason, I suggest you do that. 
Now that I got it working I probably will never touch it again.
Feel free to look at it as a basic working example, and build on it for your own project.

## How I did it
I started with [this tutorial](https://www.twilio.com/blog/build-ai-voice-assistant-whatsapp-python-whisper-chatgpt-twilio) because I did not initially know that Lex voice bots can receive audio or text; I thought I'd have to use whisper to convert my audio to text first. Nonetheless the instruction on how to set up a Twilio/Whatsapp integration (Twilio webhook) is valid, and using ngrok for local development.

For this project I made a Lex V2 bot using the AWS ui following [this tutorial](https://www.youtube.com/watch?v=RB8yw2nzA2Q&list=PLAMHV77MSKJ7s4jE7F_k_Od8qZlFGf1BY&index=1&ab_channel=PradipNichite), but [here](https://github.com/jzbruno/terraform-aws-lex-examples) is a great repo with examples of how to use terraform to set up a V1 bot. I am not using terraform because it does not support Lex V2.

## Requirements:
 - python 
 - you might need `ffmpeg` and `libav`, I'm not sure. It seems like maybe pcm conversion didn't work until I installed them. I used homebrew.

## What you need to do to get it working
 - Install system requirements
 - Read the blog posts I reference above to set up your Twilio/Whatsapp integration and make yourself a Lex v2 bot.
 - Clone this repo
 - `cd` into main directory
 - Install further requiremwents with poetry (`poetry install`)
 - Copy the `.enx.example` file as an `.env` file, but fill in the values fro your own Lex2 Bot and Twilio number.
 - Run ngrok, and fill in the url ngrok gives you in the `settings.py` file and in the webhooks at Twilio dashboard.
 - Enjoy.


## Resources:
 - [Youtube Lex how to](https://www.youtube.com/watch?v=RB8yw2nzA2Q&list=PLAMHV77MSKJ7s4jE7F_k_Od8qZlFGf1BY&index=1&ab_channel=PradipNichite)
 - [How to Build an AI Voice Assistant on WhatsApp with Python, Whisper API, ChatGPT API, and Twilio](https://www.twilio.com/blog/build-ai-voice-assistant-whatsapp-python-whisper-chatgpt-twilio)
 - [Getting started with AWS Lex using a datafile and AWS Python SDK](https://towardsaws.com/getting-started-with-aws-lex-using-a-datafile-and-aws-python-sdk-64517fd751b7) for if you want to make another v2 bot and terraofrm isn't supported yet