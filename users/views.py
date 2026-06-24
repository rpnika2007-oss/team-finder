from urllib.parse import urlencode
import json

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from team_finder.utils import get_page

from .constants import SKILL_SUGGEST_LIMIT
from .forms import LoginForm, ProfileForm, RegisterForm, UserPasswordChangeForm
from .models import Skill, User


def participants(request):
    active_skill = request.GET.get("skill")
    participants_queryset = User.objects.filter(is_active=True).order_by("-id").prefetch_related("skills")

    if active_skill:
        participants_queryset = participants_queryset.filter(skills__name=active_skill)

    page_number = request.GET.get("page")
    page_obj = get_page(participants_queryset, page_number)
    query_prefix = urlencode({"skill": active_skill}) + "&" if active_skill else ""

    return render(
        request,
        "users/participants.html",
        {
            "participants": page_obj.object_list,
            "page_obj": page_obj,
            "all_skills": Skill.objects.values_list("name", flat=True).order_by("name"),
            "active_skill": active_skill,
            "query_prefix": query_prefix,
        },
    )


def register_view(request):
    form = RegisterForm(request.POST or None)

    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("projects:list")

    return render(request, "users/register.html", {"form": form})


def login_view(request):
    form = LoginForm(request, request.POST or None)

    if form.is_valid():
        login(request, form.user)
        return redirect("projects:list")

    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:list")


def profile(request, user_id):
    user_obj = get_object_or_404(
        User.objects.prefetch_related("skills", "owned_projects"),
        pk=user_id,
        is_active=True,
    )
    return render(request, "users/user-details.html", {"user": user_obj})


@login_required
def edit_profile(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)

    if form.is_valid():
        form.save()
        return redirect("users:profile", user_id=request.user.id)

    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    form = UserPasswordChangeForm(request.user, request.POST or None)

    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect("users:profile", user_id=request.user.id)

    return render(request, "users/change_password.html", {"form": form})


@require_GET
def skill_suggest(request):
    search_query = request.GET.get("q", "").strip()
    skills = Skill.objects.filter(name__istartswith=search_query).order_by("name")[:SKILL_SUGGEST_LIMIT]
    return JsonResponse(list(skills.values("id", "name")), safe=False)


@login_required
@require_POST
def add_skill(request, user_id):
    user_obj = get_object_or_404(User, pk=user_id)

    if request.user.pk != user_obj.pk:
        return JsonResponse({"error": "Недостаточно прав"}, status=403)

    if request.content_type == "application/json":
        data = json.loads(request.body or "{}")
        skill_id = data.get("skill_id")
        skill_name = (data.get("name") or "").strip()
    else:
        skill_id = request.POST.get("skill_id")
        skill_name = request.POST.get("name", "").strip()

    is_new = False

    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
    elif skill_name:
        skill, is_new = Skill.objects.get_or_create(name=skill_name)
    else:
        return JsonResponse({"error": "skill_id или name обязателен"}, status=400)

    existed = user_obj.skills.filter(pk=skill.pk).exists()
    user_obj.skills.add(skill)

    return JsonResponse(
        {
            "id": skill.id,
            "name": skill.name,
            "skill_id": skill.id,
            "created": is_new,
            "added": not existed,
        }
    )


@login_required
@require_POST
def remove_skill(request, user_id, skill_id):
    user_obj = get_object_or_404(User, pk=user_id)

    if request.user.pk != user_obj.pk:
        return JsonResponse({"error": "Недостаточно прав"}, status=403)

    skill = get_object_or_404(Skill, pk=skill_id)
    if not user_obj.skills.filter(pk=skill.pk).exists():
        return JsonResponse({"removed": False}, status=400)

    user_obj.skills.remove(skill)
    return JsonResponse({"removed": True, "skill_id": skill.id})
