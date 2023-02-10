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

from .serializers import LoginSerializer, RegistrationSerializer

@api_view(['POST', ])
@permission_classes((AllowAny,))
def registration_view(request):

    serializer = RegistrationSerializer(data=request.data)
    data = {}
    if serializer.is_valid():
        account = serializer.save()
        data = collect_account_func(account)

    else:
        data = serializer.errors
    return Response(data)


@api_view(['POST', ])
@permission_classes((AllowAny,))
def login_view(request):

    serializer = LoginSerializer(data=request.data)
    data = {}
    if serializer.is_valid():
        account = serializer.authenticate()
        data = collect_account_func(account)

    else:
        print('valid error')
        data = serializer.errors
    return Response(data)




@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def get_users(request):

    user = request.user
    if (user.is_admin == False):
        return HttpResponse(status=401)

    response = []
    for u in Account.objects.all():
        response.append(collect_account_func(u, True))

    return Response(response)



@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def update_user_perm(request):

    user = request.user
    if (user.is_admin == False):
        return HttpResponse(status=401)

    data = json.loads(request.body.decode('utf-8'))
    user_pk = data.get('user_pk', None)
    is_admin = data.get('is_admin', None)
    is_editor = data.get('is_editor', None)

    if None in [user_pk, is_admin, is_editor]:
        return HttpResponse(status=400)
    
    new_user = Account.objects.get(pk=user_pk)
    new_user.is_admin = is_admin
    new_user.is_editor = is_editor
    new_user.save()

    response = collect_account_func(new_user, True)

    

    return Response(response)





def collect_account_func(account, safe=False):
    data = {}
    data['response'] = 'Success'
    data['email'] = account.email
    data['username'] = account.email

    if safe is False:
        token = Token.objects.get(user=account).key
        data['token'] = token
    else:
        data['token'] = ''


    data['is_admin'] = account.is_admin
    data['is_editor'] = account.is_editor
    data['id'] = account.pk
    return data
