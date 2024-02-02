from django.urls import path
from django.conf.urls import url
from .views import (
    login_view,
)

urlpatterns = [
    path('login', login_view, name="login"),
]