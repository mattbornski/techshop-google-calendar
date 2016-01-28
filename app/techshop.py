#!/usr/bin/env python

import bs4
import datetime
import event
import os
import pytz
import re
import requests
import titlecase

TIME_OF_DAY = re.compile(r'(1[012]|0?[0-9]):?([0-5][0-9])?(A|AM|P|PM)')
DURATION = re.compile(r'.*([0-9]+\.[0-9]+) Hours?.*')
SEATS = re.compile(r'.*([0-9]+) SEATS? LEFT.*')

def date_cell_filter(tag):
    # This is weak but this is the best scrapable indicator I've got right now
    return tag.has_attr('rowspan') and tag['rowspan'] == '2'

def class_cell_filter(tag):
    links = tag.find_all('a')
    for link in links:
        if link['href'].startswith('class_signup'):
            return True
    return False

def class_cell_parse(year, month, dayOfMonth, classCell):
    linkElement = classCell.find('a')
    seats = SEATS.match(linkElement['title'])
    if seats is None:
        # "SORRY, CLASS IS FULL", e.g.
        return None
    seats = int(seats.groups()[0])
    if seats <= 0:
        return None

    ret = event.Event()
    ret.title = titlecase.titlecase(linkElement.text.strip())
    ret.description = titlecase.titlecase(linkElement['title'])
    for abbreviation in ['3D', 'CAD', 'CAM', 'CNC', 'DIY', 'MIG', 'SBU', 'TIG', 'TV', 'ULS', 'II', 'III', 'IV', 'VI', 'VII', 'IX', 'XI']:
        matcher = re.compile(r'\b' + abbreviation + r'\b', re.IGNORECASE)
        ret.title = matcher.sub(abbreviation, ret.title)
        ret.description = matcher.sub(abbreviation, ret.description)
    ret.link = 'http://www.techshop.ws/' + linkElement['href']
    timeElement = classCell.find('td').text.strip()
    (hour, minute, meridian) = TIME_OF_DAY.match(timeElement).groups()
    hour = int(hour)
    minute = int(minute)
    if meridian.upper().startswith('P') and hour < 12:
        hour += 12
    ret.start_time = pytz.timezone(os.environ['TECHSHOP_LOCAL_TIMEZONE']).localize(datetime.datetime(year, month, dayOfMonth, hour, minute, 0, 0))
    duration = linkElement['title']
    ret.end_time = ret.start_time + datetime.timedelta(hours=float(DURATION.match(duration).groups()[0]))
    ret.time_zone = os.environ['TECHSHOP_LOCAL_TIMEZONE']
    ret.location = os.environ['TECHSHOP_LOCATION_STRING']
    return ret

def date_cell_parse(year, month, dayOfMonth, dateCell):
    ret = []
    classCells = dateCell.find_all('tr')
    for classCell in classCells:
        if class_cell_filter(classCell):
            parsed = class_cell_parse(year, month, dayOfMonth, classCell)
            if parsed is not None:
                ret.append(parsed)
    return ret

def calendar_scrape(storeId, month, year):
    url = "http://www.techshop.ws/class_calendar.html?storeId=" + str(storeId) + "&m=" + str(month) + "&y=" + str(year)
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.text, 'html.parser')
    dateCells = soup.find_all(date_cell_filter)
    ret = []
    for dateCell in dateCells:
        dayOfMonth = dateCell.find_all('td')[0].text.strip()
        if str(len(ret) + 1) == dayOfMonth:
            dayOfMonth = int(dayOfMonth)
            parsed = date_cell_parse(year, month, dayOfMonth, dateCell)
            if parsed is not None:
                ret.append(parsed)
    return ret
