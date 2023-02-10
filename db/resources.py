from time import time
from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponseRedirect, HttpResponse
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import datetime
from django.db.models import Q

from core.settings import *
from .onthology_driver import Onthology
from.onthology_namespace import *
from django.http import JsonResponse




# API IMPORTS
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

@api_view(['GET', ])
@permission_classes((AllowAny,))
def getAllResources(request):
    o = Onthology(DB_URI,DB_USER, DB_PASSWORD)
    res = o.getResources()
    
    o.close()

    return JsonResponse(res, safe=False)

@api_view(['POST', ])
@permission_classes((AllowAny,))
def getCorpusResources(request):
    data = json.loads(request.body.decode('utf-8'))

    c_uri = data.get('corpus_uri', '')
    res_types = data.get('res_types', [])
    text_search = data.get('text_search', '')
    lang_id = data.get('lang_id', -1)
    actor_id = data.get('actor_id', -1)
    place_id = data.get('place_id', -1)
    genre_id = data.get('genre_id', -1)
    time_search = data.get('time_search', '')
    chunk_number = data.get('chunk_number', 1)
    chunk_size = data.get('chunk_size', 50)
    o = Onthology(DB_URI,DB_USER, DB_PASSWORD)

    print('Attention: ', res_types )

    res,data_size, counters = o.getCorpusResources(c_uri, res_types, text_search, lang_id, actor_id, place_id,genre_id, time_search, chunk_number, chunk_size)
    o.close()
    
    return JsonResponse({'data': res, 'data_size': data_size, 'counters': counters}, safe=False)

@api_view(['POST', ])
@permission_classes((AllowAny,))
def createEvent(request):
    data = json.loads(request.body.decode('utf-8'))
    actors_id = data.get('actor_id', None)
    place_id = data.get('place_id', None)
    time_string = data.get('time_string', None)
    resource_id = data.get('resource_id', None)
    connection_type = data.get('connection_type', None)

    if None in [actors_id, place_id, time_string,resource_id,connection_type ]:
        return HttpResponse(status=403)


    o = Onthology(DB_URI,DB_USER, DB_PASSWORD)
    res = o.createEvent(actors_id, place_id, time_string,resource_id, connection_type )
    o.close()
    
    return HttpResponse(status=200)

