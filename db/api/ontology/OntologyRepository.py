from db.api.ontology.NeoRepository import NeoRepo
from core.settings import *
import uuid

from .namespace import *

class OntologyRepo:

    def __init__(self, ontology_uri):

        self.nr = NeoRepo(DB_URI,DB_USER, DB_PASSWORD, ontology_uri)
        self.ontology_uri = ontology_uri

    def close(self):
        self.nr.close()

    def getFullOntology(self):
        nodes, arcs = self.nr.get_nodes_and_arcs_by_labels(labels=[self.ontology_uri])
        return nodes, arcs

    def getOntologies(self):
        return self.nr.get_nodes_by_labels(['Ontology'])

    def getRandomUri(self):
        return self.ontology_uri + '/' +  str(uuid.uuid4())

    def createOntology(self, title, comment):
        labels = ['Ontology', self.ontology_uri]
        params = {}
        params[LABEL]= title
        params[COMMENT]= comment
        params[URI]= self.ontology_uri
        
        ontology_node = self.nr.create_node(labels=labels,props=params)
        return ontology_node

    def getItemsByLabels(self, labels, custom_q = None):
        if custom_q is not None:
            return self.nr.custom_query(query=custom_q, name='node')
        local_labels = labels
        local_labels.append(self.ontology_uri)
        return self.nr.get_nodes_by_labels(local_labels)

    def createClass(self, title, comment, parent_uri = None):
        uri = self.getRandomUri()
        labels = [CLASS, self.ontology_uri]
        params = {}
        params[LABEL]= title
        params[COMMENT]= comment
        params[URI]= uri

        class_node = self.nr.create_node(labels=labels,props=params)

        if parent_uri is not None:
            rel_labels = [SUB_CLASS]
            rel_node = self.nr.create_relation(from_uri=uri, to_uri=parent_uri, labels=rel_labels)
            return [class_node], [rel_node]
        return [class_node], []

    def updateClass(self, uri, params, attributes):
        class_node = self.nr.get_node_by_uri(uri=uri)
        result_nodes = self.nr.set_node(uri, params)
        
        return result_nodes, []



    def createObject(self, title, comment, class_uri):
        uri = self.getRandomUri()
        labels = [OBJECT, self.ontology_uri, class_uri]
        params = {}
        params[LABEL]= title
        params[COMMENT]= comment
        params[URI]= uri

        object_node = self.nr.create_node(labels=labels,props=params)

        rel_labels = [HAS_TYPE]
        rel_node = self.nr.create_relation(from_uri=uri, to_uri=class_uri, labels=rel_labels)

        return [object_node], [rel_node]
    
    def deleteEntity(self, uri):
        node = self.nr.get_node_by_uri(uri)

        deleted_nodes_uris = []

        # if CLASS in node['data']['labels']:
        deleted_uri = self.nr.delete_node_by_uri(uri)
        deleted_nodes_uris.append(deleted_uri)

        return deleted_nodes_uris

    def deleteRel(self, id):
        return self.nr.delete_relation(id)

    def deleteClass(self, uri):
        self.nr.delete_node_by_uri(uri)
        return uri


    def apply_pattern(self, pattern):
        nodes = pattern['nodes']
        rels = pattern['arcs']

        nodes_dict = {}

        created_nodes = []
        created_rels = []


        for n in nodes:
            node_uri = ''

            data = n['data']
            id = n['id']

            is_main = data.get('is_main', False)
            is_main_uri = data.get('is_main_uri', '')

            is_create = data.get('is_create', False)
            is_create_label = data.get('is_create_label', [])

            is_select = data.get('is_select', False)
            is_select_node = data.get('is_select_node', None)

            is_const = data.get('is_const', False)
            is_const_node = data.get('is_const_node', None)
            is_const_general = data.get('is_const_general', None)

            tag = data.get('tag', '')

            if is_main:
                node_uri = is_main_uri
            if is_select:
                node_uri = is_select_node['data']['uri']
            if is_create:
                labels = [self.ontology_uri, tag ]
                uri = self.getRandomUri()
                params = {}
                params[LABEL] = is_create_label
                params[URI]= uri

                created_node = self.nr.create_node(labels=labels,props=params)
                created_nodes.append(created_node)
                node_uri = created_node['data']['uri']

            if is_const:
                if is_const_node['data'].get('is_const_filter', False) is False:
                    node_uri = is_const_node['data']['uri']
                pass
            
            nodes_dict[id] = node_uri
        
        for r in rels:
            source = r.get('source', '')
            target = r.get('target', '')
            label = r.get('label', '')

            source_uri = nodes_dict[source]
            target_uri = nodes_dict[target]

            rel = self.nr.create_relation(source_uri, target_uri, labels=[label])
            created_rels.append(rel)

        print('created_nodes\n', created_nodes)

        return created_nodes, created_rels



    def collectPatternsTarget(self, patterns):
        result = []
        for pattern in patterns:
            query = pattern.get('target_query', '')
            print(query, self.nr.custom_query(query=query, name='node'))
            pattern['target_nodes'] = self.nr.custom_query(query=query, name='node')


            result.append(pattern)

        return result

    def collectEntity(self, uri):
        node = self.nr.get_node_by_uri(uri)
        attributes = []
        obj_attributes = []
        if CLASS in node['data']['labels']:
            attributes = self.nr.collect_signatures_datatype_custom(uri=uri)
            obj_attributes = self.nr.collect_signatures_object_custom(uri=uri)
            

        if OBJECT in node['data']['labels']:
            object_classes = self.nr.get_node_parents(uri=uri, relation_labels=[HAS_TYPE], parent_labels=[CLASS])
            object_class_uri = object_classes[0]['data']['uri']

            attributes = self.nr.collect_signatures_datatype_custom(uri=object_class_uri)
            obj_attributes = self.nr.collect_signatures_object_custom(uri=object_class_uri)

            if len(obj_attributes):
                att_uris = []
                for obj_att in obj_attributes:
                    att_uri = obj_att['field']['data']['uri']
                    att_uris.append(att_uri)
                obj_rels = self.nr.get_node_with_arcs_by_arcs(uri=uri,arcs_labels=att_uris)


                new_obj_attributes = []
                for o in obj_attributes:
                    for v in obj_rels:
                        if o['field']['data']['uri'] == v['data']['uri']:
                            start_node = v['data']['start_node']
                            end_node = v['data']['end_node']
                            placed = start_node if start_node['data']['uri'] != uri else end_node
                            o['value'] = placed
                            o['relation'] = v
                    new_obj_attributes.append(o)         
                obj_attributes = new_obj_attributes


        node['data']['attributes'] = attributes
        node['data']['obj_attributes'] = obj_attributes
        return node

    def addClassAtribute(self, uri, label):
        labels = [DATATYPE_PROPERTY, self.ontology_uri]
        props = {}
        props[LABEL] = label
        props[URI] = self.getRandomUri()

        attr_node = self.nr.create_node(labels=labels, props=props)

        rel = self.nr.create_relation(from_uri=attr_node['data']['uri'], to_uri=uri, labels=[PROPERTY_DOMAIN])

        return [attr_node], [rel]

    def addClassObjectAtribute(self, uri, label, range_uri):
        labels = [OBJECT_PROPERTY, self.ontology_uri]
        props = {}
        props[LABEL] = label
        props[URI] = self.getRandomUri()

        attr_node = self.nr.create_node(labels=labels, props=props)

        rel = self.nr.create_relation(from_uri=attr_node['data']['uri'], to_uri=uri, labels=[PROPERTY_DOMAIN])
        rel2 = self.nr.create_relation(from_uri=attr_node['data']['uri'], to_uri=range_uri, labels=[PROPERTY_RANGE])

        return [attr_node], [rel,rel2]
    
    def updateEntity(self,uri, params, obj_params = None):
        props = {}
        for l in params:
            props[l] = params[l]

        result_nodes = [self.nr.set_node(uri=uri, props=props)]
        result_arcs = []

        if (obj_params):
            for p in obj_params:
                print(p)
                value = p['value']
                field = p['field']
                if value is not None:
                    if p['direction'] == 1:
                        rel = self.nr.create_relation(from_uri=uri, to_uri=value['data']['uri'], labels=[field['data']['uri']])
                        result_arcs.append(rel)
                    else:
                        rel = self.nr.create_relation(from_uri=value['data']['uri'], to_uri=uri, labels=[field['data']['uri']])
                        result_arcs.append(rel)
                else:
                    if p['relation'] is not None:
                        self.nr.delete_relation(p['relation']['id'])

            
        # add deleted arcs
        return result_nodes, result_arcs
