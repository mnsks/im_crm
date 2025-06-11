from django import forms
from .models import Feedback, SaisieResultat

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['texte']
        widgets = {
            'texte': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class SaisieResultatForm(forms.ModelForm):
    class Meta:
        model = SaisieResultat
        fields = ['indicateur', 'valeur']
        widgets = {
            'indicateur': forms.TextInput(attrs={'class': 'form-control'}),
            'valeur': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['indicateur'].help_text = 'Exemple: Nombre d\'appels, Taux de conversion, etc.'
        self.fields['valeur'].help_text = 'La valeur mesurée pour cet indicateur'
