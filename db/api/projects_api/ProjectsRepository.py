from db.models import Project, ProjectPage, ProjectPageBlock, ProjectEmbedding
from db.api.ontology.OntologyRepository import OntologyRepo
from db.api.gpt_api.GptRepository import GptRepository
import json
from db.api.ontology.namespace import *
import time
import requests
from user_auth.models import Account

class ProjectsRepo:

    def __init__(self, account: Account):
        self.account = account

        if account.is_admin:
            self.projects = Project.objects.all()
        else:
            self.projects = Project.objects.all().filter(account__pk = account.pk)
            
        pass

    def collect_project(self, project):
        res_selected_classes_uris = json.loads(project.res_selected_classes_uris)
        res_star_classes_uris = json.loads(project.res_star_classes_uris)

        pages = ProjectPage.objects.all().filter(project__pk=project.id)

        ontologies_uris = json.loads(project.ontologies_uris)
        res_ontologies_uris = project.res_ontologies_uris

        onto_rep = OntologyRepo(self.account, ontology_uri='')

        ontologies_nodes = []
        for uri in ontologies_uris:
            ontologies_nodes.append(onto_rep.getNodeByUri(uri=uri))

        res_ontology_node = onto_rep.getNodeByUri(uri=res_ontologies_uris)

        result = {
            'id': project.id,
            'name': project.name,
            'pages': [self.collect_page(page) for page in pages],
            'ontologies_uris': ontologies_uris,
            'res_ontologies_uris': res_ontologies_uris,

            'ontologies_nodes': ontologies_nodes,
            'res_ontology_node': res_ontology_node,

            'selected_classes_uris': json.loads(project.selected_classes_uris),
            'res_selected_classes_uris': res_selected_classes_uris,
            'res_star_classes_uris': res_star_classes_uris
            # 'account': self.user.pk ,
        }
        resource_star_items = []
        resource_gallery_items = []
        
        if len(project.res_selected_classes_uris) > 0 and len(res_selected_classes_uris) != 0:
            res_ontology_uri = project.res_ontologies_uris
            o = OntologyRepo(self.account, res_ontology_uri)
            resource_gallery_items = o.getItemsByUris(res_selected_classes_uris)
            o.close()   

        if len(project.res_ontologies_uris) > 0 and len(res_star_classes_uris) != 0:
            res_ontology_uri = project.res_ontologies_uris
            o = OntologyRepo(self.account, res_ontology_uri)
            resource_star_items = o.getItemsByUris(res_star_classes_uris)
            o.close()


        result['resource_star_items'] = resource_star_items
        result['resource_gallery_items'] = resource_gallery_items
        return result

    def getProjects(self):
        return [self.collect_project(pr) for pr in self.projects]
    
    def getProject(self,id):
        print('GET_PROJECT', id)
        return self.collect_project(self.projects.filter(pk = id).first())
    
    def createProject(self, name,ontologies_uris, res_ontologies_uris):
        project = Project(name=name,ontologies_uris=json.dumps(ontologies_uris), res_ontologies_uris=res_ontologies_uris, account = self.account)
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
    
    
    def collect_page(self, page):
        temp = {}
        temp['id'] = page.id
        temp['name'] = page.name
        temp['project_id'] = page.project_id
        temp['blocks'] = [self.collect_page_block(block) for block in ProjectPageBlock.objects.all().filter(page__pk=page.id)]
        return temp
    
    def collect_page_with_data(self, page):
        temp = self.collect_page(page)
        return temp


    def updatePage(self, params):
        id = params.get('id', -1)
        name = params.get('name', '')
        project_id = params.get('project_id', -1)
        blocks = params.get('blocks', [])

        if id != -1:
            page = ProjectPage.objects.get(id=int(id))
        else:
            page = ProjectPage()


        project = Project.objects.all().filter(id = int(project_id))
        if project.count() == 1:
            page.project = project.first()

        for b in blocks:
            self.updatePageBlock(b)

        page.name = name
        page.save()
        return self.collect_page(page)
    
    def getPage(self, id):
        return self.collect_page_with_data(ProjectPage.objects.get(pk=int(id)))

    def deletePage(self, id):
        page = ProjectPage.objects.get(pk=int(id))
        page.delete()
        return id
    
# -------------------------------------------- PAGE BLOCKS ----------------------------------------------------------------
    def collect_page_block(self, block):
        data = json.loads(block.data)

        temp = {}
        temp['page_id'] = block.page.id
        temp['data'] = json.loads(block.data)
        temp['block_type'] =  block.block_type
        temp['id'] = block.id
        temp['x'] = block.x
        temp['y'] = block.y
        temp['w'] = block.w
        temp['h'] = block.h
        temp['data_nodes'] = {
            'nodes': [],
            'arcs': []
        }

        if block.block_type not in ['card_list', 'bullet_list', 'media', 'media_slide_show']:
            return temp
        
        ontology_uri = data.get('ontology_uri', None)
        class_uri = data.get('class_uri', None)

        if None in [class_uri, ontology_uri]:
            return temp
        

        onto = OntologyRepo(self.account, ontology_uri=ontology_uri)
        nodes = onto.getClassObjects(class_uri=class_uri)
        temp['data_nodes']['nodes'] = nodes

        return temp
    
    def updatePageBlock(self, params):
        id = params.get('id', -1)
        page_id = params.get('page_id', -1)
        x = params.get('x', 1)
        y = params.get('y', 1)
        h = params.get('h', 1)
        w = params.get('w', 1)
        block_type = params.get('block_type', 'text')
        data = params.get('data', {})

        if id != -1:
            block = ProjectPageBlock.objects.get(id=int(id))
        else:
            block = ProjectPageBlock()


        page = ProjectPage.objects.all().filter(id = int(page_id))
        if page.count() == 1:
            block.page = page.first()

        block.x = x
        block.y = y
        block.h = h
        block.w = w
        block.block_type = block_type
        block.data = json.dumps(data)


        block.save()
        return self.collect_page_block(block)
        
    
    def deletePageBlock(self, id):
        block = ProjectPageBlock.objects.get(pk=int(id))
        block.delete()
        return id
    

