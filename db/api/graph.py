from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponseRedirect, HttpResponse
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import datetime
from django.db.models import Q

from operator import itemgetter

from core.settings import *




# API IMPORTS
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from db.api.ontology.OntologyRepository import OntologyRepo




@api_view(['GET', ])
@permission_classes((AllowAny,))
def getGraph(request):
    uri = request.GET.get('uri', '')
    o = OntologyRepo(uri)
    result_nodes, result_arcs = o.getFullOntology()
    o.close()

    result = {
        'nodes': result_nodes,
        'arcs': result_arcs
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

