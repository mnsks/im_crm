from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from core.models import User, CentreAppels

class AgentCreationForm(UserCreationForm):
    parent_centre = forms.ModelChoiceField(
        queryset=CentreAppels.objects.all(),
        required=True,
        label="Centre d'appels"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'parent_centre')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'agent'
        if commit:
            user.save()
        return user

class AgentChangeForm(UserChangeForm):
    parent_centre = forms.ModelChoiceField(
        queryset=CentreAppels.objects.all(),
        required=True,
        label="Centre d'appels"
    )
    password = None  # Remove password field from edit form

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'parent_centre', 'is_active')
