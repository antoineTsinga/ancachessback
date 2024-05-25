# game/consumers.py
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


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

    # def game_state(self, event):
    #     # Send the game state to the WebSocket
    #     state = event["state"]
    #     self.send(text_data=json.dumps({"type": "state", "state": state}))

    def game_move(self, event):
        move = event["content"]

        self.send(text_data=json.dumps({"type": "move", "content": move}))

    def game_setcolor(self, event):
        player = event["content"]

        self.send(text_data=json.dumps({"type": "setcolor", "content": player}))

    def game_findcolor(self, event):
        players = event["content"]

        self.send(text_data=json.dumps({"type": "findcolor", "content": players}))

    def game_start(self, event):
        start = event["content"]
        print("start", start)
        self.send(text_data=json.dumps({"type": "start", "content": start}))
