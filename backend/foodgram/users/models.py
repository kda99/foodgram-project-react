from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.models import UniqueConstraint
from django.db import models


# class UserManager(BaseUserManager):
#     def create_user(self, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError('The Email field must be set')
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         if password:
#             user.set_password(password)
#         user.save(using=self._db)
#         return user
#
#     def create_superuser(self, email, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         return self.create_user(email, password, **extra_fields)


class User(AbstractUser):


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
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    # def save(self, *args, **kwargs):
    #     if not self.pk:  # Если это новый пользователь
    #         self.set_password(self.password)
    #     super().save(*args, **kwargs)


    def __str__(self):
        return self.first_name + ' ' + self.last_name



class Subscription(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followed',
        verbose_name='Подписываемый автор',
    )

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'author'],
                             name='unique_subscription'),
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
