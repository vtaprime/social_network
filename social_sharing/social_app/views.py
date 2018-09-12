from django.shortcuts import render
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
    if request.method=="POST":
        data = request.body
    else:
        return HttpResponse('Require POST method', status=405)
    ip = get_client_ip(request)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        user_info = json.loads(data)
        username = user_info['username']
        password = user_info['password']
    except Exception as e:
        return HttpResponse('Data format was wrong!', status=400)

    user = User.objects.filter(username=username)
    if len(user) > 0:
        user_pass = password
        pass_hash = user[0].password
        user_session = User.objects.get(user_id=int(user[0].user_id))
        if check_password(user_pass, pass_hash):
            key = str(uuid.uuid4())
            if int(user[0].is_super_user) == 1:
                Session.objects.create(ip_adress=ip, user=user_session, last_login=now,
                                       login_status=1, session_value=key)
                response = HttpResponse("Authentication successed!", status=200)
                response.set_cookie('session_id', key)
            else:
                response = HttpResponse("Authentication failed!", status=404)
        else:
            response = HttpResponse("Authentication failed!", status=404)
    else:
        response = HttpResponse("Authentication failed!", status=404)
    return response


def login(request):
    if request.method=="POST":
        data = request.body
    else:
        return HttpResponse('Require POST method', status=405)
    ip = get_client_ip(request)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        user_info = json.loads(data)
        username = user_info['username']
        password = user_info['password']
    except Exception as e:
        return HttpResponse('Data format was wrong!', status=400)

    user = User.objects.filter(username=username)
    if len(user) > 0:
        user_pass = password
        pass_hash = user[0].password
        user_session = User.objects.get(user_id=int(user[0].user_id))
        if check_password(user_pass, pass_hash):
            key = str(uuid.uuid4())
            Session.objects.create(ip_adress=ip, user=user_session, last_login = now,
                                       login_status = 1, session_value=key)
            response = HttpResponse("Authentication successed!", status=200)
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
            response = HttpResponse('Logout successed!', status=200)
        except Exception as e:
            response = HttpResponse('Logout failed!', status=404)
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
        if request.method == "GET":
            if "last_event" in request.GET:
                last_event_time = request.GET['last_event']
                last_event_time = datetime.datetime.strptime(last_event_time, '%Y-%m-%d %H:%M:%S') - \
                                  datetime.timedelta(seconds=1)
                last_event_time = last_event_time.strftime("%Y-%m-%d %H:%M:%S")
                events = Event.objects.filter(time__range=('',last_event_time)).order_by('-time')[0:5]
            else:
                events = Event.objects.filter(time__range=('', time)).order_by('-time')[0:5]

        dictionaries = [serializer_event(event) for event in events]

        if len(dictionaries) > 0:
            last_event_time = events[len(events) - 1].time
            next_url = "http://localhost:8000/social_app/api/events_list/?last_event=" + last_event_time
            response = HttpResponse(json.dumps({"data": dictionaries, "next": next_url}),
                                    content_type='application/json', status=200)
        else:
            response = HttpResponse('No more events!', status=200)

        return response
    else:
        response = HttpResponse('Unauthorized!', status=401)
        return response


def search_event(request):
    params = request.GET
    if 'session_id' in request.COOKIES.keys():
        session_id = request.COOKIES.get('session_id')
        try:
            Session.objects.get(session_value=session_id)
        except Exception as e:
            response = HttpResponse('Unauthorized!', status=401)
            return response
    try:
        start_time = params['start_time']
        end_time = params['end_time']
        hashtag = params['hashtag']
    except Exception as e:
        return HttpResponse('Data format was wrong!', status=400)

    events = Event.objects.filter(date_took_place__range=(start_time, end_time), hashtag=hashtag)
    dictionaries = [serializer_event(event) for event in events]
    if len(dictionaries) > 0:
        response = HttpResponse(json.dumps({"data": dictionaries}), content_type='application/json', status=200)
    else:
        response = HttpResponse('No event was found!', status=404)

    return response


