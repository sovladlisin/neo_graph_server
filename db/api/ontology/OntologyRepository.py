from db.api.ontology.NeoRepository import NeoRepo
from core.settings import *
import uuid
import pprint 
from .namespace import *

class OntologyRepo:

    def __init__(self, ontology_uri):

        self.nr = NeoRepo(DB_URI,DB_USER, DB_PASSWORD, ontology_uri)
        self.ontology_uri = ontology_uri


        ontology_node = self.nr.get_node_by_uri(uri=ontology_uri)
        if ontology_node is not None:
            self.signature = ontology_node['data']['params_values'].get(ONTOLOGY_SIGNATURE,[ontology_uri])
        else:
            self.signature = []

    def close(self):
        self.nr.close()

    def getFullOntology(self):
        labels_not = ['Ontology', 'ResourceOntology', 'Pattern']

        result_nodes = []
        result_arcs = []
        result_arc_names = []
        for s in self.signature:
            nodes, arcs = self.nr.get_nodes_and_arcs_by_labels(labels=[s])
            temp = [s]
            temp.append(OBJECT_PROPERTY)
            arc_names = self.nr.get_nodes_by_labels(temp)

            result_nodes += nodes
            result_arcs += arcs
            result_arc_names += arc_names

        r_arcs = []
        r_arcs_dict = {}
        for a in result_arcs:
            if a['data']['id'] not in r_arcs_dict.keys():
                r_arcs.append(a)
                r_arcs_dict[a['data']['id']] = 1

        return result_nodes, r_arcs, result_arc_names
    
    def getFullOntologyByUri(self, uri):
        labels = [uri]
        nodes, arcs = self.nr.get_nodes_and_arcs_by_labels(labels=labels)
        arc_names = self.nr.get_nodes_by_labels([OBJECT_PROPERTY, uri])
        return nodes, arcs, arc_names
    

    def getOntologies(self):
        return self.nr.get_nodes_by_labels(['Ontology'])
    
    def getResourceOntologies(self):
        return self.nr.get_nodes_by_labels(['ResourceOntology'])
    
    def getPatternOntologies(self):
        return self.nr.get_nodes_by_labels(['Pattern'])

    def getRandomUri(self):
        return self.ontology_uri + '/' +  str(uuid.uuid4())

    def createOntology(self, title, comment):
        labels = ['Ontology']
        params = {}
        params[LABEL]= title
        params[COMMENT]= comment
        params[URI]= self.ontology_uri
        params[ONTOLOGY_SIGNATURE] = [self.ontology_uri]
        
        ontology_node = self.nr.create_node(labels=labels,props=params)
        return ontology_node
    

    # ontology_type: Resource, Ontology, Pattern
    def branchOntology(self, title, comment, ontology_type, new_ontology_uri):
        labels = [ontology_type]
        params = {}
        params[LABEL]= title
        params[COMMENT]= comment
        params[URI]= new_ontology_uri

        signature = self.signature
        signature.append(new_ontology_uri)

        params[ONTOLOGY_SIGNATURE] = signature
        
        ontology_node = self.nr.create_node(labels=labels,props=params)
        return ontology_node
    
    def createResourceOntology(self, title, comment):
        labels = ['ResourceOntology']
        params = {}
        params[LABEL]= title
        params[COMMENT]= comment
        params[URI]= self.ontology_uri
        
        ontology_node = self.nr.create_node(labels=labels,props=params)
        return ontology_node

    def branchResourceOntology(self, title, comment):
        labels = ['ResourceOntology']
        params = {}
        params[LABEL]= title
        params[COMMENT]= comment
        params[URI]= self.ontology_uri
        
        ontology_node = self.nr.create_node(labels=labels,props=params)
        return ontology_node
    
    def createPatternOntology(self, title, comment):
        labels = ['Pattern']
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
    
    def getItemByUri(self, uri):
        return self.nr.get_node_by_uri(uri)
    
    def getClassObjects(self, class_uri):
        return self.nr.collect_nodes_from_root_uri(uri = class_uri)

    def copyOntology(self, origin_ontology_uri):
        nodes, arcs, names = self.getFullOntologyByUri(origin_ontology_uri)
        print('\n\n')
        pprint.pprint(nodes)
        print('\n\n')
        pprint.pprint(arcs)
        print('\n\n')

        uris_dict = {}

        # return None
        for node in nodes:
            data = node.get('data', {})

            old_uri = data['params_values']['uri']
            new_uri = self.getRandomUri()
            uris_dict[old_uri] = new_uri
            data['params_values']['uri'] = new_uri

            node_labels = [self.ontology_uri]
            node_labels += data.get('labels', [])
            if origin_ontology_uri in node_labels:
                node_labels.remove(origin_ontology_uri)

            print('\n\n')
            pprint.pprint(node_labels)
            print('\n\n')

            new_node = self.nr.create_node(labels=node_labels, props=data.get('params_values', {}))

       

        for arc in arcs:
            data = arc.get('data', {})
            old_label = data['uri']

            start_node_uri = arc.get('source','')
            end_node_uri = arc.get('target','')

            start = uris_dict[start_node_uri]
            end = uris_dict[end_node_uri]
            label = uris_dict.get(old_label, old_label)

            rel_node = self.nr.create_relation(from_uri=start, to_uri=end, labels=[label])

        return self.getFullOntology()

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


        return created_nodes, created_rels



    def collectPatternsTarget(self, patterns):
        result = []
        for pattern in patterns:
            query = pattern.get('target_query', '')
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
    
    def createRelation(self, source, target):
        
        from_node = self.nr.get_node_by_uri(uri=source)
        to_node = self.nr.get_node_by_uri(uri=target)

        if CLASS in from_node['data']['labels']:
            if CLASS in to_node['data']['labels']:
                rel = self.nr.create_relation(from_uri=source, to_uri=target, labels=[SUB_CLASS])

        return rel

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
    
    def getItemsByUris(self, uris):
        return self.nr.get_nodes_by_uris(uris)
    
    def updateEntity(self,uri, params, obj_params = None):
        props = {}
        for l in params:
            props[l] = params[l]

        result_nodes = [self.nr.set_node(uri=uri, props=props)]
        result_arcs = []




        if (obj_params):
            for p in obj_params:
                # print(p)
                value = p.get('value', None)
                field = p.get('field', None)
                if value is not None:
                    if p['direction'] == 1:
                        self.nr.delete_relation(p['relation']['id'])
                        rel = self.nr.create_relation(from_uri=uri, to_uri=value['data']['uri'], labels=[field['data']['uri']])
                        result_arcs.append(rel)
                    else:
                        self.nr.delete_relation(p['relation']['id'])
                        rel = self.nr.create_relation(from_uri=value['data']['uri'], to_uri=uri, labels=[field['data']['uri']])
                        result_arcs.append(rel)
                else:
                    rel = p.get('relation', None)
                    if rel is not None:
                        self.nr.delete_relation(p['relation']['id'])

            
        # add deleted arcs
        return result_nodes, result_arcs
