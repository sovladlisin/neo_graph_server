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
from .models import Resource, Markup, Entity, TextRelation
from .views import getList
from core.settings import *
from db.api.ontology.OntologyRepository import OntologyRepo


# API IMPORTS
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny



@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def getMarkups(request):
    ontoRep = OntologyRepo(request.user)

    original_object_uri = request.GET.get('original_object_uri', None)
    result = []

    for m in Markup.objects.filter(original_object_uri=original_object_uri):
        temp = model_to_dict(m)
        temp['user'] = {"id": m.account.pk, "username": m.account.vk_name}
        temp['ontology'] = ontoRep.getItemsByUris([m.ontology_uri])[0]
        result.append(temp)
    return Response(result)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def addMarkup(request):
    user = request.user

    data = json.loads(request.body.decode('utf-8'))
    name = data.get('name', 'Не указано')
    original_object_uri = data.get('original_object_uri', '')
    ontology_uri = data.get('ontology_uri', '')

    ontoRep = OntologyRepo(request.user, ontology_uri)

    new_markup = Markup(name=name, original_object_uri=original_object_uri, ontology_uri=ontology_uri, account=user)
    new_markup.save()

    result = model_to_dict(new_markup)
    result['user'] = {"id": new_markup.account.pk, "username": new_markup.account.vk_name}
    result['ontology'] = ontoRep.getItemsByUris([new_markup.ontology_uri])[0]
    return Response(result)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def editMarkup(request):
    ontoRep = OntologyRepo(request.user)

    data = json.loads(request.body.decode('utf-8'))

    name = data.get('name', 'Не указано')
    id = data.get('id', None)

    new_markup = Markup.objects.get(pk=id)
    new_markup.name = name
    new_markup.save()

    result = model_to_dict(new_markup)
    result['user'] = {"id": new_markup.account.pk, "username": new_markup.account.vk_name}
    result['ontology'] = ontoRep.getItemsByUris([new_markup.ontology_uri])[0]

    return Response(result)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def deleteMarkup(request):
    data = json.loads(request.body.decode('utf-8'))
    id = data.get('id', None)
    old_markup = Markup.objects.get(pk=id)
    old_markup.delete()
    return Response({'result': True})

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def createTextEntity(request):
    data = json.loads(request.body.decode('utf-8'))
    pos_start = data.get('pos_start', None)
    pos_end = data.get('pos_end', None)
    node_uri = data.get('node_uri', None)
    markup_id = data.get('markup', None)

    markup = Markup.objects.get(pk=markup_id)
    
    new_entity = Entity(pos_end=pos_end, pos_start=pos_start, node_uri=node_uri, markup=markup)
    new_entity.save()
    ontoRep = OntologyRepo(request.user)
    result = model_to_dict(new_entity)
    result['node'] = ontoRep.getItemsByUris([node_uri])[0]

    return JsonResponse(result, safe=False)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def getTextEntities(request):
    ontoRep = OntologyRepo(request.user)

    markup_id = request.GET.get('markup_id', None)
    result = []

    nodes_uris_dict = {}
    entities = Entity.objects.all().filter(markup__pk=markup_id)
    for e in entities:
        nodes_uris_dict[e.node_uri] = 1
    nodes = ontoRep.getItemsByUris(getList(nodes_uris_dict))
    
    nodes_dict = {}
    for n in nodes:
        nodes_dict[n['data']['uri']] = n

    for e in entities:
        temp = model_to_dict(e)
        temp['node'] = nodes_dict[e.node_uri]
        result.append(temp)

    return Response(result)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def deleteTextEntity(request):
    data = json.loads(request.body.decode('utf-8'))
    id = data.get('id', None)
    old_entity = Entity.objects.get(pk=id)
    old_entity.delete()
    return Response({'result': True})

# relations

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def createTextRelation(request):
    user = request.user

    data = json.loads(request.body.decode('utf-8'))
    start = data.get('start', None)
    end = data.get('end', None)
    connection = data.get('connection', None)
    markup_id = data.get('markup', None)

    obj_start = Entity.objects.get(pk=start)
    obj_end = Entity.objects.get(pk=end)
    obj_connection = Entity.objects.get(pk=connection)

    markup = Markup.objects.get(pk=markup_id)
    
    new_rel = TextRelation(start=obj_start, end=obj_end, connection= obj_connection, markup=markup)
    new_rel.save()
    return JsonResponse(model_to_dict(new_rel), safe=False)


@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def getTextRelations(request):
    o = Onthology(DB_URI,DB_USER, DB_PASSWORD)

    markup_id = request.GET.get('markup_id', None)
    result = []

    for e in TextRelation.objects.all().filter(markup__pk=markup_id):
        result.append(model_to_dict(e))

    o.close()

    return JsonResponse(result, safe=False)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def deleteTextRelation(request):
    user = request.user

    data = json.loads(request.body.decode('utf-8'))

    id = data.get('id', None)

    old_rel = TextRelation.objects.get(pk=id)
    old_rel.delete()

    return JsonResponse({'result': True}, safe=False)