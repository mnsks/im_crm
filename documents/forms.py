from django import forms
from .models import Document
from core.models import EntrepriseDonneuseOrdre

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['titre', 'description', 'fichier', 'type', 'entreprise']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'type': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, is_admin=False, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Ajouter le champ entreprise pour les administrateurs
        if is_admin:
            self.fields['entreprise'] = forms.ModelChoiceField(
                queryset=EntrepriseDonneuseOrdre.objects.all(),
                widget=forms.Select(attrs={'class': 'form-select'}),
                required=True
            )
        
        # Ajouter les classes Bootstrap aux champs
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})

    def clean_fichier(self):
        fichier = self.cleaned_data.get('fichier')
        if fichier:
            # Tronquer le nom du fichier si > 100 caractères
            import os
            from django.core.files.base import ContentFile
            nom, ext = os.path.splitext(fichier.name)
            if len(fichier.name) > 100:
                from django.contrib import messages
                request = self.initial.get('request')
                nouveau_nom = nom[:100-len(ext)] + ext
                fichier.name = nouveau_nom
                # Si on a accès à request, afficher un message
                if request:
                    messages.warning(request, "Le nom du fichier a été tronqué à 100 caractères pour respecter la limite autorisée.")
            return fichier
        return fichier
