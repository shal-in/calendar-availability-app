from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import datetime




def convert_date_to_iso_format(date_str):
    # Parse the input date string
    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    # Convert the datetime object to ISO format
    iso_date = date_obj.isoformat() + "Z"
    return iso_date


def get_date_string(current_str='today', days=0):
    if current_str == 'today': 
        # Get today's date
        date = datetime.date.today()
    else:
        try:
            # Convert the input string to a date object
            date = datetime.datetime.strptime(current_str, "%Y-%m-%d").date()
        except ValueError:
            # If the input string is not in the expected format, default to today's date
            date = datetime.date.today()
    
    # Add days to the date if days parameter is not 0
    if days != 0:
        date += datetime.timedelta(days=days)
    
    # Format the date as 'YYYY-MM-DD'
    formatted_date = date.strftime("%Y-%m-%d")
    
    return formatted_date

def remove_seconds(time_str):
    # Split the time string by ':'
    time_parts = time_str.split(':')
    
    # Join the first two parts (hours and minutes) with ':'
    time_without_seconds = ':'.join(time_parts[:2])
    
    return time_without_seconds



def get_service(credentials):
    service = build("calendar", "v3", credentials=credentials)

    return service


def get_events(service, calendar_id, start_date_str, days):
    start_iso = convert_date_to_iso_format(start_date_str)

    end_str = get_date_string(start_date_str, days)
    end_iso = convert_date_to_iso_format(end_str)

    events_result = (
    service.events()
    .list(
        calendarId=calendar_id,
        timeMin=start_iso,
        timeMax=end_iso,
        singleEvents=True,
        orderBy="startTime",
    )
    .execute()
    )

    events = events_result.get("items", [])

    return events


def get_tutoring_windows(events):
    availability = {}
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        end = event["end"].get("dateTime", event["end"].get("date"))

        start_parts = start.split('T')
        start_date = start_parts[0]
        start_time = start_parts[1].split('Z')[0]

        end_time = end.split('T')[1].split('Z')[0]

        start_time = datetime.datetime.strptime(start_time, '%H:%M:%S%z')
        end_time = datetime.datetime.strptime(end_time, '%H:%M:%S%z')

        # Initialize current time as start time
        current_time = start_time

        if 'summary' not in event or event['summary'].lower() == 'tutoring':
            if start_date not in availability:
                availability[start_date] = []
            

            # Loop to print 30-minute intervals until end time
            while current_time < end_time:
                current_time_str = current_time.strftime('%H:%M:%S')

                availability[start_date].append(current_time_str)

                # Increment current time by 30 minutes
                current_time += datetime.timedelta(minutes=30)

        else:
            while current_time < end_time:
                current_time_str = current_time.strftime('%H:%M:%S')

                availability[start_date].remove(current_time_str)

                # Increment current time by 30 minutes
                current_time += datetime.timedelta(minutes=30)
            
    return availability


def get_free_times(availability, duration):
    free_times = {}
    for date in availability:
        times = availability[date]

        daily_times = []
        for time_str in times:
            start_time_str = time_str + 'Z'

            start_time = datetime.datetime.strptime(start_time_str, '%H:%M:%S%z')
            end_time = start_time + datetime.timedelta(hours=duration)
            end_time_str = end_time.strftime('%H:%M:%S%z')

            current_time = start_time
            valid_start = True
            while current_time < end_time:
                current_time_str = current_time.strftime('%H:%M:%S')

                if current_time_str not in times:
                    valid_start = False
                    break

                current_time += datetime.timedelta(minutes=30)

            if valid_start:
                start_time_str = start_time_str.split('Z')[0]
                end_time_str = end_time_str.split('Z')[0]

                start_time_str = remove_seconds(start_time_str)
                end_time_str = remove_seconds(end_time_str)

                string = f'{start_time_str}-{end_time_str}'
                daily_times.append(string)
        
        free_times[date] = daily_times
        
    return free_times


def get_availability(service, calendar_id, start_date_str, days, duration):
    events = get_events(service, calendar_id, start_date_str, days)

    availability = get_tutoring_windows(events)

    free_times = get_free_times(availability, duration)


    return free_times

def create_event(service, calendar_id, summary, date, start, end, description=False, location = False):
    start_time = date + 'T' + start + 'Z'
    end_time = date + 'T' + end + 'Z'

    event = {
        'summary': summary,
        'start': {
            'dateTime': start_time,
            'timeZone': 'Europe/London'
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Europe/London'
        },
        'colorId': 9,
    }

    if description:
        event['description'] = description

    if location:
        event['location'] = location

    event = service.events().insert(calendarId=calendar_id, body=event).execute()

    return event