from django.db import models
from django.core.exceptions import ValidationError


# Create your models here.
class Word(models.Model): 
    word =  models.CharField(max_length=255, null=True, blank=True)
    phonetic = models.CharField(max_length=400, null=True, blank=True)
    short_mean = models.CharField(max_length=255, null=True, blank=True)
    
class Kanji(models.Model):
    kanji = models.CharField(max_length=255, null=True, blank=True)  # original kanji
    mean = models.CharField(max_length=255, null=True, blank=True)  # kanji meaning in short way _ Han viet
    kun = models.CharField(max_length=255, null=True, blank=True)  # kunyomi
    on = models.CharField(max_length=255, null=True, blank=True)  # onyomi
    stroke_count = models.IntegerField(default=0, blank=True, null=True)  # kanji stroke count
    level = models.JSONField(default=list, blank=True, null=True)
    detail = models.TextField(blank=True, null=True)  # fully meaning of kanji
    examples = models.JSONField(default=dict, blank=True, null=True)
    example_on = models.JSONField(default=dict, blank=True, null=True)
    example_kun = models.JSONField(default=dict, blank=True, null=True)    

class Example(models.Model):
    word_search = models.ForeignKey(
        Word,
        related_name="examples",
        on_delete=models.CASCADE
    )
    transcription = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    mean = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.jp if self.jp else "Example"