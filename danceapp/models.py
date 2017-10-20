from danceapp import db
from danceapp import bcrypt

from enum import Enum
from time import strftime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

import datetime


class Status(Enum):
    ONE_OFF = 1
    REPEAT_REG = 2
    REPEAT_STRANGE = 3

class Day(Enum):
    MO = 1
    TU = 2
    WE = 3
    TH = 4
    FR = 5
    SA = 6
    SU = 7

class Color(Enum):
    GREY = 1
    BLUE = 2
    GREEN = 3
    YELLOW = 4
    RED = 5

class TagColor(Enum):
    GREY=1
    ORANGE=6
    YELLOW=7
    GREEN=8
    BLUE=9
    PURPLE=10
    DARKGREY=11




class EventTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))

    def __init__(self,tag_id,event_id):
        self.tag_id = tag_id
        self.event_id = event_id

class EventPromoter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    promo_id = db.Column(db.Integer, db.ForeignKey('promoter.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))

    def __init__(self,promo_id,event_id):
        self.promo_id = promo_id
        self.event_id = event_id

class EventDance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dance_id = db.Column(db.Integer, db.ForeignKey('dance.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))

    def __init__(self,dance_id,event_id):
        self.dance_id = dance_id
        self.event_id = event_id

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    color = db.Column(db.Integer)
    dance_id = db.Column(db.Integer, db.ForeignKey('dance.id'))
    # taggedevents = db.relationship('Event', backref='tags', lazy='dynamic')


    def __init__(self, name, dance_id, color=Color.GREY):
        self.name = name
        self.color = color.value
        self.dance_id=dance_id

    def style(self):
        color = Color(self.color)
        return "tagged tag-%s" % color.name.lower()

class Dance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    possibletags = db.relationship('Tag', backref='dance', lazy='dynamic')
    # danceevents = db.relationship('Event', backref='dances', lazy='dynamic')

    def __init__(self,name):
        self.name=name

    def hastags(self):
        if self.possibletags.count():
            return True
        return False

class UserPromoter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    promo_id = db.Column(db.Integer, db.ForeignKey('promoter.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self,promo_id,user_id):
        self.promo_id = promo_id
        self.user_id = user_id

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(70))
    description = db.Column(db.Text)
    status = db.Column(db.Integer)

    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))

    startat=db.Column(db.Time)
    endat=db.Column(db.Time)
    date=db.Column(db.Date)
    day=db.Column(db.Integer)

    tags = relationship("Tag",
                        secondary=EventTag.__table__,
                        backref="taggedevents")
    promoters = relationship("Promoter",
                        secondary=EventPromoter.__table__,
                        backref="promoterevents")
    dances = relationship("Dance",
                        secondary=EventDance.__table__,
                        backref="danceevents")

    flyerlink = db.Column(db.String(100))

    def get_next_date(self):
        if self.status==1:
            return self.date
        elif self.status==2:
            return self.day
        else:
            return self.date

    def __init__(self, title, venue_id, description, startat, endat, day=1, status=1, date=datetime.datetime.utcnow().date()):
        self.title = title
        self.description = description
        self.status = Status.ONE_OFF.value
        self.venue_id = venue_id
        self.startat = startat
        self.endat = endat
        self.day = day
        self.date = date
        self.status=status

    def getNextDate(self):
        if self.status==1:
            return self.date
        elif self.status==2:

            today = datetime.datetime.today().weekday()+1
            inc = (self.day - today) %7
            nextdate = datetime.datetime.utcnow() + datetime.timedelta(days=inc)
            return nextdate.date()
        else:
            return self.date


class Promoter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))

    def __init__(self,name):
        self.name=name

class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    latitude=db.Column(db.Float,default=51.508530)
    longitude=db.Column(db.Float,default=-0.076132)
    venueevents = db.relationship('Event', backref='venue', lazy='dynamic')

    def __init__(self,name,latitude=51.509,longitude=-0.076):
        self.name=name
        self.latitude=latitude
        self.longitude=longitude



#
# class Event(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(70))
#     description = db.Column(db.Text)
#     status = db.Column(db.Integer)
#     storyline_id = db.Column(db.Integer, db.ForeignKey('storyline.id'))
#     # castmember_id = db.Column(db.Integer, db.ForeignKey('castmember.id'))
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     event_occurs_percent = db.Column(db.Float)
#
#
#     cast = relationship("Castmember",
#                     secondary=EventChar.__table__,
#                     backref="events")
#
#
#     def __init__(self, user_id, title, description, storyline_id, castmember_id, event_occurs_percent=0):
#         self.title = title
#         self.description = description
#         self.status = Status.TO_DO.value
#         self.storyline_id = storyline_id
#         self.castmember_id = castmember_id
#         self.event_occurs_percent = event_occurs_percent
#         self.user_id = user_id
#
#
# class Storyline(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(70))
#     description = db.Column(db.String(210))
#     tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))
#     events = db.relationship('Event', backref='storyline', lazy='dynamic')
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#
#
#     def __init__(self, user_id, title, description, tag_id):
#         self.title = title
#         self.description = description
#         self.tag_id = tag_id
#         self.user_id = user_id
#
#
# class Castmember(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(30))
#     initials = db.Column(db.String(3))
#     color = db.Column(db.Integer)
#
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#
#
#     def __init__(self, user_id, name="Unassigned", initials="U", color=Color.GREY):
#         self.name = name
#         self.color = color.value
#         self.initials = initials
#         self.user_id = user_id
#
#     def getEvents(self):
#         Events=[]
#         EventChars = EventChar.query.filter_by(castmember_id=self.id).all()
#         for e in EventChars:
#             Events.append(Event.query.filter_by(event_id=e.event_id).first())
#         return Events
#
#
#     def style(self):
#         color = CastmemberColor(self.color)
#         return "tagged tag-%s" % color.name.lower()
#
#     def bgcol(self):
#         color = CastmemberColor(self.color)
#         return "bg-%s" % color.name.lower()
#


class LogEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(30))
    message = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, message):
        self.message = message
        self.timestamp = strftime("%d-%m-%Y %H:%M:%S")
        self.user_id = 1



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True)
    _password = db.Column(db.String(128))
    email = db.Column('email', db.String(50), unique=True, index=True)
    registered_on = db.Column('registered_on', db.DateTime)
    active = db.Column('active', db.Boolean)
    is_promoter = db.Column('is_promoter',db.Boolean, default=False)
    is_admin = db.Column('is_admin',db.Boolean, default=False)
    promotesfor = relationship("Promoter",
                        secondary=UserPromoter.__table__,
                        backref="promoterusers")


    def __init__(self, username="default", password="password", email="default", is_admin=False,is_promoter=False):
        self.username = username
        self.password = password
        self.email = email
        self.registered_on = datetime.datetime.utcnow()
        self.active = True
        self.is_admin=is_admin
        self.is_promoter=is_promoter


    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def _set_password(self, plaintext):
        self._password = bcrypt.generate_password_hash(plaintext)

    def is_correct_password(self, plaintext):
        return bcrypt.check_password_hash(self._password, plaintext)

    def get_id(self):
        return str(self.id)

    def is_active(self):
        """True, as all users are active. unless theyve been deactivated"""
        return self.active

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True #self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    def is_admin_user(self):
        return self.is_admin
    def is_promoter_user(self):
        return self.is_promoter

    def is_valid_promoter_for(self,event):
        for p in self.promotesfor:
            if p in event.promoters:
                return True
        return False


    def __repr__(self):
        return '<User %r>' % (self.username)