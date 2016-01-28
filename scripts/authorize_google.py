#!/usr/bin/env python

import oauth2client.client
import oauth2client.tools
import os

SCOPES = 'https://www.googleapis.com/auth/calendar'

class InMemoryStorage(oauth2client.client.Storage):
    def __init__(self, *args, **kwargs):
        self._credentials = None
        super(InMemoryStorage, self).__init__(*args, **kwargs)

    def locked_get(self):
        return self._credentials

    def locked_put(self, credentials):
        self._credentials = credentials

    def locked_delete(self):
        self._credentials = None

def generate_credentials():
    client_id = os.environ.get('GOOGLE_CALENDAR_CLIENT_ID', None)
    client_secret = os.environ.get('GOOGLE_CALENDAR_CLIENT_SECRET', None)
    application_name = os.environ.get('GOOGLE_CALENDAR_APPLICATION_NAME', None)

    flow = oauth2client.client.OAuth2WebServerFlow(client_id=client_id, client_secret=client_secret, scope=SCOPES, redirect_uri='')
    flow.user_agent = application_name
    storage = InMemoryStorage()
    flags = oauth2client.tools.argparser.parse_args(args=[])
    credentials = oauth2client.tools.run_flow(flow, storage, flags)
    print 'Set GOOGLE_CALENDAR_CREDENTIALS environment variable to:'
    print credentials.to_json()
    return credentials

if __name__ == '__main__':
    generate_credentials()
