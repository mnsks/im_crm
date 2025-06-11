from django import forms
from .models import SaisieResultat

class SaisieResultatForm(forms.ModelForm):
    class Meta:
        model = SaisieResultat
        fields = ['mission', 'client', 'status', 'commentaire', 'duree_appel', 'rappel_prevu']
        widgets = {
            'commentaire': forms.Textarea(attrs={'rows': 3}),
            'rappel_prevu': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'duree_appel': forms.TimeInput(attrs={'type': 'time', 'step': '1'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Appliquer Bootstrap à tous les champs sauf status (radio custom)
        for name, field in self.fields.items():
            if name == 'status':
                continue  # rendu custom radio dans le template
            css_class = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (css_class + ' form-control').strip()
        # Filtrer les clients pour n'afficher que ceux de la mission
        if 'mission' in self.initial:
            mission = self.initial['mission']
            self.fields['client'].queryset = mission.clients.all()
