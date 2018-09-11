import bcrypt


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


def handle_uploaded_file(f, path):
    with open(path + f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return path+f.name.encode('utf-8')


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