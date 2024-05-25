import random
import string
from django.db import models
from django.contrib.auth.models import User


class Game(models.Model):
    player1 = models.ForeignKey(User, related_name="player1", on_delete=models.CASCADE)
    player2 = models.ForeignKey(User, related_name="player2", on_delete=models.CASCADE)
    state = models.JSONField(default=dict)  # to store the board state as a JSON object
    fen = models.TextField()
    is_active = models.BooleanField(default=True)
