from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    firebase_id = models.CharField(max_length=255, unique=True)
    fullname = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.fullname
