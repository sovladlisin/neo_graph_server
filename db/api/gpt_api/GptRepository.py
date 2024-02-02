from pathlib import Path
import json
import requests
import re
import json
import numpy as np
import time


from db.api.ontology.OntologyRepository import OntologyRepo
from db.api.ontology.namespace import *


class GptRepository():
    def __init__(self):
        key_id = 'ajeh46rg7s9ss5cj8ico'
        key = 'AQVN0SG3A_E84Vk0SZjDfgLS_8TSE-KpIfG_Zk-o'
        folder_id = 'b1gmd3fh2g2nrfo251cr'

        headers = {
            'Authorization': 'Api-Key ' + key,
            'x-folder-id': folder_id
        }
        self.headers = headers
        self.folder_id = folder_id


    def load_search_indexes(self, project) -> str:
        return self.create_embedding(project)

    def similarity_search(self, question, nodes, max_result_vectors=3):
        r_data = {
                'modelUri': 'emb://' + str(self.folder_id) + '/text-search-query/latest',
                'text': question
        }
        r = requests.post('https://llm.api.cloud.yandex.net/foundationModels/v1/textEmbedding',
                          headers=self.headers, data=json.dumps(r_data)).json()
        embedding = r.get('embedding')

        def cosine_similarity(a, b):
            if None in [a, b]:
                return 0
            vector = np.dot(a, b)/(np.linalg.norm(a)*np.linalg.norm(b))
            return vector
        
        similarity_array = []

        for node in nodes:
            similarity = cosine_similarity(embedding, node['embedding'])
            if similarity != 0:
                similarity_array.append({
                    'node': node['node'],
                    'similarity': similarity
                })

            # if similarity > current_similarity:
            #     current_similarity = similarity
            #     current_text = d['text']

        sorted_similarity = list(
            sorted(similarity_array, key=lambda d: -1 * d['similarity']))
        print('\n\n\n', sorted_similarity, '\n\n\n')

        result_similarity = []
        result_similarity = sorted_similarity[:max_result_vectors]
        return result_similarity

    def create_embedding(self, project_embedding, nodes):
        result = []

        i = 0
        for node in nodes:
            i += 1
            r_data = {
                'modelUri': 'emb://' + str(self.folder_id) + '/text-search-query/latest',
                'text': node['full_text']
            }
            time.sleep(1)
            print(i)
            embedding = requests.post('https://llm.api.cloud.yandex.net/foundationModels/v1/textEmbedding',
                                      headers=self.headers, data=json.dumps(r_data)).json()
            if embedding.get('code') == 16:
                time.sleep(1)
                embedding = requests.post('https://llm.api.cloud.yandex.net/foundationModels/v1/textEmbedding',
                                          headers=self.headers, data=json.dumps(r_data)).json()
            if embedding.get('code') == 16:
                time.sleep(1)
                embedding = requests.post('https://llm.api.cloud.yandex.net/foundationModels/v1/textEmbedding',
                                          headers=self.headers, data=json.dumps(r_data)).json()
            if embedding.get('code') == 16:
                time.sleep(2)
                embedding = requests.post('https://llm.api.cloud.yandex.net/foundationModels/v1/textEmbedding',
                                          headers=self.headers, data=json.dumps(r_data)).json()
            if embedding.get('code') == 16:
                time.sleep(3)
                embedding = requests.post('https://llm.api.cloud.yandex.net/foundationModels/v1/textEmbedding',
                                          headers=self.headers, data=json.dumps(r_data)).json()

            print(embedding)

            result.append({
                'embedding': embedding.get('embedding'),
                'node': node
            })
            current_emb = i
            project_embedding.progress = current_emb / + len(nodes)
            project_embedding.save()

        project_embedding.data = json.dumps(result)
        project_embedding.is_complete = True
        project_embedding.is_running = False
        project_embedding.progress = 1
        project_embedding.save()
        return True

    def get_chat_response(self, prompt):
         # data = {
        #     "model": "general",
        #     "generationOptions": {
        #         "partialResults": False,
        #         "temperature": 0.6,
        #         "maxTokens": 7400
        #     },
        #     "messages": [
        #         {
        #             "role": 'user',
        #             'text': topic
        #         }
        #     ],
        #     "instructionText": prompt + f"{message_content}",
        # }

        data = {
            "modelUri": "gpt://" + self.folder_id + "/yandexgpt-lite/latest",
            "completionOptions": {
                "stream": False,
                "temperature": 0.3,
                "maxTokens": 7400
            },
            "messages": [
                {
                "role": "user",
                "text": prompt
                }
                ]
            }
        r = requests.post('https://llm.api.cloud.yandex.net/foundationModels/v1/completion',
                          data=json.dumps(data), headers=self.headers)
        r = r.json()
        return r

    def answer_index(self, project_embedding, question):
        nodes = json.loads(project_embedding.data)
        # r = self.get_chat_response(topic=topic, prompt=prompt, message_content=' Предугадай ответ.')

        # Выборка документов по схожести с вопросом
        docs = self.similarity_search(question, nodes, 2)
 

        doc_content = re.sub(r'\n{2}', ' ', '\n '.join(
            [f'\nТекст №{i+1}\n=====================\n' + doc['node']['full_text'] + '\n=====================' for i, doc in enumerate(docs)]))
        


        prompt = '''
            Ты помощник информационного ресурса "Ассистенты". У тебя есть тексты с информацией.
            Тебе задает вопрос клиент в чате, дай ему ответ, опираясь на документ.
            Отвечай максимально точно по текстам, не придумывай ничего от себя.
            Вопрос: {question}

            Тексты с информацией для ответа клиенту:

            {doc_content}
        '''.format(question=question, doc_content=doc_content)

        print('prompt',prompt)


        r = self.get_chat_response(prompt)
        print('\n\n\n', r, '\n\n\n')
        # message = r.get('result', {}).get('message', {}).get('text', '')
        message = r.get('result', {}).get(
            'alternatives', [{}])[0].get('message', {}).get('text', '')
        
        response = {
            'message': message,
            'nodes': [d['node'] for d in docs],
            'role': 'assistant',
            'project_id': project_embedding.project.id
        }

        # num_tokens = r.get('result', {}).get('num_tokens', 0)
        # print('\n\n', num_tokens, '\n\n')

        return response
        # TEMP ----------------------------------
        response = {
            'role': 'assistant',
            'text': message,
            'context': [{'text': doc['text'], 'similarity': doc['similarity']} for i, doc in enumerate(docs)],
            'extended_request': refined_message
        }
        return response
