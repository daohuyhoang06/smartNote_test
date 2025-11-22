from django.db import models
from django.utils import timezone
from notes.models import VocaDetail

class Vocabulary(models.Model):
    hiragana = models.CharField(max_length=100)
    kanji = models.CharField(max_length=100, blank=True, null=True)
    katakana = models.CharField(max_length=100, blank=True, null=True)
    meaning = models.CharField(max_length=255, blank=True, null=True)
    level = models.CharField(max_length=10)  # N5, N4, ...
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return self.kanji or self.katakana or self.hiragana


class Exercise(models.Model):
    DISPLAY_MODES = (
        ('kanji', 'Kanji'),
        ('no_kanji', 'No Kanji'),
    )

    vocabulary = models.ForeignKey(
        Vocabulary,               # liên kết trực tiếp sang model ở app notes
        on_delete=models.CASCADE,
        related_name='exercises'
    )
    display_mode = models.CharField(max_length=10, choices=DISPLAY_MODES)
    sentence = models.TextField()
    options = models.JSONField()
    answer = models.CharField(max_length=100)
    explanation = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vocabulary} [{self.display_mode}]"
