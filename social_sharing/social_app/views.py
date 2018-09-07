from django.shortcuts import render
import request
from django.http import HttpResponse, JsonResponse
from utils import check_password, get_hashed_password
# Create your views here.
from models import User, Reaction, Event
from serializers import serializer_event
import json

def check_log():
    pass

def index(request):
    return HttpResponse('Welcome!!!')

def login(request):
    data = request.body
    print 'abc', type(data)
    return HttpResponse(data)

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