from django.urls import path, include
from django_private_chat2 import urls as django_private_chat2_urls

urlpatterns = [
    path(r'chat', include(django_private_chat2_urls)),
]
