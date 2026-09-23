from unittest.mock import patch

import jwt
from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Question


def auth_header(user_id, username):
    token = jwt.encode(
        {"user_id": user_id, "username": username}, settings.JWT_SECRET, algorithm="HS256"
    )
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}


class QuizFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        for i in range(settings.NUM_QUESTIONS_PER_ROOM):
            Question.objects.create(
                text=f"Question {i}",
                choice_a="a",
                choice_b="b",
                choice_c="c",
                choice_d="d",
                correct_choice="a",
            )

    def create_room(self, user_id=1, username="alice"):
        return self.client.post("/api/rooms/", **auth_header(user_id, username))

    def test_create_room_requires_auth(self):
        response = self.client.post("/api/rooms/")
        self.assertIn(response.status_code, (401, 403))

    def test_create_room_success(self):
        response = self.create_room()
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["status"], "waiting")
        self.assertEqual(len(data["players"]), 1)

    def test_join_room_activates_it_and_rejects_a_third_player(self):
        code = self.create_room().json()["code"]

        joined = self.client.post(f"/api/rooms/{code}/join/", **auth_header(2, "bob"))
        self.assertEqual(joined.status_code, 200)
        self.assertEqual(joined.json()["status"], "active")

        rejected = self.client.post(f"/api/rooms/{code}/join/", **auth_header(3, "carol"))
        self.assertEqual(rejected.status_code, 400)

    def test_questions_endpoint_hides_the_correct_answer(self):
        code = self.create_room().json()["code"]
        self.client.post(f"/api/rooms/{code}/join/", **auth_header(2, "bob"))

        questions = self.client.get(
            f"/api/rooms/{code}/questions/", **auth_header(1, "alice")
        ).json()
        self.assertEqual(len(questions), settings.NUM_QUESTIONS_PER_ROOM)
        self.assertNotIn("correct_choice", questions[0])

    def test_answering_the_same_question_twice_is_rejected(self):
        code = self.create_room().json()["code"]
        self.client.post(f"/api/rooms/{code}/join/", **auth_header(2, "bob"))
        question = Question.objects.first()

        first = self.client.post(
            f"/api/rooms/{code}/answer/",
            {"question_id": question.id, "choice": "a"},
            format="json",
            **auth_header(1, "alice"),
        )
        self.assertEqual(first.status_code, 200)

        second = self.client.post(
            f"/api/rooms/{code}/answer/",
            {"question_id": question.id, "choice": "a"},
            format="json",
            **auth_header(1, "alice"),
        )
        self.assertEqual(second.status_code, 400)

    @patch("quiz.views.report_match_result")
    def test_full_match_scores_correctly_and_reports_the_result(self, mock_report):
        code = self.create_room().json()["code"]
        self.client.post(f"/api/rooms/{code}/join/", **auth_header(2, "bob"))

        questions = self.client.get(
            f"/api/rooms/{code}/questions/", **auth_header(1, "alice")
        ).json()

        # alice answers every question correctly, bob gets every one wrong
        for q in questions:
            self.client.post(
                f"/api/rooms/{code}/answer/",
                {"question_id": q["id"], "choice": "a"},
                format="json",
                **auth_header(1, "alice"),
            )
            self.client.post(
                f"/api/rooms/{code}/answer/",
                {"question_id": q["id"], "choice": "z"},
                format="json",
                **auth_header(2, "bob"),
            )

        final = self.client.get(f"/api/rooms/{code}/", **auth_header(1, "alice")).json()
        self.assertEqual(final["status"], "finished")

        alice = next(p for p in final["players"] if p["user_id"] == 1)
        bob = next(p for p in final["players"] if p["user_id"] == 2)
        self.assertEqual(alice["score"], settings.NUM_QUESTIONS_PER_ROOM * settings.POINTS_PER_CORRECT)
        self.assertEqual(bob["score"], 0)

        mock_report.assert_any_call(1, True)
        mock_report.assert_any_call(2, False)
