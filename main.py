import azure.cognitiveservices.speech as speech_sdk
import json
import os
import urllib3
from dotenv import load_dotenv

def main():
    global speech_config

    load_dotenv()
    cog_key = os.getenv('COG_SERVICE_KEY')
    cog_region = os.getenv('COG_SERVICE_REGION')
    openai_key = os.environ.get('OPENAI_API_KEY')
    speech_config = speech_sdk.SpeechConfig(cog_key, cog_region)
    messages = [{"role": "system", "content": "Your name is Gabby."}]

    text_to_speech('Hi, my name is Gabby, how can I assist you?')

    while True:
        question = speech_to_text()
        if question:
            if 'thanks' in question.lower():
                print(question)
                save_conversation(messages)
                exit()
            print('Question: ' + question)
        else:
            print('Error, please try again')

        messages.append({'role': 'user', 'content': question})

        response = chat_with_gpt(openai_key, messages)
        if response:
            chat_id = response['id']
            with open('output.json', 'w') as f:
                json.dump(response, f)
            answer = response['choices'][0]['message']['content']

        print('Answer: ' + answer)
        text_to_speech(answer)
        messages.append({'role': 'assistant', 'content': answer})

def save_conversation(messages):
    text_to_speech('Before you go, do you want to save your question and answer? Yes or no')
    reply = speech_to_text()

    print(reply)

    if 'yes' in reply.lower():
        text_to_speech('Saving now')
        with open('output.json', 'w') as f:
            json.dump(messages, f)
        text_to_speech('Saved, please check output.json, bye!')
    elif 'no' in reply.lower():
        text_to_speech('Alright, bye!')
    else:
        text_to_speech('I am unsure what you meant, it is not saved, bye!')

def chat_with_gpt(openai_key, messages):
    http = urllib3.PoolManager(num_pools=1, timeout=10.0)
    url = 'https://api.openai.com/v1/chat/completions'
    apiKey = 'Bearer ' + openai_key
    headers = {
        'Content-Type': 'application/json',
        'Authorization': apiKey
        }

    body = {
        'model': 'gpt-3.5-turbo-0125',
        'messages': messages
    }
    encoded_body = json.dumps(body).encode('utf-8')

    r = http.request('POST', url, body=encoded_body, headers=headers)

    if r.status == 200:
        j = json.loads(r.data)
        return j
    else:
        print(r.status)

def speech_to_text():
    audio_config = speech_sdk.AudioConfig(use_default_microphone=True)

    while True:
        speech_recognizer = speech_sdk.SpeechRecognizer(speech_config, audio_config)
        print('Speak now...')

        speech = speech_recognizer.recognize_once_async().get()
        if speech.reason == speech_sdk.ResultReason.RecognizedSpeech:
            return speech.text
        else:
            print(speech.reason)
            if speech.reason == speech_sdk.ResultReason.Canceled:
                cancellation = speech.cancellation_details
                print(cancellation.reason)
                print(cancellation.error_details)
                

def text_to_speech(answer):
    speech_config.speech_synthesis_voice_name = 'en-AU-CarlyNeural' # en-SG-LunaNeural, en-GB-MaisieNeural, en-AU-CarlyNeural
    speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config=speech_config)
    speak = speech_synthesizer.speak_text_async(answer).get()
    if not speak.reason == speech_sdk.ResultReason.SynthesizingAudioCompleted:
        cancellation_details = speak.cancellation_details
        print("Speech synthesis cancelled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speech_sdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))

if __name__ == '__main__':
    main()