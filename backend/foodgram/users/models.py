from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models import UniqueConstraint


class User(AbstractUser):
    email = models.EmailField(unique=True,
                              verbose_name='email adress',
                              max_length=254,)
    username = models.CharField(max_length=150,
                                unique=True,
                                verbose_name='логин пользователя',)
    first_name = models.CharField(max_length=150,
                                  unique=True,
                                  verbose_name='имя пользователя',)
    last_name = models.CharField(max_length=150,
                                 unique=True,
                                 verbose_name='фамилия пользователя',)
    password = models.CharField(max_length=150,
                                unique=True,
                                verbose_name='пароль',)


class Following(models.Model):
    """Подписка на автора."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'following'], name='unique_following'
            )
        ]
