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
from .models import Resource, Entity, Markup
from operator import itemgetter

from core.settings import *




# API IMPORTS
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny


@api_view(['GET', ])
@permission_classes((AllowAny,))
def getVisualConnectedObjects(request):
    id = request.GET.get('id', None)
    if id is None:
        return HttpResponse(status=400)

    o = Onthology(DB_URI,DB_USER, DB_PASSWORD)
    res = o.getVisualConnectedObjects(id)
    result = []
    for node in res:
        result.append(o.nodeToDict(node))

    o.close()
    return Response(result)

@api_view(['GET', ])
@permission_classes((AllowAny,))
def getDomainOntologies(request):
    o = Onthology(DB_URI,DB_USER, DB_PASSWORD)
    res = o.getDomainOntologies()
    result = []
    for node in res:
        result.append(o.nodeToDict(node))

    o.close()
    
    return JsonResponse(result, safe=False)

@api_view(['GET', ])
@permission_classes((AllowAny,))
def getAllClasses(request):
    domain = request.GET.get('domain', '')
    o = Onthology(DB_URI,DB_USER, DB_PASSWORD,domain)
    res = o.getClasses()
    result = []
    for node in res:
        result.append(o.nodeToDict(node))

    o.close()
    
    return JsonResponse(result, safe=False)


@api_view(['GET', ])
@permission_classes((AllowAny,))
def getClasses(request):
    domain = request.GET.get('domain', '')
    domain = RESOURCE_NAMESPACE if domain == 'Resource' else domain
    o = Onthology(DB_URI,DB_USER, DB_PASSWORD,domain)
    res = o.getParentClasses()
    result = []
    for node in res:
        result.append(o.nodeToDict(node))

    o.close()
    
    return JsonResponse(result, safe=False)


@api_view(['GET', ])
@permission_classes((AllowAny,))
def getClassObjects(request):
    id = request.GET.get('id', None)
    if id is None:
        return HttpResponse(status=404)
    o = Onthology(DB_URI,DB_USER, DB_PASSWORD)
    res = o.getClassObjects(id)
    result = []
    for node in res:
        result.append(o.nodeToDict(node))

    o.close()
    
    return JsonResponse(result, safe=False)

@api_view(['GET', ])
@permission_classes((AllowAny,))
def getClassObject(request):
    id = request.GET.get('id', None)

    if id is None:
        return HttpResponse(status=404)

    o = Onthology(DB_URI,DB_USER, DB_PASSWORD)

    node, signature, attributes, attributes_obj, resources = o.getClassObject(id)

    obj = o.nodeToDict(node)

    attrs = []
    attrs_obj = []
    for a in attributes:
        attrs.append(o.nodeToDict(a))
    for a in attributes_obj:
        r = o.relToDict(a)

        if VISUAL_ITEM in r['start_node']['labels']:
            try:
                res_uri = r['start_node']['uri']
                res = Resource.objects.all().filter(original_object_uri=res_uri).first()
                fileLink = res.source.url
            except:
                pass
        attrs_obj.append(r)

    entities = []
    text_uris_dict = {}
    texts = []
    for en in Entity.objects.all().filter(node_uri=obj['uri']):
        temp =model_to_dict(en)
        text_uri = en.markup.original_object_uri
        temp['text_uri'] = text_uri
        temp['markup_object'] = model_to_dict(en.markup)
        entities.append(temp)
        text_uris_dict[text_uri] = '1'

    text_uris = getList(text_uris_dict)
    text_nodes = o.getNodesByUris(text_uris)

    for t in text_nodes:
        texts.append(o.nodeToDict(t))

    o.close()
    

    return JsonResponse({'object': obj, 'class_signature': signature, 'class_attributes': attrs, 'relations': attrs_obj, 'entities': entities, 'texts': texts, 'resources': resources }, safe=False)