# ---------------------------------------------------------------------------------------

    def collect_project_embedding(self, project_embedding):
        temp = {}
        temp['id'] = project_embedding.id
        temp['project_id'] = project_embedding.project.id
        temp['is_complete'] = project_embedding.is_complete
        temp['is_running'] = project_embedding.is_running
        temp['progress'] = project_embedding.progress
        return temp

    def getProjectEmbedding(self, id):
        project = self.projects.filter(pk=id).first()

        project_embedding = ProjectEmbedding.objects.all().filter(project__pk=project.id)
        if project_embedding.count() == 0:
            project_embedding = ProjectEmbedding(project = project)
            project_embedding.save()
        else:
            project_embedding = project_embedding.first()
        return self.collect_project_embedding(project_embedding)



    def getNodeNameByUri(self, nodes, uri):
        for n in nodes:
            if n.get('data', {}).get('uri', '') == uri:
                return n.get('data',{}).get('params_values',{}).get(LABEL, ['1','1'])[0].split('@')[0]
        return '3'

    def collectProjectEmdeddings(self, id):
        project = self.projects.filter(pk=id).first()
        gr = GptRepository()

        project_embedding = ProjectEmbedding.objects.all().filter(project__pk=project.id)
        if project_embedding.count() == 0:
            project_embedding = ProjectEmbedding(project = project)
        else:
            project_embedding = project_embedding.first()

        project_embedding.is_running = True
        project_embedding.progress = 0
        project_embedding.save()
        

        ontologies_uris = json.loads(project.ontologies_uris)
        res_ontologies_uris = project.res_ontologies_uris
        ontologies_uris.append(res_ontologies_uris)


        source_nodes = []
        source_arc_names = {}
        for o_uri in ontologies_uris:
            o = OntologyRepo(self.account, o_uri)
            result_nodes, r_arcs, result_arc_names = o.getFullOntology()
            for ran in result_arc_names:
                source_arc_names[ran.get('data', {}).get('uri', '')]= ran.get('data',{}).get('params_values',{}).get(LABEL, ['1','1'])[0].split('@')[0]
            print(source_arc_names)
            for node in result_nodes:
                ontology_uri = node.get('data',{}).get('ontology_uri', '')
                node_uri = node.get('data',{}).get('uri', '')
                node_full = o.collectEntity(node_uri)

                attributes_names = node_full.get('data',{}).get('attributes', [])

                object_class_name_string = node_full['data'].get('obj_class_name', None)

                is_class = False
                is_object = False
                type_string = ''
                if CLASS in node.get('data',{}).get('labels',[]):
                    is_class = True
                    type_string = 'Класс'
                elif OBJECT in node.get('data',{}).get('labels',[]):
                    is_object = True
                    type_string = 'Объект'

                if type_string != '':
                    name = node.get('data',{}).get('params_values',{}).get(LABEL, ['',''])[0].split('@')[0]
                    description = node.get('data',{}).get('params_values',{}).get(COMMENT, '')
                    attributes = node.get('attributes', [])
                    if object_class_name_string: # этот параметр в collect_entity только у объектов
                        node_text = object_class_name_string + ' ' + name + '\n' # Первая строка (название и принадлежность)
                    else:
                        node_text = 'Класс ' + name + '\n' # Первая строка (название и принадлежность)
                    

                    if description != '' and description != 'Описание':
                        node_text += description + '\n' # Описание

                    node_text += 'Тип: ' + type_string + '\n' # Описание

                    for attr_key in node.get('data',{}).get('params_values',{}).keys():
                        attr_text = ''
                        if attr_key != 'file' and attr_key != 'uri' and attr_key not in [LABEL, COMMENT]:
                            attr_text = self.getNodeNameByUri(attributes, attr_key)
                            attr_text += ': ' + node.get('data',{}).get('params_values',{}).get(attr_key, '')
                        
                        if attr_text != '':
                            node_text += attr_text + ' \n'

                    node['full_text'] = node_text
                    print(node['data']['uri'], node_text)
                    source_nodes.append(node)
        
        


        gr = GptRepository()
        # gr.create_embedding(project_embedding,source_nodes)


        return True
    
    def getProjectMessage(self, id, text):
        project = self.projects.filter(pk=id).first()

        project_embedding = ProjectEmbedding.objects.all().filter(project__pk=project.id)
        if project_embedding.count() == 0:
            return None
        else:
            project_embedding = project_embedding.first()

        gr = GptRepository()
        message = gr.answer_index(project_embedding, text)


        return message