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
    collectClassSimpleSignature,
    createPatternOntology,
    getPatternOntologies,
    branchOntology,
    deleteOntology,
    getOntologyTree,
    getItemsByUris
)

from db.api.projects import (
    getProject,
    getProjects,
    createProject,
    updateProject,
    deleteProject,
    getCustomPage,

    createPage,
    updatePage,
    deletePage,
    getPage,

    createPageBlock,
    updatePageBlock,
    deletePageBlock,

    collectProjectEmbeddings,
    getProjectEmbedding,
    getProjectMessage
)

from db.files import (
    uploadFile,
    getFile,
    getFiles,
    updateFile,
    deleteFile
)

from db.workspace import (
    getMarkups,
    editMarkup,
    addMarkup,
    deleteMarkup,

    createTextEntity,
    deleteTextEntity,
    getTextEntities,

    getTextRelations,
    createTextRelation,
    deleteTextRelation
)
    


urlpatterns = [
    path('getTextRelations',getTextRelations , name='getTextRelations'),
    path('createTextRelation',createTextRelation , name='createTextRelation'),
    path('deleteTextRelation',deleteTextRelation , name='deleteTextRelation'),

    path('createTextEntity',createTextEntity , name='createTextEntity'),
    path('deleteTextEntity',deleteTextEntity , name='deleteTextEntity'),
    path('getTextEntities',getTextEntities , name='getTextEntities'),

    path('getMarkups',getMarkups , name='getMarkups'),
    path('editMarkup',editMarkup , name='editMarkup'),
    path('addMarkup',addMarkup , name='addMarkup'),
    path('deleteMarkup',deleteMarkup , name='deleteMarkup'),




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
    path('collectProjectEmbeddings',collectProjectEmbeddings , name='collectProjectEmbeddings'),
    path('getProjectEmbedding',getProjectEmbedding , name='getProjectEmbedding'),
    path('getProjectMessage',getProjectMessage , name='getProjectMessage'),

    path('createPage',createPage , name='createPage'),
    path('updatePage',updatePage , name='updatePage'),
    path('deletePage',deletePage , name='deletePage'),
    path('getPage',getPage , name='getPage'),

    path('createPageBlock',createPageBlock , name='createPageBlock'),
    path('updatePageBlock',updatePageBlock , name='updatePageBlock'),
    path('deletePageBlock',deletePageBlock , name='deletePageBlock'),




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
    path('getItemsByUris', getItemsByUris, name= 'getItemsByUris'),
    path('collectEntity',collectEntity , name='collectEntity'),
    path('collectClassSimpleSignature',collectClassSimpleSignature , name='collectClassSimpleSignature'),
    path('getOntologyTree',getOntologyTree , name='getOntologyTree'),



    path('applyOntologyPattern',applyOntologyPattern , name='applyOntologyPattern'),
    path('createPatternOntology',createPatternOntology , name='createPatternOntology'),
    path('getPatternOntologies',getPatternOntologies , name='getPatternOntologies'),

    path('branchOntology',branchOntology , name='branchOntology'),

    path('createRelation',createRelation , name='createRelation'),
    path('deleteOntology',deleteOntology , name='deleteOntology'),
    
    
    
]