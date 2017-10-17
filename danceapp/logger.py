from danceapp import app, db
from danceapp.models import LogEntry
from danceapp.signals import event_created, venue_created, promoter_created


@event_created.connect
def log_event_creation(event, **kwargs):
    message = "The event {} was created." .format(event.title)
    log_entry(message)


@promoter_created.connect
def log_promoter_creation(promoter, **kwargs):
    message = "The character {} was created ." .format(promoter.name)
    log_entry(message)

@venue_created.connect
def log_storyline_creation(venue, **kwargs):
    message = "The storyline {} was created ." .format( venue.name)
    log_entry(message)


def log_entry(message):
    log_entry = LogEntry(message)
    db.session.add(log_entry)
    db.session.commit()
