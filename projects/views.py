from urllib.parse import urlencode


from django.contrib.auth.decorators import login_required

from django.http import JsonResponse, Http404

from django.shortcuts import get_object_or_404, redirect, render

from django.views.decorators.http import require_POST


from team_finder.utils import get_page

from users.models import Skill


from .forms import ProjectForm

from .models import Project



def project_list(request):

    active_skill = request.GET.get("skill")

    projects_queryset = Project.objects.select_related("owner").prefetch_related(

        "participants",

        "required_skills",

        "favorites",

    )


    if active_skill:

        projects_queryset = projects_queryset.filter(required_skills__name=active_skill)


    page_number = request.GET.get("page")

    page_obj = get_page(projects_queryset, page_number)

    query_prefix = urlencode({"skill": active_skill}) + "&" if active_skill else ""


    return render(

        request,

        "projects/project_list.html",

        {

            "projects": page_obj.object_list,

            "page_obj": page_obj,

            "all_skills": Skill.objects.values_list("name", flat=True).order_by("name"),

            "active_skill": active_skill,

            "query_prefix": query_prefix,

        },

    )



def project_detail(request, project_id):

    project = get_object_or_404(

        Project.objects.select_related("owner").prefetch_related(

            "participants",

            "required_skills",

            "favorites",

        ),

        pk=project_id,

    )

    return render(request, "projects/project-details.html", {"project": project})



@login_required

def create_project(request):

    form = ProjectForm(request.POST or None)


    if form.is_valid():

        project = form.save(commit=False)

        project.owner = request.user

        project.save()

        form.save_m2m()

        project.participants.add(request.user)

        return redirect("projects:detail", project_id=project.id)


    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})



@login_required

def edit_project(request, project_id):

    project = get_object_or_404(Project, pk=project_id)


    if request.user != project.owner and not request.user.is_staff:

        return JsonResponse({"error": "Недостаточно прав"}, status=403)


    form = ProjectForm(request.POST or None, instance=project)


    if form.is_valid():

        form.save()

        return redirect("projects:detail", project_id=project.id)


    return render(request, "projects/create-project.html", {"form": form, "is_edit": True, "project": project})



@login_required

@require_POST

def complete_project(request, project_id):

    project = get_object_or_404(Project, pk=project_id)


    if request.user != project.owner and not request.user.is_staff:

        return JsonResponse({"error": "Недостаточно прав"}, status=403)


    if project.status == Project.OPEN:

        project.status = Project.CLOSED

        project.save(update_fields=["status"])


    return JsonResponse({"status": "ok", "project_status": project.status})



@login_required

@require_POST

def toggle_participate(request, project_id):

    project = get_object_or_404(Project, pk=project_id)


    if project.owner_id == request.user.id:

        return JsonResponse({"status": "ok", "participant": True})


    is_participant = project.participants.filter(pk=request.user.pk).exists()

    if is_participant:

        project.participants.remove(request.user)

    else:

        project.participants.add(request.user)


    return JsonResponse({"status": "ok", "participant": is_participant})



@login_required

@require_POST

def toggle_favorite(request, project_id):

    project = get_object_or_404(Project, pk=project_id)


    is_favorite = project.favorites.filter(pk=request.user.pk).exists()

    if is_favorite:

        project.favorites.remove(request.user)

    else:

        project.favorites.add(request.user)


    return JsonResponse({"status": "ok", "favorite": is_favorite})



@login_required

def favorite_projects(request):

    projects = request.user.favorite_projects.select_related("owner").prefetch_related(

        "participants",

        "required_skills",

        "favorites",

    )


    return render(request, "projects/favorite_projects.html", {"projects": projects})
