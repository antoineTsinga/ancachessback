from django.urls import path

from .views import create_game, join_game

urlpatterns = [
    path("create_game/", create_game, name="create_game"),
    path("join_game/", join_game, name="join_game"),
]
