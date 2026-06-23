from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import UserManager
from .utils import make_default_avatar

SKILL_NAME_LIMIT = 124
USER_NAME_LIMIT = 124
PHONE_LIMIT = 12
ABOUT_LIMIT = 256


class Skill(models.Model):
    name = models.CharField(
        "Название навыка",
        max_length=SKILL_NAME_LIMIT,
        unique=True,
        db_index=True,
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"

    def __str__(self):
        return self.name


def avatar_upload_to(instance, filename):
    return f"avatars/user_{instance.pk or 'new'}/{filename}"


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("Email", unique=True)
    name = models.CharField("Имя", max_length=USER_NAME_LIMIT)
    surname = models.CharField("Фамилия", max_length=USER_NAME_LIMIT)
    avatar = models.ImageField(
        "Аватар", 
        upload_to=avatar_upload_to, 
        blank=True
    )
    phone = models.CharField(
        "Телефон",
        max_length=PHONE_LIMIT,
        unique=True,
        blank=True,
        null=True
    )
    github_url = models.URLField("GitHub", blank=True)
    about = models.TextField(
        "О себе",
        max_length=ABOUT_LIMIT,
        blank=True
    )
    skills = models.ManyToManyField(
        Skill, 
        blank=True, 
        related_name="users"
    )
    is_active = models.BooleanField("Активный", default=True)
    is_staff = models.BooleanField("Администратор", default=False)
    created_at = models.DateTimeField("Дата регистрации", auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("name", "surname")

    class Meta:
        ordering = ("id",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.name} {self.surname}"

    @property
    def full_name(self):
        return f"{self.name} {self.surname}".strip()

    def save(self, *args, **kwargs):
        if not self.avatar:
            default_avatar = make_default_avatar(self.name, self.email)
            self.avatar.save("avatar.png", default_avatar, save=False)
        super().save(*args, **kwargs)