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
from rest_framework.permissions import IsAuthenticated, IsAuthenticated

from db.api.ontology.OntologyRepository import OntologyRepo




@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def getOntologies(request):
    o = OntologyRepo(request.user, '')
    result = o.getOntologies()
    return Response(result)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def getResourceOntologies(request):
    o = OntologyRepo(request.user, '')
    result = o.getResourceOntologies()
    return Response(result)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def getPatternOntologies(request):
    o = OntologyRepo(request.user, '')
    result = o.getPatternOntologies()
    return Response(result)


@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def getOntologyTree(request):
    ontology_uri = request.GET.get('ontology_uri', None)
    if ontology_uri is None:
        return HttpResponse(status=400)
    
    o = OntologyRepo(request.user, ontology_uri=ontology_uri)
    result_nodes, r_arcs, result_arc_names = o.getFullOntology()
    response = {
        'nodes': result_nodes,
        'arcs': r_arcs,
        'ontology_uri': ontology_uri
    }
    return Response(response)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def createOntology(request):
    data = json.loads(request.body.decode('utf-8'))
    title = data.get('title', '')
    comment = data.get('comment', '')

    uri = MAIN_ONTOLOGY + '/' +  str(uuid.uuid4())

    o = OntologyRepo(request.user, uri)
    result = o.createOntology(title=title, comment=comment)
    o.close()

    return Response(result)

@api_view(['DELETE', ])
@permission_classes((IsAuthenticated,))
def deleteOntology(request):
    ontology_uri = request.GET.get('ontology_uri', None)
    o = OntologyRepo(request.user,ontology_uri)
    result = o.deleteOntology()
    return Response(result)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def branchOntology(request):
    data = json.loads(request.body.decode('utf-8'))
    ontology_uri = data.get('ontology_uri', '')
    title = data.get('title', '')
    comment = data.get('comment', '')
    ontology_type = data.get('ontology_type', '') # Resource | Ontology 


    base = MAIN_ONTOLOGY if ontology_type == 'Ontology' else MAIN_RESOURCE
    uri = base + '/' +  str(uuid.uuid4())

    o = OntologyRepo(request.user,ontology_uri)
    result = o.branchOntology(title=title, comment=comment, new_ontology_uri=uri, ontology_type=ontology_type)
    o.close()

    return Response(result)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def createResourceOntology(request):
    data = json.loads(request.body.decode('utf-8'))
    title = data.get('title', '')
    comment = data.get('comment', '')

    uri = MAIN_RESOURCE + '/' +  str(uuid.uuid4())

    o = OntologyRepo(request.user,uri)
    result = o.createResourceOntology(title=title, comment=comment)
    o.close()

    return Response(result)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def createPatternOntology(request):
    data = json.loads(request.body.decode('utf-8'))
    title = data.get('title', '')
    comment = data.get('comment', '')

    uri = MAIN_PATTERN + '/' +  str(uuid.uuid4())
    o = OntologyRepo(request.user,uri)
    result = o.createPatternOntology(title=title, comment=comment)
    o.close()

    return Response(result)

# @api_view(['POST', ])
# @permission_classes((IsAuthenticated,))
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
@permission_classes((IsAuthenticated,))
def getItemsByLabels(request):
    data = json.loads(request.body.decode('utf-8'))
    labels = data.get('labels', None)
    ontology_uri = data.get('ontology_uri', None)
    custom_q = data.get('custom_q', None)
    

    o = OntologyRepo(request.user, ontology_uri)
    result_nodes = o.getItemsByLabels(labels, custom_q)
    o.close()

   
    return Response(result_nodes)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def getItemsByUris(request):
    data = json.loads(request.body.decode('utf-8'))
    ontology_uri = data.get('ontology_uri', None)
    uris = data.get('uris', None)
    

    o = OntologyRepo(request.user,ontology_uri)
    result_nodes = o.getItemsByUris(uris)
    o.close()
   
    return Response(result_nodes)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def collectEntity(request):
    ontology_uri = request.GET.get('ontology_uri', None)
    uri = request.GET.get('uri', None)

    o = OntologyRepo(request.user,ontology_uri)
    node = o.collectEntity(uri)
    o.close()

    return Response(node)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def collectClassSimpleSignature(request):
    data = json.loads(request.body.decode('utf-8'))

    ontology_uri =data.get('ontology_uri', None)
    class_uri = data.get('class_uri', None)

    o = OntologyRepo(request.user,ontology_uri)
    node = o.collect_class_simple_signature(class_uri)
    o.close()

    return Response(node)



