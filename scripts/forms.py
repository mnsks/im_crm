from django import forms
from .models import Script

class ScriptForm(forms.ModelForm):
    class Meta:
        model = Script
        fields = ['titre', 'contenu', 'mission']
        widgets = {
            'contenu': forms.Textarea(attrs={'rows': 10}),
        }
