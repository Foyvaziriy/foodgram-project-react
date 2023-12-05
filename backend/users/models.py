from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    first_name = models.CharField(
        _("first name"),
        max_length=150,
        blank=False,
        null=False,
    )
    last_name = models.CharField(
        _("last name"),
        max_length=150,
        blank=False,
        null=False,
    )
    email = models.EmailField(
        _("email address"),
        unique=True,
        blank=False,
        null=False,
    )

    @property
    def data(self):
        return {
            'email': self.email,
            'id': self.id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
        }


class UserSubs(models.Model):
    user_id = models.ForeignKey(
        User,
        related_name='user_id',
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )
    sub_id = models.ForeignKey(
        User,
        related_name='sub_id',
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )
