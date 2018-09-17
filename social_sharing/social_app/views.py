from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from models import User, Reaction, Event, Session, Participant, Comment
from forms import EventForm
from utils.utils import check_password, get_client_ip, handle_uploaded_file, serializer_event, serializer_comment,\
    login_require
import json
import uuid
import datetime
import time
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.conf import settings

from utils.logger import Logger
logger = Logger().logger


def index(request):
    return HttpResponse('Welcome!!!')


@require_http_methods(["POST"])
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
        logger.error('Error when loading user info: {}'.format(e))
        return HttpResponse(json.dumps({"error": "Data format was wrong!"}), status=400)

    try:
        user = User.user_objects.get_user(username=username)
    except Exception as e:
        logger.error('Error when get user {}'.formar(e))
        response = HttpResponse(json.dumps({"error": "Authentication failed!"}), status=404)
        return response
    user_pass = password
    pass_hash = user.password
    user_session = User.user_objects.get_user(user_id=int(user.user_id))
    if check_password(user_pass, pass_hash):
        key = str(uuid.uuid4())
        if int(user.is_super_user) == 1:
            Session.session_objects.create_session(ip_adress=ip, user=user_session, last_login=last_login,
                                   login_status=1, session_value=key)
            response = HttpResponse(json.dumps({"success": "Authentication successed!"}), status=200)
            response.set_cookie('session_id', key)
        else:
            response = HttpResponse(json.dumps({"error": "Authentication failed!"}), status=404)
    else:
        response = HttpResponse(json.dumps({"error": "Authentication failed!"}), status=404)

    return response


@require_http_methods(["POST"])
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
        logger.error('Error when loading user info: {}'.format(e))
        return HttpResponse(json.dumps({"error": "Data format was wrong!"}), status=400)

    try:
        user = User.user_objects.get_user(username=username)
    except Exception as e:
        logger.error('Error when get user {}'.formar(e))
        response = HttpResponse(json.dumps({"error": "Authentication failed!"}), status=404)
        return response
    user_pass = password
    pass_hash = user.password
    user_session = User.user_objects.get_user(user_id=int(user.user_id))
    if check_password(user_pass, pass_hash):
        key = str(uuid.uuid4())
        Session.session_objects.create_session(ip_adress=ip, user=user_session, last_login=last_login,
                                               login_status=1, session_value=key)
        response = HttpResponse(json.dumps({"success": "Authentication successed!"}), status=200)
        response.set_cookie('session_id', key)
    else:
        response = HttpResponse(json.dumps({"error": "Authentication failed!"}), status=404)

    return response


@require_http_methods(["GET", "POST"])
def logout(request):
    if 'session_id' in request.COOKIES.keys():
        session_id = request.COOKIES.get('session_id')
        try:
            session = Session.session_objects.get_session(session_value=session_id)
            session.delete()
            response = HttpResponse(json.dumps({"success": "Logout successed!"}), status=200)
        except Exception as e:
            logger.error("Error when check session {}".format(e))
            response = HttpResponse(json.dumps({"error": "Logout failed!"}), status=404)
    else:
        return HttpResponse(json.dumps({"error": "Unauthorized!"}), status=401)
    return response


@require_http_methods(["GET"])
@login_require
def get_events_list(request):
    cache_key = 'events_list'
    cache_time = 1800  # time to live in seconds

    if request.method == "GET":
        if "last_event" in request.GET:
            cache_key = cache_key + '_' + request.GET['last_event']
            events = cache.get(cache_key)
            if not events:
                print 'no 1'
                last_event_time = request.GET['last_event']
                last_event_time = int(last_event_time) - 1
                events = Event.event_objects.filter_time_range(0, last_event_time)
                cache_key = cache_key + str(last_event_time)
                cache.set(cache_key, events, cache_time)
        else:
            events = cache.get(cache_key)
            if not events:
                print 'no 2'
                now = datetime.datetime.now()
                now_second = int(time.mktime(now.timetuple()))
                events = Event.event_objects.filter_time_range(0, now_second)
                cache.set(cache_key, events, cache_time)
    else:
        return HttpResponse(json.dumps({"error": "Require GET method"}), status=405)

    dictionaries = [serializer_event(event) for event in events]
    logger.info('Number of events: {}'.format(len(dictionaries)))

    if len(dictionaries) > 0:
        last_event_time = events[len(events) - 1].time
        next_url = "http://localhost:8000/social_app/api/events_list/?last_event=" + str(last_event_time)
        response = HttpResponse(json.dumps({"data": dictionaries, "next": next_url}),
                                content_type='application/json', status=200)
    else:
        response = HttpResponse('No more events!', status=200)

    return response


@require_http_methods(["GET"])
@login_require
def get_event_details(request):
    try:
        params = request.GET
        event_id = params['event_id']
    except Exception as e:
        logger.error('Error when get event_id {}'.formar(e))
        return HttpResponse('Data format was wrong!', status=400)

    try:
        event = Event.event_objects.get_event_details(event_id=event_id)
        event = serializer_event(event)
        logger.info('Get event {} success'.format(event_id))
        response = HttpResponse(json.dumps({"data": event}), content_type='application/json', status=200)
    except Exception as e:
        logger.error("Error when get event {}: {}".format(event_id, e))
        response = HttpResponse(json.dumps({"error": "No event was found!"}), status=404)

    return response


@require_http_methods(["GET"])
@login_require
def search_event(request):
    try:
        params = request.GET
        start_time = params['start_time']
        end_time = params['end_time']
        hashtag = params['hashtag']
    except Exception as e:
        logger.error('Error when search event: {}'.format(e))
        return HttpResponse(json.dumps({"error": "Data format was wrong!"}), status=400)

    events = Event.event_objects.search_event(start_time, end_time, hashtag)
    dictionaries = [serializer_event(event) for event in events]
    logger.info('Number of events: {}'.format(e))
    if len(dictionaries) > 0:
        response = HttpResponse(json.dumps({"data": dictionaries}), content_type='application/json', status=200)
    else:
        response = HttpResponse(json.dumps({"error": "No event was found!"}), status=404)

    return response


@require_http_methods(["POST"])
@login_require
def admin_upload(request):
    if request.method=="POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                data = request.POST
                images = request.FILES.getlist('file')
                description = data['description']
                date_took_place = data['time']
                location = data['location']
                title = data['title']
                hashtag = data['hashtag']
                user_name = data['username']
            except Exception as e:
                logger.error('Error when upload event: {}'.format(e))
                return HttpResponse(json.dumps({"error": "Data format was wrong!"}), status=400)
        else:
            return HttpResponse(json.dumps({"error": "Data format was wrong!"}), status=400)
    else:
        return HttpResponse(json.dumps({"error": "Require POST method"}), status=405)

    now = datetime.datetime.now()
    create_time = int(time.mktime(now.timetuple()))

    list_path = []
    path = './media/images/'
    for f in images:
        image_path = handle_uploaded_file(f, path)
        list_path.append(image_path)

    user = User.user_objects.get_user(username=user_name)

    Event.event_objects.create_event(title=title, description=description, photo=list_path, date_took_place=date_took_place,
                         location=location, user=user, time=create_time, hashtag=hashtag)

    response = HttpResponse('Upload successed!', status=201)

    return response


@require_http_methods(["POST", "PUT"])
@login_require
def join_event(request):
    if request.method == 'POST' or request.method == 'PUT':
        try:
            data = json.loads(request.body)
            user_id = data['user_id']
            event_id = data['event_id']
        except Exception as e:
            logger.error('Error when join event: {}'.format(e))
            return HttpResponse(json.dumps({"error": "Data format was wrong!"}), status=400)
    else:
        return HttpResponse(json.dumps({"error": "Require POST or PUT method"}), status=405)

    user = User.user_objects.get_user(user_id=user_id)
    event = Event.event_objects.get_event_details(event_id=event_id)

    if request.method == 'POST':
        try:
            Participant.participant_objects.create_participant(user=user, event=event)
            response = HttpResponse(json.dumps({"error": "Join event successed!"}), status=200)

        except Exception as e:
            response = HttpResponse(json.dumps({"error": "Join event failed"}), status=500)
        return response
    elif request.method == 'PUT':
        try:
            Participant.participant_objects.delete_participant(user=user, event=event)
            response = HttpResponse(json.dumps({"success": "Update successed!"}), status=201)
        except Exception as e:
            response = HttpResponse(json.dumps({"error": "Update failed!"}), status=500)
        return response


