import azure.cognitiveservices.speech as speech_sdk
import datetime
import json
import os
import threading
import time
import urllib3
from dotenv import load_dotenv

import functions_format
import google_calendar

def main():
    global speech_config
    global speech_recognizer
    global openai_key

    load_dotenv()
    cog_key = os.getenv('COG_SERVICE_KEY')
    cog_region = os.getenv('COG_SERVICE_REGION')
    openai_key = os.environ.get('OPENAI_API_KEY')
    speech_config = speech_sdk.SpeechConfig(cog_key, cog_region)
    speech_config.speech_synthesis_voice_name = 'en-AU-CarlyNeural'
    speech_recognizer = speech_sdk.SpeechRecognizer(speech_config)
    tools = functions_format.google_calendar_function()

    current_datetime = datetime.datetime.now()
    date = current_datetime.date()
    time = current_datetime.time()

    system_messages = [ # End each sentence with a full stop
        'You are Gabby.',
        f'The date is {date} and time is {time} Singapore time.',
        'You can chat, save the output of the chat and add events to google calendar.'
        'If I tell you to save the output, return only "GCMD:save".',
        'If I tell you to shutdown or turn off, return only "GCMD:shutdown".'
    ]
    messages = [{'role': 'system', 'content': ' '.join(system_messages)}]
    messages = gabby('I am Gabby, how can I help?', messages)

    while True:
        print('1. Chat mode')
        print('2. Add calendar event mode')
        print('Q. Quit')

        choice = input('[You] ')

        if choice.lower() == '1':
            talk_to_gabby(messages)
        elif choice.lower() == '2':
            add_to_calendar(messages, tools)
        elif choice.lower() == 'q':
            print('Quitting')
            break
        else:
            print('[Gabby] Invalid choice, please try again.')

def talk_to_gabby(messages):
    while True:
        messages = your_question(messages)
        response = send_to_gpt(openai_key, messages)
        answer = response['choices'][0]['message']['content'].replace('**', '')

        if answer[:5] == 'GCMD:':
            if answer[5:].lower() == 'save':
                save_conversation(messages)
            elif answer[5:].lower() == 'shutdown':
                messages = gabby('Shutting down now.', messages)
                break
        else:
            messages = gabby(answer, messages)

def add_to_calendar(messages, tools):
    done = False
    while not done:
        messages = gabby('What event do you want to add?', messages)
        messages = your_question(messages)
        response = send_to_gpt(openai_key, messages, tools)

        if response['choices'][0]['message'].get('tool_calls'):
            answer = response['choices'][0]['message']['tool_calls'][0]['function']['arguments']
            messages = gabby(answer, messages)

            while True:
                messages = gabby('Do you want to add this? Yes or no.', messages)
                messages = your_question(messages)

                if 'yes' in messages[-1]['content'].lower() and not 'no' in messages[-1]['content'].lower():
                    if google_calendar.insert_event(answer):
                        messages = gabby('Successfully added!', messages)
                        done = True
                        break
                    else:
                        messages = gabby('Unsuccessful! Please try again.', messages)
                        done = True
                        break
                    #     messages = gabby('Unsuccessful! Do you want to try again? If not, I will exit out of the calendar mode.', messages)
                    #     messages = your_question(messages)

                    #     if 'yes' in messages[-1]['content'].lower() and not 'no' in messages[-1]['content'].lower():
                    #         continue
                    #     elif 'no' in messages[-1]['content'].lower() and not 'yes' in messages[-1]['content'].lower():
                    #         break
                    #     else:
                    #         messages = gabby('Ambiguious message, please let me know again.')

                elif 'no' in messages[-1]['content'].lower() and not 'yes' in messages[-1]['content'].lower():
                    messages = gabby('Ok, I won\'t add it then. Going back to normal mode.', messages)
                    done = True
                    break
                else:
                    messages = gabby('Ambiguious message, please let me know again.', messages)

        else:
            answer = response['choices'][0]['message']['content'].replace('**', '')
            messages = gabby(f'{answer} I did not find any events to add, try again? yes or no.', messages)
            messages = your_question(messages)

            while True:
                if 'yes' in messages[-1]['content'].lower() and not 'no' in messages[-1]['content'].lower():
                    break
                elif 'no' in messages[-1]['content'].lower() and not 'yes' in messages[-1]['content'].lower():
                    done = True
                    break
                else:
                    messages = gabby('Ambiguious message, please let me know again.', messages)

def save_conversation(messages):
    messages = gabby('Saving now.', messages)
    timestamp = str(datetime.datetime.now().strftime("%Y%m%d_%H%M"))
    with open(f'output_{timestamp}hrs.json', 'w') as f:
        json.dump(messages, f)
    with open(f'output_{timestamp}hrs.txt', 'w') as f:
        for i in messages[1:]:
            if i['role'] == 'user':
                f.write(f'[You] {i["content"]}\n')
            elif i['role'] == 'assistant':
                f.write(f'[gabby] {i["content"]}\n')
    messages = gabby('Saved, please check the output file.', messages)

def send_to_gpt(openai_key, messages, tools=[]):
    http = urllib3.PoolManager(num_pools=1)
    url = 'https://api.openai.com/v1/chat/completions'
    apiKey = 'Bearer ' + openai_key
    headers = {
        'Content-Type': 'application/json',
        'Authorization': apiKey
        }
    if tools:
        body = {
                'model': 'gpt-3.5-turbo-0125',
                'messages': messages,
                'tools': tools
            }
    else:
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

def gabby(message, messages):
    print(f'[Gabby] {message}')
    # text_to_speech(message)
    messages.append({'role': 'assistant', 'content': message})
    return messages

def your_question(messages):
    question = speech_to_text()
    print(f'[You] {question}')
    messages.append({'role': 'user', 'content': question})
    return messages

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

if __name__ == '__main__':
    print('''
   ______      __    __          ___    ____
  / ____/___ _/ /_  / /_  __  __/   |  /  _/
 / / __/ __ `/ __ \/ __ \/ / / / /| |  / /  
/ /_/ / /_/ / /_/ / /_/ / /_/ / ___ |_/ /   
\____/\__,_/_.___/_.___/\__, /_/  |_/___/   
                       /____/        by xygz
    ''')
    print('*Requires microphone and speaker')
    print()
    main()