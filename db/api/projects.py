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

from db.api.ontology.namespace import *


# API IMPORTS
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from db.api.projects_api.ProjectsRepository import ProjectsRepo
from db.api.ontology.OntologyRepository import OntologyRepo




@api_view(['GET', ])
@permission_classes((AllowAny,))
def getProjects(request):
    o = ProjectsRepo()
    result = o.getProjects()
    return Response(result)

@api_view(['GET', ])
@permission_classes((AllowAny,))
def getProject(request):
    id = request.GET.get('id', None)
    o = ProjectsRepo()
    result = o.getProject(id=id)
    return Response(result)

@api_view(['DELETE', ])
@permission_classes((AllowAny,))
def deleteProject(request):
    id = request.GET.get('id', None)
    o = ProjectsRepo()
    result = o.deleteProject(id=id)
    return Response(result)

@api_view(['POST', ])
@permission_classes((AllowAny,))
def createProject(request):
    data = json.loads(request.body.decode('utf-8'))
    name = data.get('name', '')
    ontologies_uris = data.get('ontologies_uris', [])
    res_ontologies_uris = data.get('res_ontologies_uris', [])
    o = ProjectsRepo()
    result = o.createProject(name=name, ontologies_uris=ontologies_uris, res_ontologies_uris=res_ontologies_uris)
    return Response(result)

@api_view(['POST', ])
@permission_classes((AllowAny,))
def updateProject(request):
    data = json.loads(request.body.decode('utf-8'))
    name = data.get('name', '')
    id = data.get('id', None)
    selected_classes_uris = data.get('selected_classes_uris', [])
    res_selected_classes_uris = data.get('res_selected_classes_uris', [])
    res_star_classes_uris = data.get('res_star_classes_uris', [])
    
    o = ProjectsRepo()
    result = o.updateProject(id=id,name=name, selected_classes_uris=selected_classes_uris ,res_selected_classes_uris=res_selected_classes_uris,res_star_classes_uris=res_star_classes_uris)
    return Response(result)


@api_view(['GET', ])
@permission_classes((AllowAny,))
def getCustomPage(request):
    class_uri = request.GET.get('class_uri', None)
    ontology_uri = request.GET.get('ontology_uri', None)

    o = OntologyRepo(ontology_uri)

    class_node = o.getItemByUri(class_uri)
    objects = o.getClassObjects(class_uri)

    return Response({'class_node': class_node, 'object_nodes': objects})

@api_view(['POST', ])
@permission_classes((AllowAny,))
def collectProjectEmbeddings(request):
    data = json.loads(request.body.decode('utf-8'))
    id = data.get('id', None)
    project_repo = ProjectsRepo()
    project_repo.collectProjectEmdeddings(id)
    return HttpResponse(status=200)

@api_view(['GET', ])
@permission_classes((AllowAny,))
def getProjectEmbedding(request):
    id = request.GET.get('id', None)
    project_repo = ProjectsRepo()
    return Response(project_repo.getProjectEmbedding(id))

@api_view(['GET', ])
@permission_classes((AllowAny,))
def getProjectMessage(request):
    id = request.GET.get('id', None)
    text = request.GET.get('text', None)
    project_repo = ProjectsRepo()
    return Response(project_repo.getProjectMessage(id,text))


# -----------------------------PAGES------------------------------------------

@api_view(['POST', ])
@permission_classes((AllowAny,))
def createPage(request):
    data = json.loads(request.body.decode('utf-8'))
    page_params = data.get('params', {})
    o = ProjectsRepo()
    return Response(o.updatePage(params=page_params))

@api_view(['POST', ])
@permission_classes((AllowAny,))
def updatePage(request):
    data = json.loads(request.body.decode('utf-8'))
    page_params = data.get('params', {})
    o = ProjectsRepo()
    return Response(o.updatePage(params=page_params))

@api_view(['DELETE', ])
@permission_classes((AllowAny,))
def deletePage(request):
    id = request.GET.get('id', None)
    o = ProjectsRepo()
    result = o.deletePage(id=id)
    return Response(result)

@api_view(['GET', ])
@permission_classes((AllowAny,))
def getPage(request):
    id = request.GET.get('id', None)
    o = ProjectsRepo()
    return Response(o.getPage(id=id))

# -----------------------------PAGE BLOCKS------------------------------------------

@api_view(['DELETE', ])
@permission_classes((AllowAny,))
def deletePageBlock(request):
    id = request.GET.get('id', None)
    o = ProjectsRepo()
    result = o.deletePageBlock(id=id)
    return Response(result)

@api_view(['POST', ])
@permission_classes((AllowAny,))
def updatePageBlock(request):
    data = json.loads(request.body.decode('utf-8'))
    page_block_params = data.get('params', {})
    o = ProjectsRepo()
    return Response(o.updatePageBlock(params=page_block_params))

@api_view(['POST', ])
@permission_classes((AllowAny,))
def createPageBlock(request):
    data = json.loads(request.body.decode('utf-8'))
    page_block_params = data.get('params', {})
    o = ProjectsRepo()
    return Response(o.updatePageBlock(params=page_block_params))