from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['mission', 'agent', 'note', 'commentaire']
        widgets = {
            'commentaire': forms.Textarea(attrs={'rows': 4}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Appliquer Bootstrap sur tous les champs sauf radio/checkbox
        for name, field in self.fields.items():
            if not isinstance(field.widget, (forms.RadioSelect, forms.CheckboxInput)):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs.update({'class': 'form-check-input'})
        # Filtrer les agents pour n'afficher que ceux qui sont assignés à la mission
        if 'mission' in self.initial:
            mission = self.initial['mission']
            self.fields['agent'].queryset = mission.agents.all()
