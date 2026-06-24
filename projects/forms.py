from django import forms
from users.models import Skill
from users.mixins import GitHubURLMixin
from .models import Project


class ProjectForm(GitHubURLMixin, forms.ModelForm):
    required_skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Необходимые навыки",
    )

    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status", "required_skills")
        widgets = {
            "status": forms.Select(choices=Project.STATUS_OPTIONS),
        }
