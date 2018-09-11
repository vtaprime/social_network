from django.shortcuts import render
import request
from django.http import HttpResponse, JsonResponse
from model import User, Reaction, Event, Session
from utils import check_password, get_client_ip, handle_uploaded_file
from serializers import serializer_event
import json
import uuid
import datetime

from django.conf import settings


def index(request):
    return HttpResponse('Welcome!!!')


def admin_login(request):
    data = request.body
    ip = get_client_ip(request)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_info = json.loads(data)

    user = User.objects.filter(username=user_info['username'])
    if len(user) > 0:
        user_pass = user_info['password']
        pass_hash = user[0].password
        user_session = User.objects.get(user_id=int(user[0].user_id))
        if check_password(user_pass, pass_hash):
            key = str(uuid.uuid4())
            if int(user[0].is_super_user) == 1:
                Session.objects.create(ip_adress=ip, user=user_session, last_login=now,
                                       login_status=1, session_value=key)
                response = HttpResponse("Authentication success!", status=200)
                response.set_cookie('session_id', key)
            else:
                response = HttpResponse("Authentication failed!", status=401)
        else:
            response = HttpResponse("Authentication failed!", status=401)
    else:
        response = HttpResponse("Authentication failed!", status=401)
    return response


def login(request):
    data = request.body
    ip = get_client_ip(request)
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
    if 'session_id' in request.COOKIES.keys():
        session_id = request.COOKIES.get('session_id')
        try:
            session = Session.objects.get(session_value=session_id)
            session.delete()
            response = HttpResponse('Logout success!', status=200)
        except Exception as e:
            response = HttpResponse('Logout failed!', status=401)
    return response


def get_events_list(request):
    events = Event.objects.all()
    dictionaries = [serializer_event(event) for event in events]
    return HttpResponse(json.dumps({"data": dictionaries}), content_type='application/json')


def search_event(request):
    params = request.GET
    print 'param'
    return HttpResponse()


def admin_upload(request):
    if 'session_id' in request.COOKIES.keys():
        session_id = request.COOKIES.get('session_id')
        try:
            session = Session.objects.get(session_value=session_id)
        except Exception as e:
            response = HttpResponse('Unauthorized!', status=401)
            return response
    data = request.POST
    images = request.FILES.getlist('file')
    desciption = data['description']
    date_took_place = data['time']
    location = data['location']
    title = data['title']
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    list_path = []
    path = './templates/images/'
    for f in images:
        image_path = handle_uploaded_file(f, path)
        list_path.append(image_path)

    user_id = session.user_id
    user = User.objects.get(user_id=int(user_id))

    Event.objects.create(title=title, desciption=desciption, photo=list_path, date_took_place=date_took_place,
                         location=location, user=user, time = time)
    response = HttpResponse('Upload success!', status=200)

    return response