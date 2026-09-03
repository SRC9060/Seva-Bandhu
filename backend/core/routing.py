from django.urls import re_path
from . import consumers

websocket_urlpatterns = [

    re_path( # type: ignore
        r'^ws/requests/$',
        consumers.RequestConsumer.as_asgi()
    ),

    re_path( # type: ignore
        r'^ws/tracking/(?P<id>\d+)/$',
        consumers.RequestConsumer.as_asgi()
    ),

    re_path( # type: ignore
        r'^ws/chat/(?P<request_id>\d+)/$',
        consumers.ChatConsumer.as_asgi()
    ),
]