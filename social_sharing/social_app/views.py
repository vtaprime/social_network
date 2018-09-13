from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from models import User, Reaction, Event, Session, Participant, Comment
from utils import check_password, get_client_ip, handle_uploaded_file, serializer_event, serializer_comment
import json
import uuid
import datetime
import time

from django.conf import settings


def index(request):
    return HttpResponse('Welcome!!!')


def admin_login(request):
    if request.method=="POST":
        data = request.body
    else:
        return HttpResponse(json.dumps({"error": "Require POST method"}), status=405)
    ip = get_client_ip(request)
    now = datetime.datetime.now()
    last_login = int(time.mktime(now.timetuple()))

    try:
        user_info = json.loads(data)
        username = user_info['username']
        password = user_info['password']
    except Exception as e:
        return HttpResponse(json.dumps({"error": "Data format was wrong!"}), status=400)

    user = User.objects.filter(username=username)
    if len(user) > 0:
        user_pass = password
        pass_hash = user[0].password
        user_session = User.objects.get(user_id=int(user[0].user_id))
        if check_password(user_pass, pass_hash):
            key = str(uuid.uuid4())
            if int(user[0].is_super_user) == 1:
                Session.objects.create(ip_adress=ip, user=user_session, last_login=last_login,
                                       login_status=1, session_value=key)
                response = HttpResponse(json.dumps({"success": "Authentication successed!"}), status=200)
                print 'kyeeee', key
                response.set_cookie('session_id', key)
            else:
                response = HttpResponse(json.dumps({"error": "Authentication failed!"}), status=404)
        else:
            response = HttpResponse(json.dumps({"error": "Authentication failed!"}), status=404)
    else:
        response = HttpResponse(json.dumps({"error": "Authentication failed!"}), status=404)
    return response


def login(request):
    if request.method=="POST":
        data = request.body
    else:
        return HttpResponse(json.dumps({"error": "Require POST method"}), status=405)
    ip = get_client_ip(request)
    now = datetime.datetime.now()
    last_login = int(time.mktime(now.timetuple()))
    try:
        user_info = json.loads(data)
        username = user_info['username']
        password = user_info['password']
    except Exception as e:
        return HttpResponse(json.dumps({"error": "Data format was wrong!"}), status=400)

    user = User.objects.filter(username=username)
    if len(user) > 0:
        user_pass = password
        pass_hash = user[0].password
        user_session = User.objects.get(user_id=int(user[0].user_id))
        if check_password(user_pass, pass_hash):
            key = str(uuid.uuid4())
            Session.objects.create(ip_adress=ip, user=user_session, last_login = last_login,
                                       login_status = 1, session_value=key)
            response = HttpResponse(json.dumps({"success": "Authentication successed!"}), status=200)
            response.set_cookie(key='session_id', value=key)
        else:
            response = HttpResponse(json.dumps({"error": "Authentication failed!"}), status=401)
    else:
        response = HttpResponse(json.dumps({"error": "Authentication failed!"}), status=401)

    return response


def logout(request):
    if 'session_id' in request.COOKIES.keys():
        session_id = request.COOKIES.get('session_id')
        try:
            session = Session.objects.get(session_value=session_id)
            session.delete()
            response = HttpResponse(json.dumps({"success": "Logout successed!"}), status=200)
        except Exception as e:
            response = HttpResponse(json.dumps({"error": "Logout failed!"}), status=404)
    else:
        return HttpResponse(json.dumps({"error": "Unauthorized!"}), status=401)
    return response


def get_events_list(request):
    if 'session_id' in request.COOKIES.keys():
        session_id = request.COOKIES.get('session_id')
        try:
            Session.objects.get(session_value=session_id)
        except Exception as e:
            response = HttpResponse(json.dumps({"error": "Unauthorized!"}), status=401)
            return response
        now = datetime.datetime.now()
        now_second = int(time.mktime(now.timetuple()))
        if request.method == "GET":
            if "last_event" in request.GET:
                last_event_time = request.GET['last_event']
                last_event_time = int(last_event_time) - 1

                events = Event.objects.filter(time__range=('',last_event_time)).order_by('-time')[0:5]
            else:
                events = Event.objects.filter(time__range=('', now_second)).order_by('-time')[0:5]

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
        response = HttpResponse(json.dumps({"error": "Unauthorized!"}), status=401)
        return response


def get_event_details(request):
    params = request.GET
    if 'session_id' in request.COOKIES.keys():
        session_id = request.COOKIES.get('session_id')
        try:
            Session.objects.get(session_value=session_id)
        except Exception as e:
            response = HttpResponse(json.dumps({"error": "Unauthorized!"}), status=401)
            return response
    else:
        return HttpResponse(json.dumps({"error": "Unauthorized!"}), status=401)
    try:
        event_id = params['event_id']
    except Exception as e:
        return HttpResponse('Data format was wrong!', status=400)

    try:
        event = Event.objects.get(event_id=event_id)
        event = serializer_event(event)

        response = HttpResponse(json.dumps({"data": event}), content_type='application/json', status=200)
    except Exception as e:
        response = HttpResponse(json.dumps({"error": "No event was found!"}), status=404)

    return response


def search_event(request):
    params = request.GET
    if 'session_id' in request.COOKIES.keys():
        session_id = request.COOKIES.get('session_id')
        try:
            Session.objects.get(session_value=session_id)
        except Exception as e:
            response = HttpResponse(json.dumps({"error": "Unauthorized!"}), status=401)
            return response
    else:
        return HttpResponse(json.dumps({"error": "Unauthorized!"}), status=401)
    try:
        start_time = params['start_time']
        end_time = params['end_time']
        hashtag = params['hashtag']
    except Exception as e:
        return HttpResponse(json.dumps({"error": "Data format was wrong!"}), status=400)

    events = Event.objects.filter(date_took_place__range=(start_time, end_time), hashtag=hashtag)
    dictionaries = [serializer_event(event) for event in events]
    if len(dictionaries) > 0:
        response = HttpResponse(json.dumps({"data": dictionaries}), content_type='application/json', status=200)
    else:
        response = HttpResponse(json.dumps({"error": "No event was found!"}), status=404)

    return response


def admin_upload(request):
    print 'iii', request.COOKIES.get('session_id')
    if 'session_id' in request.COOKIES.keys():
        session_id = request.COOKIES.get('session_id')
        try:
            print 'sesss', session_id
            session = Session.objects.get(session_value=session_id)
        except Exception as e:
            response = HttpResponse(json.dumps({"error": "Unauthorized!"}), status=401)
            return response
    else:
        return HttpResponse(json.dumps({"error": "Unauthorized!"}), status=401)
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
            return HttpResponse(json.dumps({"error": "Data format was wrong!"}), status=400)
    else:
        return HttpResponse(json.dumps({"error": "Require POST method"}), status=405)

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
            response = HttpResponse(json.dumps({"error": "Unauthorized!"}), status=401)
            return response
    else:
        return HttpResponse(json.dumps({"error": "Unauthorized!"}), status=401)

    if request.method == "POST" or request.method == "PUT":
        try:
            data = json.loads(request.body)
            user_id = data['user_id']
            event_id = data['event_id']
        except Exception as e:
            return HttpResponse(json.dumps({"error": "Data format was wrong!"}), status=400)
    else:
        return HttpResponse(json.dumps({"error": "Require POST or PUT method"}), status=405)

    user = User.objects.get(user_id=user_id)
    event = Event.objects.get(event_id=event_id)

    if request.method == 'POST':
        try:
            Participant.objects.create(user=user, event=event)
            response = HttpResponse(json.dumps({"error": "Join event successed!"}), status=200)
        except Exception as e:
            response = HttpResponse(json.dumps({"error": "Join event failed"}), status=500)
            return response
    if request.method == 'PUT':
        try:
            user = Participant.objects.get(user=user_id, event=event_id)
            user.delete()
            response = HttpResponse(json.dumps({"success": "Update successed!"}), status=201)
        except Exception as e:
            response = HttpResponse(json.dumps({"error": "Update failed!"}), status=500)
            return response
    return response


