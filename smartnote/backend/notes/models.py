from django.db import models
from django.contrib.auth.models import User
from users.models import User
from django.conf import settings

class Note(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name="note")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"Note của {self.user.username}"

class Topic(models.Model):
    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name="topics",
        null=True,
        blank=True
    )
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)  # Lưu thời điểm tạo
    updated_at = models.DateTimeField(auto_now=True)      # Lưu thời điểm cập nhật

    class Meta:
        # mỗi note (tức mỗi user) không được có 2 topic trùng title
        constraints = [
            models.UniqueConstraint(
                fields=['note', 'title'],
                name='unique_topic_title_per_note',
            )
        ]

    def delete(self, *args, **kwargs):
        vocas = [vt.voca for vt in self.voca_topics.all()]
        super().delete(*args, **kwargs)
        for voca in vocas:
            if not voca.voca_topics.exists():  # orphan -> xóa luôn
                voca.delete()

    def __str__(self):
        return f"{self.title} ({self.note.user.username})"


class Voca(models.Model):
    word = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.word
    

class VocaTopic(models.Model):
    topic = models.ForeignKey(
        "Topic",
        on_delete=models.CASCADE,
        related_name="voca_topics"
    )
    voca = models.ForeignKey(
        "Voca",
        on_delete=models.CASCADE,
        related_name="voca_topics"
    )

    class Meta:
        unique_together = ("topic", "voca")  # tránh trùng từ trong 1 topic

    def __str__(self):
        return f"{self.voca.word} in {self.topic.title}"
    


class VocaDetail(models.Model):
    voca_topic = models.ForeignKey(
        VocaTopic,
        on_delete=models.CASCADE,
        related_name="details"   
    )
     
    kanji = models.CharField(max_length=255, blank=True, null=True)
    katakana = models.CharField(max_length=255, blank=True, null=True)
    hiragana = models.CharField(max_length=255, blank=True, null=True)
    phonetic = models.CharField(max_length=400, blank=True, null=True)
    meaning = models.CharField(max_length=255, blank=True, null=True)
    example = models.CharField(max_length=255, blank=True, null=True)
    level = models.CharField(max_length=50, blank=True, null=True, default="N4")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Detail of {self.voca_topic.voca.word}"