def admin_upload(request):
    if 'session_id' in request.COOKIES.keys():
        session_id = request.COOKIES.get('session_id')
        try:
            session = Session.objects.get(session_value=session_id)
        except Exception as e:
            response = HttpResponse('Unauthorized!', status=401)
            return response
    if request.method=="POST":
        try:
            data = request.POST
            images = request.FILES.getlist('file')
            desciption = data['description']
            date_took_place = data['time']
            location = data['location']
            title = data['title']
            hashtag = data['hashtag']
        except Exception as e:
            return HttpResponse('Data format was wrong!', status=400)
    else:
        return HttpResponse('Require POST method', status=405)

    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    list_path = []
    path = './media/images/'
    for f in images:
        image_path = handle_uploaded_file(f, path)
        list_path.append(image_path)

    user_id = session.user_id
    user = User.objects.get(user_id=int(user_id))

    Event.objects.create(title=title, description=desciption, photo=list_path, date_took_place=date_took_place,
                         location=location, user=user, time = time, hashtag = hashtag)
    response = HttpResponse('Upload successed!', status=201)

    return response


def join_event(request):
    if 'session_id' in request.COOKIES.keys():
        session_id = request.COOKIES.get('session_id')
        try:
            Session.objects.get(session_value=session_id)
        except Exception as e:
            response = HttpResponse('Unauthorized!', status=401)
            return response

    if request.method == "POST" or request.method == "PUT":
        try:
            data = json.loads(request.body)
            user_id = data['user_id']
            event_id = data['event_id']
        except Exception as e:
            return HttpResponse('Data format was wrong!', status=400)
    else:
        return HttpResponse('Require POST or PUT method', status=405)

    user = User.objects.get(user_id=user_id)
    event = Event.objects.get(event_id=event_id)

    if request.method == 'POST':
        try:
            Participant.objects.create(user=user, event=event)
            response = HttpResponse('Join event successed!', status=200)
        except Exception as e:
            response = HttpResponse('Join event failed')
            return response
    if request.method == 'PUT':
        try:
            user = Participant.objects.get(user=user_id, event=event_id)
            user.delete()
            response = HttpResponse('Update successed!', status=201)
        except Exception as e:
            response = HttpResponse('Update failed!')
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
    if request.method == "POST" or request.method == "PUT":
        try:
            data = json.loads(request.body)
            user_id = data['user_id']
            event_id = data['event_id']
        except Exception as e:
            return HttpResponse('Data format was wrong!', status=400)
    else:
        return HttpResponse('Require POST or PUT method', status=405)

    user = User.objects.get(user_id=user_id)
    event = Event.objects.get(event_id=event_id)

    if request.method == 'POST':
        try:
            Reaction.objects.create(user=user, event=event)
            response = HttpResponse('Like event successed', status=200)
        except Exception as e:
            response = HttpResponse('Like event failed')
            return response
    if request.method == 'PUT':
        try:
            user = Reaction.objects.get(user=user_id, event=event_id)
            user.delete()
            response = HttpResponse('Success update!', status=200)
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
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = data['user_id']
            event_id = data['event_id']
            content = data['content']
        except Exception as e:
            return HttpResponse('Data format was wrong!', status=400)
    else:
        return HttpResponse('Require POST method', status=405)

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
    if request.method == "GET":
        event_id = request.GET['event_id']
    else:
        return HttpResponse('Require GET method', status=405)
    event = Event.objects.get(event_id=event_id)
    participants = Participant.objects.filter(event_id=event)
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
    if request.method == "GET":
        event_id = request.GET['event_id']
    else:
        return HttpResponse('Require GET method', status=405)

    event = Event.objects.get(event_id=event_id)
    reactions = Reaction.objects.filter(event_id=event)
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

    if request.method == "GET":
        event_id = request.GET['event_id']
    else:
        return HttpResponse('Require GET method', status=405)

    event = Event.objects.get(event_id=event_id)
    comments = Comment.objects.filter(event_id=event)

    dictionaries = [serializer_comment(comment) for comment in comments]

    response = HttpResponse(json.dumps({"data": dictionaries}), content_type='application/json', status=200)

    return response