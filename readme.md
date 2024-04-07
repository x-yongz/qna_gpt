# GabbyAI

This project attempts to use AI to do multiple things like chatting and helping you do some basic task.

This is built on the general urllib3 and API calls. It will persist your conversations until you restart the script. 

This is just a side project that I am doing and learning, future improvements may include a web frontend and I may host this on cloud. 

### Requirements

1. Azure speech services resource
2. OpenAI subscription and API key
3. Microphone and speaker

### Setup

1. Create a .env file in the directory

2. Enter the following into the .env file

   - OPENAI_API_KEY=\<your OpenAI apikey>
   - COG_SERVICE_KEY=\<your cognitive service key>
   - COG_SERVICE_REGION=\<your cognitive service region>

3. Run "main.py"

4. Select the option

   4.1 Chat mode

      - Chat normally to Gabby
      - Tell Gabby to save your output in chat mode
      - Tell Gabby to shutdown

   4.2 Add calendar event mode

      - Only works for Google calendars
      - Requires you to sign-in to GabbyAI using your google account
      - Tell Gabby what you want to add, and she will form the function call
      - Confirm if you want to add

### Backend engines
- Azure cognitive services (speech service)
- OpenAI chatGPT
- Google API services