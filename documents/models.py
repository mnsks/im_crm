from django.db import models
from django.utils import timezone
from core.models import EntrepriseDonneuseOrdre

class Document(models.Model):
    TYPE_CHOICES = [
        ('contrat', 'Contrat'),
        ('facture', 'Facture'),
        ('autre', 'Autre'),
    ]

    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    fichier = models.FileField(upload_to='documents/')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='autre')
    entreprise = models.ForeignKey(EntrepriseDonneuseOrdre, on_delete=models.CASCADE, related_name='documents_uploaded')
    date_creation = models.DateTimeField(default=timezone.now)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_modification']
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'

    def __str__(self):
        return self.titre

class RapportGenere(models.Model):
    TYPE_CHOICES = [
        ('mission', 'Rapport de mission'),
        ('performance', 'Rapport de performance'),
        ('financier', 'Rapport financier'),
        ('activite', 'Rapport d\'activité'),
    ]

    titre = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    entreprise = models.ForeignKey(EntrepriseDonneuseOrdre, on_delete=models.CASCADE, related_name='documents_generated')
    contenu = models.JSONField(help_text='Données utilisées pour générer le rapport')
    date_generation = models.DateTimeField(default=timezone.now)
    derniere_consultation = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date_generation']
        verbose_name = 'Rapport généré'
        verbose_name_plural = 'Rapports générés'

    def __str__(self):
        return f"{self.get_type_display()} - {self.titre}"

    def marquer_comme_consulte(self):
        self.derniere_consultation = timezone.now()
        self.save()
