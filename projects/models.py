from django.conf import settings
from django.db import models

from users.models import Skill

from .constants import PROJECT_NAME_LIMIT, PROJECT_STATUS_LIMIT


class Project(models.Model):

    OPEN = "open"

    CLOSED = "closed"

    STATUS_OPTIONS = (
        (OPEN, "Открыт"),
        (CLOSED, "Закрыт"),
    )

    name = models.CharField("Название проекта", max_length=PROJECT_NAME_LIMIT)

    description = models.TextField("Описание проекта", blank=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name="Автор",
    )

    created_at = models.DateTimeField("Дата создания", auto_now_add=True, db_index=True)

    github_url = models.URLField("GitHub", blank=True)

    status = models.CharField(
        "Статус",
        max_length=PROJECT_STATUS_LIMIT,
        choices=STATUS_OPTIONS,
        default=OPEN,
    )

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="participated_projects",
        verbose_name="Участники",
    )

    required_skills = models.ManyToManyField(
        Skill,
        blank=True,
        related_name="projects",
        verbose_name="Необходимые навыки",
    )

    favorites = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="favorite_projects",
        verbose_name="Избранное",
    )

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.name
    