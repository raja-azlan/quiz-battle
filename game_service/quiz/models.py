import random
import string

from django.db import models


def generate_room_code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


class Question(models.Model):
    text = models.CharField(max_length=300)
    choice_a = models.CharField(max_length=100)
    choice_b = models.CharField(max_length=100)
    choice_c = models.CharField(max_length=100)
    choice_d = models.CharField(max_length=100)
    correct_choice = models.CharField(
        max_length=1, choices=[("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")]
    )
    category = models.CharField(max_length=50, default="general")

    def __str__(self):
        return self.text


class Room(models.Model):
    STATUS_CHOICES = [
        ("waiting", "Waiting"),
        ("active", "Active"),
        ("finished", "Finished"),
    ]

    code = models.CharField(max_length=6, unique=True, default=generate_room_code)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="waiting")
    questions = models.ManyToManyField(Question, through="RoomQuestion")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Room {self.code} ({self.status})"


class RoomQuestion(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["order"]
        unique_together = ("room", "order")


class RoomPlayer(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="players")
    user_id = models.PositiveIntegerField()
    username = models.CharField(max_length=150)
    score = models.PositiveIntegerField(default=0)
    finished = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("room", "user_id")

    def __str__(self):
        return f"{self.username} in {self.room.code}"


class Answer(models.Model):
    player = models.ForeignKey(RoomPlayer, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.CharField(max_length=1)
    is_correct = models.BooleanField()
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("player", "question")
