from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"wss/game/(?P<room_name>\w+)/$", consumers.GameConsumer.as_asgi()),
]


# ws/game/7ec73432-7cc5-40a5-a9eb-abc1467e16b1/'
