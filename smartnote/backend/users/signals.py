from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from notes.models import Note  # import model Note từ app notes

@receiver(post_save, sender=User)
def create_note_for_user(sender, instance, created, **kwargs):
    """
    Khi một user mới được tạo (created=True), tạo luôn Note cho user đó.
    """
    if created:
        Note.objects.create(user=instance)
