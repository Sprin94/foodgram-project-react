from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError

from django.db import models


def username_not_me(username):
    if username == 'me':
        raise ValidationError('username не может быть "me"')


class User(AbstractUser):
    "Пользовательская модель юзера"
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator, username_not_me],
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
    )
    email = models.EmailField(
        verbose_name='Email',
        unique=True,
        max_length=254,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

    class Meta(AbstractUser.Meta):
        ordering = ('-id',)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE)
    following = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_follow')
        ]
