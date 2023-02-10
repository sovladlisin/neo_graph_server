from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponseRedirect, HttpResponse
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import datetime
from django.db.models import Q
from .onthology_driver import Onthology
from.onthology_namespace import *

from core.settings import *



# API IMPORTS
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny


@api_view(['GET', ])
@permission_classes((AllowAny,))
def getCorpuses(request):
    o = Onthology(DB_URI,DB_USER, DB_PASSWORD)
    res = o.getCorpuses()
    o.close()
    
    return JsonResponse(res, safe=False)


@api_view(['GET', ])
@permission_classes((AllowAny,))
def getSubCorpuses(request):
    id = request.GET.get('id', None)
    if id is None:
        return HttpResponse(status=404)

    o = Onthology(DB_URI,DB_USER, DB_PASSWORD)
    res = o.getSubCorpuses(id)
    result = []
    for node in res:
        result.append(o.nodeToDict(node))
    o.close()
    return JsonResponse(result, safe=False)
