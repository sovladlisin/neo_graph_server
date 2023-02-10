from django.contrib import admin

from django.db import models
from .models import Entity, Resource, TextRelation, Markup


class ResourceAdmin(admin.ModelAdmin):
    model = Resource
class EntityAdmin(admin.ModelAdmin):
    model = Entity
class TextRelationAdmin(admin.ModelAdmin):
    model = TextRelation
class MarkupAdmin(admin.ModelAdmin):
    model = Markup
    


admin.site.register(Resource, ResourceAdmin)
admin.site.register(Entity, EntityAdmin)
admin.site.register(TextRelation, TextRelationAdmin)
admin.site.register(Markup, MarkupAdmin)