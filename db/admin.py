from django.contrib import admin

from django.db import models
from .models import Entity, Resource, TextRelation, Markup, Project, ProjectPageBlock, ProjectEmbedding


class ResourceAdmin(admin.ModelAdmin):
    model = Resource
class EntityAdmin(admin.ModelAdmin):
    model = Entity
class TextRelationAdmin(admin.ModelAdmin):
    model = TextRelation
class MarkupAdmin(admin.ModelAdmin):
    model = Markup

class ProjectAdmin(admin.ModelAdmin):
    model = Project  

class ProjectPageBlockAdmin(admin.ModelAdmin):
    model = ProjectPageBlock 

class ProjectEmbeddingAdmin(admin.ModelAdmin):
    model = ProjectEmbedding 


admin.site.register(Resource, ResourceAdmin)
admin.site.register(ProjectEmbedding, ProjectEmbeddingAdmin)
admin.site.register(Entity, EntityAdmin)
admin.site.register(TextRelation, TextRelationAdmin)
admin.site.register(Markup, MarkupAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectPageBlock, ProjectPageBlockAdmin)