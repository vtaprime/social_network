import bcrypt
from social_app.models import Session
from django.http import HttpResponse
import json
import uuid
import datetime
import mimetypes
import magic
import os


def get_hashed_password(plain_text_password):
    # Hash a password for the first time
    #   (Using bcrypt, the salt is saved into the hash itself)
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())


def check_password(plain_text_password, hashed_password):
    # Check hased password. Useing bcrypt, the salt is saved into the hash itself
    return bcrypt.checkpw(plain_text_password.encode('utf8'), hashed_password.encode('utf8'))


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def check_in_memory_mime(in_memory_file):
    mime = magic.from_buffer(in_memory_file.read(), mime=True)
    return mime


def handle_uploaded_file(f, path):
    file_mime = check_in_memory_mime(f)
    if 'image' in file_mime:
        type = file_mime.split('/')[-1]
        date = datetime.datetime.now()
        dir = "{0:%Y_%j}".format(date)
        path = path + dir
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError as error:
                if error.errno != errno.EEXIST:
                    raise

        uid = uuid.uuid1()
        path = path + '/' + str(uid) + '.' + type

        with open(path, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        return path
    else:
        return None


def serializer_event(event):
    return {
        "event_id": event.event_id,
        "tile": event.title,
        "description": event.description,
        "photo": event.photo,
        "date_took_place": event.date_took_place,
        "location": event.location,
        "user_id": event.user_id,
        "time": event.time,
        "hashtag": event.hashtag
    }


def serializer_comment(comment):
    return {
        "comment_id": comment.comment_id,
        "content": comment.content,
        "event_id": comment.event_id,
        "user_id": comment.user_id,
        "create_time": comment.create_time
    }


def login_require(f):
    def wrapper(request):
        if 'session_id' in request.COOKIES.keys():
            session_id = request.COOKIES.get('session_id')
            try:
                Session.session_objects.get_session(session_value=session_id)
            except Exception as e:
                response = HttpResponse(json.dumps({"error": "Unauthorized!"}), status=401)
                return response
            return f(request)
        else:
            response = HttpResponse(json.dumps({"error": "Unauthorized!"}), status=401)
            return response
    return wrapper
