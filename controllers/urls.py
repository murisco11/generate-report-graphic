# example/urls.py
from django.urls import path

from controllers.views import index


urlpatterns = [
    path('', index),
]