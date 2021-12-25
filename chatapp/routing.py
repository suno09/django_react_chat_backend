from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
# from django_channels_jwt_auth_middleware.auth import JWTAuthMiddlewareStack
from django.conf.urls import url
from . import consumers

websocket_urlpatterns = [
    url(r'^ws/chat$', consumers.ChatConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})