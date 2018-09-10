from django.shortcuts import render
import request
from django.http import HttpResponse, JsonResponse
from models import User, Reaction, Event, Session
from utils import check_password, get_client_ip, handle_uploaded_file
from serializers import serializer_event
import json
import uuid
import datetime

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
    print 'param'
    return HttpResponse()

def admin_upload(request):
    print 'abc', request.POST
    data = request.POST
    images = request.FILES.getlist('file')
    desciption = data['description']
    time = data['time']
    location = data['location']
    title = data['title']
    list_path = []
    path = './templates/images/'
    for f in images:
        image_path = handle_uploaded_file(f, path)
        list_path.push(image_path)
    session_id = request.COOKIES.get('session_id')
    user_id = Session.objects.get(session_value=session_id).user_id
    user = User.objects.get(user_id=int(user_id))
    Event.objects.create(title=title, desciption=desciption, photo=list_path, date=time,
                         location=location, user=user)
    return HttpResponse('Upload success!', status=200)