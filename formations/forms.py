from django import forms
from .models import InscriptionFormation, Formation, Participation

class FormationForm(forms.ModelForm):
    class Meta:
        model = Formation
        fields = ['titre', 'description', 'date', 'duree', 'centre', 'missions']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'missions': forms.SelectMultiple(attrs={'class': 'form-control'})
        }

class InscriptionFormationForm(forms.ModelForm):
    date_naissance = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = InscriptionFormation
        fields = ['nom_prenom', 'email', 'telephone', 'date_naissance', 'budget', 'num_edof', 'formation', 'adresse_postale']
        widgets = {
            'adresse_postale': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'nom_prenom': 'Nom et prénom',
            'email': 'Adresse mail',
            'telephone': 'Téléphone',
            'date_naissance': 'Date de naissance',
            'budget': 'Budget',
            'num_edof': 'Numéro EDOF',
            'formation': 'Formation',
            'adresse_postale': 'Adresse postale',
        }

class ParticipationForm(forms.ModelForm):
    class Meta:
        model = Participation
        fields = ['commentaire']
        widgets = {
            'commentaire': forms.Textarea(attrs={'rows': 3})
        }
