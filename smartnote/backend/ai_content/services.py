import random
from django.db import transaction
from django.db.models import Q
from .models import  Exercise, Vocabulary
from openai_api.services import generate_fill_in_blank
from notes.models import VocaDetail


def get_or_create_exercises(word: str, level: str = "N5",
                            display_mode: str = "kanji", count: int = 15):
    if not word.strip():
        return []

    vocabulary = (
        Vocabulary.objects
        .filter(Q(kanji=word) | Q(hiragana=word) | Q(katakana=word))
        .order_by("id")
        .first()
    )

    if not vocabulary:
        vocabulary = Vocabulary.objects.create(
            kanji=word,
            hiragana=word,
            level=level,
            meaning="",
        )

    exercises_qs = Exercise.objects.filter(
        vocabulary=vocabulary,
        display_mode=display_mode
    )
    if exercises_qs.exists():
        return list(exercises_qs)

    try:
        generated = generate_fill_in_blank(
            word=word,
            level=vocabulary.level or level,
            display_mode=display_mode,
            count=count,
        )
    except Exception:
        return []

    exercises = []
    # print(generated + "------------------ generated") 
    with transaction.atomic():
        for item in generated:
            exercises.append(
                Exercise.objects.create(
                    vocabulary=vocabulary,
                    display_mode=display_mode,
                    sentence=item.get("sentence", ""),
                    options=item.get("options") or [],
                    answer=item.get("answer", ""),
                    explanation=item.get("explanation") or {},
                )
            )
    return exercises


def get_random_exercises(word: str, level: str = "N5", display_mode: str = "kanji", count: int = 15):
    """
    Lấy 1 câu random duy nhất (trả về object Exercise).
    """
    exercises = get_or_create_exercises(word, level, display_mode, count)
    if not exercises:
        return None
    return random.choice(exercises)
