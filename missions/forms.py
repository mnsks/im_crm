from django import forms
from .models import Mission
from core.models import EntrepriseDonneuseOrdre, CentreAppels

class MissionForm(forms.ModelForm):
    entreprise = forms.ModelChoiceField(
        queryset=EntrepriseDonneuseOrdre.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Entreprise Donneuse d'Ordre"
    )
    centre = forms.ModelChoiceField(
        queryset=CentreAppels.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Centre d'Appels",
        required=False
    )
    date_debut = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Date de début"
    )
    date_fin = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Date de fin",
        required=False
    )

    class Meta:
        model = Mission
        fields = ['titre', 'description', 'type', 'objectifs', 'entreprise', 'centre', 'date_debut', 'date_fin']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'objectifs': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
