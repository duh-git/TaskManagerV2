from django import forms
from .models import Task
from django.contrib.auth import get_user_model

User = get_user_model()


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = "__all__"
        widgets = {
            "start_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "due_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].queryset = User.objects.all()
        self.fields["assigned_to"].required = False
