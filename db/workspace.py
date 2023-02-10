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



# API IMPORTS
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny


@api_view(['GET', ])
@permission_classes((AllowAny,))
def getWorkspace(request):
    o = Onthology(DB_URI,DB_USER, DB_PASSWORD)
    id = request.GET.get('id', None)

    origin_node,translation_node,commentary_node = o.getWorkspace(id)

    origin_node_dict  = o.nodeToDict(origin_node)
    translation_node_dict  = o.nodeToDict(translation_node)
    commentary_node_dict = o.nodeToDict(commentary_node)

    origin_text_obj = Resource.objects.filter(original_object_uri=origin_node_dict['uri']).first()
    translation_text_obj = Resource.objects.filter(original_object_uri=translation_node_dict['uri']).first()
    commentary_text_obj = Resource.objects.filter(original_object_uri=commentary_node_dict['uri']).first()

    origin_url = origin_text_obj.source.url
    translation_url = translation_text_obj.source.url
    commentary_url = commentary_text_obj.source.url

    node, signature, attributes, attributes_obj, resources = o.getClassObject(origin_node.id)

    obj = o.nodeToDict(node)
    attrs = []
    attrs_obj = []
    # for a in attributes:
    #     attrs.append(o.nodeToDict(a))
    for a in attributes_obj:
        attrs_obj.append( o.relToDict(a))

    origin_node_extended = {'node': obj, 'relations' : attrs_obj }

    
    resources = o.getObjectVisualItems(origin_node.id)
    result = {
        "origin_url":origin_url,
        "translation_url":translation_url,
        "origin_node":origin_node_dict,
        "translation_node":translation_node_dict,
        "commentary_node": commentary_node_dict,
        "commentary_url": commentary_url,
        'resources': resources,
        'origin_node_extended': origin_node_extended
    }

    o.close()


    return JsonResponse(result, safe=False)



@api_view(['GET', ])
@permission_classes((AllowAny,))
def getMarkups(request):
    o = Onthology(DB_URI,DB_USER, DB_PASSWORD)

    original_object_uri = request.GET.get('original_object_uri', None)
    result = []

    for m in Markup.objects.filter(original_object_uri=original_object_uri):
        temp = model_to_dict(m)
        temp['user'] = {"id": m.account.pk, "username": m.account.username}
        temp['ontology'] = o.nodeToDict(o.getEntityByUri(m.ontology_uri))
        result.append(temp)

    o.close()
    

    return JsonResponse(result, safe=False)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def addMarkup(request):
    user = request.user

    o = Onthology(DB_URI,DB_USER, DB_PASSWORD)

    data = json.loads(request.body.decode('utf-8'))

    name = data.get('name', 'Не указано')
    original_object_uri = data.get('original_object_uri', '')
    ontology_uri = data.get('ontology_uri', '')

    new_markup = Markup(name=name, original_object_uri=original_object_uri, ontology_uri=ontology_uri, account=user)
    new_markup.save()

    result = model_to_dict(new_markup)
    result['user'] = {"id": new_markup.account.pk, "username": new_markup.account.email}
    result['ontology'] = o.nodeToDict(o.getEntityByUri(new_markup.ontology_uri))

    o.close()

    return JsonResponse(result, safe=False)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def editMarkup(request):
    user = request.user
    o = Onthology(DB_URI,DB_USER, DB_PASSWORD)

    data = json.loads(request.body.decode('utf-8'))

    name = data.get('name', 'Не указано')
    id = data.get('id', None)

    new_markup = Markup.objects.get(pk=id)
    new_markup.name = name
    new_markup.save()

    result = model_to_dict(new_markup)
    result['user'] = {"id": new_markup.user.pk, "username": new_markup.user.username}
    result['ontology'] = o.nodeToDict(o.getEntityByUri(new_markup.ontology_uri))

    o.close()

    return JsonResponse(result, safe=False)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def deleteMarkup(request):
    
    user = request.user

    data = json.loads(request.body.decode('utf-8'))

    id = data.get('id', None)

    old_markup = Markup.objects.get(pk=id)
    old_markup.delete()

    return JsonResponse({'result': True}, safe=False)

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
    o = Onthology(DB_URI,DB_USER, DB_PASSWORD)
    result = model_to_dict(new_entity)
    result['node'] = o.nodeToDict(o.getEntityByUri(new_entity.node_uri))

    o.close()


    return JsonResponse(result, safe=False)

@api_view(['GET', ])
@permission_classes((AllowAny,))
def getTextEntities(request):
    o = Onthology(DB_URI,DB_USER, DB_PASSWORD)

    markup_id = request.GET.get('markup_id', None)
    result = []

    nodes_uris_dict = {}
    entities = Entity.objects.all().filter(markup__pk=markup_id)
    for e in entities:
        nodes_uris_dict[e.node_uri] = 1
    nodes = o.getNodesByUrisInDict(getList(nodes_uris_dict))

    for e in entities:
        temp = model_to_dict(e)
        temp['node'] = o.nodeToDict(nodes[e.node_uri])
        result.append(temp)

    o.close()

    return JsonResponse(result, safe=False)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def deleteTextEntity(request):
    user = request.user

    data = json.loads(request.body.decode('utf-8'))

    id = data.get('id', None)

    old_entity = Entity.objects.get(pk=id)
    old_entity.delete()

    return JsonResponse({'result': True}, safe=False)


@api_view(['GET', ])
@permission_classes((AllowAny,))
def getNodeAttributes(request):
    o = Onthology(DB_URI,DB_USER, DB_PASSWORD)
    node_uri = request.GET.get('node_uri', None)
    class_node, attributes, attributes_obj = o.getClassAttributes(node_uri) 

    
    attributes_dict = []
    attributes_obj_dict = []
    class_node_dict = o.nodeToDict(class_node)

    for at in attributes:
        attributes_dict.append(o.nodeToDict(at))
    for at in attributes_obj:
        attributes_obj_dict.append(o.nodeToDict(at))

    result = {
        "class_node": class_node_dict,
        "attributes": attributes_dict,
        "attributes_obj": attributes_obj_dict,
    }

    o.close()


    return JsonResponse(result, safe=False)

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
@permission_classes((AllowAny,))
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