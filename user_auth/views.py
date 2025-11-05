from django.http.response import HttpResponse
import jwt
from django.forms.models import model_to_dict
from rest_framework.authtoken.models import Token

import json

from user_auth.models import Account 
KEY = "qwerqwqwefknskacnfjbnjvgjeriuyweoLKUHHLKJEfhkerjnfkjrw1lklk~~~fesfdcvse"
# Create your views here.

# API IMPORTS
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
import uuid
import requests


@api_view(['POST', ])
@permission_classes((AllowAny,))
def login_view(request):
    print('testtest')
    data = json.loads(request.body.decode('utf-8'))

    code = data.get('code')
    device_id = data.get('device_id')
    code_verifier = data.get('code_verifier')
    redirect_uri = data.get('redirect_uri')
    client_id = data.get('client_id')

    url = 'https://id.vk.ru/oauth2/auth'
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'code_verifier': code_verifier,
        'device_id': device_id,
        'state': 'state123',
        'client_id': client_id,
        'redirect_uri': redirect_uri
    }
    r = requests.post(url=url, data=data)
    token_data = r.json()
    access_token = token_data.get('access_token')
    # print(r.json())

    url = 'https://id.vk.ru/oauth2/user_info'
    data2 = {
        'client_id': client_id,
        'access_token': access_token
    }
    r2 = requests.post(url=url, data=data2)
    print(r2.content)
    user_data = r2.json()

    data = user_data.get('user', {})
    vk_id = data.get("user_id")
    vk_name = data.get("first_name", '') + ' ' + data.get("last_name", '')
    vk_avatar = data.get("avatar")
    print('\n\n\n',vk_id, vk_name,vk_avatar, '\n\n\n')
    found = Account.objects.all().filter(vk_id=int(vk_id))
    if found.count() == 1:
        account = found.first()
        account.vk_avatar = vk_avatar
        account.vk_name = vk_name
        account.save()

    else:
        account = Account(
            email=str(vk_id) + '@local.com',
            username=vk_name,
            vk_id=int(vk_id),
            vk_name=vk_name,
            vk_avatar=vk_avatar
        )
        account.set_password(str(uuid.uuid4()))
        account.is_active = True
        account.save()
    
    return Response(collect_account(account))

def collect_account(account):
    temp = {}
    token = Token.objects.get(user=account).key
    temp['token'] = token
    temp['id'] = account.id
    temp['vk_name'] = account.vk_name
    temp['vk_id'] = account.vk_id
    temp['vk_avatar'] = account.vk_avatar
    return temp
