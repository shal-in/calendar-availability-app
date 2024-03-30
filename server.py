import datetime
import os.path

from flask import Flask, jsonify, render_template, request

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import helper

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

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

with open("calendar_id.txt", "r") as file:
    calendar_id = file.read().strip()







app = Flask(__name__)

@app.route('/')
def home():
    return 'Home'

@app.route('/api/tutoring-availability/get', methods = ['POST'])
def get_tutoring_availability():
    data = request.get_json()

    start_str = data['start_date']
    days = data['days']

    service = helper.get_service(creds)
    availability = helper.get_availability(service, calendar_id, start_str, days)

    return jsonify(availability), 200

@app.route('/api/tutoring-availability/create', methods = ['POST'])
def create_tutoring_event():
    data = request.get_json()

    summary = data['summary']
    date = data['date']
    start = data['start']
    end = data['end']

    if 'description' in data:
        description = data['description']
    else:
        description = False

    if 'location' in data:
        location = data['location']
    else:
        location = False

    service = helper.get_service(creds)

    event = helper.create_event(service, calendar_id, summary, date, start, end, description, location)

    if event:
        return event['summary'], 200
    
    else:
        return 400

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=2020, debug=True)

