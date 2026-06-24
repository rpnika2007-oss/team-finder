from django.contrib import admin

from django.contrib.auth import get_user_model

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


from .models import Skill


User = get_user_model()



@admin.register(User)

class UserAdmin(BaseUserAdmin):

    ordering = ("email",)

    list_display = ("email", "name", "surname", "is_staff", "is_active")

    search_fields = ("email", "name", "surname")

    filter_horizontal = ("groups", "user_permissions", "skills")

    fieldsets = (

        (None, {"fields": ("email", "password")}),

        ("Профиль", {"fields": ("name", "surname", "avatar", "about", "phone", "github_url", "skills")}),

        ("Права", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),

        ("Даты", {"fields": ("last_login",)}),

    )

    add_fieldsets = (

        (None, {

            "classes": ("wide",),

            "fields": ("email", "name", "surname", "password1", "password2", "is_staff", "is_superuser"),

        }),

    )



@admin.register(Skill)

class SkillAdmin(admin.ModelAdmin):

    search_fields = ("name",)

    list_display = ("name",)
