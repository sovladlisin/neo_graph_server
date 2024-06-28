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


@api_view(['POST', ])
@permission_classes((AllowAny,))
def login_view(request):

    data = json.loads(request.body.decode('utf-8'))

    vk_id = data.get("vk_id")
    vk_name = data.get("vk_name")
    vk_avatar = data.get("vk_avatar")
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
