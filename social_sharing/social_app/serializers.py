from model import User, Comment, Reaction, Event
from django.conf import settings

def serializer_event(event):
    return {
        "tile": event.title,
        "description": event.description,
        "photo": event.photo,
        "date": event.date,
        "location": event.location,
        "participant": event.participant,
        "user_id": event.user_id
    }