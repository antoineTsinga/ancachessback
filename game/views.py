import uuid
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
@csrf_exempt
def create_game(request):
    if request.method == "POST":
        room_id = str(uuid.uuid4())
        return JsonResponse({"room_id": room_id})


@csrf_exempt
def join_game(request):
    if request.method == "POST":
        room_id = str(uuid.uuid4())
        return JsonResponse({"message": "Game joined"})
