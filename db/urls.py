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
    addClassObjectAttribute
)
from db.api.ontology_views import (
    getOntologies,
    createOntology,
    getItemsByLabels,
    collectEntity
)
urlpatterns = [
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
    path('addClassObjectAttribute',addClassObjectAttribute , name='addClassObjectAttribute'),

    path('getOntologies',getOntologies , name='getOntologies'),
    path('createOntology',createOntology , name='createOntology'),
    path('getItemsByLabels', getItemsByLabels, name= 'getItemsByLabels'),
    path('collectEntity',collectEntity , name='collectEntity'),
]