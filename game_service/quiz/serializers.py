from rest_framework import serializers

from .models import Question, Room, RoomPlayer


class QuestionPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "text", "choice_a", "choice_b", "choice_c", "choice_d", "category"]


class RoomPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomPlayer
        fields = ["user_id", "username", "score", "finished"]


class RoomSerializer(serializers.ModelSerializer):
    players = RoomPlayerSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = ["code", "status", "players", "created_at"]
