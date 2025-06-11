from django import forms
from .models import KPI

class KPIForm(forms.ModelForm):
    class Meta:
        model = KPI
        fields = ['nom', 'valeur', 'date', 'mission', 'centre', 'entreprise']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
