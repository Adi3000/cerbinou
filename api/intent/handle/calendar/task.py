import httpx
import os
from ics import Calendar
from cachetools import cached, TTLCache
from datetime import datetime, timezone
import arrow
import logging
import pytz

calendar = TTLCache(maxsize=1, ttl=3600)
ICS_URL = os.getenv("ICS_URL", "")
TIMEZONE = pytz.timezone(os.getenv("TZ", "Europe/Paris"))
@cached(calendar)
def get_next_tasks():
    event_summary = ""
    if ICS_URL:
        response = httpx.get(ICS_URL)
        calendar =  Calendar(response.text)
        date_format =  "%A %d %B %Y à %H heures %M"
        today = arrow.get(datetime.now())
        next_events = sorted(filter(lambda e: e.begin > today, calendar.events), key=lambda e: e.begin)
        context_events = next_events[0:min(10,len(next_events))]
        for event in context_events:
            event_summary = event_summary + f"Le {event.begin.astimezone(tz=TIMEZONE).strftime(date_format)}, il y a {event.name}"
            if event.location:
                event_summary = event_summary + f" à {event.location}"
            event_summary = event_summary + ".\n"
    logging.info("Events : %s", event_summary)
    return event_summary

def get_time_speech(): 
    now = datetime.now().astimezone(tz=TIMEZONE)
    return now.strftime("On est le %A %d %B %Y et il est %H heures %M et %S secondes")