@api_view(['GET', ])
@permission_classes((AllowAny,))
def getClassFullSignature(request):
    c_uri = request.GET.get('uri', None)
    if c_uri is None:
        return HttpResponse(status=404)
    o = Onthology(DB_URI,DB_USER, DB_PASSWORD)
    class_sig, parent_sig, type_nodes, class_node = o.getClassFullSignature(c_uri)
    class_node_dict = o.nodeToDict(class_node)
    type_dicts = []
    for node in type_nodes:
        type_dicts.append(o.nodeToDict(node))

    o.close()
    

    return JsonResponse({'class_signature':class_sig, 'parents_signature':parent_sig,'type_nodes':  type_dicts, 'class_node': class_node_dict}, safe=False)

@api_view(['GET', ])
@permission_classes((AllowAny,))
def getClass(request):
    id = request.GET.get('id', None)
    if id is None:
        return HttpResponse(status=404)
    o = Onthology(DB_URI,DB_USER, DB_PASSWORD)
    class_node, attributes, objects, attr_types, attributes_obj, attributes_types_obj = o.getClassById(id)
    class_obj = o.nodeToDict(class_node)
    attrs = []
    objs = []
    types = {}
    attrs_obj = []
    types_attr = {}

    for a in attributes:
        attrs.append(o.nodeToDict(a))
    for a in attributes_obj:
        attrs_obj.append(o.nodeToDict(a))

    for obj in objects:
        objs.append(o.nodeToDict(obj))

    for a_t in attr_types:
        types[a_t] = o.nodeToDict(attr_types[a_t])
    for a_t in attributes_types_obj:
        types_attr[a_t] = o.nodeToDict(attributes_types_obj[a_t])

    entities = []
    text_uris_dict = {}
    texts = []
    for en in Entity.objects.all().filter(node_uri=class_obj['uri']):
        temp =model_to_dict(en)
        text_uri = en.markup.original_object_uri
        temp['text_uri'] = text_uri
        temp['markup_object'] = model_to_dict(en.markup)
        entities.append(temp)
        text_uris_dict[text_uri] = '1'

    text_uris = getList(text_uris_dict)
    text_nodes = o.getNodesByUris(text_uris)

    for t in text_nodes:
        texts.append(o.nodeToDict(t))

    o.close()
    

    return JsonResponse({'class': class_obj, 'attributes': attrs, 'objects': objs, 'types': types, 'attributes_obj':attrs_obj ,'attribute_types':types_attr, 'entities': entities, 'texts': texts}, safe=False)

@api_view(['GET', ])
@permission_classes((AllowAny,))
def getSubClasses(request):
    id = request.GET.get('id', None)
    if id is None:
        return HttpResponse(status=404)
    o = Onthology(DB_URI,DB_USER, DB_PASSWORD)
    res = o.getSubClassesById(id)
    result = []
    for node in res:
        result.append(o.nodeToDict(node))

    o.close()
    
    return JsonResponse(result, safe=False)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def addClassAttribute(request):

    data = json.loads(request.body.decode('utf-8'))

    domain = data.get('domain', '')
    o = Onthology(DB_URI,DB_USER, DB_PASSWORD,domain)

    class_id = data.get('class_id', None)

    props = {}
    props[LABEL] = data.get('label', None)
    props['uri'] = data.get('uri', None)
    

    res = o.addClassAttribute(class_id, STRING, props)
    result = o.nodeToDict(res)

    o.close()

    return JsonResponse(result, safe=False)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def addClassAttributeObject(request):

    data = json.loads(request.body.decode('utf-8'))

    domain = data.get('domain', '')
    o = Onthology(DB_URI,DB_USER, DB_PASSWORD,domain)

    class_id = data.get('class_id', None)
    attribute_class_id = data.get('attribute_class_id', None)

    props = {}
    props[LABEL] = data.get('label', None)
    props['uri'] = data.get('uri', None)

    res = o.addClassAttributeObject(class_id, attribute_class_id, props)
    result = o.nodeToDict(res)

    o.close()

    return JsonResponse(result, safe=False)


