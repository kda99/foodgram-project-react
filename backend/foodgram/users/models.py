from django.contrib.auth.models import AbstractUser
from django.db.models import UniqueConstraint
from django.db import models


class User(AbstractUser):

 #   USER = 'user'
 #   ADMIN = 'admin'

    email = models.EmailField(
        'Электронная почта',
        max_length=254,
        blank=False,
        null=False,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=False,
        null=False,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=False,
        null=False,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'last_name', 'first_name', ]

    class Meta:
        ordering = ['-id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'



# class Subscription(models.Model):
#     """Подписки на авторов."""
#
#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='follower',
#         verbose_name='Подписчик',
#     )
#     author = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='following',
#         verbose_name='Автор, на которого подписываются',
#     )
#
#     class Meta:
#         verbose_name = 'Подписка'
#         verbose_name_plural = 'Подписки'
#         constraints = [
#             UniqueConstraint(fields=['user', 'author'], name='unique_subscription'),
#         ]
