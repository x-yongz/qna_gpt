# Averlie the QnA bot

A simple project that takes in a voice question and tells you the answer.

This is built on the general urllib3 and API calls. It will persist your conversations until you close and reopen the script. Just keep talking to it. :)

### Requirements

1. Azure speech services resource
2. OpenAI subscription and API key

### Setup

1. Create a .env file in the directory

2. Enter the following into the .env file

   - OPENAI_API_KEY=\<your OpenAI apikey>
   - COG_SERVICE_KEY=\<your cognitive service key>
   - COG_SERVICE_REGION=\<your cognitive service region>

3. run "main.py"

4. Ask your questions in English or do one of the following,
  
   - Say "Shut down" to close the conversation
   - Say "Save output" to save the output to a text file

### Backend engines
- Azure cognitive services (speech service)
- OpenAI chatGPT