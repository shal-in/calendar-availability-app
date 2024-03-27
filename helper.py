from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import datetime

def get_service(credentials):
    service = build("calendar", "v3", credentials=credentials)

    return service

def get_events(service, calendar_id, current_date, days=14):
    # Calculate the end time as now plus x days
    end_time = datetime.datetime.utcnow() + datetime.timedelta(days=days)
    end_time_iso = end_time.isoformat() + "Z"

    # Call the Calendar API
    events_result = (
        service.events()
        .list(
            calendarId=calendar_id,
            timeMin=current_date,
            timeMax=end_time_iso,  # Set the end time
            maxResults=20,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    return events

def get_availability(events):
    available_times = {}

    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        end = event["end"].get("dateTime", event["end"].get("date"))

        data = start.split('T')
        date = data[0]
        start_time = data[1]
        start_time = datetime.datetime.strptime(start_time, '%H:%M:%SZ')

        end_time = end.split('T')[1]
        end_time = datetime.datetime.strptime(end_time, '%H:%M:%SZ')
        
        # Find slots
        if event["summary"].lower() == 'tutoring':
            if date not in available_times:
                times = []
                available_times[date] = times
        
            current_time = start_time
            while current_time < end_time:
                time = current_time.strftime('%H:%M:%S')

                available_times[date].append(time)
                current_time += datetime.timedelta(minutes=30)

        # Remove lessons
        else:
            current_time = start_time
            while current_time < end_time:
                time = current_time.strftime('%H:%M:%S')
                
                if time in available_times[date]:
                    available_times[date].remove(time)
                current_time += datetime.timedelta(minutes=30)
        
    return available_times

def get_free_times(service, calendar_id, current_date, days=14):
    events = get_events(service, calendar_id, current_date, days)

    availability = get_availability(events)

    return availability

