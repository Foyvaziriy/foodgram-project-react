from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    auth_token = models.SlugField('Ключ аутентификации', unique=True)


class UserSubs(models.Model):
    user_id = models.ForeignKey(
        User,
        related_name='user_id',
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )
    sub_id = models.ForeignKey(
        User,
        related_name='sub_id',
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )
