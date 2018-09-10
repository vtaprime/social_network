from django.shortcuts import render
import request
from django.http import HttpResponse, JsonResponse
from models import User, Reaction, Event, Session
from utils import check_password, get_client_ip
# Create your views here.
from serializers import serializer_event
import json
import uuid
import datetime


# def new_session(db):
#     """Make a new session key, store it in the db.
#     Add a cookie to the response with the session key and
#     return the new session key"""
#
#     # use the uuid library to make the random key
#
#     cur = db.cursor()
#     # store this new session key in the database with no likes in the value
#     cur.execute("INSERT INTO sessions VALUES (?)", (key,))
#     db.commit()
#
#     response.set_cookie(COOKIE_NAME, key)
#
#     return key
#
# def get_session(db):
#     """Get the current session key if any, if not, return None"""
#
#     key = request.get_cookie(COOKIE_NAME)
#
#     cur = db.cursor()
#     cur.execute("SELECT key FROM sessions WHERE key=?", (key,))
#
#     row = cur.fetchone()
#     if not row:
#         # no existing session so we create a new one
#         key = new_session(db)
#
#     return keyfrom models import User, Comment, Reaction, Event
from django.conf import settings


def check_log():
    pass

def index(request):
    return HttpResponse('Welcome!!!')

def login(request):
    data = request.body
    ip = get_client_ip(request)
    print 'ipppppppp', ip
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_info = json.loads(data)

    user = User.objects.filter(username=user_info['username'])
    if len(user) > 0:
        user_pass = user_info['password']
        pass_hash = user[0].password
        user_session = User.objects.get(user_id=int(user[0].user_id))
        if check_password(user_pass, pass_hash):
            key = str(uuid.uuid4())
            Session.objects.create(ip_adress=ip, user=user_session, last_login = now,
                                       login_status = 1, session_value=key)
            response = HttpResponse("Authentication success!", status=200)
            response.set_cookie(key='session_id', value=key)
        else:
            response = HttpResponse("Authentication failed!", status=401)
    else:
        response = HttpResponse("Authentication failed!", status=401)
    return response

def logout(request):
    pass

def get_events_list(request):
    events = Event.objects.all()
    dictionaries = [serializer_event(event) for event in events]
    return HttpResponse(json.dumps({"data": dictionaries}), content_type='application/json')

def search_event(request):
    params = request.GET
    print 'param',
    return HttpResponse()