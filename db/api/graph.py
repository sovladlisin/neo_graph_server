from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponseRedirect, HttpResponse
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import datetime
from django.db.models import Q

from operator import itemgetter
import pprint
from core.settings import *




# API IMPORTS
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from db.api.ontology.OntologyRepository import OntologyRepo

from db.models import Resource
from db.files import collect_file

@api_view(['GET', ])
@permission_classes((AllowAny,))
def getGraph(request):
    uri = request.GET.get('uri', '')
    o = OntologyRepo(uri)
    result_nodes, result_arcs, arc_names = o.getFullOntology()
    o.close()

    result = {
        'nodes': result_nodes,
        'arcs': result_arcs,
        'arc_names': arc_names
    }
    return Response(result)

@api_view(['POST', ])
@permission_classes((AllowAny,))
def createClass(request):
    data = json.loads(request.body.decode('utf-8'))

    ontology_uri = data.get('ontology_uri', '')
    title = data.get('title', '')
    comment = data.get('comment', '')
    parent_uri = data.get('parent_uri', None)

    o = OntologyRepo(ontology_uri)
    result_nodes, result_arcs = o.createClass(title, comment, parent_uri)
    o.close()

    result = {
        'nodes': result_nodes,
        'arcs': result_arcs
    }
    return Response(result)

@api_view(['POST', ])
@permission_classes((AllowAny,))
def updateClass(request):
    data = json.loads(request.body.decode('utf-8'))

    ontology_uri = data.get('ontology_uri', '')
    uri = data.get('uri', {})
    params = data.get('params', {})
    attributes = data.get('params', [])

    o = OntologyRepo(ontology_uri)
    result_nodes, result_arcs = o.updateClass(uri=uri, params=params, attributes=attributes)
    o.close()

    result = {
        'nodes': result_nodes,
        'arcs': result_arcs
    }
    return Response(result)

@api_view(['POST', ])
@permission_classes((AllowAny,))
def createObject(request):
    data = json.loads(request.body.decode('utf-8'))

    ontology_uri = data.get('ontology_uri', '')
    title = data.get('title', '')
    comment = data.get('comment', '')
    class_uri = data.get('class_uri', None)

    o = OntologyRepo(ontology_uri)
    result_nodes, result_arcs = o.createObject(title, comment, class_uri)
    o.close()

    result = {
        'nodes': result_nodes,
        'arcs': result_arcs
    }
    return Response(result)

@api_view(['DELETE', ])
@permission_classes((AllowAny,))
def deleteEntity(request):

    ontology_uri = request.GET.get('ontology_uri', None)
    uri = request.GET.get('uri', None)

    o = OntologyRepo(ontology_uri)
    result_nodes_uris = o.deleteEntity(uri)
    o.close()

    result = {
        'nodes': result_nodes_uris,
        'arcs': []
    }
    return Response(result)

@api_view(['DELETE', ])
@permission_classes((AllowAny,))
def deleteRelation(request):

    ontology_uri = request.GET.get('ontology_uri', None)
    id = request.GET.get('id', None)

    o = OntologyRepo(ontology_uri)
    result_arcs_id = o.deleteRel(id)
    o.close()

    result = {
        'nodes': [],
        'arcs': [result_arcs_id]
    }
    return Response(result)


@api_view(['POST', ])
@permission_classes((AllowAny,))
def applyPattern(request):
    data = json.loads(request.body.decode('utf-8'))

    pattern = data.get('pattern', None)

    o = OntologyRepo(pattern.get('ontology_uri',None))
    result_nodes, result_arcs = o.apply_pattern(pattern)
    o.close()

    result = {
        'nodes': result_nodes,
        'arcs': result_arcs
    }
    return Response(result)


@api_view(['POST', ])
@permission_classes((AllowAny,))
def collectPatterns(request):
    data = json.loads(request.body.decode('utf-8'))

    patterns = data.get('patterns', None)
    
    o = OntologyRepo(patterns[0].get('ontology_uri',None))

    result = o.collectPatternsTarget(patterns)

    return Response(result)

@api_view(['GET', ])
@permission_classes((AllowAny,))
def getClassObjects(request):
    ontology_uri = request.GET.get('ontology_uri', None)
    class_uri = request.GET.get('class_uri', None)

    o = OntologyRepo(ontology_uri=ontology_uri)
    result = o.getClassObjects(class_uri=class_uri)

    return Response(result)

