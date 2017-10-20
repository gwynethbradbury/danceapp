from danceapp import db
from danceapp.models import Event, EventTag, Venue, User, Dance, Tag, Color, Promoter, EventDance, EventPromoter, UserPromoter#, Storyline, Event, CastmemberColor, Castmember, User, EventChar
import datetime


def create_dance_types():
    dt1= Dance('Salsa')
    db.session.add(dt1)
    db.session.commit()
    tag1 = Tag(name="On1",dance_id= dt1.id, color= Color.GREY)
    tag2 = Tag(name="On2", dance_id= dt1.id, color= Color.GREY)
    tag3 = Tag(name="Cuban", dance_id= dt1.id, color= Color.GREY)
    db.session.add(tag1)
    db.session.add(tag2)
    db.session.add(tag3)


    dt2= Dance('Bachata')
    db.session.add(dt2)
    db.session.commit()
    tag4 = Tag(name="Dominican",dance_id= dt2.id, color= Color.GREY)
    tag5 = Tag(name="Sensual",dance_id= dt2.id, color= Color.GREY)
    tag6 = Tag(name="Moderna",dance_id= dt2.id, color= Color.GREY)
    tag7 = Tag(name="Traditional",dance_id= dt2.id, color= Color.GREY)
    db.session.add(tag4)
    db.session.add(tag5)
    db.session.add(tag6)
    db.session.add(tag7)

    dt3= Dance('Kizomba')
    db.session.add(dt3)
    db.session.commit()
    tag8 = Tag(name="Urban",dance_id= dt3.id, color= Color.GREY)
    tag9 = Tag(name="Traditional",dance_id= dt3.id, color= Color.GREY)
    db.session.add(tag8)
    db.session.add(tag9)


    dt4= Dance('West Coast Swing')
    db.session.add(dt4)

    db.session.commit()


def create_promoters():
    promo1 = Promoter(name="Oxford University Salsa Society")
    # promo2 = Promoter(name="Unnamed promo2")
    db.session.add(promo1)
    # db.session.add(promo2)
    db.session.commit()

def create_events():
    dances=Dance.query.all()
    promoters=Promoter.query.all()
    venues=Venue.query.all()
    for d in dances:
        for v in venues:
            for p in promoters:

                event1 = Event(title="First Event",venue_id=v.id,
                               description= "{}, {}, {}".format(d.name,v.name,p.name),
                               startat=datetime.datetime.utcnow().time(), endat=datetime.datetime.utcnow().time())
                db.session.add(event1)
                db.session.commit()
                c=event1.id
                ep = EventPromoter(p.id,c)
                ed = EventDance(d.id, c)

                db.session.add(ed)
                db.session.add(ep)
    db.session.commit()

def crete_venues():
    venue0 = Venue("Anuba",51.752817, -1.265868)
    venue1 = Venue("Wesley Memorial Church",51.752994, -1.260758)
    venue2 = Venue("St Columba's Church Hall",51.751752, -1.255746)
    venue3 = Venue("Wadham College, Old Refectory",51.755718, -1.254721)
    venue4 = Venue("Green Templeton College Bar",51.760832, -1.263126)
    db.session.add(venue0)
    db.session.add(venue1)
    db.session.add(venue2)
    db.session.add(venue3)
    db.session.add(venue4)
    db.session.commit()

def create_user():
    u = User(username="default", password="password", email="default", is_admin=False,is_promoter=False)
    db.session.add(u)
    u = User(username="admin", password="password", email="admin", is_admin=True,is_promoter=False)
    db.session.add(u)

    u = User(username="promoter", password="password", email="promoter", is_admin=False,is_promoter=True)
    db.session.add(u)
    db.session.commit()
    promoters = Promoter.query.all()
    for p in promoters:
        ep = UserPromoter(p.id,u.id)
        db.session.add(ep)
    db.session.commit()


def link_event_tag():
    t = Tag.query.first()
    es = Event.query.all()
    for e in es:
        te = EventTag(t.id,e.id)
        db.session.add(te)
    db.session.commit()

def link_user_promoter():
    t = Promoter.query.first()
    es = User.query.all()
    for e in es:
        te = UserPromoter(t.id,e.id)
        db.session.add(te)
    db.session.commit()




def run_seed():
    print("Creating default user")
    create_defaults()
    create_user()
    print("Adding promoter to user ...")
    link_user_promoter()

def create_defaults():
    print("creating dances and tags")
    create_dance_types()

    print("creating venues")
    crete_venues()

    print("creating promoters")
    create_promoters()

    # print("creating events")
    # create_events()

    print("Adding tag to event ...")
    link_event_tag()


    return
