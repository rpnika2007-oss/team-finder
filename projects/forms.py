from django import forms

from users.models import Skill
from users.utils import validate_github_url

from .models import Project


class ProjectForm(forms.ModelForm):
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
            "status": forms.Select(choices=((Project.OPEN, "Открыт"), (Project.CLOSED, "Закрыт"))),
        }

    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url")
        validate_github_url(github_url)
        return github_url