# AWS Lex Whatsapp Voice BFF
whatsapp voice message -> twillio -> EP -> AWS Lex  

## Why?
The reason for this chain is that the Lex-> Twillio -> Whatsapp integration doesn't support audio messages out-of-the box. If you set up a Whatsapp conversation between you and your twillio number/Lex bot, and you send it an audio message, you will get "Input message cannot be empty". If you set up an AWS lambda, it won't even be triggered. I don't know exactly where the chain breaks, but it breaks somewhere.

This BFF serves as an intermediary to catch the audio file from Whatsapp and then send it to Lex.

This is just a toy project to get to know Lex. It works locally for me (*famous last words*) but it is not production ready. Feel free to look at it as a basic working example, and build on it for your own project.

## How?
I started with [this tutorial](https://www.twilio.com/blog/build-ai-voice-assistant-whatsapp-python-whisper-chatgpt-twilio) because I did not initially know that Lex voice bots can receive audio or text; I thought I'd have to use whisper to convert my audio to text first. Nonetheless the instruction on how to set up a Twilio/Whatsapp integration (Twilio webhook) is valid, and using ngrok for local development.

For this project I made a Lex V2 bot using the AWS ui following [this tutorial](https://www.youtube.com/watch?v=RB8yw2nzA2Q&list=PLAMHV77MSKJ7s4jE7F_k_Od8qZlFGf1BY&index=1&ab_channel=PradipNichite), but [here](https://github.com/jzbruno/terraform-aws-lex-examples) is a great repo with examples of how to use terraform to set up a V1 bot. I am not using terraform because it does not support Lex V2.

## Resources:
 - [Youtube Lex how to](https://www.youtube.com/watch?v=RB8yw2nzA2Q&list=PLAMHV77MSKJ7s4jE7F_k_Od8qZlFGf1BY&index=1&ab_channel=PradipNichite)
 - [How to Build an AI Voice Assistant on WhatsApp with Python, Whisper API, ChatGPT API, and Twilio](https://www.twilio.com/blog/build-ai-voice-assistant-whatsapp-python-whisper-chatgpt-twilio)
