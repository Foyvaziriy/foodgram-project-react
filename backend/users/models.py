from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    first_name = models.CharField(
        _('first name'),
        max_length=150,
    )
    last_name = models.CharField(
        _('last name'),
        max_length=150,
    )
    email = models.EmailField(
        _('email address'),
        unique=True,
    )

    class Meta:
        ordering = ('first_name',)

    @property
    def data(self):
        return {
            'email': self.email,
            'id': self.id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
        }

    def __str__(self) -> str:
        return self.username


class UserSubs(models.Model):
    user = models.ForeignKey(
        User,
        related_name='user_id',
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )
    sub = models.ForeignKey(
        User,
        related_name='sub_id',
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )

    class Meta:
        ordering = ('user',)