@require_http_methods(["POST", "PUT"])
@login_require
def reaction(request):
    if request.method == 'POST' or request.method == 'PUT':
        try:
            data = json.loads(request.body)
            user_id = data['user_id']
            event_id = data['event_id']
        except Exception as e:
            logger.error('Error when reaction event: {}'.format(e))
            return HttpResponse(json.dumps({"error": "Data format was wrong!"}), status=400)
    else:
        return HttpResponse(json.dumps({"error": "Require POST or PUT method"}), status=405)

    user = User.user_objects.get_user(user_id=user_id)
    event = Event.event_objects.get_event_details(event_id=event_id)

    if request.method == 'POST':
        try:
            Reaction.reaction_objects.create_reaction(user=user, event=event)
            response = HttpResponse(json.dumps({"success": "Like event successed"}), status=200)
        except Exception as e:
            response = HttpResponse(json.dumps({"error": "Like event failed"}), status=500)
        return response
    if request.method == 'PUT':
        try:
            Reaction.reaction_objects.delete_reaction(user=user, event=event)
            response = HttpResponse(json.dumps({"success": "Success update!"}), status=200)
        except Exception as e:
            response = HttpResponse(json.dumps({"error": "Update fail!"}), status=500)
        return response


@require_http_methods(["POST", "PUT"])
@login_require
def comment(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = data['user_id']
            event_id = data['event_id']
            content = data['content']
        except Exception as e:
            logger.error('Error when comment event: {}'.format(e))
            return HttpResponse(json.dumps({"error": "Data format was wrong!"}), status=400)
    else:
        return HttpResponse(json.dumps({"error": "Require POST method"}), status=405)

    now = datetime.datetime.now()
    create_time = int(time.mktime(now.timetuple()))

    try:
        user = User.user_objects.get_user(user_id=user_id)
        event = Event.event_objects.get_event_details(event_id=event_id)
        Comment.comment_objects.create_comment(content=content, user=user, event=event, create_time=create_time)
        response = HttpResponse(json.dumps({"success": "comment success"}), status=200)
    except Exception as e:
        print e
        response = HttpResponse(json.dumps({"error": "Comment fail"}), status=500)

    return response


@require_http_methods(["GET"])
@login_require
def get_participant(request):
    if request.method == "GET":
        try:
            event_id = request.GET['event_id']
        except Exception as e:
            logger.error('Error when get participants of event: {}'.format(e))
            return HttpResponse(json.dumps({"error": "Data format was wrong!"}), status=400)
    else:
        return HttpResponse(json.dumps({"error": "Require GET method"}), status=405)
    event = Event.event_objects.get_event_details(event_id=event_id)
    participants = Participant.participant_objects.filter_by_event(event=event)
    logger.info('Number of participants: {}'.format(e))
    users = []
    for participant in participants:
        user_id = participant.user_id
        user=User.user_objects.get_user(user_id=user_id)
        user_name=user.name
        users.append(user_name)
    response = HttpResponse(json.dumps({"data": users}), content_type='application/json', status=200)
    return response


@require_http_methods(["GET"])
@login_require
def get_reaction(request):
    if request.method == "GET":
        try:
            event_id = request.GET['event_id']
        except Exception as e:
            logger.error('Error when get reactions of event: {}'.format(e))
            return HttpResponse(json.dumps({"error": "Data format was wrong!"}), status=400)
    else:
        return HttpResponse(json.dumps({"error": "Require GET method"}), status=405)

    event = Event.event_objects.get_event_details(event_id=event_id)
    reactions = Reaction.reaction_objects.filter_by_event(event=event)
    logger.info('Number of reactions: {}'.format(e))
    users = []
    for reaction in reactions:
        user_id = reaction.user_id
        user=User.user_objects.get_user(user_id=user_id)
        user_name=user.name
        users.append(user_name)
    response = HttpResponse(json.dumps({"data": users}), content_type='application/json', status=200)
    return response


@require_http_methods(["GET"])
@login_require
def get_comment(request):
    if request.method == "GET":
        try:
            event_id = request.GET['event_id']
        except Exception as e:
            logger.error('Error when get comments of event: {}'.format(e))
            return HttpResponse(json.dumps({"error": "Data format was wrong!"}), status=400)
    else:
        return HttpResponse(json.dumps({"error": "Require GET method"}), status=405)

    event = Event.event_objects.get_event_details(event_id=event_id)
    comments = Comment.comment_objects.filter_by_event(event=event)

    dictionaries = [serializer_comment(comment) for comment in comments]
    logger.info('Number of comments: {}'.format(e))
    response = HttpResponse(json.dumps({"data": dictionaries}), content_type='application/json', status=200)

    return response