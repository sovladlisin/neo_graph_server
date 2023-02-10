from rest_framework import serializers

from .models import Account
from django.contrib.auth import authenticate
import datetime
import json


class RegistrationSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = Account
        fields = ['email', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def save(self):

        account = Account(
            email=self.validated_data['email'],
            username=self.validated_data['email'] + 'username'
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError(
                {'password': 'Passwords must match.'})
        account.set_password(password)
        account.is_active = True
        account.save()
        return account


class LoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ['username', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def authenticate(self):
        print(self.validated_data)
        accounts = Account.objects.all().filter(
            email=self.validated_data['username'])
        if accounts.count() == 0:
            raise serializers.ValidationError(
                {'response': 'Error', 'message': 'Пользователь с таким почтовым адресом не существует', 'type': 'UserNotFound'})

        if accounts.count() == 1:
            found_account = accounts.first()
            if found_account.is_active is False:

                raise serializers.ValidationError(
                    {'response': 'Error', 'message': 'Аккаунт не подтвержден', 'type': 'UserNotActive'})

        account = authenticate(
            username=self.validated_data['username'], password=self.validated_data['password'])
        if account is None:
            raise serializers.ValidationError(
                {'response': 'Error', 'message': 'Неправильно введен пароль', 'type': 'WrongPassword'})

        return account
