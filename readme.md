# QnA GPT

A simple project that takes in a voice question and tells you the answer.

This is built on the general urllib3 and API calls, not the OpenAI python package. 

### Requirements

1. Azure speech services resource
2. OpenAI subscription and API key

### Setup

1. Create a .env file in the directory

2. Enter the following into the .env file

   OPENAI_API_KEY=\<your OpenAI apikey>
   COG_SERVICE_KEY=\<your cognitive service key>
   COG_SERVICE_REGION=\<your cognitive service region>

3. run "main.py"

### Backend engines
- Azure cognitive services (speech service)
- OpenAI chatGPT