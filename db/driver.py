from os import dup
from db.onthology_namespace import CARRIES, IDENTIFIED_BY, PROPERTY_DOMAIN, PROPERTY_LABEL, PROPERTY_LABEL_OBJECT, PROPERTY_RANGE, SUB_CLASS
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
import json
from operator import itemgetter
import datetime
from  neo4j import time
from .onthology_namespace import *
import uuid

class NeoApp:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    def get_nodes_by_uris_in_dict(self, uris):
        def _service_func(tx,uris):
            query = "match (n) where n.uri in {uris} return n".format(uris=json.dumps(uris))
            request = tx.run(query)
            result = {}
            for record in request:
                temp = record['n']
                result[temp.get('uri')] = temp
            return result

        with self.driver.session() as session:
            result = session.write_transaction(_service_func, uris)
        
        return result

    def get_nodes_by_labels(self, labels):

        def _service_func(tx,labels):
            t_labels = self.transform_labels(labels)
            query = 'MATCH (n:{labels}) RETURN n AS node'.format(labels=t_labels)
            request = tx.run(query)
            return [record['node'] for record in request]

        with self.driver.session() as session:
            result = session.write_transaction(_service_func, labels)
        
        return list(result)

    def get_node_by_uri(self, uri):
        def _service_func(tx,uri):
            query = "MATCH (n) WHERE n.uri = '{uri}' RETURN n AS node".format(uri=uri)
            request = tx.run(query)
            return [record['node'] for record in request]

        with self.driver.session() as session:
            result = session.write_transaction(_service_func, uri)
        
        return result[0] if len(result) > 0 else None

    def get_nodes_by_params(self, labels, params):

        def _service_func(tx,labels, params):
            search_query = "WHERE"
            iter = 0
            for param in params:
                value = params[param]
                key = param
                link = " " if iter == 0 else " AND"  
                search_query += "{link} n.`{key}` = {value} ".format(link=link ,key=key, value=json.dumps(value))
                iter += 1
            t_labels = self.transform_labels(labels)

            query = "MATCH (n:{labels}) {search} RETURN n AS node".format(labels=t_labels, search=search_query)
            request = tx.run(query)
            return [record["node"] for record in request]

        with self.driver.session() as session:
            result = session.write_transaction(_service_func, labels, params)
        
        return list(result)

    def get_node_with_parent_by_ID(self, id, parent_labels):
        def _service_func(tx,id):
            t_labels = self.transform_labels(parent_labels)
            query = "match(n) where ID(n) = {id} match(c:{labels}) where c.uri in labels(n) return n,c".format(id=id, labels=t_labels)
            request = tx.run(query)
            return [{"object": record["n"], "class": record["c"]} for record in request]

        with self.driver.session() as session:
            result = session.write_transaction(_service_func,id)
        
        return result[0]

    def get_node_with_parent_by_uri(self, uri, parent_labels):
        def _service_func(tx,uri):
            t_labels = self.transform_labels(parent_labels)
            query = "match(n) where n.uri = '{uri}' match(c:{labels}) where c.uri in labels(n) return n,c".format(uri=uri, labels=t_labels)
            request = tx.run(query)
            return [{"object": record["n"], "class": record["c"]} for record in request]

        with self.driver.session() as session:
            result = session.write_transaction(_service_func,uri)
        
        return result[0]

    def getResources(self, corpus_uri, res_types, text_search, lang_id, actor_id, place_id, genre_id, time_search, chunk_number, chunk_size):
        def _service_func(tx,corpus_uri, res_types, text_search, lang_id, actor_id, place_id,genre_id, time_search, chunk_number, chunk_size):
            q = '''
           match (:`http://erlangen-crm.org/current/F74_Corpus` {uri: 'AFDSHGTKCNGFKDOMDLFG'})-[:`http://erlangen-crm.org/current/P165_incorporates`]->(resource) where resource:`http://erlangen-crm.org/current/E33_Linguistic_Object` or resource:`http://erlangen-crm.org/current/E36_Visual_Item`

            optional match (resource)<-[role]-(e:`http://erlangen-crm.org/current/F8_Preparing_to_publish`)
            optional match (actor:`http://erlangen-crm.org/current/E21_Person`)<-[:`http://erlangen-crm.org/current/P14_carried_out_by`]-(e)
            optional match (e)-[:`http://erlangen-crm.org/current/P7_took_place_at`]->(place:`http://erlangen-crm.org/current/E53_Place`)

            with resource,actor,place,type(role) as role

            optional match (op:`http://www.w3.org/2002/07/owl#ObjectProperty`) where op.uri=role
            optional match (resource)<-[:`http://erlangen-crm.org/current/P67_refers_to`]-(media)
            optional match (resource)-[:`http://erlangen-crm.org/current/P2_has_type`]->(genre:`http://erlangen-crm.org/current/F62_Genre`)
            optional match (resource)-[:`http://erlangen-crm.org/current/P72_has_language`]->(lang:`http://erlangen-crm.org/current/E56_Language`)

            with resource,media as media,genre as genres, lang,op as role,actor,place

            with resource,media,genres,lang,role,actor,place

            with resource,collect(media) as media,collect(genres) as genres,lang,case role when null then null else {
                actor: actor,
                role: role,
                place: place
            } end as event

            return resource,media,genres,lang,collect(event) as events
            '''
            if len(corpus_uri) == 0:
                q = q.replace("{uri: 'AFDSHGTKCNGFKDOMDLFG'}","")
            else:
                q = q.replace('AFDSHGTKCNGFKDOMDLFG',corpus_uri)

            request = tx.run(q)

            result = []


            # res_types = []
            new_request = []
            # text_search = ''
            # lang_id = -1
            # actor_id = -1
            # place_id = -1
            # time_search = ''

            # chunk_size = 50
            # chunk_number = 1

            images = 0
            video = 0
            audio = 0
            notes = 0
            articles = 0
            langs = []
            actors = []
            places = []
            genres = []
            texts = 0

            langs_ids = []
            actors_ids = []
            places_ids = []
            genres_ids = []

            data_size = 0

            global_ids = []

            for record in request:
                check = True

                duplicate_check = False
                current_id = record['resource'].id
                if current_id in global_ids:
                    duplicate_check = True
                else:
                    global_ids.append(current_id)

                if duplicate_check == False:

                    current_res_type = record['resource'].get('res_type', '')

                    # collecting
                    # 
                    # 
                    if current_res_type != '':
                        images = images + 1 if 'image' == current_res_type else images
                        video = video + 1 if 'video' == current_res_type else video
                        audio = audio + 1 if 'audio' == current_res_type else audio
                        notes = notes + 1 if 'note' == current_res_type else notes
                        articles = articles + 1 if 'article' == current_res_type else articles

                    if LING_OBJECT in record['resource'].labels:
                        texts += 1

                    if record['lang'] and record['lang'].id not in langs_ids:
                        langs.append(self.nodeToDict(record['lang']))
                        langs_ids.append(record['lang'].id)
                    #
                    #  
                    # end collecting

                    res_type_check = True
                    if len(res_types) > 0:
                        if LING_OBJECT not in record['resource'].labels and current_res_type not in res_types:
                            res_type_check = False

                        if 'text' not in res_types and LING_OBJECT in record['resource'].labels:
                            res_type_check = False



                    if len(text_search) > 0 and text_search.lower() not in json.dumps(self.nodeToDict(record['resource']),ensure_ascii=False).lower():
                        check = False

                    lang_check = True if lang_id == -1 else False
                    if record['lang'] and lang_id == record['lang'].id:
                        lang_check = True
                    

                    actor_check = True if actor_id == -1 else False
                    place_check = True if place_id == -1 else False
                    for event in record['events']:
                        
                        # collecting
                        # 
                        # 
                        if event['actor'] and event['actor'].id not in actors_ids:
                            actors.append(self.nodeToDict(event['actor']))
                            actors_ids.append(event['actor'].id)
                        if event['place'] and event['place'].id not in places_ids:
                            places.append(self.nodeToDict(event['place']))
                            places_ids.append(event['place'].id)

                        # 
                        # 
                        # end collecting 


                        if actor_id != -1:
                            if event['actor'] and actor_id == event['actor'].id:
                                actor_check = True

                        if place_id != -1:
                            if event['place'] and place_id == event['place'].id:
                                place_check = True

                    genre_check = True if genre_id == -1 else False
                    for genre in record['genres']:

                        # collecting
                        # 
                        # 
                        if genre.id not in genres_ids:
                            genres.append(self.nodeToDict(genre))
                            genres_ids.append(genre.id)
                        # 
                        # 
                        # end collecting

                        if genre_id != -1 and genre_id == genre.id:
                            genre_check = True

                    if check and res_type_check and genre_check and actor_check and place_check and lang_check:
                        new_request.append(record)


            chunk_number = int(chunk_number)
            chunk_size = int(chunk_size)
            chunk_counter = 0
            start = chunk_size * (chunk_number - 1)
            end = chunk_size * chunk_number


            for record in new_request:
                data_size += 1

                chunk_counter += 1
                if chunk_counter <= end and chunk_counter > start:

                    temp = {}
                    temp['resource'] = self.nodeToDict(record['resource'])
                    temp['media'] = []
                    temp['genres'] = []
                    temp['lang'] = self.nodeToDict(record['lang'])
                    temp['events'] = []

                    media_ids = []
                    for node1 in record['media']:
                        media_id = node1.id
                        if media_id in media_ids:
                            pass
                        else:
                            temp['media'].append(self.nodeToDict(node1))
                            media_ids.append(media_id)


                    genre_ids = [] 
                    for node2 in record['genres']:
                        genre_id = node2.id
                        if genre_id in genre_ids:
                            pass
                        else:
                            temp['genres'].append(self.nodeToDict(node2))
                            genre_ids.append(genre_id)

                    for node3 in record['events']:
                        temp2 = {}
                        temp2['actor'] = self.nodeToDict(node3['actor'])
                        temp2['role']= self.nodeToDict(node3['role'])
                        temp2['place']= self.nodeToDict(node3['place'])
                        temp['events'].append(temp2)

                    result.append(temp)

            counters = {
            'images': images,
            'video': video,
            'audio': audio,
            'notes': notes,
            'articles':articles,
            'langs': langs,
            'actors': actors,
            'places': places,
            'genres': genres,
            'texts': texts
            }


            return result, data_size, counters

        with self.driver.session() as session:
            result, request_size, counters = session.write_transaction(_service_func,corpus_uri, res_types, text_search, lang_id, actor_id, place_id, genre_id,time_search, chunk_number, chunk_size)
        return result, request_size ,counters

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
            if isinstance(value, uuid.UUID):
                result[param] = str(value)
            else:
                result[param] = value
        return result

    def collect_class(self, id):
        def _service_func(tx,id):
      
            query = "match (c) <- [:`{domain}`] - (atr) - [:`{range}`] -> (type) where ID(c) = {id} return atr,type".format(id=id,domain=PROPERTY_DOMAIN, range=PROPERTY_RANGE)
            res = tx.run(query)

            attributes = []
            attributes_obj = []
            attributes_types = {}
            attributes_types_obj = {}

            for r in res:
                print(r)
                if (PROPERTY_LABEL in list(r['atr'].labels)):
                    attributes.append(r['atr'])
                    attributes_types[r['atr'].id] = r['type']

                if (PROPERTY_LABEL_OBJECT in list(r['atr'].labels)):
                    attributes_obj.append(r['atr'])
                    attributes_types_obj[r['atr'].id] = r['type']
            return attributes, attributes_types, attributes_obj, attributes_types_obj
            

        with self.driver.session() as session:      
            result = session.write_transaction(_service_func,id)
        
        return result

    def collect_signatures(self, uri):
        
        def _service_func(tx,uri):
            class_node = self.get_node_by_uri(uri)
            query = "match(n)-[:`{sub}`*]->(s) where n.uri='{uri}' return apoc.convert.fromJsonMap(s.signature) as parent_signs".format(sub=SUB_CLASS, uri=uri)
            request = tx.run(query)

            class_sig_string = class_node.get('signature', '{}')
            class_sig = json.loads(class_sig_string)
            parents_sig = []
            keys = []
            for record in request:
                parents_sig.append(record['parent_signs'])

            def getList(dict):
                return list(map(itemgetter(0), dict.items()))
            keys = getList(class_sig)
            for s in parents_sig:
                if s is not None:
                    keys = keys + getList(s)
            
            query2 = "match (n) where n.uri in {keys} return n".format(keys=json.dumps(keys))
            request2 = tx.run(query2)

            type_nodes = []
            for record in request2:
                type_nodes.append(record['n'])

            return class_sig, parents_sig, type_nodes, class_node

        with self.driver.session() as session:      
            result = session.write_transaction(_service_func,uri)
        
        return result

    def get_node_by_params(self, params):

        def _service_func(tx, params):
            search_query = "WHERE"
            iter = 0
            for param in params:
                value = params[param]
                key = param
                link = " " if iter == 0 else " AND"  
                search_query += "{link} n.`{key}` = {value} ".format(link=link ,key=key, value=json.dumps(value))
                iter += 1

            query = "MATCH (n) {search} RETURN n AS node".format(search=search_query)
            request = tx.run(query)
            return [record["node"] for record in request]

        with self.driver.session() as session:
            result = session.write_transaction(_service_func, params)
        
        return result[0]
    
    def get_all_labels(self):

        def _service_func(tx):
            request = tx.run("MATCH (n) RETURN distinct labels(n), count(*)")
            return [{"label": record["labels(n)"][0], "count": record["count(*)"]} for record in request]

        with self.driver.session() as session:
            result = session.write_transaction(_service_func)
        
        return result

    def run_command(self, command):
        def _service_func(tx, command):
            request = tx.run(command)
            return request

        with self.driver.session() as session:
            result = session.write_transaction(_service_func, command)
        
        return True


    def get_node_by_ID(self, id):
        def _service_func(tx,id):
            query = "MATCH (n) WHERE ID(n) = {id} RETURN n as node".format(id=id)
            request = tx.run(query)
            return [record["node"] for record in request]

        with self.driver.session() as session:
            result = session.write_transaction(_service_func, id)
        
        return result[0]

    def get_node_children(self, id, relation_labels, child_labels):
        def _service_func(tx,id,relation_labels,child_labels):
            t_child_labels = self.transform_labels(child_labels)
            t_relation_labels = self.transform_labels(relation_labels)
            query = "MATCH (node:{child_labels}) -[r:{relation_labels}]-> (n) WHERE ID(n) = {id} RETURN node".format(id=id, relation_labels=t_relation_labels, child_labels=t_child_labels)
            
            request = tx.run(query)
            return [record["node"] for record in request]

        with self.driver.session() as session:
            result = session.write_transaction(_service_func, id,relation_labels,child_labels)
        
        return result

    def get_node_parents(self, id, relation_labels, child_labels):
        def _service_func(tx,id,relation_labels,child_labels):
            t_child_labels = self.transform_labels(child_labels)
            t_relation_labels = self.transform_labels(relation_labels)
            query = "MATCH (node:{child_labels}) <-[r:{relation_labels}]- (n) WHERE ID(n) = {id} RETURN node".format(id=id, relation_labels=t_relation_labels, child_labels=t_child_labels)
            
            request = tx.run(query)
            return [record["node"] for record in request]

        with self.driver.session() as session:
            result = session.write_transaction(_service_func, id,relation_labels,child_labels)
        return result

    def get_node_without_children(self, parent_labels ,relations, child_labels):
        def _service_func(tx, parent_labels ,relations, child_labels):
            t_child_labels = self.transform_labels(child_labels)
            t_relation_labels = self.transform_labels(relations)
            t_parent_labels = self.transform_labels(parent_labels)

            query = "MATCH (node:{parent_label}) WHERE NOT (node) - [:{relation}] -> (:{child_label}) RETURN node".format(
                relation=t_relation_labels, 
                child_label=t_child_labels, 
                parent_label=t_parent_labels
                )
            request = tx.run(query)
            return [record["node"] for record in request]

        with self.driver.session() as session:
            result = session.write_transaction(_service_func, parent_labels ,relations, child_labels)
        
        return result

    def get_node_without_children_reverse(self, parent_labels ,relations, child_labels):
        def _service_func(tx, parent_labels ,relations, child_labels):
            t_child_labels = self.transform_labels(child_labels)
            t_relation_labels = self.transform_labels(relations)
            t_parent_labels = self.transform_labels(parent_labels)

            query = "MATCH (node:{child_label}) WHERE NOT (node) <- [:{relation}] - (:{parent_label}) RETURN node".format(
                relation=t_relation_labels, 
                child_label=t_child_labels, 
                parent_label=t_parent_labels
                )
            request = tx.run(query)
            return [record["node"] for record in request]

        with self.driver.session() as session:
            result = session.write_transaction(_service_func, parent_labels ,relations, child_labels)
        
        return result

    def get_connections_with_labels(self, id, labels):
        def _service_func(tx,id, labels):
            t_labels = self.transform_labels(labels)

            query = "MATCH (node) - [r] - (n:{labels}) WHERE ID(node) = {id} RETURN n,r".format(id=id, labels=t_labels)
            request = tx.run(query)
            return [record["r"] for record in request]

        with self.driver.session() as session:
            result = session.write_transaction(_service_func, id, labels)
        
        return result

    def custom_query(self, query, params):
        def _service_func(tx,query,params):
            request = tx.run(query)
            return [record[params] for record in request]

        with self.driver.session() as session:
            result = session.write_transaction(_service_func,query,params)
        
        return result

    def create_node(self, labels, props):
        def _service_func(tx, labels, props):
            data = self.transform_props(props)
            t_labels = self.transform_labels(labels)
            query = ("CREATE (n:{labels} {data}) RETURN n AS node").format(labels=t_labels, data=data)
            request = tx.run(query)
            return [record["node"] for record in request]

        with self.driver.session() as session:
            result = session.write_transaction(_service_func,  labels, props)
        
        return result[0]

    def create_relation_forward(self, id_1, id_2, r_labels, props):
        def _service_func(tx, id_1, id_2, r_labels, props):
            data = self.transform_props(props)
            t_labels = self.transform_labels(r_labels)
            query = """
                    MATCH
                    (a),
                    (b)
                    WHERE ID(a) = {id_1} AND ID(b) = {id_2}
                    CREATE (a)-[r:{r_labels} {data}]->(b)
                    RETURN r
            """.format(id_1=id_1, id_2=id_2, r_labels = t_labels, data=data)

            request = tx.run(query, r_labels=r_labels, props=props)
            return [record["r"] for record in request]

        with self.driver.session() as session:
            result = session.write_transaction(_service_func,  id_1, id_2, r_labels, props)
        
        return result[0]

    def set_node(self, id, props):
        def _service_func(tx, id, props):
            data = self.transform_props(props)
            query = "MATCH (n) WHERE ID(n) = {id} SET n += {data} RETURN n AS node".format(id=id, data=data)
            request = tx.run(query)
            return [record["node"] for record in request]

        with self.driver.session() as session:
            result = session.write_transaction(_service_func,  id, props)
        
        return result[0]
    
    def delete_node_by_ID(self, id):
        def _service_func(tx, id):
            # data = self.transform_props(props)
            query = "MATCH (n) WHERE ID(n) = {id} DETACH DELETE n".format(id=id)
            request = tx.run(query)
            return True

        with self.driver.session() as session:
            result = session.write_transaction(_service_func,  id)
        
        return result

    def delete_text_by_ID(self, id):
        def _service_func(tx, id):
            # data = self.transform_props(props)
            query = 'match (a) - [:`{translation}` | :`{commentary}`] -> (b) <- [:`{carries}`] - (c) - [:`{identified}`] -> (d) where ID(a) = {id} detach delete a,b,c,d'.format(translation=HAS_TRANSLATION, commentary =HAS_COMMENTARY, id=id, carries=CARRIES, identified=IDENTIFIED_BY)
            request = tx.run(query)
            return True

        with self.driver.session() as session:
            result = session.write_transaction(_service_func,  id)
        
        return result

    def delete_resource_by_ID(self, id):
        def _service_func(tx, id):
            # data = self.transform_props(props)
            query = "match (g) <- [:`{carries}`] - (f) - [:`{identified}`] -> (node) where ID(g) = {id} detach delete g,f,node".format(carries=CARRIES, identified=IDENTIFIED_BY, id=id)
            request = tx.run(query)
            return True

        with self.driver.session() as session:
            result = session.write_transaction(_service_func,  id)
        
        return result

    def delete_relation_by_label(self, node_id, relation_labels, direction):
        def _service_func(tx, node_id, relation_labels):
            r_labels = self.transform_labels(relation_labels)

            if direction == 0:
                query = "MATCH (n)<-[r:{labels}]-() WHERE ID(n) = {id} DELETE r".format(id=node_id, labels=r_labels)
            else:
                query = "MATCH (n)-[r:{labels}]->() WHERE ID(n) = {id} DELETE r".format(id=node_id, labels=r_labels)

            request = tx.run(query)
            return True

        with self.driver.session() as session:
            result = session.write_transaction(_service_func,  node_id, relation_labels)
        
        return result

    def delete_relation_by_id(self, rel_id):
        def _service_func(tx, rel_id):
            query = "MATCH ()-[r]-() WHERE ID(r) = {id} DELETE r".format(id=rel_id)
            request = tx.run(query)
            return True

        with self.driver.session() as session:
            result = session.write_transaction(_service_func,  rel_id)
        
        return result

    def transform_labels(self, labels):
        if len(labels) == 0:
            return '``'
        res = ''
        for l in labels:
            res +='`{l}`:'.format(l=l)
        return res[:-1]

    def transform_props(self, props):
        if len(props) == 0:
            return ''
        data = "{"
        # print(props)
        for p in props:
            temp = "`{p}`".format(p=p)
            temp +=':'
            temp += "{val}".format(val = json.dumps(props[p]))
            data += temp + ','
        data = data[:-1]
        data += "}"
        return data



        