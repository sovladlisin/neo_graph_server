from django.urls import path
from django.conf.urls import url
from .views import (
    registration_view,
    login_view,
    get_users,
    update_user_perm
)

urlpatterns = [
    path('register', registration_view, name="register"),
    path('login', login_view, name="login"),
    path('getUsers', get_users, name="getUsers"),
    path('updateUserPerm', update_user_perm, name="updateUserPerm"),
]