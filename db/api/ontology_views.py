from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponseRedirect, HttpResponse
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import datetime
from django.db.models import Q
import uuid

from operator import itemgetter

from core.settings import *

from db.api.ontology.namespace import *


# API IMPORTS
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from db.api.ontology.OntologyRepository import OntologyRepo




@api_view(['GET', ])
@permission_classes((AllowAny,))
def getOntologies(request):
    o = OntologyRepo('')
    result = o.getOntologies()
    return Response(result)

@api_view(['GET', ])
@permission_classes((AllowAny,))
def getResourceOntologies(request):
    o = OntologyRepo('')
    result = o.getResourceOntologies()
    return Response(result)

@api_view(['GET', ])
@permission_classes((AllowAny,))
def getPatternOntologies(request):
    o = OntologyRepo('')
    result = o.getPatternOntologies()
    return Response(result)

@api_view(['POST', ])
@permission_classes((AllowAny,))
def createOntology(request):
    data = json.loads(request.body.decode('utf-8'))
    title = data.get('title', '')
    comment = data.get('comment', '')

    uri = MAIN_ONTOLOGY + '/' +  str(uuid.uuid4())

    o = OntologyRepo(uri)
    result = o.createOntology(title=title, comment=comment)
    o.close()

    return Response(result)

@api_view(['POST', ])
@permission_classes((AllowAny,))
def branchOntology(request):
    data = json.loads(request.body.decode('utf-8'))
    ontology_uri = data.get('ontology_uri', '')
    title = data.get('title', '')
    comment = data.get('comment', '')
    ontology_type = data.get('ontology_type', '')


    base = MAIN_ONTOLOGY if ontology_type == 'Ontology' else MAIN_RESOURCE
    uri = base + '/' +  str(uuid.uuid4())

    o = OntologyRepo(ontology_uri)
    result = o.branchOntology(title=title, comment=comment, new_ontology_uri=uri, ontology_type=ontology_type)
    o.close()

    return Response(result)

@api_view(['POST', ])
@permission_classes((AllowAny,))
def createResourceOntology(request):
    data = json.loads(request.body.decode('utf-8'))
    title = data.get('title', '')
    comment = data.get('comment', '')

    uri = MAIN_RESOURCE + '/' +  str(uuid.uuid4())

    o = OntologyRepo(uri)
    result = o.createResourceOntology(title=title, comment=comment)
    o.close()

    return Response(result)

@api_view(['POST', ])
@permission_classes((AllowAny,))
def createPatternOntology(request):
    data = json.loads(request.body.decode('utf-8'))
    title = data.get('title', '')
    comment = data.get('comment', '')

    uri = MAIN_PATTERN + '/' +  str(uuid.uuid4())
    o = OntologyRepo(uri)
    result = o.createPatternOntology(title=title, comment=comment)
    o.close()

    return Response(result)

# @api_view(['POST', ])
# @permission_classes((AllowAny,))
# def branchResourceOntology(request):
#     data = json.loads(request.body.decode('utf-8'))
#     ontology_uri = data.get('uri', '')
#     title = data.get('title', '')
#     comment = data.get('comment', '')

#     o = OntologyRepo(ontology_uri)
#     result = o.createResourceOntology(title=title, comment=comment)
#     o.close()

#     return Response(result)

@api_view(['POST', ])
@permission_classes((AllowAny,))
def getItemsByLabels(request):
    data = json.loads(request.body.decode('utf-8'))
    labels = data.get('labels', None)
    ontology_uri = data.get('ontology_uri', None)
    custom_q = data.get('custom_q', None)
    

    o = OntologyRepo(ontology_uri)
    result_nodes = o.getItemsByLabels(labels, custom_q)
    o.close()

   
    return Response(result_nodes)

@api_view(['POST', ])
@permission_classes((AllowAny,))
def getItemsByUris(request):
    data = json.loads(request.body.decode('utf-8'))
    ontology_uri = data.get('ontology_uri', None)
    uris = data.get('uris', None)
    

    o = OntologyRepo(ontology_uri)
    result_nodes = o.getItemsByUris(uris)
    o.close()
   
    return Response(result_nodes)

@api_view(['GET', ])
@permission_classes((AllowAny,))
def collectEntity(request):
    ontology_uri = request.GET.get('ontology_uri', None)
    uri = request.GET.get('uri', None)

    o = OntologyRepo(ontology_uri)
    node = o.collectEntity(uri)
    o.close()

    return Response(node)


