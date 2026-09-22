import random

from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Answer, Question, Room, RoomPlayer, RoomQuestion
from .serializers import QuestionPublicSerializer, RoomSerializer
from .utils import report_match_result


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_room(request):
    questions = list(Question.objects.all())
    if len(questions) < settings.NUM_QUESTIONS_PER_ROOM:
        return Response(
            {"detail": "Not enough questions seeded yet"}, status=status.HTTP_400_BAD_REQUEST
        )

    chosen = random.sample(questions, settings.NUM_QUESTIONS_PER_ROOM)

    with transaction.atomic():
        room = Room.objects.create()
        for order, question in enumerate(chosen):
            RoomQuestion.objects.create(room=room, question=question, order=order)
        RoomPlayer.objects.create(room=room, user_id=request.user.id, username=request.user.username)

    return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def join_room(request, code):
    try:
        room = Room.objects.get(code=code)
    except Room.DoesNotExist:
        return Response({"detail": "Room not found"}, status=status.HTTP_404_NOT_FOUND)

    if room.players.filter(user_id=request.user.id).exists():
        return Response(RoomSerializer(room).data)

    if room.status != "waiting":
        return Response({"detail": "Room is not accepting players"}, status=status.HTTP_400_BAD_REQUEST)

    if room.players.count() >= 2:
        return Response({"detail": "Room is full"}, status=status.HTTP_400_BAD_REQUEST)

    RoomPlayer.objects.create(room=room, user_id=request.user.id, username=request.user.username)
    room.status = "active"
    room.save()

    return Response(RoomSerializer(room).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def room_detail(request, code):
    try:
        room = Room.objects.get(code=code)
    except Room.DoesNotExist:
        return Response({"detail": "Room not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response(RoomSerializer(room).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def room_questions(request, code):
    try:
        room = Room.objects.get(code=code)
    except Room.DoesNotExist:
        return Response({"detail": "Room not found"}, status=status.HTTP_404_NOT_FOUND)

    questions = [
        rq.question for rq in room.roomquestion_set.select_related("question").order_by("order")
    ]
    return Response(QuestionPublicSerializer(questions, many=True).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_answer(request, code):
    try:
        room = Room.objects.get(code=code)
    except Room.DoesNotExist:
        return Response({"detail": "Room not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        player = room.players.get(user_id=request.user.id)
    except RoomPlayer.DoesNotExist:
        return Response({"detail": "You are not in this room"}, status=status.HTTP_403_FORBIDDEN)

    if player.finished:
        return Response({"detail": "You already finished this room"}, status=status.HTTP_400_BAD_REQUEST)

    question_id = request.data.get("question_id")
    selected_choice = request.data.get("choice")

    try:
        question = Question.objects.get(id=question_id, roomquestion__room=room)
    except Question.DoesNotExist:
        return Response({"detail": "Question not in this room"}, status=status.HTTP_400_BAD_REQUEST)

    if Answer.objects.filter(player=player, question=question).exists():
        return Response({"detail": "Already answered"}, status=status.HTTP_400_BAD_REQUEST)

    is_correct = selected_choice == question.correct_choice
    Answer.objects.create(
        player=player, question=question, selected_choice=selected_choice, is_correct=is_correct
    )

    if is_correct:
        player.score += settings.POINTS_PER_CORRECT
        player.save()

    total_questions = room.roomquestion_set.count()
    if player.answers.count() >= total_questions:
        player.finished = True
        player.save()
        _finish_room_if_ready(room)

    return Response({"correct": is_correct, "score": player.score})


def _finish_room_if_ready(room):
    players = list(room.players.all())
    if len(players) < 2 or not all(p.finished for p in players):
        return

    room.status = "finished"
    room.save()

    top_score = max(p.score for p in players)
    is_tie = sum(1 for p in players if p.score == top_score) > 1
    for p in players:
        won = (not is_tie) and p.score == top_score
        report_match_result(p.user_id, won)
