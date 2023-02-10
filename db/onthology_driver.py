from gettext import translation
from .driver import NeoApp
from .onthology_namespace import *
import json
import datetime
from  neo4j import time
from .models import Resource, Markup
import uuid
from pprint import pprint
from datetime import date, datetime
class Onthology:

    def __init__(self, uri, user, password, domain = ''):
        self.driver = NeoApp(uri,user, password)
        self.main_label = RESOURCE_NAMESPACE if len(domain) == 0 or domain == 'Resource' else domain

    def getDomainOntologies(self):
        return self.driver.get_nodes_by_labels([DOMAIN_ONTOLOGY])

    def getClasses(self):
        if self.main_label == RESOURCE_NAMESPACE:
            res = self.driver.get_nodes_by_labels([CLASS])
            return list(filter(lambda x: self.main_label == "/".join([item for item in x.get('uri').split('/')[:-1]]), res))
        else:
            query = "MATCH (node:`{class_l}`:`{domain}`) RETURN node".format(class_l=CLASS,  domain=self.main_label)
            return self.driver.custom_query(query, 'node')

        

    def getEntityById(self, id):
        return self.driver.get_node_by_ID(id)
   
    def getEntityByUri(self, uri):
        return self.driver.get_node_by_params({'uri': uri})

    def getObjectWithClassByObjectUri(self, uri):
        return self.driver.get_node_with_parent_by_uri(uri, [CLASS])

    def getSubClassesById(self, id):
        return self.driver.get_node_children(id, [SUB_CLASS], [CLASS])

    def getParentClasses(self):
        if self.main_label == RESOURCE_NAMESPACE:
            res = self.driver.get_node_without_children([CLASS], [SUB_CLASS], [CLASS])
            return list(filter(lambda x: self.main_label == "/".join([item for item in x.get('uri').split('/')[:-1]]), res))
        else:
            query = "MATCH (node:`{class_l}`:`{domain}`) WHERE NOT (node) - [:`{r}`] -> (:`{class_l}`) RETURN node".format(class_l=CLASS, r=SUB_CLASS, domain=self.main_label)
            return self.driver.custom_query(query, 'node')
    def getClassAttributes(self, uri):
        class_node = self.driver.get_node_by_params({'uri': uri})
        attributes = self.driver.get_node_children(class_node.id, [PROPERTY_DOMAIN],[PROPERTY_LABEL])
        attributes_obj = self.driver.get_node_children(class_node.id, [PROPERTY_DOMAIN],[PROPERTY_LABEL_OBJECT])
        return class_node, attributes, attributes_obj

    def getClassById(self, id):
        class_node = self.driver.get_node_by_ID(id)

        attributes, attributes_types, attributes_obj, attributes_types_obj = self.driver.collect_class(class_node.id)

        objects = self.driver.get_nodes_by_labels([class_node.get('uri')])
        return class_node, attributes, objects, attributes_types, attributes_obj, attributes_types_obj

    def getClassObjects(self, id):
        node = self.driver.get_node_by_ID(id)
        return self.driver.get_nodes_by_labels([node.get('uri')])

    def getClassObject(self, id):
        object_request = self.driver.get_node_with_parent_by_ID(id, [CLASS])

        node = object_request['object']
        class_node = object_request['class']

        class_sig, parents_sig, type_nodes, class_node = self.driver.collect_signatures(class_node['uri'])

        signature = {}
        if class_sig is not None:
            signature = {**signature, **class_sig}

        for p in parents_sig:
            if p is not None:
                signature = {**signature, **p}

        attributes = type_nodes
        attributes_obj = self.driver.get_connections_with_labels(id, [OBJECT])
        resources = self.getObjectVisualItems(id)

        return node, signature, attributes, attributes_obj, resources

    def nodeToDict(self, node):
        result = {}
        if node is None:
            return None
        result['id'] = node.id
        result['labels'] = list(node.labels)
        result['params'] = list(node.keys())
        for param in node.keys():
            value = node.get(param)
            if isinstance(value, time.DateTime):
                pass
            elif isinstance(value, uuid.UUID):
                result[param] = str(value)
            else:
                result[param] = value
        return result

    def relToDict(self, node):
        result = {}
        if node is None:
            return None
        result['id'] = node.id
        result['labels'] = [node.type]
        result['params'] = list(node.keys())
        result['start_node'] = self.nodeToDict(node.start_node)
        result['end_node'] = self.nodeToDict(node.end_node)
        for param in node.keys():
            result[param] = node.get(param)
        return result

    def updateEntity(self, new_node):
        props = {}
        obj_props = {}
        for param in new_node:
            if isinstance(new_node[param], dict):
                obj_props[param] = new_node[param]
            else: 
                props[param] = new_node[param]
        
        updated_node = self.driver.set_node(new_node['id'], props)

        for key in obj_props:
            rel = obj_props[key]
            self.driver.delete_relation_by_id(rel['id'])
            if rel['direction'] == 1 and rel['object'] is not None:
                self.driver.create_relation_forward(new_node['id'], rel['object']['id'], [rel['label']], {})
            if rel['direction'] == 0 and rel['object'] is not None:
                self.driver.create_relation_forward( rel['object']['id'],new_node['id'], [rel['label']], {})

        return updated_node

    def createEntity(self, labels, new_node):
        props = {}
        obj_props = {}
        for param in new_node:
            if isinstance(new_node[param], dict):
                obj_props[param] = new_node[param]
            else: 
                props[param] = new_node[param]
        
        props['uri'] = self.getRandomUri()
        created_node = self.driver.create_node(labels, props)

        for key in obj_props:
            rel = obj_props[key]
            if (rel['direction'] == 1):
                if rel['object'] is not None:
                    self.driver.create_relation_forward(created_node.id, rel['object']['id'], [key], {})
            if (rel['direction'] == 0):
                if rel['object'] is not None:
                    self.driver.create_relation_forward( rel['object']['id'],created_node.id, [key], {})

        return created_node

    def createDigitalCarrier(self, file_id, file_name, carrier_uri, type_uri, object_id):
        carrier = self.driver.create_node(['Resource', DIGITAL_CARRIER_URI, OBJECT], {'uri': carrier_uri})

        carrier_class = self.driver.get_node_by_uri(DIGITAL_CARRIER_URI)
        self.driver.create_relation_forward(carrier.id,carrier_class.id, [RDF_TYPE], {})

        appelation = self.driver.create_node(['Resource', APPELATION, OBJECT], {NOTE_URI: "{id}_{name}".format(id=file_id, name=file_name), 'uri': carrier_uri + '_Appellation'})
        appelation_class = self.driver.get_node_by_uri(APPELATION)
        self.driver.create_relation_forward(appelation.id,appelation_class.id, [RDF_TYPE], {})
        
        self.driver.create_relation_forward(carrier.id,appelation.id, [IDENTIFIED_BY], {})

        type_node = self.driver.get_nodes_by_labels(['Resource', type_uri])[0]
        self.driver.create_relation_forward(carrier.id,type_node.id, [HAS_TYPE], {})


        self.driver.create_relation_forward(carrier.id,object_id, [CARRIES], {})


        return carrier

    def getRandomUri(self):
        return 'http://erlangen-crm.org/current/' +  str(uuid.uuid4())

    def getCorpusResources(self, corpus_uri, res_types, text_search, lang_id, actor_id, place_id, genre_id,time_search, chunk_number, chunk_size):
        data, data_size, counters = self.driver.getResources(corpus_uri, res_types, text_search, lang_id, actor_id, place_id, genre_id,time_search, chunk_number, chunk_size)
        for res in data:
            for m in res['media']:
                if m:
                    m['resources'] = self.getMediaVisualItems(m['id'])
            res['media_carrier'] = self.getMediaVisualItems(res['resource']['id'])
            # res['notations'] = Markup.objects.all().filter(original_object_uri=res['resource']['uri']).count()


        return data, data_size, counters

    def getResourceCorpus(self, node_id):
        query = "MATCH (node) - [:`{inc}`] -> (n) where ID(n) = {node_id} RETURN node".format(inc=CORPUS_RELATION, node_id=node_id)
        r = self.driver.custom_query(query, 'node')
        for item in r:
            return item.id

    def close(self):
        self.driver.close()
        return True

    # 0 - none
    # image
    # note
    # article
    def connectDigitalToResource(self, file_type, file_id, file_name, resource_id, note, picture_type = None):
        carrier = self.driver.create_node(['Resource', DIGITAL_CARRIER_URI, OBJECT], {'uri': self.getRandomUri(), NOTE_URI: note})

        # that its digital
        carrier_class = self.driver.get_node_by_uri(DIGITAL_CARRIER_URI)
        self.driver.create_relation_forward(carrier.id,carrier_class.id, [RDF_TYPE], {})

        # that its mp4/audio etc.
        if file_type == 'jpg':
            file_type = 'jpeg'
        recource_type_uri = 'http://erlangen-crm.org/current/' + file_type
   

        
        recource_type = self.driver.get_node_by_uri(recource_type_uri)
        self.driver.create_relation_forward(carrier.id,recource_type.id, [HAS_TYPE], {})

        appelation = self.driver.create_node(['Resource', APPELATION, OBJECT], {NOTE_URI: note, 'uri': self.getRandomUri() + "-{id}".format(id=file_id)})
        appelation_class = self.driver.get_node_by_uri(APPELATION)
        self.driver.create_relation_forward(carrier.id,appelation_class.id, [RDF_TYPE], {})
        self.driver.create_relation_forward(carrier.id,appelation.id, [IDENTIFIED_BY], {})

        # create visual item
        vi_type = ''
        if picture_type:
            vi_type = picture_type
        visual_item = self.driver.create_node(['Resource', VISUAL_ITEM, OBJECT], {'uri':  self.getRandomUri(), TITLE: file_name, NOTE_URI: note, 'res_type': vi_type})
        self.driver.create_relation_forward(carrier.id,visual_item.id, [CARRIES], {})

        # connect to resource

        resource = self.getEntityById(resource_id)
        resource = self.nodeToDict(resource)
        if PERSON_URI in resource['labels']:
            self.driver.create_relation_forward(visual_item.id,resource_id, [DEPICTS], {})
        elif CORPUS in resource['labels']:
            self.driver.create_relation_forward(resource_id,visual_item.id, [CORPUS_RELATION], {})
       
        else:
            self.driver.create_relation_forward(visual_item.id,resource_id, [REFERS_TO], {})
        
        # incorporate to corpus
        if CORPUS not in resource['labels']:
            corpsus_id = self.getResourceCorpus(resource_id)
            self.driver.create_relation_forward(corpsus_id,visual_item.id, [CORPUS_RELATION], {})


        return carrier, visual_item

    def createText(self, new_node, corpus_id, origin_r_id, trans_r_id, commentary_r_id):
        props = {}
        obj_props = {}
        for param in new_node:
            if isinstance(new_node[param], dict):
                obj_props[param] = new_node[param]
            else: 
                props[param] = new_node[param]
        props['uri'] = self.getRandomUri()
        created_node = self.driver.create_node(['Resource', LING_OBJECT], props)


        for key in obj_props:
            rel = obj_props[key]
            if (rel['direction'] == 1):
                if rel['object'] is not None:
                    self.driver.create_relation_forward(created_node.id, rel['object']['id'], [key], {})
            if (rel['direction'] == 0):
                if rel['object'] is not None:
                    self.driver.create_relation_forward( rel['object']['id'],created_node.id, [key], {})

        origin_node = created_node
        transaltion_node = self.driver.create_node(['Resource', LING_OBJECT, OBJECT], {'uri': self.getRandomUri()})
        commentary_node = self.driver.create_node(['Resource', LING_OBJECT, OBJECT], {'uri': self.getRandomUri()})

        # create carriers
        carrier_class = self.driver.get_node_by_uri(DIGITAL_CARRIER_URI)

        origin_carrier = self.driver.create_node(['Resource', DIGITAL_CARRIER_URI, OBJECT], {'uri': self.getRandomUri()})
        self.driver.create_relation_forward(origin_carrier.id,carrier_class.id, [RDF_TYPE], {})
        transaltion_carrier = self.driver.create_node(['Resource', DIGITAL_CARRIER_URI, OBJECT], {'uri': self.getRandomUri()})
        self.driver.create_relation_forward(transaltion_carrier.id,carrier_class.id, [RDF_TYPE], {})
        commentary_carrier = self.driver.create_node(['Resource', DIGITAL_CARRIER_URI, OBJECT], {'uri': self.getRandomUri()})
        self.driver.create_relation_forward(commentary_carrier.id,carrier_class.id, [RDF_TYPE], {})


        recource_type = self.driver.get_node_by_uri('http://erlangen-crm.org/current/txt')
        self.driver.create_relation_forward(origin_carrier.id,recource_type.id, [HAS_TYPE], {})
        self.driver.create_relation_forward(transaltion_carrier.id,recource_type.id, [HAS_TYPE], {})
        self.driver.create_relation_forward(commentary_carrier.id,recource_type.id, [HAS_TYPE], {})

        # connect carriers

        self.driver.create_relation_forward(origin_carrier.id,origin_node.id, [CARRIES], {})
        self.driver.create_relation_forward(transaltion_carrier.id,transaltion_node.id, [CARRIES], {})
        self.driver.create_relation_forward(commentary_carrier.id,commentary_node.id, [CARRIES], {})


        # create appelations
        origin_appelation = self.driver.create_node(['Resource', APPELATION, OBJECT], { 'uri': self.getRandomUri() + "-{id}".format(id=origin_r_id)})
        translation_appelation = self.driver.create_node(['Resource', APPELATION, OBJECT], { 'uri': self.getRandomUri() + "-{id}".format(id=trans_r_id)})
        commentary_appelation = self.driver.create_node(['Resource', APPELATION, OBJECT], { 'uri': self.getRandomUri() + "-{id}".format(id=commentary_r_id)})

        appelation_class = self.driver.get_node_by_uri(APPELATION)
        
        self.driver.create_relation_forward(origin_appelation.id,appelation_class.id, [RDF_TYPE], {})
        self.driver.create_relation_forward(translation_appelation.id,appelation_class.id, [RDF_TYPE], {})
        self.driver.create_relation_forward(commentary_appelation.id,appelation_class.id, [RDF_TYPE], {})

        # connect appelations

        self.driver.create_relation_forward(origin_carrier.id,origin_appelation.id, [IDENTIFIED_BY], {})
        self.driver.create_relation_forward(transaltion_carrier.id,translation_appelation.id, [IDENTIFIED_BY], {})
        self.driver.create_relation_forward(commentary_carrier.id,commentary_appelation.id, [IDENTIFIED_BY], {})

        # connect origin + trans + commentary
        self.driver.create_relation_forward(origin_node.id,transaltion_node.id, [HAS_TRANSLATION], {})
        self.driver.create_relation_forward(origin_node.id,commentary_node.id, [HAS_COMMENTARY], {})


        # incorporate to corpus
        self.driver.create_relation_forward(corpus_id,origin_node.id, [CORPUS_RELATION], {})

        origin_node = self.nodeToDict(origin_node)
        transaltion_node = self.nodeToDict(transaltion_node)
        commentary_node = self.nodeToDict(commentary_node)
        return origin_node['uri'], transaltion_node['uri'], commentary_node['uri'], origin_node

    def createEvent(self, actors_ids, place_id, time_string, resource_id, connection_type ):

        for item in actors_ids:
            actor_id = item['actor_id']
            label = item['title']



            event_class = self.driver.get_node_by_uri(EVENT)
            appelation_class = self.driver.get_node_by_uri(APPELATION)
            time_class = self.driver.get_node_by_uri(TIME)
            object_class = self.driver.get_node_by_uri(OBJECT)

            created_event = self.driver.create_node(['Resource', EVENT, OBJECT], {'uri': self.getRandomUri(), LABEL: label})
            self.driver.create_relation_forward(created_event.id,event_class.id, [RDF_TYPE], {})
            self.driver.create_relation_forward(created_event.id,object_class.id, [RDF_TYPE], {})

            self.driver.create_relation_forward(created_event.id,actor_id, [EVENT_PERMORMED_BY], {})

            self.driver.create_relation_forward(created_event.id,resource_id, [connection_type], {})


            if place_id != -1:
                self.driver.create_relation_forward(created_event.id,place_id, [EVENT_TOOK_PLACE], {})

            if len(time_string) != 0:
                created_time = self.driver.create_node(['Resource', TIME, OBJECT], {'uri': self.getRandomUri()})
                self.driver.create_relation_forward(created_time.id,time_class.id, [RDF_TYPE], {})
                self.driver.create_relation_forward(created_time.id,object_class.id, [RDF_TYPE], {})



                created_time_appelation = self.driver.create_node(['Resource', TIME, OBJECT], {'uri': self.getRandomUri(), NOTE_URI: time_string})
                self.driver.create_relation_forward(created_time_appelation.id,appelation_class.id, [RDF_TYPE], {})
                self.driver.create_relation_forward(created_time_appelation.id,object_class.id, [RDF_TYPE], {})

                self.driver.create_relation_forward(created_event.id,created_time.id, [TIME_RELATION], {})


                self.driver.create_relation_forward(created_time.id,created_time_appelation.id, [IDENTIFIED_BY], {})

            

        return True

    


        

    def getObjectVisualItems(self,node_id):
        s = self.driver.custom_query(
            'match (k) <- [:`{refers}` | :`{depicts}`] - (g) <- [:`{carries}`] - (f) - [:`{identified}`] -> (node) where ID(k) = {id} return node'.format(refers=REFERS_TO, carries=CARRIES, identified=IDENTIFIED_BY, id=node_id, depicts=DEPICTS), 'node')
        response = []
        for i in s:
            node_uri = i['uri']
            if '-' not in node_uri:
                pass
            else:

                r_id = node_uri.split('-')[-1]
                try:
                    f = Resource.objects.get(pk=int(r_id))
                    temp = {}
                    temp['name'] = f.name
                    temp['source'] = f.source.url
                    temp['id'] = f.pk
                    temp['type'] = f.resource_type
                    response.append({
                        'file': temp,
                        'node': self.getVisualItemDesc(i.id)
                    })
                except:
                    pass
        return response

    def getVisualConnectedObjects(self, node_id):
        s = self.driver.custom_query(
            'match (node) - [:`{refers}` | :`{depicts}` | :`{corpus_r}`] - (g) where ID(g) = {id} return node'.format(refers=REFERS_TO, id=node_id, depicts=DEPICTS, corpus_r=CORPUS_RELATION), 'node')

        return s

    def deleteObject(self, node_id):
        node = self.driver.get_node_by_ID(node_id)
        node = self.nodeToDict(node)
        if VISUAL_ITEM in node['labels']:
            mvi = self.getMediaVisualItems(node_id)
            self.driver.delete_resource_by_ID(node_id)

            for m in mvi:
                pk = m['file']['id']
                res = Resource.objects.get(pk=int(pk))
                res.delete()
               

        elif LING_OBJECT in node['labels']:
            self.deleteText(node_id)
        else:
            self.driver.delete_node_by_ID(node_id)
        return True

    def cleanUp(self):
        resources = Resource.objects.all()
        counter = 0
        for r in resources:
            node = self.driver.get_node_by_uri(r.original_object_uri)
            if node:
                pass
            else:
                r.delete()
                counter += 1

        return counter

    def deleteText(self, node_id):
        origin = self.driver.get_node_by_ID(node_id)
        origin_node = self.nodeToDict(origin)
        origin_uri = origin_node['uri']

        nodes = self.driver.custom_query(
            'match (origin) - [:`{translation}` | :`{commentary}`] -> (node) where ID(origin) = {id} return node'.format(translation=HAS_TRANSLATION, commentary =HAS_COMMENTARY, id=node_id ), 'node')
        for n in nodes:
            t_n = self.nodeToDict(n)
            resource_f = Resource.objects.all().filter(original_object_uri = t_n['uri'])
            if resource_f.count() > 0:
                resource_f = resource_f.first()
                resource_f.delete()

        resource_f = Resource.objects.all().filter(original_object_uri = origin_uri)
        if resource_f.count() > 0:
            resource_f = resource_f.first()
            resource_f.delete()

        
        s = self.driver.delete_text_by_ID(node_id)

        return True

    def getMediaVisualItems(self,node_id):
        s = self.driver.custom_query(
            'match (g) <- [:`{carries}`] - (f) - [:`{identified}`] -> (node) where ID(g) = {id} return node'.format(refers=REFERS_TO, carries=CARRIES, identified=IDENTIFIED_BY, id=node_id, depicts=DEPICTS), 'node')
        response = []
        for i in s:
            node_uri = i['uri']
            if '-' not in node_uri:
                pass
            else:

                r_id = node_uri.split('-')[-1]
                try:
                    f = Resource.objects.get(pk=int(r_id))
                    temp = {}
                    temp['name'] = f.name
                    temp['source'] = f.source.url
                    temp['id'] = f.pk
                    temp['type'] = f.resource_type
                    response.append({
                        'file': temp,
                    })
                except:
                    pass
        return response

    def getVisualItemDesc(self, id):
        s = self.driver.custom_query(
            'match (node) <- [:`{carries}`] - (f) - [:`{identified}`] -> (n) where ID(n) = {id} return node'.format(carries=CARRIES, identified=IDENTIFIED_BY, id=id), 'node')
        for i in s:
            return self.nodeToDict(i)

        


    def addClassAttribute(self, class_id, type_uri, props):
        type_node = self.driver.get_node_by_params({'uri': type_uri})
        type_id = type_node.id
        created_attr = self.driver.create_node([self.main_label,PROPERTY_LABEL, 'Resource'], props)
        attr_id = created_attr.id
        
        new_rel1 = self.driver.create_relation_forward(attr_id, class_id, [PROPERTY_DOMAIN], {})
        new_rel2 = self.driver.create_relation_forward(attr_id, type_id, [PROPERTY_RANGE], {})

        return created_attr

    def addClassAttributeObject(self, class_id, attribute_class_id, props):
        created_attr = self.driver.create_node([self.main_label,PROPERTY_LABEL_OBJECT, 'Resource'], props)
        attr_id = created_attr.id

        new_rel1 = self.driver.create_relation_forward(attr_id, class_id, [PROPERTY_DOMAIN], {})
        new_rel2 = self.driver.create_relation_forward(attr_id, attribute_class_id, [PROPERTY_RANGE], {})

        return created_attr

    def getResources(self):
        result = {
            'actors_count': 0,
            'places_count': 0,
            'texts_count': 0,
            'video_count': 0,
            'audio_count': 0,
            'images_count': 0,

            'actors': [],
            'places': [],
            'texts': [],
            'video': [],
            'audio': [],
            'images': [],
        }
        res = self.driver.get_nodes_by_labels([OBJECT])
        for r in res:
            temp = self.nodeToDict(r)
            if PERSON_URI in temp['labels']:
                result['actors_count'] = result['actors_count'] + 1
                result['actors'].append(temp)
            if PLACE_URI in temp['labels']:
                result['places_count'] = result['places_count'] + 1
                result['places'].append(temp)

            if LING_OBJECT in temp['labels']:
                result['texts_count'] = result['texts_count'] + 1
                result['texts'].append(temp)

            if VISUAL_ITEM in temp['labels']:
                result['images_count'] = result['images_count'] + 1
                result['images'].append(temp)



        return result

    def getCorpuses(self):
        result = []
        res = self.driver.get_node_without_children_reverse([CORPUS],[CORPUS_RELATION], [CORPUS])
        for r in res:
            # query = "match (n)-[:`{r}`*]-(node:`{l}`) where ID(n)={id} return node".format(r=CORPUS_RELATION, l=LING_OBJECT, id=r.id)
            # res2 = self.driver.custom_query(query, 'node')

            temp = self.nodeToDict(r)
            texts = []
            resources = []
            # for t in res2:
            #     texts.append(self.nodeToDict(t))
            #     resources.append(self.getObjectVisualItems(t.id))
            temp['texts'] = texts
            temp['resources'] = resources
            result.append(temp)

        return result


    def getSubCorpuses(self,id):
        res = self.driver.get_node_parents(id,[CORPUS_RELATION], ['Resource'])
        return res

    def getClassesWithSignatures(self):
        query = "match (node:`{class_}`) where not node.signature is null return node".format(class_=CLASS)
        res = self.driver.custom_query(query, 'node')
        return res

    def getClassFullSignature(self, uri):
        return self.driver.collect_signatures(uri)

    def getObjectsByClassUri(self, uri):

        query = "match (node) - [:`{sub}`*] -> (s) where s.uri='{uri}' match(n) -[:`{rdf_type}`] -> (node) return n".format(sub=SUB_CLASS, uri=uri,rdf_type=RDF_TYPE)
        objects = self.driver.custom_query(query, 'n')
        query2 = "match (node) where node.uri='{uri}' match(n) -[:`{rdf_type}`] -> (node) return n".format(uri=uri,rdf_type=RDF_TYPE)
        objects2= self.driver.custom_query(query2, 'n')
        res= objects + objects2
        return res
        keys = [uri]
        for c in classes:
            keys.append(c.get('uri'))
        
        query2 = "match (n:`{named}`) -[:`{rdf_type}`] -> (s) where s.uri in {keys} return n".format(named=OBJECT,rdf_type=RDF_TYPE, keys=json.dumps(keys))
        res = self.driver.custom_query(query2, 'n')
        return res

    def deleteEntity(self, id):
        return self.driver.delete_node_by_ID(id)

    def updateIndex(self):
        print(self.main_label)
        index_name = self.main_label + '/index'
       
        if self.main_label == RESOURCE_NAMESPACE:
            labels = [CORPUS, PLACE_URI, PERSON_URI,DIGITAL_CARRIER_URI,VISUAL_ITEM,LING_OBJECT, LANGUAGE,GENRE]
            params_query = "match (n) <- [:`{domain}`] - (r:`{datatype}`) return r.uri as node".format(domain=PROPERTY_DOMAIN, datatype=PROPERTY_LABEL, namespace=self.main_label)

        else:
            params_query = "match (n:`{namespace}`) <- [:`{domain}`] - (r:`{datatype}`) return r.uri as node".format(domain=PROPERTY_DOMAIN, datatype=PROPERTY_LABEL, namespace=self.main_label)
            labels = [self.main_label]
        
        params = self.driver.custom_query(params_query, 'node')
        params.append('http://www.universals.com/ontologies/2020/1/cultural_universals#Название')
        params.append('https://www.geonames.org/ontology#name')
        params = list(set(params))

        
        config = "{analyzer: 'russian'}"
        create_query = "CALL db.index.fulltext.createNodeIndex( '{index_name}', {labels}, {params}, {config})".format(index_name=index_name,labels = labels, params=params,config=config )
        drop_query = "CALL db.index.fulltext.drop('{index_name}')".format(index_name=index_name)

        try:
            self.driver.run_command(drop_query)
            print('deleted')
        except:
            pass
        self.driver.run_command(create_query)

        return True

    def searchIndex(self, search_array, connector):

        def transform_search(array, connector='OR'):
            res = ''
            temp = []
            for s in array:
                temp.append(s)
                temp.append(connector)
            for s in temp[:-1]:
                res += s + '~2 '
            return res[:-1]

        index_name = self.main_label + '/index'
        search = search_array
        query = "CALL db.index.fulltext.queryNodes('{index_name}', '{search}') YIELD node RETURN node".format(search=search,index_name=index_name )
        return self.driver.custom_query(query, 'node')

    def getWorkspace(self, id):
        node = self.driver.get_node_by_ID(id)
        labels1 = self.driver.transform_labels([HAS_TRANSLATION])
        labels2 = self.driver.transform_labels([IS_TRANSLATION_OF])

        query = "match (n) - [r:{labels}] - (node) where ID(n) = {id} return r".format(id=id, labels = labels1)
        query2 = "match (n) - [r:{labels}] - (node) where ID(n) = {id} return r".format(id=id, labels = labels2)
        
        res = self.driver.custom_query(query, 'r')
        rel_name = HAS_TRANSLATION
        if len(res) == 0:
            rel_name = IS_TRANSLATION_OF
            res = self.driver.custom_query(query2, 'r')
        if len(res) == 0:
            return None

        rel = res[0]
        if rel_name == HAS_TRANSLATION:
            origin = rel.start_node
            translation = rel.end_node
        else:
            origin = rel.end_node
            translation = rel.start_node

        query3 = "match (n) - [r:`{label}`] -> (node) where ID(n) = {id} return node".format(id=origin.id, label = HAS_COMMENTARY)
        commentary_node = self.driver.custom_query(query3, 'node')[0]
        

        origin_node = self.driver.get_node_by_ID(origin.id)
        translation_node = self.driver.get_node_by_ID(translation.id)

        return origin_node,translation_node,commentary_node

    def getNodesByUris(self, uris):
        query = "match (n) where n.uri in {uris} return n".format(uris=json.dumps(uris))
        return self.driver.custom_query(query, 'n')

    def getNodesByUrisInDict(self, uris):
        return self.driver.get_nodes_by_uris_in_dict(uris)

    def deleteOntology(self):
        index_name = self.main_label + '/index'

        drop_query = "match (n:Resource) where n10s.rdf.getIRINamespace(n.uri) = '{namespace}/' detach delete n".format(namespace=self.main_label)
        drop_query2 = "match (n) where n.uri = '{namespace}' detach delete n".format(namespace=self.main_label)
        drop_query3 = "CALL db.index.fulltext.drop('{index_name}')".format(index_name=index_name)

        self.driver.run_command(drop_query)
        self.driver.run_command(drop_query2)

        try:
            self.driver.run_command(drop_query3)
        except:
            pass
        return True

    def close(self):
        self.driver.close()
        return True