def reaction(request):
    if 'session_id' in request.COOKIES.keys():
        session_id = request.COOKIES.get('session_id')
        try:
            Session.objects.get(session_value=session_id)
        except Exception as e:
            response = HttpResponse(json.dumps({"error": "Unauthorized!"}), status=401)
            return response
    else:
        return HttpResponse(json.dumps({"error": "Unauthorized!"}), status=401)
    if request.method == "POST" or request.method == "PUT":
        try:
            data = json.loads(request.body)
            user_id = data['user_id']
            event_id = data['event_id']
        except Exception as e:
            return HttpResponse(json.dumps({"error": "Data format was wrong!"}), status=400)
    else:
        return HttpResponse(json.dumps({"error": "Require POST or PUT method"}), status=405)

    user = User.objects.get(user_id=user_id)
    event = Event.objects.get(event_id=event_id)

    if request.method == 'POST':
        try:
            Reaction.objects.create(user=user, event=event)
            response = HttpResponse(json.dumps({"success": "Like event successed"}), status=200)
        except Exception as e:
            response = HttpResponse(json.dumps({"error": "Like event failed"}), status=500)
            return response
    if request.method == 'PUT':
        try:
            user = Reaction.objects.get(user=user_id, event=event_id)
            user.delete()
            response = HttpResponse(json.dumps({"success": "Success update!"}), status=200)
        except Exception as e:
            response = HttpResponse(json.dumps({"error": "Update fail!"}), status=500)
            return response
    return response


def comment(request):
    if 'session_id' in request.COOKIES.keys():
        session_id = request.COOKIES.get('session_id')
        try:
            Session.objects.get(session_value=session_id)
        except Exception as e:
            response = HttpResponse(json.dumps({"error": "Unauthorized!"}), status=401)
            return response
    else:
        return HttpResponse(json.dumps({"error": "Unauthorized!"}), status=401)
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = data['user_id']
            event_id = data['event_id']
            content = data['content']
        except Exception as e:
            return HttpResponse(json.dumps({"error": "Data format was wrong!"}), status=400)
    else:
        return HttpResponse(json.dumps({"error": "Require POST method"}), status=405)

    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")

    try:
        user = User.objects.get(user_id=user_id)
        event = Event.objects.get(event_id=event_id)
        Comment.objects.create(content=content, user=user, event=event, create_time=time)
        response = HttpResponse(json.dumps({"success": "comment success"}), status=200)
    except Exception as e:
        response = HttpResponse(json.dumps({"error": "Comment fail"}), status=500)

    return response


def get_participant(request):
    if 'session_id' in request.COOKIES.keys():
        session_id = request.COOKIES.get('session_id')
        try:
            Session.objects.get(session_value=session_id)
        except Exception as e:
            response = HttpResponse(json.dumps({"error": "Unauthorized!"}), status=401)
            return response
    else:
        return HttpResponse(json.dumps({"error": "Unauthorized!"}), status=401)
    if request.method == "GET":
        try:
            event_id = request.GET['event_id']
        except Exception as e:
            return HttpResponse(json.dumps({"error": "Data format was wrong!"}), status=400)
    else:
        return HttpResponse(json.dumps({"error": "Require GET method"}), status=405)
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
            response = HttpResponse(json.dumps({"error": "Unauthorized!"}), status=401)
            return response
    else:
        return HttpResponse(json.dumps({"error": "Unauthorized!"}), status=401)
    if request.method == "GET":
        try:
            event_id = request.GET['event_id']
        except Exception as e:
            return HttpResponse(json.dumps({"error": "Data format was wrong!"}), status=400)
    else:
        return HttpResponse(json.dumps({"error": "Require GET method"}), status=405)

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
            response = HttpResponse(json.dumps({"error": "Unauthorized!"}), status=401)
            return response
    else:
        return HttpResponse(json.dumps({"error": "Unauthorized!"}), status=401)

    if request.method == "GET":
        try:
            event_id = request.GET['event_id']
        except Exception as e:
            return HttpResponse(json.dumps({"error": "Data format was wrong!"}), status=400)
    else:
        return HttpResponse(json.dumps({"error": "Require GET method"}), status=405)

    event = Event.objects.get(event_id=event_id)
    comments = Comment.objects.filter(event_id=event)

    dictionaries = [serializer_comment(comment) for comment in comments]

    response = HttpResponse(json.dumps({"data": dictionaries}), content_type='application/json', status=200)

    return response