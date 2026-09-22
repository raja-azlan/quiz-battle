from django.core.management.base import BaseCommand

from quiz.models import Question

QUESTIONS = [
    ("What is the capital of France?", "London", "Paris", "Berlin", "Rome", "b"),
    ("Which planet is known as the Red Planet?", "Venus", "Mars", "Jupiter", "Saturn", "b"),
    ("What is 7 x 8?", "54", "56", "58", "64", "b"),
    ("Who wrote 'Romeo and Juliet'?", "Dickens", "Shakespeare", "Austen", "Hemingway", "b"),
    ("What is the largest ocean on Earth?", "Atlantic", "Indian", "Arctic", "Pacific", "d"),
    ("How many continents are there?", "5", "6", "7", "8", "c"),
    (
        "What gas do plants primarily absorb for photosynthesis?",
        "Oxygen",
        "Nitrogen",
        "Carbon Dioxide",
        "Hydrogen",
        "c",
    ),
    ("What is the chemical symbol for gold?", "Au", "Ag", "Gd", "Go", "a"),
    ("Which country hosted the 2016 Summer Olympics?", "China", "UK", "Brazil", "Japan", "c"),
    ("What is the smallest prime number?", "0", "1", "2", "3", "c"),
]


class Command(BaseCommand):
    help = "Seed the database with a starter set of trivia questions"

    def handle(self, *args, **options):
        created = 0
        for text, a, b, c, d, correct in QUESTIONS:
            _, was_created = Question.objects.get_or_create(
                text=text,
                defaults={
                    "choice_a": a,
                    "choice_b": b,
                    "choice_c": c,
                    "choice_d": d,
                    "correct_choice": correct,
                },
            )
            created += int(was_created)
        self.stdout.write(
            self.style.SUCCESS(f"Seeded {created} new question(s); {len(QUESTIONS)} total in bank")
        )
