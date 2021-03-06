from flask import render_template, request, redirect, url_for, abort, jsonify, flash
from collections import defaultdict
from danceapp import app, db
from danceapp.models import *
from danceapp.signals import event_created, venue_created, promoter_created

from flask_login import current_user
import os

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/dances')
def dances():
    dances = Dance.query.all()
    return render_template('dance/index.html', dances=dances)

@app.route('/venues')
def venues():
    venues = Venue.query.all()
    return render_template('venue/index.html', venues=venues)

@app.route('/venues/new', methods=['POST', 'GET'])
def new_venue():
    if current_user.is_authenticated:

        cu = User.query.get_or_404(current_user.id)
        if cu.is_admin or cu.is_promoter:
            if request.method == 'POST':
                venue = Venue(name=request.form.get('name'))
                db.session.add(venue)
                db.session.commit()
                venue_created.send(venue)
                return redirect(url_for('venues'))
            else:
                return render_template('venue/new.html', tags=tags)
        else:
            flash("not authorised to create new venue", category="error")
    venues = Venue.query.all()
    return render_template('venue/index.html', venues=venues)

@app.route('/events')
def events():
    venue = None
    promoter = None
    if request.args.get('venue_id'):
        venue = Venue.query.get_or_404(request.args.get('venue_id'))
        events = Event.query.filter_by(venue_id=venue.id,).order_by(Event.date.asc()).all()
    elif request.args.get('dance_id'):
        dance = Dance.query.get_or_404(request.args.get('dance_id'))
        events = dance.danceevents
    elif request.args.get('promoter_id'):
        promoter = Promoter.query.get_or_404(request.args.get('promoter_id'))
        events = promoter.promoterevents
    else:
        # events = Event.query.order_by(Event.get_next_date().asc()).all()
        events = Event.query.all()

    events_by_status = defaultdict(list)
    for event in events:
        status = Status(event.status).name
        events_by_status[status].append(event)

    events.sort(key=lambda x: x.getNextDate())

    return render_template('event/index.html', events=events_by_status, events_by_time=events,
                           venue=venue,promoter=promoter)

@app.route('/promoters')
def promoters():
    promoters = Promoter.query.filter_by().all()

    if request.args.get('venue_id'):
        venue = Venue.query.get_or_404(request.args.get('storyline_id'))
        events = Event.query.filter_by(venue_id=venue.id).all()
    elif request.args.get('promoter_id'):
        promoter = Promoter.query.get_or_404(request.args.get('promoter_id'))
        if not promoter.user_id==current_user.id:
            abort(404)
        events = Event.query.filter_by(promoter_id=promoters.id).all()
    else:
        events = Event.query.all()


    events.sort(key=lambda x: x.date)
    return render_template('promoter/index.html', promoters=promoters, events=events)

@app.route('/promoters/new', methods=['POST', 'GET'])
def new_promoter():
    if current_user.is_authenticated:

        cu = User.query.get_or_404(current_user.id)
        if cu.is_admin:
            # id = db.Column(db.Integer, primary_key=True)
            # name = db.Column(db.String(30), unique=True)
            # initials = db.Column(db.String(3), unique=True)
            # color = db.Column(db.Integer)
            # events = db.relationship('Event', backref='castmember', lazy='dynamic')
            if request.method == 'POST':

                promoter = Promoter( name=request.form.get('name'))
                db.session.add(promoter)
                db.session.commit()
                promoter_created.send(promoter)
                return redirect('/promoters')
                # return redirect('/castmembers?castmember_id={}'.format(request.form.get('castmember_id')))
            else:
                venues = Venue.query.all()
                promoters = Promoter.query.all()
                colors = { color.name: color.value for color in TagColor }
                return render_template('promoter/new.html', venues=venues, promoters = promoters, colors=colors)
        else:
            flash("not authorised to create new promoter", category="error")
    else:
        events = Event.query.all()
        promoters=Promoter.query.all()
        events.sort(key=lambda x: x.date)
        return render_template('promoter/index.html', promoters=promoters, events=events)

