# game/consumers.py
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from datetime import datetime
from django.core.cache import cache


class GameConsumer(WebsocketConsumer):

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chess_{self.room_name}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        message = data["content"]
        type = "game." + data["type"]

        if data["type"] == "start":
            start_time = datetime.timestamp(datetime.now())
            time = 600
            cache.set(f"{self.room_group_name}_start_time", start_time)
            cache.set(f"{self.room_group_name}_timer", {"black": time, "white": time})
            cache.set(f"{self.room_group_name}_current", "white")

        if data["type"] == "move":
            now = datetime.timestamp(datetime.now())
            self.timer[self.current] -= now - self.start_time
            self.start_time = now
            now = datetime.timestamp(datetime.now())
            self.timer[self.current] -= now - self.start_time
            self.start_time = now
            message["timer"] = self.timer[self.current]
            message["color"] = self.current
            self.current = "black" if self.current == "white" else "white"

            self.set_cache()

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": type, "content": message}
        )

    def game_message(self, event):
        message = event["content"]
        # Send message to WebSocket
        self.send(text_data=json.dumps({"type": "message", "content": message}))

    def game_move(self, event):
        self.get_cache()
        move = event["content"]

        self.send(
            text_data=json.dumps(
                {
                    "type": "move",
                    "content": {"move": move, "startTime": self.start_time},
                }
            )
        )

    def game_setcolor(self, event):
        player = event["content"]

        self.send(text_data=json.dumps({"type": "setcolor", "content": player}))

    def game_findcolor(self, event):
        self.get_cache()
        players = event["content"]

        self.send(text_data=json.dumps({"type": "findcolor", "content": players}))

    def game_start(self, event):
        self.get_cache()
        start = event["content"]
        time = 600
        self.send(
            text_data=json.dumps(
                {
                    "type": "start",
                    "content": {"startTime": self.start_time, "time": time},
                }
            )
        )

    def game_rematch(self, event):
        self.get_cache()
        rematch = event["content"]
        self.send(text_data=json.dumps({"type": "rematch", "content": rematch}))

    def game_viewMatch(self, event):
        self.get_cache()
        viewMatch = event["content"]
        now = datetime.timestamp(datetime.now())
        self.timer[self.current] -= now - self.start_time
        self.start_time = now
        viewMatch["timers"] = self.timer
        viewMatch["startTime"] = self.start_time
        self.send(text_data=json.dumps({"type": "viewMatch", "content": viewMatch}))

    def get_cache(self):
        if cache.get(f"{self.room_group_name}_start_time"):
            self.timer = cache.get(f"{self.room_group_name}_timer")
            self.current = cache.get(f"{self.room_group_name}_current")
            self.start_time = cache.get(f"{self.room_group_name}_start_time")

    def set_cache(self):
        cache.set(f"{self.room_group_name}_timer", self.timer)
        cache.set(f"{self.room_group_name}_current", self.current)
        cache.set(f"{self.room_group_name}_start_time", self.start_time)
