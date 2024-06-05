# game/consumers.py
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from datetime import datetime


class GameConsumer(WebsocketConsumer):

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chess_{self.room_name}"
        self.timer = {"black": 600, "white": 600}
        self.current = "white"

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
        print(data)
        message = data["content"]
        type = "game." + data["type"]

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": type, "content": message}
        )

    def game_message(self, event):

        message = event["content"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"type": "message", "content": message}))

    def game_move(self, event):
        move = event["content"]
        now = datetime.timestamp(datetime.now())
        self.timer[self.current] -= now - self.start_time
        self.start_time = now
        move["timer"] = self.timer[self.current]
        move["color"] = self.current
        self.current = "black" if self.current == "white" else "white"

        self.send(
            text_data=json.dumps(
                {"type": "move", "content": {"move": move, "startTime": now}}
            )
        )

    def game_setcolor(self, event):
        player = event["content"]

        self.send(text_data=json.dumps({"type": "setcolor", "content": player}))

    def game_findcolor(self, event):
        players = event["content"]

        self.send(text_data=json.dumps({"type": "findcolor", "content": players}))

    def game_start(self, event):
        start = event["content"]
        self.start_time = datetime.timestamp(datetime.now())
        self.send(text_data=json.dumps({"type": "start", "content": self.start_time}))

    def game_rematch(self, event):
        rematch = event["content"]
        print("rematch", rematch)
        self.send(text_data=json.dumps({"type": "rematch", "content": rematch}))

    def game_getTime(self, event):
        now = event["content"]
        self.timer[self.current] -= now - self.start_time
        self.start_time = now
        timer = {}
        timer["timer"] = self.timer[self.current]
        timer["color"] = self.current
        timer["startTime"] = now
        self.current = "black" if self.current == "white" else "white"
        self.send(text_data=json.dumps({"type": "timer", "content": timer}))
