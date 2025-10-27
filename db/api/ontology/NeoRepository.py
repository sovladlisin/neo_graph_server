from neo4j import GraphDatabase
from  neo4j import time
import uuid
import json 
from .namespace import *
from db.models import Resource, Entity
import base64
from io import StringIO, BytesIO
from PIL import Image


class NeoRepo:

    def __init__(self, uri, user, password, main_uri = ''):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.main_uri = main_uri
        pass

    def close(self):
        self.driver.close()

    def delete_node_by_labels(self, labels):
        def _service_func(tx, labels):
            t_labels = self.transform_labels(labels)
            query = "MATCH (n:{labels}) DETACH DELETE n".format(labels=t_labels)
            request = tx.run(query)
            return True

        with self.driver.session() as session:
            result = session.write_transaction(_service_func,  labels)
        
        return result

    def delete_node_by_uri(self, uri):
        def _service_func(tx, uri):
            # data = self.transform_props(props)
            query = "MATCH (n) WHERE n.uri = '{uri}' DETACH DELETE n".format(uri=uri)
            request = tx.run(query)
            return True

        with self.driver.session() as session:
            result = session.write_transaction(_service_func,  uri)
        
        return uri

    def create_node(self, labels, props):
        def _service_func(tx, labels, props):
            data = self.transform_props(props)
            t_labels = self.transform_labels(labels)
            query = ("CREATE (n:{labels} {data}) RETURN n AS node").format(labels=t_labels, data=data)
            request = tx.run(query)
            return [self.nodeToDict(record["node"]) for record in request]

        with self.driver.session() as session:
            result = session.write_transaction(_service_func,  labels, props)
        
        return result[0]

    def create_relation(self, from_uri, to_uri, labels):
        def _service_func(tx, from_uri, to_uri, labels):
            t_labels = self.transform_labels(labels)

            query = """
                    MATCH
                    (a),
                    (b)
                    WHERE a.uri = '{from_uri}' AND b.uri = '{to_uri}'
                    CREATE (a)-[r:{r_labels}]->(b)
                    RETURN r,a,b
            """.format(from_uri=from_uri, to_uri=to_uri, r_labels = t_labels)

            request = tx.run(query)
            return [self.relToDict(record["r"]) for record in request]

        with self.driver.session() as session:
            result = session.write_transaction(_service_func,  from_uri, to_uri, labels)
        
        return result[0]

    def delete_relation(self, id):
        def _service_func(tx, id):
            query = """
                    MATCH ()-[r]-()
                    WHERE id(r) = {id}
                    DELETE r
            """.format(id=id)

            request = tx.run(query)
            return id

        with self.driver.session() as session:
            result = session.write_transaction(_service_func,  id)
        
        return int(id)
    

    def get_nodes_and_arcs_by_labels(self, labels):

        def _service_func(tx,labels):

            if len(labels):
                t_labels = self.transform_labels(labels)
                query = 'MATCH (n:{labels}) WHERE NOT n:Ontology:Resource:Pattern OPTIONAL MATCH (n)-[r]-(d) WHERE NOT n:Ontology:ResourceOntology:Pattern RETURN n,r,d'.format(labels=t_labels)
            else:
                query = 'MATCH (n)-[r]-() RETURN n,r'

            request = tx.run(query)

            result_nodes = []
            result_arcs = []

            ids_nodes = []
            ids_arcs = []
            for record in request:
                if record['n'] is not None and record['n'].id not in ids_nodes:
                    result_nodes.append(self.nodeToDict(record['n']))
                    ids_nodes.append(record['n'].id)
                if record['r'] is not None and record['r'].id not in ids_arcs:
                    result_arcs.append(self.relToDict(record['r']))
                    ids_arcs.append(record['r'].id)
            return result_nodes, result_arcs

        with self.driver.session() as session:
            result_nodes, result_arcs = session.write_transaction(_service_func, labels)
        
        return result_nodes, result_arcs

    def set_node(self, uri, props):
        def _service_func(tx, uri, props):
            data = self.transform_props(props)
            query = "MATCH (n) WHERE n.uri = '{uri}' SET n += {data} RETURN n AS node".format(uri=uri, data=data)
            request = tx.run(query)
            return [self.nodeToDict(record["node"]) for record in request]

        with self.driver.session() as session:
            result = session.write_transaction(_service_func,  uri, props)

        return result[0]

    def update_entity(self, uri, params, node_params, rels_forward, rels_backward):
        props = {}
        obj_props = {}
        # for param in node_params:
        #     props[param] = new_node[param]
        
        updated_node = self.set_node(uri, params)

        # for key in obj_props:
        #     rel = obj_props[key]
        #     self.driver.delete_relation_by_id(rel['id'])
        #     if rel['direction'] == 1 and rel['object'] is not None:
        #         self.driver.create_relation_forward(new_node['id'], rel['object']['id'], [rel['label']], {})
        #     if rel['direction'] == 0 and rel['object'] is not None:
        #         self.driver.create_relation_forward( rel['object']['id'],new_node['id'], [rel['label']], {})

        return updated_node

    def get_node_by_uri(self, uri):
        def _service_func(tx,uri):
            query = "MATCH (n) WHERE n.uri = '{uri}' RETURN n AS node".format(uri=uri)
            request = tx.run(query)
            return [self.nodeToDict(record['node']) for record in request]

        with self.driver.session() as session:
            result = session.write_transaction(_service_func, uri)

        return result[0] if len(result) > 0 else None
    
    def get_nodes_by_uris(self, uris):
        def _service_func(tx,uris):
            uris_string = json.dumps(uris)
            query = "MATCH (n) WHERE n.uri in {uris} RETURN n AS node".format(uris=uris_string)
            request = tx.run(query)
            return [self.nodeToDict(record['node']) for record in request]

        with self.driver.session() as session:
            result = session.write_transaction(_service_func, uris)

        return result

    def get_node_with_arcs_by_arcs(self, uri, arcs_labels):
        def _service_func(tx,uri,arcs_labels):
            t_labels = self.transform_labels(arcs_labels, separator='|')

            query = "MATCH (n)-[r:{labels}]-(s) WHERE n.uri = '{uri}' RETURN s,r,n".format(uri=uri, labels=t_labels)
            request = tx.run(query)
            return [self.relToDict(record['r']) for record in request]

        with self.driver.session() as session:
            result = session.write_transaction(_service_func, uri,arcs_labels)

        return result

    def get_nodes_by_labels(self, labels):

        def _service_func(tx,labels):
            if len(labels):
                t_labels = self.transform_labels(labels)
                query = 'MATCH (n:{labels}) RETURN n AS node'.format(labels=t_labels)
            else:
                query = 'MATCH (n) RETURN n AS node'

            request = tx.run(query)
            return [self.nodeToDict(record['node']) for record in request]

        with self.driver.session() as session:
            result = session.write_transaction(_service_func, labels)
        
        
        return result

    def get_node_children(self, uri, relation_labels, child_labels):
        def _service_func(tx,uri,relation_labels,child_labels):

            if len(relation_labels) and len(child_labels):
                t_relation_labels = self.transform_labels(relation_labels)
                t_child_labels = self.transform_labels(child_labels)
                query = "MATCH (node:{child_labels}) -[r:{relation_labels}]-> (n) WHERE n.uri = '{uri}' RETURN node".format(uri=uri, relation_labels=t_relation_labels, child_labels=t_child_labels)
            elif len(relation_labels):
                t_relation_labels = self.transform_labels(relation_labels)
                query = "MATCH (node) -[r:{relation_labels}]-> (n) WHERE n.uri = '{uri}' RETURN node".format(uri=uri, relation_labels=t_relation_labels)
            elif len(child_labels):
                t_child_labels = self.transform_labels(child_labels)
                query = "MATCH (node:{child_labels}) -[r]-> (n) WHERE n.uri = '{uri}' RETURN node".format(uri=uri, child_labels=t_child_labels)
            
            request = tx.run(query)
            return [self.nodeToDict(record["node"]) for record in request]

        with self.driver.session() as session:
            result = session.write_transaction(_service_func, uri,relation_labels,child_labels)
        
        return result

    def get_node_parents(self, uri, relation_labels, parent_labels):
        def _service_func(tx,uri,relation_labels,parent_labels):

            if len(relation_labels) and len(parent_labels):
                t_relation_labels = self.transform_labels(relation_labels)
                t_parent_labels = self.transform_labels(parent_labels)
                query = "MATCH (node) -[r:{relation_labels}]-> (n:{parent_labels}) WHERE node.uri = '{uri}' RETURN n".format(uri=uri, relation_labels=t_relation_labels, parent_labels=t_parent_labels)
            elif len(relation_labels):
                t_relation_labels = self.transform_labels(relation_labels)
                query = "MATCH (node) -[r:{relation_labels}]-> (n) WHERE node.uri = '{uri}' RETURN n".format(uri=uri, relation_labels=t_relation_labels)
            elif len(parent_labels):
                t_parent_labels = self.transform_labels(parent_labels)
                query = "MATCH (node) -[r]-> (n:{parent_labels}) WHERE node.uri = '{uri}' RETURN n".format(uri=uri, parent_labels=t_parent_labels)
            
            request = tx.run(query)
            return [self.nodeToDict(record["n"]) for record in request]

        with self.driver.session() as session:
            result = session.write_transaction(_service_func, uri,relation_labels,parent_labels)
        
        return result

    def get_connected_nodes_by_labels(self, uri, labels):
        def _service_func(tx,uri, labels):
            t_labels = self.transform_labels(labels)

            query = "MATCH (node) - [r] - (n:{labels}) WHERE node.uri = '{uri}' RETURN n".format(uri=uri, labels=t_labels)
            request = tx.run(query)

            return [self.nodeToDict(record["n"]) for record in request]

        with self.driver.session() as session:
            result = session.write_transaction(_service_func, uri, labels)
        
        return result

    # todo
    def collect_signatures_datatype_custom(self, uri):
        def _service_func(tx,uri):
            query = '''
                    match (n)-[:`{sub}`*]->(s)<-[:`{domain}`]-(d:`{type}`)
                    where n.uri = '{uri}' 
                    return d
                    '''.format(sub=SUB_CLASS, uri=uri, domain=PROPERTY_DOMAIN, type=DATATYPE_PROPERTY)
            request = tx.run(query)
            query = '''
                    match (d:`{type}`)-[:`{domain}`]->(n)
                    where n.uri = '{uri}' 
                    return d
                    '''.format(uri=uri, domain=PROPERTY_DOMAIN, type=DATATYPE_PROPERTY)
            request2 = tx.run(query)
            result = []
            result += [self.nodeToDict(record["d"])for record in request]
            result += [self.nodeToDict(record["d"])for record in request2]
            return result
            
        with self.driver.session() as session:
            result = session.write_transaction(_service_func, uri)
        
        return result

    # Для сбора всех объектов класса с его подклассами
    def collect_nodes_from_root_uri(self, uri):
        def _service_func(tx,uri):
            query = '''
                    match(n)<-[:`{sub}`*]-(s)<-[:`{type}`]-(d)
                    where n.uri = '{uri}' 
                    return d
                    '''.format(sub=SUB_CLASS, uri=uri, type=HAS_TYPE)
            request_forward_1 = tx.run(query)

            query = '''
                    match(n)<-[:`{type}`]-(d)
                    where n.uri = '{uri}' 
                    return d
                    '''.format(uri=uri, type=HAS_TYPE)
            request_forward_2 = tx.run(query)

            result = []
            result += [self.nodeToDict(record['d']) for record in request_forward_1]
            result += [self.nodeToDict(record['d']) for record in request_forward_2]
            return result
        with self.driver.session() as session:
            result = session.write_transaction(_service_func, uri)
        
        return result

    def collect_signatures_object_custom(self, uri):
        def _service_func(tx,uri):
            query = '''
                    match(n)-[:`{sub}`*]->(s)<-[:`{domain}`]-(d:`{type}`)-[:`{range}`]->(r) 
                    where n.uri = '{uri}' 
                    return d,r
                    '''.format(sub=SUB_CLASS, uri=uri, domain=PROPERTY_DOMAIN, type=OBJECT_PROPERTY, range=PROPERTY_RANGE)
            request_forward_1 = tx.run(query)

            query = '''
                    match(n)<-[:`{domain}`]-(d:`{type}`)-[:`{range}`]->(r) 
                    where n.uri = '{uri}' 
                    return d,r
                    '''.format(uri=uri, domain=PROPERTY_DOMAIN, type=OBJECT_PROPERTY, range=PROPERTY_RANGE)
            request_forward_2 = tx.run(query)

            query = '''
                    match(n)-[:`{sub}`*]->(s)<-[:`{range}`]-(d:`{type}`)-[:`{domain}`]->(r) 
                    where n.uri = '{uri}' 
                    return d,r
                    '''.format(sub=SUB_CLASS, uri=uri, domain=PROPERTY_DOMAIN, type=OBJECT_PROPERTY, range=PROPERTY_RANGE)
            request_backward_1 = tx.run(query)
            
            query = '''
                    match(n)<-[:`{range}`]-(d:`{type}`)-[:`{domain}`]->(r) 
                    where n.uri = '{uri}' 
                    return d,r
                    '''.format(uri=uri, domain=PROPERTY_DOMAIN, type=OBJECT_PROPERTY, range=PROPERTY_RANGE)
            request_backward_2 = tx.run(query)

            def collect_record(record, direction):
                temp = {}
                temp['field'] = self.nodeToDict(record["d"])
                temp['range'] = self.nodeToDict(record["r"])
                temp['direction'] = direction
                return temp

            result = []
            result += [collect_record(record, 1) for record in request_forward_1]
            result += [collect_record(record, 1) for record in request_forward_2]
            result += [collect_record(record, 0) for record in request_backward_1]
            result += [collect_record(record, 0) for record in request_backward_2]
                
            return result
        with self.driver.session() as session:
            result = session.write_transaction(_service_func, uri)
        
        return result

    def nodeToDict(self, node):
        if node is None:
            return None
        result = {
            'id': node.get('uri'),
            'position': {'x': 0, 'y': 0},
            'type': 'mainNode',
            'data': {}
        }
        data = {}
        data['id'] = node.element_id
        data['labels'] = list(node.labels)
        data['params'] = list(node.keys())
        data[LABEL] = node.get(LABEL)
        data['uri'] = node.get('uri')
        data['ontology_uri'] = self.main_uri
        data['is_toggled'] = False
        data['toggled_data'] = []
        data['params_values'] = {}

        



        data['file'] = None
        for r in Resource.objects.all().filter(ontology_uri=self.main_uri).filter(file_uri=node.get('uri')):
            temp = {}
            temp['id'] = r.id
            temp['url'] = r.source.url
            if r.resource_type not in ['mp4', 'pdf', 'mp3', 'avi', 'mov']:
                temp['file_object'] = self.transformFileToBase64(r.source)
            else:
                temp['file_object'] = ''
            temp['name'] = r.name
            temp['resource_type'] = r.resource_type
            temp['file_uri'] = r.file_uri
            temp['ontology_uri'] = r.ontology_uri
            data['file'] = temp

        data['connected_file'] = None
        for r in Resource.objects.all().filter(ontology_uri=self.main_uri).filter(connected_entity_uri=node.get('uri')):
            temp = {}
            temp['id'] = r.id
            temp['url'] = r.source.url
            if r.resource_type not in ['mp4', 'pdf', 'mp3', 'avi', 'mov']:
                temp['file_object'] = self.transformFileToBase64(r.source)
            else:
                temp['file_object'] = ''
            temp['name'] = r.name
            temp['resource_type'] = r.resource_type
            temp['file_uri'] = r.file_uri
            temp['ontology_uri'] = r.ontology_uri
            data['connected_file'] = temp

        data['text_mentions'] = []
        for e in Entity.objects.all().filter(node_uri=node.get('uri')):
            temp = {}
            temp['pos_start'] = e.pos_start
            temp['pos_end'] = e.pos_end
            temp['markup'] = e.markup.id
            temp['original_object_uri'] = e.markup.original_object_uri


            a = data['text_mentions']
            a.append(temp)
            data['text_mentions'] = a

       

        for param in node.keys():
            value = node.get(param)
            data['params_values'][param] = ''
            if isinstance(value, time.DateTime):
                pass
            if isinstance(value, uuid.UUID):
                data['params_values'][param] = str(value)
            else:
                data['params_values'][param] = value


        result['data'] = data

        return result

    def relToDict(self, node):
        if node is None:
            return None

        result = {
            'id': node.id,
            'source': str(node.start_node['uri']),
            'target': str(node.end_node['uri']),
            'type': 'mainEdge',
            'data': {}
        }

        data = {}
        data['id'] = node.id
        data['uri'] = node.type
        data['labels'] = [node.type]
        data['params'] = list(node.keys())
        data['start_node'] = self.nodeToDict(node.start_node)
        data['end_node'] = self.nodeToDict(node.end_node)
        data['ontology_uri'] = self.main_uri
        
        result['data'] = data
        for param in node.keys():
            data[param] = node.get(param)

        return result

    def transformFileToBase64(self, source_file):
        if source_file.name is not None and len(source_file.name) != 0:
            content_file = source_file.read()
            stream = BytesIO(content_file)
            # image = Image.open(stream)
            # img_byte_arr = BytesIO()
            # image.save(img_byte_arr, format='WEBP')

            img_str = base64.b64encode(stream.getvalue())

            result =  img_str.decode("utf-8")
            return result
        return ''
    
    def custom_query(self, query, name, is_node = True):
        def _service_func(tx,query,name,is_node):
            request = tx.run(query)
            ids = []
            result = []
            for record in request:
                node = record[name]
                if node.id not in ids:
                    ids.append(node.id)
                    if is_node:
                        result.append(self.nodeToDict(node))
                    else:
                        result.append(self.relToDict(node))
            return result
            # if is_node:
            #     return [self.nodeToDict(record[name]) for record in request]
            # else:
            #     return [self.relToDict(record[name]) for record in request]


        with self.driver.session() as session:
            result = session.write_transaction(_service_func,query,name,is_node)
        
        return result

    def transform_labels(self, labels, separator = ':'):
        if len(labels) == 0:
            return '``'
        res = ''
        for l in labels:
            i = '`{l}`'.format(l=l) + separator
            res +=i
        return res[:-1]

    def transform_props(self, props):
        if len(props) == 0:
            return ''
        data = "{"
        for p in props:
            temp = "`{p}`".format(p=p)
            temp +=':'
            temp += "{val}".format(val = json.dumps(props[p]))
            data += temp + ','
        data = data[:-1]
        data += "}"

        return data
