import azure.cognitiveservices.speech as speech_sdk
import json
import os
import time
import urllib3
from dotenv import load_dotenv

def main():
    global speech_config

    load_dotenv()
    cog_key = os.getenv('COG_SERVICE_KEY')
    cog_region = os.getenv('COG_SERVICE_REGION')
    openai_key = os.environ.get('OPENAI_API_KEY')
    speech_config = speech_sdk.SpeechConfig(cog_key, cog_region)
    messages = [{"role": "system", "content": "You are Gabby."}]

    gabby('I am Gabby, how can I help?')

    while True:
        question = speech_to_text()

        print(f'[You] {question}')

        if 'save output' in question.lower() or 'safe output' in question.lower():
            save_conversation(messages)
            continue
        elif 'shut down' in question.lower() or 'shutdown' in question.lower():
            gabby('Shutting down now.')
            exit()
        else:
            messages.append({'role': 'user', 'content': question})
            response = chat_with_gpt(openai_key, messages)
            if response:
                answer = response['choices'][0]['message']['content'].replace('**', '')
                gabby(answer)
                messages.append({'role': 'assistant', 'content': answer})
            else:
                gabby('There is an error, please repeat your question.')

def save_conversation(messages):
    if len(messages) == 1:
        gabby('Nothing to save.')
    else:
        gabby('Saving now.')
        # with open('output.json', 'w') as f:
        #     json.dump(messages, f)
        with open('output.txt', 'w') as f:
            for i in messages[1:]:
                if i['role'] == 'user':
                    f.write(f'[You] {i["content"]}\n')
                elif i['role'] == 'assistant':
                    f.write(f'[gabby] {i["content"]}\n')
        gabby('Saved, please check the output file.')

def chat_with_gpt(openai_key, messages):
    http = urllib3.PoolManager(num_pools=1)
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

    for i in range(3):
        if r.status == 200:
            j = json.loads(r.data)
            return j
        else:
            print(f'Error {r.status}... Trying again')
            time.sleep(5)

def speech_to_text():
    audio_config = speech_sdk.AudioConfig(use_default_microphone=True)
    
    while True:
        speech_recognizer = speech_sdk.SpeechRecognizer(speech_config, audio_config)
        print('Speak now...')
        speech = speech_recognizer.recognize_once_async().get()
        if speech.reason == speech_sdk.ResultReason.RecognizedSpeech:
            return speech.text
        else:
            print('Try again...')
                
def text_to_speech(message):
    speech_config.speech_synthesis_voice_name = 'en-AU-CarlyNeural' # en-SG-LunaNeural, en-GB-MaisieNeural, en-AU-CarlyNeural
    speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config=speech_config)
    speak = speech_synthesizer.speak_text_async(message).get()
    if not speak.reason == speech_sdk.ResultReason.SynthesizingAudioCompleted:
        cancellation_details = speak.cancellation_details
        print(f'Speech synthesis cancelled: {cancellation_details.reason}')
        if cancellation_details.reason == speech_sdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print(f'Error details: {cancellation_details.error_details}')

def gabby(message):
    print(f'[Gabby] {message}')
    text_to_speech(message)

if __name__ == '__main__':
    main()