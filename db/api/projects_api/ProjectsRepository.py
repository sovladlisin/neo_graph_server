from db.models import Project
from db.api.ontology.OntologyRepository import OntologyRepo
import json
class ProjectsRepo:

    def __init__(self):
        self.projects = Project.objects.all()
        pass

    def collect_project(self, project):
        res_selected_classes_uris = json.loads(project.res_selected_classes_uris)
        res_star_classes_uris = json.loads(project.res_star_classes_uris)
        result = {
            'id': project.id,
            'name': project.name,
            'ontologies_uris': json.loads(project.ontologies_uris),
            'res_ontologies_uris': project.res_ontologies_uris,
            'selected_classes_uris': json.loads(project.selected_classes_uris),
            'res_selected_classes_uris': res_selected_classes_uris,
            'res_star_classes_uris': res_star_classes_uris
            # 'account': self.user.pk ,
        }
        resource_star_items = []
        resource_gallery_items = []
        
        if len(project.res_selected_classes_uris) > 0 and len(res_selected_classes_uris) != 0:
            res_ontology_uri = project.res_ontologies_uris
            o = OntologyRepo(res_ontology_uri)
            resource_gallery_items = o.getItemsByUris(res_selected_classes_uris)
            o.close()   

        if len(project.res_ontologies_uris) > 0 and len(res_star_classes_uris) != 0:
            res_ontology_uri = project.res_ontologies_uris
            o = OntologyRepo(res_ontology_uri)
            resource_star_items = o.getItemsByUris(res_star_classes_uris)
            o.close()


        result['resource_star_items'] = resource_star_items
        result['resource_gallery_items'] = resource_gallery_items
        return result

    def getProjects(self):
        return [self.collect_project(pr) for pr in self.projects]
    
    def getProject(self,id):
        return self.collect_project(self.projects.filter(pk = id).first())
    
    def createProject(self, name,ontologies_uris, res_ontologies_uris):
        project = Project(name=name,ontologies_uris=json.dumps(ontologies_uris), res_ontologies_uris=res_ontologies_uris)
        project.save()
        return self.collect_project(project)
    
    def updateProject(self,id, name,selected_classes_uris, res_selected_classes_uris,res_star_classes_uris):
        project = self.projects.filter(pk=id).first()
        project.name = name
        project.selected_classes_uris = json.dumps(selected_classes_uris)
        project.res_selected_classes_uris = json.dumps(res_selected_classes_uris)
        project.res_star_classes_uris = json.dumps(res_star_classes_uris)
        
        project.save()
        return self.collect_project(project)
    
    def deleteProject(self,id):
        project = self.projects.filter(pk=id).first()
        project.delete()
        return id