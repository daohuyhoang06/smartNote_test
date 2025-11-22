# tasks.py
from celery import shared_task
from notes.models import VocaDetail
from ai_content.models import Vocabulary
from ai_content.services import get_or_create_exercises
from django.utils import timezone

@shared_task
def sync_and_generate_exercises_task(ids):
    """
    Đồng bộ từ VocaDetail sang Vocabulary và sinh quiz cho từ mới.
    """
    details = VocaDetail.objects.filter(id__in=ids).select_related("voca_topic")

    for detail in details:
        # Tìm hoặc tạo Vocabulary tương ứng
        vocab, created = Vocabulary.objects.update_or_create(
            kanji=detail.kanji,
            hiragana=detail.hiragana,
            katakana=detail.katakana,
            defaults={
                "meaning": detail.meaning,
                "level": detail.level,
                "updated_at": timezone.now(),
            },
        )

        # Sau khi đã có Vocabulary -> sinh quiz
        get_or_create_exercises(
            word=vocab.kanji or vocab.hiragana or vocab.katakana,
            count=15,
        )
