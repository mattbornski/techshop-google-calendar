#!/usr/bin/env python

import apiclient.discovery
import datetime
import dateutil.relativedelta
import event
import httplib2
import oauth2client.client
import os

def get_credentials():
    return oauth2client.client.OAuth2Credentials.from_json(os.environ['GOOGLE_CALENDAR_CREDENTIALS'])

def list_events(calendarId, month, year):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('calendar', 'v3', http=http)

    startOfMonth = datetime.datetime(year, month, 1)
    endOfMonth = (startOfMonth + dateutil.relativedelta.relativedelta(months=+1)).isoformat() + 'Z'
    startOfMonth = startOfMonth.isoformat() + 'Z'

    request = service.events().list(calendarId=calendarId, timeMin=startOfMonth, timeMax=endOfMonth, singleEvents=True, orderBy='startTime')
    ret = []
    while request is not None:
        response = request.execute(http=http)
        for item in response.get('items', []):
            ret.append(event.Event.from_google_calendar(item))
        request = service.events().list_next(request, response)
    return ret

def create_event(calendarId, techShopEvent):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    service.events().insert(calendarId=calendarId, body=techShopEvent.to_google_calendar()).execute()

def remove_event(calendarId, eventId):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    service.events().delete(calendarId=calendarId, eventId=eventId).execute()
