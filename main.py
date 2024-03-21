import azure.cognitiveservices.speech as speech_sdk
import datetime
import json
import os
import threading
import time
import urllib3
from dotenv import load_dotenv

def main():
    global speech_config
    global speech_recognizer

    load_dotenv()
    cog_key = os.getenv('COG_SERVICE_KEY')
    cog_region = os.getenv('COG_SERVICE_REGION')
    openai_key = os.environ.get('OPENAI_API_KEY')
    speech_config = speech_sdk.SpeechConfig(cog_key, cog_region)
    speech_config.speech_synthesis_voice_name = 'en-AU-CarlyNeural'
    speech_recognizer = speech_sdk.SpeechRecognizer(speech_config)

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
        timestamp = str(datetime.datetime.now().strftime("%Y%m%d_%H%M"))
        with open(f'output_{timestamp}hrs.json', 'w') as f:
            json.dump(messages, f)
        with open(f'output_{timestamp}hrs.txt', 'w') as f:
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
    print('Speak now...')
    question = None

    def recognized_callback(evt):
        nonlocal question
        question = evt.result.text

    speech_recognizer.recognized.connect(recognized_callback)
    speech_recognizer.start_continuous_recognition_async()
    while question is None:
        time.sleep(0.1)
    speech_recognizer.stop_continuous_recognition_async().get()

    return question

def text_to_speech(message):
    speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config)
    speaking = True

    def synthesize_speech():
        nonlocal speaking
        speak = speech_synthesizer.speak_text_async(message).get()
        if not speak.reason == speech_sdk.ResultReason.SynthesizingAudioCompleted:
            cancellation_details = speak.cancellation_details
            print(f'Speech synthesis cancelled: {cancellation_details.reason}')
            if cancellation_details.reason == speech_sdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print(f'Error details: {cancellation_details.error_details}')
        speaking = False
    
    def listen_for_stop():
        recognition_active = True

        def recognized_callback(evt):
            nonlocal recognition_active
            if evt.result.reason == speech_sdk.ResultReason.RecognizedSpeech:
                if "stop" in evt.result.text.lower():
                    print(f'[You] {evt.result.text}')
                    speech_recognizer.stop_continuous_recognition_async()
                    speech_synthesizer.stop_speaking_async().get()
                    recognition_active = False

        speech_recognizer.recognized.connect(recognized_callback) # Attach a callback function
        speech_recognizer.start_continuous_recognition_async() # Starts listening
        while speaking and recognition_active:
            time.sleep(0.1)
        speech_recognizer.stop_continuous_recognition_async().get() # Stop if its not already stopped

    speech_thread = threading.Thread(target=synthesize_speech)
    stop_thread = threading.Thread(target=listen_for_stop)
    speech_thread.start()
    stop_thread.start()
    speech_thread.join()
    stop_thread.join()

def gabby(message):
    print(f'[Gabby] {message}')
    text_to_speech(message)

if __name__ == '__main__':
    main()