@api_view(['GET', ])
@permission_classes((AllowAny,))
def getClassesWithSignatures(request):
    o = Onthology(DB_URI,DB_USER, DB_PASSWORD)
    res = o.getClassesWithSignatures()
    result = []
    for r in res:
        result.append(o.nodeToDict(r))

    o.close()

    return JsonResponse(result, safe=False)

@api_view(['GET', ])
@permission_classes((AllowAny,))
def getObjectsByClassUri(request):
    uri_s = request.GET.get('uri', None)
    if uri_s is None:
        return HttpResponse(status=404)

    o = Onthology(DB_URI,DB_USER, DB_PASSWORD)
    res = o.getObjectsByClassUri(uri_s)
    result = []
    for r in res:
        result.append(o.nodeToDict(r))

    o.close()

    return Response({'objects': result})

# @csrf_exempt
# def updateEntity(request):
#     if request.method == 'POST':

#         token = request.headers.get('Token', None)
#         if token is None:
#             return HttpResponse(status=401)
#         DB_USER = authenticate_DB_USER(token)
#         if DB_USER is None:
#             return HttpResponse(status=401)
#         if DB_USER.is_editor == False:
#             return HttpResponse(status=401)

#         data = json.loads(request.body.decode('utf-8'))
#         o = Onthology(DB_URI,DB_USER, DB_PASSWORD)
#         node = o.updateEntity(data)
#         return JsonResponse(o.nodeToDict(node), safe=False)
#     return HttpResponse('Wrong request')

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def addEntity(request):

    data = json.loads(request.body.decode('utf-8'))
    labels = data['labels']
    node = data['node']
    o = Onthology(DB_URI,DB_USER, DB_PASSWORD)
    created_node = o.createEntity(labels, node)


    o.close()

    return JsonResponse(o.nodeToDict(created_node), safe=False)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def updateEntity(request):

    data = json.loads(request.body.decode('utf-8'))
    node = data['node']
    o = Onthology(DB_URI,DB_USER, DB_PASSWORD)
    created_node = o.updateEntity(node)

    o.close()

    return JsonResponse(o.nodeToDict(created_node), safe=False)

@api_view(['DELETE', ])
@permission_classes((IsAuthenticated,))
def deleteEntity(request):
            
    id = request.GET.get('id', None)
    if id is None:
        return HttpResponse(status=403)

    o = Onthology(DB_URI,DB_USER, DB_PASSWORD)

    node = o.deleteObject(id)

    o.close()

    return JsonResponse({"result": True}, safe=False)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def updateIndex(request):

    data = json.loads(request.body.decode('utf-8'))

    domain = data.get('domain', None)
    if domain is None:
        return HttpResponse('Wrong request', status=404)
    o = Onthology(DB_URI,DB_USER, DB_PASSWORD,domain)
    res = o.updateIndex()

    o.close()


    return JsonResponse({'result': res}, safe=False)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def searchIndex(request):

    data = json.loads(request.body.decode('utf-8'))

    domain = data.get('domain', '')
    search = data.get('search', '')
    connector = data.get('connector', '')
    if domain is None or search is None or connector is None:
        return HttpResponse('Wrong request', status=404)

    o = Onthology(DB_URI,DB_USER, DB_PASSWORD,domain)
    res = o.searchIndex(search, connector)
    result = []
    for r in res:
        result.append(o.nodeToDict(r))

    o.close()


    return JsonResponse(result, safe=False)


def getList(dict):
    return list(map(itemgetter(0), dict.items()))


@api_view(['DELETE', ])
@permission_classes((IsAuthenticated,))
def deleteOntology(request):
    domain = request.GET.get('domain', None)
    if domain is None:
        return HttpResponse(status=404)

    o = Onthology(DB_URI,DB_USER, DB_PASSWORD, domain)
    node = o.deleteOntology()

    for m in Markup.objects.all().filter(ontology_uri=domain):
        m.delete()


    o.close()

    return JsonResponse({"result": True}, safe=False)