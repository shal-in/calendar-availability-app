import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import helper

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

        
    try:
        service = helper.get_service(creds)

        calendar_id = "190b48c9901f71f99bd0f617feaf517ade09b1590859f2b26199fb845e678f62@group.calendar.google.com"

        # Call the Calendar API
        current_date = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time

        availability = helper.get_free_times(service, calendar_id, current_date, days=4)

        for date in availability:
            print (f'Times on {date}:')
            for time in availability[date]:
                print (time)

            print ()


    except HttpError as error:
        print(f"An error occurred: {error}")




if __name__ == "__main__":
      main()