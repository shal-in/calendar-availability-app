from flask import Flask, jsonify, render_template, request
import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import helper

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



app = Flask(__name__)

@app.route('/')
def home():
    return 'Home'

@app.route('/api/test/<variable>')
def test(variable):
    print (variable)

    payload = {
        'message': 'request received',
        'variable': variable
    }

    extra = request.args.get('extra')
    if extra:
        payload['extra'] = extra
    
    more = request.args.get('more')
    if more:
        payload['more'] = more

    return jsonify(payload), 200


@app.route('/api/test/post', methods=['POST'])
def create_user():
    data = request.get_json()

    data['response'] = "success"

    return jsonify(data), 201

@app.route('/api/tutoring-availability', methods=['POST'])
def get_events():
    data = request.get_json()

    service = helper.get_service(creds)

    with open("calendar_id.txt", "r") as file:
        calendar_id = file.read().strip()

    # Call the Calendar API
    date = data['date']     
    current_date = datetime.datetime.strptime(date, "%Y-%m-%d").isoformat() + "Z"


    print (current_date)

    availability = helper.get_free_times(service, calendar_id, current_date, days=4)
    
    return jsonify(availability), 201


if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=2020, debug=True)
    