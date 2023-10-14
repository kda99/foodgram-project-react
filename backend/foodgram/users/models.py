from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint


class User(AbstractUser):
    email = models.EmailField(
        "Электронная почта",
        max_length=254,
        blank=False,
        null=False,
        unique=True,
    )
    first_name = models.CharField(
        "Имя",
        max_length=150,
        blank=False,
        null=False,
    )
    last_name = models.CharField(
        "Фамилия",
        max_length=150,
        blank=False,
        null=False,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
        "last_name",
        "first_name",
    ]

    class Meta:
        ordering = ["id"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.first_name + " " + self.last_name


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followed",
        verbose_name="Подписываемый автор",
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["user", "author"],
                name="unique_subscription"), ]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ['author',]
