import json
import os
import urllib3
import urllib.parse
from datetime import datetime, timedelta
from dotenv import load_dotenv
from requests_oauthlib import OAuth2Session

def insert_event(answer):
    load_dotenv()
    calendar = os.getenv('GOOGLE_CALENDAR')
    refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN')
    google_token = refresh_access_token(refresh_token)

    answer = json.loads(answer)
    if not answer.get('timeZone'):
        answer['timeZone'] = 'Asia/Singapore'
    if not answer.get('location'):
        answer['location'] = ''

    http = urllib3.PoolManager(num_pools=1)
    url = f'https://www.googleapis.com/calendar/v3/calendars/{calendar}/events'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {google_token}'
        }
    body = message_body(answer)
    print(body)
    encoded_body = json.dumps(body).encode('utf-8')

    r = http.request('POST', url, headers=headers, body=encoded_body)

    if r.status == 200:
        j = json.loads(r.data)
        return True
    else:
        print(f'Error {r.status}')
        print(r.data.decode('utf-8'))
        return False

def message_body(answer):
    if answer['allDay'] == 'no':
        return {
            'summary': answer['summary'],
            'location': answer['location'],
            'start': {
                'dateTime': answer['start'],
                'timeZone': answer['timeZone']
            },
            'end': {
                'dateTime': answer['end'],
                'timeZone': answer['timeZone']
            }
        }

    else:
        start = answer['start'][:10]
        date_str = datetime.strptime(answer['end'][:10], "%Y-%m-%d") + timedelta(days=1)
        end = str(date_str.strftime("%Y-%m-%d"))
        return {
            'summary': answer['summary'],
            'location': answer['location'],
            'start': {
                'date': start,
                'timeZone': answer['timeZone']
            },
            'end': {
                'date': end,
                'timeZone': answer['timeZone']
            }
        }

def new_access_token():
    with open('client_secret.json') as f:
        client_secrets = json.load(f)

    client_id = client_secrets['installed']['client_id']
    client_secret = client_secrets['installed']['client_secret']
    redirect_uri = client_secrets['installed']['redirect_uris'][0]

    # Define the scope
    scope = ['https://www.googleapis.com/auth/calendar']

    # Create an OAuth2 session
    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)

    # Generate the authorization URL
    authorization_url, state = oauth.authorization_url(
        'https://accounts.google.com/o/oauth2/auth',
        access_type="offline",  # Offline access so that you can refresh the access token without re-prompting the user
        prompt="consent"  # Prompt for consent so that the user is always shown the authorization page
    )

    print(f'Please go to {authorization_url} and authorize access.')

    # Get the authorization code from the callback URL
    redirect_response = input('Paste the full redirect URL here: ')

    # Extract the access token
    token = oauth.fetch_token(
        'https://oauth2.googleapis.com/token',
        authorization_response=redirect_response,
        client_secret=client_secret
    )

def refresh_access_token(refresh_token):
    http = urllib3.PoolManager()

    # Load your client secrets
    with open('client_secret.json') as f:
        client_secrets = json.load(f)

    client_id = client_secrets['installed']['client_id']
    client_secret = client_secrets['installed']['client_secret']

    # Define the token endpoint and the parameters for the POST request
    token_url = 'https://oauth2.googleapis.com/token'
    params = {
        'grant_type': 'refresh_token',
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token
    }
    params = urllib.parse.urlencode(params)

    # Make the POST request to refresh the access token
    r = http.request(
        'POST',
        token_url,
        body=params,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    # Check if the request was successful
    if r.status == 200:
        # Parse the response and extract the new access token
        new_token_info = json.loads(r.data.decode('utf-8'))
        new_access_token = new_token_info['access_token']
        return new_access_token
    else:
        print(f'Failed to refresh token: {r.status}')
        print(r.data.decode('utf-8'))