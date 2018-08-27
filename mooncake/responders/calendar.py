import datetime
import os.path
import pprint
from collections import namedtuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file calendar_token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

credentials_path = os.path.abspath('credentials/mooncake_calendar_secret.json')
token_path = os.path.abspath('credentials/calendar_token.json')
calendar_id = ('7304e91b1051c078c561adc8143c9ca58d5e73950b6c0a91e5fca48850188e1a@group.calendar.google.com')

Event = namedtuple('Event', ['summary', 'start', 'end', 'active', 'upcoming', 'remains', 'starts_in', 'description'])


def get_events(event_limit=5):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file calendar_token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        # print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId=calendar_id, timeMin=now,
                                              maxResults=event_limit, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        if not events:
            print('No upcoming events found.')
            return

        results = []
        # Prints the start and name of the next 10 events
        for event in events:
            # pprint.pprint(event)
            start = datetime.datetime.strptime(event['start'].get('date'), '%Y-%m-%d')
            end = datetime.datetime.strptime(event['end'].get('date'), '%Y-%m-%d')
            now = datetime.datetime.utcnow()
            active = start < now < end
            upcoming = now < start
            remains = end - now
            starts_in = start - now
            results.append(Event(
                summary=event.get('summary'),
                start=start,
                end=end,
                active=active,
                upcoming=upcoming,
                remains=remains,
                starts_in=starts_in,
                description=event.get('description'),
            ))
        return (results)

    except HttpError as error:
        print('An error occurred: %s' % error)


def respond_rally(message):
    events = get_events()
    result = []
    if events:
        result.append('Dirt 2.0 Rally events:')
        for event in events:
            marker = ''
            remains = ''
            if event.active:
                marker = '🟢 '
                if event.remains.days:
                    remains = f' ... remains: {event.remains.days}d'
                else:
                    remains = f' ... remains: {event.remains.seconds / 3600}h'
            if event.upcoming:
                marker = '🔴 '
                if event.starts_in.days < 5:
                    marker = '🟡 '
                if event.starts_in.days:
                    remains = f' ... starts in: {event.starts_in.days}d'
                else:
                    remains = f' ... starts in: {event.starts_in.seconds / 3600}h'

            result.append(f'{marker}**{event.summary}** {event.start.date()} -> {event.end.date()}{remains}')
            if event.description:
                result.append(event.description)
        return '\n'.join(result)


def respond_rally_now(message):
    events = get_events()
    result = []
    if events:
        result.append('Current Dirt 2.0 Rally event:')
        for event in events:
            if event.active:
                result.append(f'**{event.summary}** {event.start.date()} -> {event.end.date()}')
                if event.description:
                    result.append(event.description)
                return '\n'.join(result)


def respond_rally_next(message):
    events = get_events()
    result = []
    if events:
        result.append('Current Dirt 2.0 Rally event:')
        for event in events:
            if event.upcoming:
                result.append(f'**{event.summary}** {event.start.date()} -> {event.end.date()}')
                if event.description:
                    result.append(event.description)
        return '\n'.join(result)


def announce_rally_next():
    events = get_events(2)
    result = []
    if events:
        for event in events:
            if event.upcoming and event.starts_in.days in [2]:
                result.append(f'🗓 [REMINDER]  **{event.summary}** starts in **{event.starts_in.days}** days on {event.start.date()}')
                if event.description:
                    result.append(event.description)
    return '\n'.join(result)

def announce_rally_end():
    events = get_events(2)
    result = []
    if events:
        for event in events:
            if event.active and event.remains.days in [3,1]:
                result.append(f'🏁 [LAST CHANCE]  **{event.summary}** ends in **{event.remains.days}** days on {event.end.date()}')
                if event.description:
                    result.append(event.description)
    return '\n'.join(result)

