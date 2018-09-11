from django.shortcuts import render
import request
from django.http import HttpResponse, JsonResponse
from models import User, Reaction, Event, Session, Participant, Comment
from utils import check_password, get_client_ip, handle_uploaded_file, serializer_event, serializer_comment
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
            if 'last_event' in request.COOKIES.keys():
                response.delete_cookie('last_event')
        except Exception as e:
            response = HttpResponse('Logout failed!', status=401)
    return response


def get_events_list(request):
    if 'session_id' in request.COOKIES.keys():
        session_id = request.COOKIES.get('session_id')
        try:
            Session.objects.get(session_value=session_id)
        except Exception as e:
            response = HttpResponse('Unauthorized!', status=401)
            return response
        now = datetime.datetime.now()
        time = now.strftime("%Y-%m-%d %H:%M:%S")
        if 'last_event' in request.COOKIES.keys():
            last_event_time = request.COOKIES.get('last_event')
            last_event_time = datetime.datetime.strptime(last_event_time, '%Y-%m-%d %H:%M:%S') - datetime.timedelta(seconds=1)
            last_event_time = last_event_time.strftime("%Y-%m-%d %H:%M:%S")
            events = Event.objects.filter(time__range=('',last_event_time)).order_by('-time')[0:5]
        else:
            events = Event.objects.filter(time__range=('', time)).order_by('-time')[0:5]

        dictionaries = [serializer_event(event) for event in events]
        if len(dictionaries) > 0:
            last_event_time = events[len(events) - 1].time
            response = HttpResponse(json.dumps({"data": dictionaries}), content_type='application/json', status=200)
            response.set_cookie('last_event', last_event_time)
        else:
            response = HttpResponse('No more events!', status=200)

        return response
    else:
        response = HttpResponse('Unauthorized!', status=401)
        return response


def search_event(request):
    params = request.GET
    print 'param', params['date']
    if 'session_id' in request.COOKIES.keys():
        session_id = request.COOKIES.get('session_id')
        try:
            Session.objects.get(session_value=session_id)
        except Exception as e:
            response = HttpResponse('Unauthorized!', status=401)
            return response
    start_time = params['start_time']
    end_time = params['end_time']
    hashtag = params['hashtag']

    events = Event.objects.filter(date_took_place__range=(start_time, end_time), hashtag=hashtag)
    dictionaries = [serializer_event(event) for event in events]
    if len(dictionaries>0):
        response = HttpResponse(json.dumps({"data": dictionaries}), content_type='application/json', status=200)
    else:
        response = HttpResponse('No events was found!', status=404)

    return response


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
    hashtag = data['hashtag']
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    list_path = []
    path = './templates/images/'
    for f in images:
        image_path = handle_uploaded_file(f, path)
        list_path.append(image_path)

    user_id = session.user_id
    user = User.objects.get(user_id=int(user_id))

    Event.objects.create(title=title, description=desciption, photo=list_path, date_took_place=date_took_place,
                         location=location, user=user, time = time, hashtag = hashtag)
    response = HttpResponse('Upload success!', status=200)

    return response


def join_event(request):
    if 'session_id' in request.COOKIES.keys():
        session_id = request.COOKIES.get('session_id')
        try:
            Session.objects.get(session_value=session_id)
        except Exception as e:
            response = HttpResponse('Unauthorized!', status=401)
            return response
    data = json.loads(request.body)
    user_id = data['user_id']
    event_id = data['event_id']

    if request.method == 'POST':
        try:
            Participant.objects.create(user=user_id, event=event_id)
            response = HttpResponse('Success', status=200)
        except Exception as e:
            response = HttpResponse('Join event failed')
            return response
    if request.method == 'UPDATE':
        try:
            user = Participant.objects.get(user=user_id, event=event_id)
            user.delete()
        except Exception as e:
            response = HttpResponse('Update fail!')
            return response
    return response


def reaction(request):
    if 'session_id' in request.COOKIES.keys():
        session_id = request.COOKIES.get('session_id')
        try:
            Session.objects.get(session_value=session_id)
        except Exception as e:
            response = HttpResponse('Unauthorized!', status=401)
            return response
    data = json.loads(request.body)
    user_id = data['user_id']
    event_id = data['event_id']

    user = User.objects.get(user_id=user_id)
    event = Event.objects.get(event_id=event_id)

    if request.method == 'POST':
        try:
            Reaction.objects.create(user=user, event=event)
            response = HttpResponse('Success', status=200)
        except Exception as e:
            response = HttpResponse('Like event failed')
            return response
    if request.method == 'UPDATE':
        try:
            user = Reaction.objects.get(user=user_id, event=event_id)
            user.delete()
        except Exception as e:
            response = HttpResponse('Update fail!')
            return response
    return response


def comment(request):
    if 'session_id' in request.COOKIES.keys():
        session_id = request.COOKIES.get('session_id')
        try:
            Session.objects.get(session_value=session_id)
        except Exception as e:
            response = HttpResponse('Unauthorized!', status=401)
            return response

    data = json.loads(request.body)
    user_id = data['user_id']
    event_id = data['event_id']
    content = data['content']
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")

    try:
        user = User.objects.get(user_id=user_id)
        event = Event.objects.get(event_id=event_id)
        Comment.objects.create(content=content, user=user, event=event, create_time=time)
        response = HttpResponse('Success', status=200)
    except Exception as e:
        response = HttpResponse('Comment fail', status=500)

    return response


def get_participant(request):
    if 'session_id' in request.COOKIES.keys():
        session_id = request.COOKIES.get('session_id')
        try:
            Session.objects.get(session_value=session_id)
        except Exception as e:
            response = HttpResponse('Unauthorized!', status=401)
            return response
    event_id = request.GET['event_id']
    event = Event.objects.get(event_id=event_id)
    participants = Participant.object.filter(event_id=event)
    users = []
    for participant in participants:
        user_id = participant.user_id
        user=User.objects.get(user_id=user_id)
        user_name=user.name
        users.append(user_name)
    response = HttpResponse(json.dumps({"data": users}), content_type='application/json', status=200)
    return response


def get_reaction(request):
    if 'session_id' in request.COOKIES.keys():
        session_id = request.COOKIES.get('session_id')
        try:
            Session.objects.get(session_value=session_id)
        except Exception as e:
            response = HttpResponse('Unauthorized!', status=401)
            return response
    event_id = request.GET['event_id']
    event = Event.objects.get(event_id=event_id)
    reactions = Reaction.object.filter(event_id=event)
    users = []
    for reaction in reactions:
        user_id = reaction.user_id
        user=User.objects.get(user_id=user_id)
        user_name=user.name
        users.append(user_name)
    response = HttpResponse(json.dumps({"data": users}), content_type='application/json', status=200)
    return response


def get_comment(request):
    if 'session_id' in request.COOKIES.keys():
        session_id = request.COOKIES.get('session_id')
        try:
            Session.objects.get(session_value=session_id)
        except Exception as e:
            response = HttpResponse('Unauthorized!', status=401)
            return response

    event_id = request.GET['event_id']
    event = Event.objects.get(event_id=event_id)
    comments = Comment.objects.filter(event_id=event)

    dictionaries = [serializer_comment(comment) for comment in comments]

    response = HttpResponse(json.dumps({"data": dictionaries}), content_type='application/json', status=200)

    return response