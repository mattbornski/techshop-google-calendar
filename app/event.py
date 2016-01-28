import datetime
import functools
import pytz

@functools.total_ordering
class Event(object):
    def __init__(self):
        self.source = None
        self.source_id = None
        self.title = None
        self.location = None
        self.start_time = None
        self.end_time = None
        self.time_zone = None
        self.description = None
        self.link = None

    def _comparable(self):
        if self.start_time is None:
            return None
        if self.end_time is None:
            return None

        return [
            self.start_time.isoformat(),
            self.end_time.isoformat(),
            self.title or '',
            self.description or '',
            self.location or '',
            self.link or '',
        ]

    def __lt__(self, other):
        myComparables = self._comparable()
        otherComparables = other._comparable()

        for i in xrange(0, len(myComparables)):
            if myComparables[i] < otherComparables[i]:
                return True
            elif myComparables[i] > otherComparables[i]:
                return False

        return False

    def __eq__(self, other):
        myComparables = self._comparable()
        try:
            otherComparables = other._comparable()
        except AttributeError:
            return False

        for i in xrange(0, len(myComparables)):
            if myComparables[i] < otherComparables[i]:
                return False
            elif myComparables[i] > otherComparables[i]:
                return False

        return True

    def __str__(self):
        return self.to_google_calendar()['summary'] + ' ' + self.to_google_calendar()['start']['dateTime']

    def to_google_calendar(self):
        return {
            'summary': self.title or '',
            'location': self.location or '',
            'description': self.description or '',
            'start': {
                'dateTime': self.start_time.isoformat(),
                'timeZone': self.time_zone or 'UTC',
            },
            'end': {
                'dateTime': self.end_time.isoformat(),
                'timeZone': self.time_zone or 'UTC',
            },
            'reminders': {
                'useDefault': False,
            },
            'source': {
                'url': self.link or '',
                'title': self.title or '',
            },
        }

    @classmethod
    def from_google_calendar(cls, data):
        instance = cls()
        instance.source_id = data['id']
        instance.title = data['summary']
        instance.location = data['location']
        instance.description = data['description']
        instance.start_time = datetime.datetime.strptime(data['start']['dateTime'].rsplit('-', 1)[0], '%Y-%m-%dT%H:%M:%S')
        if 'timeZone' in data['start']:
            instance.start_time = pytz.timezone(data['start']['timeZone']).localize(instance.start_time)
        instance.end_time = datetime.datetime.strptime(data['end']['dateTime'].rsplit('-', 1)[0], '%Y-%m-%dT%H:%M:%S')
        if 'timeZone' in data['end']:
            instance.end_time = pytz.timezone(data['end']['timeZone']).localize(instance.end_time)
        instance.time_zone = data['start']['timeZone'] or data['end']['timeZone']
        if 'source' in data and 'url' in data['source']:
            instance.link = data['source']['url']
        return instance
