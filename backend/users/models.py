from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models


def username_not_me(username):
    if username == 'me':
        raise ValidationError('username не может быть "me"')


class UserManager(BaseUserManager):
    def create_user(self, email, password, first_name='', last_name=''):
        """ Создает и возвращает пользователя с email и именем. """

        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(
            first_name=first_name,
            last_name=last_name,
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.is_superuser = False
        user.is_staff = False
        user.save()
        return user

    def create_superuser(self, email, password):
        """ Создает и возвращает пользователя с привилегиями суперадмина."""

        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


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

    objects = UserManager()

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
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_follow')
        ]
