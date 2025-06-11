from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, CentreAppels

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'password1', 'password2', 'role', 'first_name', 'last_name', 'email', 'parent_centre', 'parent_entreprise', 'parent_client_entreprise')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'role', 'first_name', 'last_name', 'email', 'parent_centre', 'parent_entreprise', 'parent_client_entreprise')

class AgentCreationForm(UserCreationForm):
    parent_centre = forms.ModelChoiceField(
        queryset=CentreAppels.objects.all(), 
        required=False, 
        label="Centre d'appels de rattachement"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'parent_centre')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'agent' # Définit automatiquement le rôle à 'agent'
        if commit:
            user.save()
        return user

class AgentUpdateForm(forms.ModelForm):
    parent_centre = forms.ModelChoiceField(
        queryset=CentreAppels.objects.all(), 
        required=False, 
        label="Centre d'appels de rattachement",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'parent_centre', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # On s'assure que le rôle ne peut pas être changé via ce formulaire
        # et qu'il est bien 'agent' si l'instance est un agent.
        if self.instance and self.instance.pk and self.instance.role != 'agent':
            # Idéalement, ce formulaire ne devrait être utilisé que pour les agents.
            # On pourrait lever une exception ou désactiver les champs.
            pass 
        # On pourrait aussi s'assurer que le rôle est 'agent' si on crée un utilisateur via ce form,
        # mais AgentCreationForm est plus adapté pour ça.
