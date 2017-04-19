from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash
from sqlalchemy import create_engine, asc, func, distinct, or_
from sqlalchemy.orm import sessionmaker
from database_setup import Base, PQ, Deputy, Session, Constituency, User, Party, PNQ
from flask import Markup
from flask import session as login_session
import urllib2, random, string, json
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from functools import wraps
from flask import make_response
from os import path
from os.path import isfile, join, exists
import httplib2
import requests
from pprint import pprint
import random
from collections import OrderedDict
import os.path, datetime

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Nos deputes"

# folder to upload product and subcategory pictures
UPLOAD_FOLDER = 'static/products/'
SUBCAT_FOLDER = 'static/subcategories/'

# allowed file extensions for images
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///PQs.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

def sortFreqDict(freqdict):
    aux = [(freqdict[key], key) for key in freqdict]
    aux.sort()
    aux.reverse()
    return aux

def removeStopwords(wordlist, stopwords):
    return [w for w in wordlist if w not in stopwords]

def createUser(login_session):
    """ create a new user ready to be registered """
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """ retrieve user record from ID """
    user = session.query(User).filter_by(id=user_id).one()
    return user

def isAdmin(user):
    """ retrieve user record from ID """
    if user.role == "admin":
        return True
    else:
        return None

def getUserID(email):
    """ get user record from email """
    try:
        user = session.query(User).filter_by(email=email).one()
        return user
    except:
        return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash("you are not allowed here")
            return redirect(url_for('login'))
    return decorated_function

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # OAuth Login/Logout functions from Full Stack Foundations Course
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        username = login_session['email']
        error_msg = 'Current user is already connected.'
        response = make_response(json.dumps(error_msg), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # create new user if not registered
    if getUserID(login_session['email']):
        login_session['user_id'] = getUserID(login_session['email'])
    else:
        login_session['user_id'] = createUser(login_session)

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: \
    150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    """ DISCONNECT - Revoke a current user's token and reset 
    their login_session """
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    token = login_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        # response.headers['Content-Type'] = 'application/json'
        # return response
        return redirect('/')
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/signup',methods=['GET'])
def signup():
    """ signup page """
    if request.method == 'GET':
        return render_template('signup.html')

@app.route('/login',methods=['GET'])
def login():
    """ gmail authentication page """
    if request.method == 'GET':
        state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
        login_session['state'] = state
        return render_template('login.html', STATE=state)

@app.route('/logout',methods=['GET'])
def logout():
        return redirect('/gdisconnect')

@app.route('/blank',methods=['GET'])
def blank():
    """ display blank page - for testing purposes only """
    if request.method == 'GET':
        return render_template('blank.html')

@app.route('/',methods=['GET'])
def home():
    """ home page """
    if request.method == 'GET':
        start = datetime.datetime.now()
        latest = session.query(Session.id).order_by(Session.date.desc()).first()
        latest_pqs = session.query(PQ.title, PQ.pq, PQ.id).filter_by(session_id=latest.id).limit(3).all()
        
        params = dict()
        parties = session.query(Party.name, Party.color).all()
        labels = [ ]
        by_party = dict()
        latest_sessions = session.query(Session.id, Session.date).order_by(Session.date.desc()).limit(20)

        for sess in latest_sessions:
            dat = sess.date.strftime('%d-%b-%Y')
            labels.append(dat)

        colors = dict()
        for party in parties:
            colors[party.name] = party.color

        params['pqs'] = latest_pqs
        params['colors'] = colors
        params['labels'] = labels

        with open('graph.json') as data_file:    
            data = json.load(data_file)

        params['data'] = data
       
        pqs = session.query(PQ.title).all()
        print "t7: ", datetime.datetime.now() - start

        tags = []
        for pq in pqs:
            words = str(pq).split()
            ws = [w.replace('/\n',w) for w in words]
            for word in ws:
                w = word.rstrip()
                w2 = w.lstrip().replace('\n\n', '')

                tags.append(w2)

        tags = list(set(tags))
        tags2 = []
        for tag in tags:
            if random.random() < 0.7:
                tags2.append([tag, 'isbold'])
            else:
                tags2.append([tag, 'notbold'])
        params['tags2'] = tags2[1:70]

        if 'email' in login_session and isAdmin(getUserID(login_session['email'])):
        # check if the current user is logged in
            print 'the admin is here'
            params['logged_in']=True

        return render_template('home.html', **params)

@app.route('/pqs/all_by_date/<date>/JSON')
def pqs_by_dateJSON(date):
    """ output all PQs asked on a given date (JSON endpoint) """
    pqs = session.query(PQ).filter_by(date_asked=date)
    return jsonify(Questions=[pq.serialize for pq in pqs])

@app.route('/pqs/all_count_by_date/JSON')
def pqs_by_date_count_JSON():
    pqs = session.query(PQ.date_asked, func.count(PQ.date_asked).label('number')).group_by(PQ.date_asked).all()
    return jsonify(Questions=[pq for pq in pqs])


@app.route('/pqs/all_count_by_deputy/JSON')
def pqs_by_deputy_count_JSON():
    pqs = session.query(PQ.asked_by, func.count(PQ.asked_by).label('number')).group_by(PQ.asked_by).all()
    return jsonify(Questions=[pq for pq in pqs])


@app.route('/pqs/all_by_deputy/<deputy>/JSON')
def pqs_by_deputyJSON(deputy):
    pqs = session.query(PQ).filter_by(asked_by=deputy)
    return jsonify(Questions=[pq.serialize for pq in pqs])

@app.route('/constituencies/JSON', methods=['GET', 'POST'])
def constituenciesJSON():
    """ list of constituencies (JSON endpoint) """
    if request.method == 'POST':
        constituencies = session.query(Constituency).all()
        return jsonify(Constituencies=[constituency.serialize for constituency in constituencies])


@app.route('/pqs/by_id/<int:id>/JSON')
def pqs_by_idJSON(id):
    """ PQ by id (JSON endpoint) """
    pqs = session.query(PQ).filter_by(id=id)
    return jsonify(Questions=[pq.serialize for pq in pqs])

@app.route('/users/JSON')
def usersJSON():
    users = session.query(User).all()
    return jsonify(Users=[user.serialize for user in users])

@app.route('/pqs/all/JSON')
def pqsJSON():
    """ retrieve all PQs (JSON endpoint) """
    pqs = session.query(PQ).all()
    return jsonify(Questions=[pq.serialize for pq in pqs])

@app.route('/search',methods=['GET', 'POST'])
def search():
    """ search function """
    if request.method == 'POST':
        if request.form.get('search_term'):
            search = request.form.get('search_term')
            pqs = session.query(PQ).filter(or_(PQ.title.ilike("%" + search + "%"), 
                PQ.pq.ilike("%" + search + "%")))
            deputies = session.query(Deputy).filter(or_(Deputy.name.ilike("%" + search + "%"),
                                            Deputy.first_name.ilike("%" + search + "%")))
            params = dict()
            params['deputies'] = deputies
            params['search'] = search
            params['pqs'] = pqs
            return render_template('search.html', **params)
        else:
            return 'no search term submitted'
        # pqs = session.query(PQ).filter(or_(PQ.title.ilike("%" + search + "%"),
        #                                     PQ.pq.ilike("%" + search + "%")))
        # deputies = session.query(Deputy).filter(or_(Deputy.name.ilike("%" + search + "%"),
        #                                     Deputy.first_name.ilike("%" + search + "%")))
        # params = dict()
        # params['deputies'] = deputies
        # params['search'] = search
        # params['pqs'] = pqs
        # return render_template('search.html', **params)
    else:
        return render_template('search.html')

@app.route('/alltags',methods=['GET'])
def alltags():
    """ list all keywords """
    pqs = session.query(PQ.title).all()

    tags = []
    for pq in pqs:
        words = str(pq).split()
        ws = [w.replace('/\n',w) for w in words]
        print ws
        for word in ws:
            w = word.rstrip()
            w2 = w.lstrip().replace('\n\n', '')
            tags.append(w2)

    tags = list(set(tags))
    params = dict()
    params['tags'] = tags

    return render_template('keywords.html', **params)

@app.route('/pq/<int:id>/public')
def showPQ(id):
    """ show a single PQ """
    pq = session.query(PQ).filter_by(id=id).one()
    params = dict()
    print pq.id
    params['pq'] = pq
    if 'username' in login_session:
        # check if the current user is logged in
        params['logged_in']=True

    return render_template('single.html', **params)

@app.route('/pnq/<int:id>/public')
def showPNQ(id):
    """ show a single PQ """
    pnq = session.query(PNQ).filter_by(id=id).one()
    params = dict()
    params['pnq'] = pnq
    if 'username' in login_session:
        # check if the current user is logged in
        params['logged_in']=True
    return render_template('single_pnq_public.html', **params)

@app.route('/pq/<int:id>')
@login_required
def showPQAdmin(id):
    """ show a single PQ """
    pq = session.query(PQ).filter_by(id=id).one()
    params = dict()
    print pq.id
    params['pq'] = pq
    return render_template('single.html', **params)

@app.route('/pq/<int:id>/edit',methods=['GET', 'POST'])
@login_required
def editPQ(id):
    """ edit a PQ """
    if request.method == 'POST':
        editedpq = session.query(PQ).filter_by(id=id).one()
        if request.form['title']:
            editedpq.title = request.form['title']
        if request.form['pq']:
            editedpq.pq = request.form['pq']
        session.add(editedpq)
        session.commit()
        flash('PQ Successfully Edited')
        return redirect(url_for('showPQ', id=id))
    else:
        """ home page: show all categories """
        pq = session.query(PQ).filter_by(id=id).one()
        params = dict()
        print pq.id
        params['pq'] = pq
        return render_template('edit.html', **params)

@app.route('/pq/<int:id>/delete',methods=['POST'])
@login_required
def deletePQ(id):
    """ edit a PQ """
    if request.method == 'POST':
        print 'you are in the delete form'
        pqtodelete = session.query(PQ).filter_by(id=id).one()
        session.delete(pqtodelete)
        session.commit()
        flash('PQ Successfully deleted. Please run update script to recount.')
        return redirect(url_for('showAll'))
    else:
        """ home page: show all categories """
        pq = session.query(PQ).filter_by(id=id).one()
        params = dict()
        print pq.id
        params['pq'] = pq
        return render_template('edit.html', **params)

@app.route('/deputiesbyconstituency',methods=['GET', 'POST'])
def deputiesbyconstituency():
    """ display all deputies for a constituency """
    if request.method == 'POST':
        if request.form['constituencies']:
            consti = request.form['constituencies']
            const = session.query(Constituency).filter_by(id=consti).one()
            print const.constituency
            deputies = session.query(Deputy).filter_by(constituency=consti).all()
            for dep in deputies:
                print dep.name
            params = dict()
            params['constituency_no'] = consti
            params['constituency'] = const.constituency
            params['deputies']=deputies
            return render_template('depsbyconst.html', **params)

@app.route('/pqsbysession',methods=['GET', 'POST'])
def pqsbysession():
    """ output all PQs asked by session """
    if request.method == 'POST':
        if request.form['sessions']:
            sessions = session.query(Session).all()
            sess = request.form['sessions']
            sess2 = session.query(Session).filter_by(date=sess).one()
            pqs = session.query(PQ).filter_by(session_id=sess2.id).all()
            params = dict()
            params['session'] = sess2
            params['sessions'] = sessions
            params['pqs'] = pqs
            return render_template('pqsbysession.html', **params)

@app.route('/pqbydep/<name>/<title>')
def pqnewdep(name, title):
    """ display all PQs asked by a deputy """
    deputy = session.query(Deputy).filter_by(name=name).one()
    tit = title
    title =unicode('('+ title.encode('utf-8').strip() + ')', "utf-8")
    pqs = session.query(PQ).filter_by(deputy_id=deputy.id).all()
    query = session.query(PQ.date_asked.distinct().label("date_asked")).order_by(PQ.date_asked)
    dates = [row.date_asked for row in query.all()]

    dates.sort()

    sessions = session.query(Session).all()

    dat = dict()
    for sess in sessions:
         dat[sess.date.strftime('%b-%d-%Y')] = 0

    for pq in pqs:
        for sess in sessions:
            if pq.session_id == sess.id:
                dat[sess.date.strftime('%b-%d-%Y')]+= 1
                break;

    print dat.values()

    params = dict()
    params['pqs'] = pqs

    if (os.path.exists('static/wordclouds/'+name.strip())):
        params['wordcloud'] = name.strip

    params['name'] = name.strip()
    params['deputy_id'] = str(deputy.id)
    params['img_url'] = deputy.img_url
    params['title'] = title.strip()
    params['count'] = len(pqs)
    params['labels'] = dat.keys()
    params['values'] = dat.values()
    return render_template('pqbydeputy.html', **params)

@app.route('/deputies')
def deputiesdb():
    """ show all deputies in alphabetical order """
    alpha = list(string.ascii_uppercase)
    deputies = session.query(Deputy).filter(Deputy.title.isnot("")).order_by(Deputy.name).all()

    for dep in deputies:
        consti = session.query(Constituency).filter_by(id=dep.constituency).one()
        dep.zone = consti.constituency

    params = dict()
    params['deputies'] = deputies
    params['alpha'] = alpha

    deps = dict()

    deps['A'] = 'hello'

    for a in alpha:
        de = session.query(Deputy).filter(Deputy.name.like(format(a)+"%")).order_by(Deputy.name).all()
        for d in de:
            d.id = str(d.id)
        if len(de) < 1:
            deps[a] = 'nothing'
        else:
            deps[a] = de
        # deps[a].append('hello')

    params['deps'] = deps

    if 'username' in login_session:
        # check if the current user is logged in
        params['logged_in']=True

    return render_template('deputies_clean.html', **params)
       
@app.route('/pqs/all')
def showAll():
    """ show all PQs """
    pqs = session.query(PQ).order_by(asc(PQ.date_asked)).limit(50).all()
    pqs_count = session.query(PQ.id).count()
    params = dict()
    params['pqs'] = pqs
    params['pqs_count'] = pqs_count

    sessions = session.query(Session).all()
    params['sessions'] = sessions

    dat = dict()

    for sess in sessions:
        dat[sess.date]=sess.count

    params['labels']=dat.keys()
    params['values']=dat.values()
    
    if 'username' in login_session:
        # check if the current user is logged in
        params['logged_in']=True

    return render_template('all.html', **params)

@app.route('/hansard')
def hansard():
    """ display all hansards available in txt and pdf format """
    sessions = session.query(Session).order_by(asc(Session.date)).all()
    params = dict()
    params['sessions'] = sessions

    if 'username' in login_session:
        # check if the current user is logged in
        params['logged_in']=True

    return render_template('hansard.html', **params)

@app.route('/pnq')
def pnq():
    """ display list of all PNQs """
    sessions = session.query(Session).order_by(asc(Session.date)).all()
    pnqs = session.query(PNQ).all()

    params = dict()
    params['sessions'] = sessions
    params['pnqs'] = pnqs

    if 'username' in login_session:
        # check if the current user is logged in
        params['logged_in']=True

    return render_template('pnq.html', **params)

@app.route('/committees')
def committees():
    """ list of parliamentary committees - UNDER CONSTRUCTION """
    sessions = session.query(Session).order_by(asc(Session.date)).all()
    params = dict()
    params['sessions'] = sessions

    if 'username' in login_session:
        # check if the current user is logged in
        params['logged_in']=True

    return render_template('committees.html', **params)

@app.route('/bills')
def bills():
    """ list of Bills debated in parliament - UNDER CONSTRUCTION """
    sessions = session.query(Session).order_by(asc(Session.date)).all()
    params = dict()
    params['sessions'] = sessions

    if 'username' in login_session:
        # check if the current user is logged in
        params['logged_in']=True

    return render_template('bills.html', **params)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