@api_view(['POST', ])
@permission_classes((AllowAny,))
def addClassAttribute(request):
    data = json.loads(request.body.decode('utf-8'))

    ontology_uri = data.get('ontology_uri', None)
    uri = data.get('uri', None)
    label = data.get('label', None)
    
    o = OntologyRepo(ontology_uri)

    result_nodes, result_arcs = o.addClassAtribute(uri=uri, label=label)

    result = {
        'nodes': result_nodes,
        'arcs': result_arcs
    }
    return Response(result)

@api_view(['POST', ])
@permission_classes((AllowAny,))
def addClassObjectAttribute(request):
    data = json.loads(request.body.decode('utf-8'))

    ontology_uri = data.get('ontology_uri', None)
    uri = data.get('uri', None)
    label = data.get('label', None)
    range_uri = data.get('range_uri', None)
    
    o = OntologyRepo(ontology_uri)

    result_nodes, result_arcs = o.addClassObjectAtribute(uri=uri, label=label,range_uri=range_uri)

    result = {
        'nodes': result_nodes,
        'arcs': result_arcs
    }
    return Response(result)

@api_view(['POST', ])
@permission_classes((AllowAny,))
def updateEntity(request):
    data = json.loads(request.body.decode('utf-8'))

    ontology_uri = data.get('ontology_uri', None)
    uri = data.get('uri', None)
    params = data.get('params', None)
    obj_params = data.get('obj_params', None)

    o = OntologyRepo(ontology_uri)

    result_nodes, result_arcs = o.updateEntity(uri=uri,params=params,obj_params=obj_params)

    result = {
        'nodes': result_nodes,
        'arcs': result_arcs
    }
    return Response(result)

@api_view(['POST', ])
@permission_classes((AllowAny,))
def applyOntologyPattern(request):
    data = json.loads(request.body.decode('utf-8'))

    origin_ontology_uri = data.get('origin_ontology_uri', None)
    ontology_uri = data.get('ontology_uri', None)

    o = OntologyRepo(ontology_uri)

    result_nodes, result_arcs, arc_names = o.copyOntology(origin_ontology_uri=origin_ontology_uri)
    o.close()

    result = {
        'nodes': result_nodes,
        'arcs': result_arcs,
        'arc_names': arc_names
    }
    return Response(result)


@api_view(['POST', ])
@permission_classes((AllowAny,))
def updateEntityFile(request):
    data = json.loads(request.body.decode('utf-8'))
    ontology_uri = data.get('ontology_uri', None)
    file_id = data.get('file_id', None)
    uri = data.get('uri', None)
    property_uri = data.get('property_uri', None)

    file_d = Resource.objects.get(pk=int(file_id))

    

    o = OntologyRepo(ontology_uri)

    node = o.nr.get_node_by_uri(uri)
    prev_file_url = node.get('data',{}).get('params_values',{}).get(property_uri,'')
    prev_file = None
    for f in Resource.objects.all():
        if f.source.url == prev_file_url:
            prev_file = f


    result_nodes, result_arcs = o.updateEntity(uri=uri,params={property_uri: file_d.source.url},obj_params=None)
    
    if prev_file:
        uris_temp =json.loads(prev_file.uris)
        if uri in uris_temp:
            uris_temp.remove(uri)
            prev_file.uris = json.dumps(uris_temp)
            prev_file.save()

    uris_temp =json.loads(file_d.uris)
    uris_temp.append(uri)
    file_d.uris = json.dumps(uris_temp)
    file_d.save()


    o.close()

    result = {
        'nodes': result_nodes,
        'arcs': result_arcs,
        'file_1': collect_file(file_d),
    }

    if prev_file:
        result['file_2'] = collect_file(prev_file)
   
    return Response(result)

@api_view(['POST', ])
@permission_classes((AllowAny,))
def createRelation(request):
    data = json.loads(request.body.decode('utf-8'))

    source = data.get('source', None)
    target = data.get('target', None)
    ontology_uri = data.get('ontology_uri', None)

    o = OntologyRepo(ontology_uri)

    rel = o.createRelation(source=source, target=target)
    o.close()

    result = {
        'nodes': [],
        'arcs': [rel],
        'arc_names': []
    }
    return Response(result)