@app.route('/events/new', methods=['POST', 'GET'])
def new_event():
    dances = Dance.query.all()

    if request.method == 'POST':
        event = Event(title=request.form.get('title'),
                    description=request.form.get('description'),
                    venue_id=request.form.get('venue_id'),
                      date=request.form.get('nextdate'),
                      startat=request.form.get('starttime'),endat=request.form.get('endtime'))
        if request.form.get('repeatsweekly')=="Yes":
            event.status=2
            event.day = Day[request.form.get('day_id')].value
        elif request.form.get('repeatreminder'):
            event.status=3
        else:
            event.status=1


        db.session.add(event)
        db.session.commit()

        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            # return redirect(request.url)
        else:
            file = request.files['file']
            msg = event.setFlyerLink(file)
            if not msg=='':
                flash(msg)

        for d in dances:
            if d.possibletags.count():
                c = 0
                for t in d.possibletags:
                    x = (request.form.get(str(d.id) + '_' + str(t.id)) == str(t.id))
                    y = (t in event.tags)
                    if not x == y:
                        set_tag(event.id, t.id)
                    if x:
                        c = c + 1
                if c > 0:
                    set_genre(event.id, t.dance.id)
            else:
                x=(request.form.get(str(d.id)+'_') == 'genre')
                y=(d in event.dances)
                if not x==y:
                    set_genre(event.id,d.id)


        db.session.add(event)
        db.session.commit()

        ep = EventPromoter(request.form.get('promoter_id'),event.id)
        db.session.add(ep)
        db.session.commit()
        event_created.send(event)
        return redirect('/events?promoter_id={}'.format(request.form.get('promoter_id')))
    else:
        venues = Venue.query.all()
        promoters = Promoter.query.all()

        return render_template('event/new.html', promoters=promoters, venues = venues, dances=dances)



@app.route('/events/<int:event_id>', methods=['POST', 'GET'])
def event(event_id):
    pass
    event = Event.query.get_or_404(event_id)
    promoters = event.promoters
    venue = event.venue
    dances = Dance.query.all()

    if request.method == 'POST':
        try:
            event.description = request.form.get('description')
            event.venue_id = request.form.get('storyline_id')
            event.date=request.form.get('nextdate')
            event.startat=request.form.get('starttime')
            event.endat=request.form.get('endtime')
            if request.form.get('repeatsweekly') == "Yes":
                event.status = 2
                event.day = Day[request.form.get('day_id')].value
            elif request.form.get('repeatreminder'):
                event.status = 3
            else:
                event.status = 1

            for d in dances:
                if d.possibletags.count():
                    c=0
                    for t in d.possibletags:
                        x=(request.form.get(str(d.id)+'_'+str(t.id)) == str(t.id))
                        y=( t in event.tags)
                        if not x==y:
                            set_tag(event_id,t.id)
                        if x:
                            c=c+1
                    if c>0:
                        set_genre(event_id,t.dance.id)
                else:
                    x=(request.form.get(str(d.id)+'_') == 'genre')
                    y=(d in event.dances)
                    if not x==y:
                        set_genre(event_id,d.id)

            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                # return redirect(request.url)
            else:
                file = request.files['file']
                msg=event.setFlyerLink(file)
                if not msg=='':
                    flash(msg)

            db.session.add(event)
            db.session.commit()
        except KeyError:
            abort(400)

        flash("Saved",category='message')

    return render_template('event/event.html', event=event, promoters=promoters, venue=venue, dances=dances)

@app.route('/events/<int:event_id>/set_status/<status>')
def set_status(event_id, status):
    if current_user.is_authenticated():
        cu = User.query.get_or_404(current_user.id)
        if cu.is_admin or cu.is_promoter:
            event = Event.query.get_or_404(event_id)
            try:
                event.status = Status[status.upper()].value
            except KeyError:
                abort(400)

            db.session.add(event)
            db.session.commit()
    return redirect(url_for('events'))\

@app.route('/events/<int:event_id>/set_genre/<genre_id>')
def toggle_genre(event_id, genre_id):
    if current_user.is_authenticated():
        cu = User.query.get_or_404(current_user.id)
        if cu.is_admin or cu.is_promoter:
            try:
                set_genre(event_id, genre_id)
            except KeyError:
                abort(400)
    return redirect(url_for('events'))
def set_genre(event_id, genre_id):
    event = Event.query.get_or_404(event_id)
    dance = Dance.query.get_or_404(genre_id)
    if dance in event.dances:
        eventdances_count = EventDance.query.filter_by(event_id=event_id,dance_id=genre_id).count()
        if eventdances_count>0:
            EDList = EventDance.query.filter_by(event_id=event_id,dance_id=genre_id).all()
            for e in EDList:
                db.session.delete(e)
    else:
        ed = EventDance(genre_id,event_id)
        db.session.add(ed)
    db.session.commit()


@app.route('/events/<int:event_id>/set_tag/<tag_id>')
def toggle_tag(event_id, tag_id):
    if current_user.is_authenticated():
        cu = User.query.get_or_404(current_user.id)
        if cu.is_admin or cu.is_promoter:

            try:
                set_tag(event_id,tag_id)
            except KeyError:
                abort(400)

    return redirect(url_for('events'))
