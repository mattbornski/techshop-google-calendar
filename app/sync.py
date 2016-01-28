#!/usr/bin/env python

import datetime
import dateutil.relativedelta
import itertools
import os

import techshop
import google

def sync():
    today = datetime.date.today()
    while True:
        print 'Checking TechShop calendar for ' + str(today.year) + '/' + str(today.month)
        anyEvents = False

        techShopIterator = iter(itertools.chain(*techshop.calendar_scrape(os.environ['TECHSHOP_STORE_ID'], today.month, today.year)))
        techShopEvent = next(techShopIterator, None)
        noEventsThisMonth = (techShopEvent is None)
        googleIterator = iter(google.list_events(os.environ['GOOGLE_CALENDAR_ID'], today.month, today.year))
        googleEvent = next(googleIterator, None)

        # This depends on them both being sorted in the same order
        # We order by ascending start time, and tie-break by alphabetical title
        events = {
            'matched': 0,
            'added': 0,
            'removed': 0,
        }
        while techShopEvent is not None:
            if techShopEvent == googleEvent:
                # Same event, advance both iterators
                events['matched'] += 1
                techShopEvent = next(techShopIterator, None)
                googleEvent = next(googleIterator, None)
            else:
                # Not the same event
                if googleEvent is None or techShopEvent < googleEvent:
                    # We should have seen the tech shop event already if it existed in the Google calendar, therefore it does not.
                    # Create it.
                    events['added'] += 1
                    google.create_event(os.environ['GOOGLE_CALENDAR_ID'], techShopEvent)
                    techShopEvent = next(techShopIterator, None)
                else:
                    # We should have seen the matching tech shop event for this google event if it still existed, therefore it does not.
                    # Remove it.
                    events['removed'] += 1
                    google.remove_event(os.environ['GOOGLE_CALENDAR_ID'], googleEvent.source_id)
                    googleEvent = next(googleIterator, None)

            if sum(events.values()) % 10 == 0:
                print events

        # No more TechShop events: remove all remaining Google events
        while googleEvent is not None:
            google.remove_event(os.environ['GOOGLE_CALENDAR_ID'], googleEvent.source_id)
            googleEvent = next(googleIterator, None)
        
        if noEventsThisMonth:
            # A completely empty month probably means that we've run off the end of the relevant calendar
            break
        today += dateutil.relativedelta.relativedelta(months=1)

if __name__ == '__main__':
    sync()
