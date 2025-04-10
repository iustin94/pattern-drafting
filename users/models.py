from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Extended user model with additional profile information
    """
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profile_pics', blank=True)

    # You could add more user-specific fields here

    def __str__(self):
        return self.username
