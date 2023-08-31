from django.urls import path
from django.conf.urls import url

from db.api.graph import (
    getGraph,
    createClass,
    createObject,
    updateClass,
    deleteEntity,
    applyPattern,
    collectPatterns,
    deleteRelation,
    addClassAttribute,
    updateEntity,
    addClassObjectAttribute,
    getClassObjects,
    updateEntityFile,
    applyOntologyPattern,
    createRelation
)
from db.api.ontology_views import (
    getOntologies,
    getResourceOntologies,
    createOntology,
    createResourceOntology,
    getItemsByLabels,
    collectEntity,
    createPatternOntology,
    getPatternOntologies,
    branchOntology
)

from db.api.projects import (
    getProject,
    getProjects,
    createProject,
    updateProject,
    deleteProject,
    getCustomPage
)

from db.files import (
    uploadFile,
    getFile,
    getFiles,
    updateFile,
    deleteFile
)
    


urlpatterns = [
    path('uploadFile',uploadFile , name='uploadFile'),
    path('getFile',getFile , name='getFile'),
    path('getFiles',getFiles , name='getFiles'),
    path('updateFile',updateFile , name='updateFile'),
    path('deleteFile',deleteFile , name='deleteFile'),

    path('getProject',getProject , name='getProject'),
    path('getProjects',getProjects , name='getProjects'),
    path('createProject',createProject , name='createProject'),
    path('updateProject',updateProject , name='updateProject'),
    path('deleteProject',deleteProject , name='deleteProject'),
    path('getCustomPage',getCustomPage , name='getCustomPage'),


    path('getGraph',getGraph , name='getGraph'),
    path('createClass',createClass , name='createClass'),
    path('createObject',createObject , name='createObject'),
    path('updateClass',updateClass , name='updateClass'),
    path('applyPattern',applyPattern , name='applyPattern'),
    path('deleteEntity',deleteEntity , name='deleteEntity'),
    path('collectPatterns',collectPatterns , name='collectPatterns'),
    path('deleteRelation',deleteRelation , name='deleteRelation'),
    path('addClassAttribute',addClassAttribute , name='addClassAttribute'),
    path('updateEntity',updateEntity , name='updateEntity'),
    path('updateEntityFile',updateEntityFile , name='updateEntityFile'),
    path('addClassObjectAttribute',addClassObjectAttribute , name='addClassObjectAttribute'),
    path('getClassObjects',getClassObjects , name='getClassObjects'),

    path('getOntologies',getOntologies , name='getOntologies'),
    path('getResourceOntologies',getResourceOntologies , name='getResourceOntologies'),

    
    path('createOntology',createOntology , name='createOntology'),
    path('createResourceOntology',createResourceOntology , name='createResourceOntology'),

    path('getItemsByLabels', getItemsByLabels, name= 'getItemsByLabels'),
    path('collectEntity',collectEntity , name='collectEntity'),



    path('applyOntologyPattern',applyOntologyPattern , name='applyOntologyPattern'),
    path('createPatternOntology',createPatternOntology , name='createPatternOntology'),
    path('getPatternOntologies',getPatternOntologies , name='getPatternOntologies'),

    path('branchOntology',branchOntology , name='branchOntology'),

    path('createRelation',createRelation , name='createRelation'),
    
    
]