def set_tag(event_id, tag_id):
    event = Event.query.get_or_404(event_id)
    tag = Tag.query.get_or_404(tag_id)
    if tag in event.tags:
        eventtags_count = EventTag.query.filter_by(event_id=event_id, tag_id=tag_id).count()
        if eventtags_count > 0:
            ETList = EventTag.query.filter_by(event_id=event_id, tag_id=tag_id).all()
            for e in ETList:
                db.session.delete(e)
    else:
        et = EventTag(tag_id, event_id)
        db.session.add(et)
    db.session.commit()


@app.route('/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    if current_user.is_authenticated():
        cu = User.query.get_or_404(current_user.id)
        if cu.is_admin or (cu.is_promoter and cu.is_valid_promoter_for(event)):
            db.session.delete(event)
            db.session.commit()
    return url_for('events')


@app.route('/tags/new', methods=['POST', 'GET'])
def new_tag():
    if request.method == 'POST':
        try:
            color = Color(int(request.form.get('color_id')))
        except ValueError:
            abort(400)
        tag = Tag( name=request.form.get('name'),color= color)
        db.session.add(tag)
        db.session.commit()
        return redirect(url_for('venues'))
    else:
        colors = { color.name: color.value for color in Color }
        return render_template('tags/new.html', colors=colors)


@app.route('/log')
def log():
    log_entries = LogEntry.query.all()
    return render_template('log.html', log_entries=log_entries)



# SECURITY

from forms import EmailPasswordForm
from util.security import ts
from util.email import send_email
from .models import User
from flask_login import login_user, logout_user, current_user, login_required
from .forms import UsernamePasswordForm, EmailForm, PasswordForm

# from flask.ext.login import login_user , logout_user , current_user , login_required

@app.route('/accounts/create', methods=["GET", "POST"])
def create_account():
    form = EmailPasswordForm()
    if form.validate_on_submit():
        user = User( username=form.email.data,
            password = form.password.data,
            email = form.email.data
        )
        db.session.add(user)
        db.session.commit()

        # Now we'll send the email confirmation link
        subject = "Confirm your email"

        token = ts.dumps(self.email, salt='email-confirm-key')

        confirm_url = url_for(
            'confirm_email',
            token=token,
            _external=True)

        html = render_template(
            'email/activate.html',
            confirm_url=confirm_url)

        # We'll assume that send_email has been defined in myapp/util.py
        send_email(user.email, subject, html)

        return redirect(url_for("index"))

    return render_template("accounts/create.html", form=form)

@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = ts.loads(token, salt="email-confirm-key", max_age=86400)
    except:
        abort(404)

    user = User.query.filter_by(email=email).first_or_404()

    user.email_confirmed = True

    db.session.add(user)
    db.session.commit()

    return redirect(url_for('signin'))


from database.seed import create_defaults


@app.route('/signup', methods=["GET", "POST"])
def signup():
    form = EmailPasswordForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user, force=True)
        #todo: create default event etc
        # create_defaults(user.id)
        return redirect(url_for('index'))

    return render_template('signup.html', form=form)

@app.route('/signin', methods=["GET", "POST"])
def signin():
    form = UsernamePasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first_or_404()
        if user is None:
            flash('Username or Password is invalid', 'error')
            return redirect(url_for('login'))

        if user.is_correct_password(form.password.data):
            login_user(user, force=True)
            flash('Logged in successfully')
            return redirect(url_for('index'))
        else:
            return redirect(url_for('signin'))
    return render_template('signin.html', form=form)



@app.route('/signout')
def signout():
    logout_user()

    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/reset', methods=["GET", "POST"])
def reset():
    form = EmailForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first_or_404()

        subject = "Password reset requested"

        # Here we use the URLSafeTimedSerializer we created in `util` at the
        # beginning of the chapter
        token = ts.dumps(user.email, salt='recover-key')

        recover_url = url_for(
            'reset_with_token',
            token=token,
            _external=True)

        html = render_template(
            'email/recover.html',
            recover_url=recover_url)

        # Let's assume that send_email was defined in myapp/util.py
        send_email(user.email, subject, html)

        return redirect(url_for('index'))
    return render_template('reset.html', form=form)

@app.route('/reset/<token>', methods=["GET", "POST"])
def reset_with_token(token):
    try:
        email = ts.loads(token, salt="recover-key", max_age=86400)
    except:
        abort(404)

    form = PasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first_or_404()

        user.password = form.password.data

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('signin'))

    return render_template('reset_with_token.html', form=form, token=token)