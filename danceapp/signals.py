from blinker import Namespace


flasktasks_signals = Namespace()
event_created = flasktasks_signals.signal('event-created')
promoter_created = flasktasks_signals.signal('castmember-created')
venue_created = flasktasks_signals.signal('venue-created')
