from django.db import models
from django.conf import settings
from core.models import EntrepriseDonneuseOrdre, CentreAppels

class Mission(models.Model):
    TYPE_CHOICES = [
        ('commercial', 'Commercial'),
        ('support', 'Support/SAV'),
        ('information', 'Information'),
    ]
    
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
    ]
    
    titre = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='en_attente')
    objectifs = models.TextField()
    entreprise = models.ForeignKey(EntrepriseDonneuseOrdre, on_delete=models.CASCADE, related_name='missions')
    centre = models.ForeignKey(CentreAppels, on_delete=models.SET_NULL, null=True, blank=True, related_name='missions')
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    agents = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='missions_assignees', blank=True)
    kpis = models.ManyToManyField('KPI', related_name='missions', blank=True)
    def __str__(self):
        return self.titre

class KPI(models.Model):
    TYPE_CHOICES = [
        ('quantitatif', 'Quantitatif'),
        ('qualitatif', 'Qualitatif'),
        ('temporel', 'Temporel'),
    ]

    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    unite = models.CharField(max_length=50, blank=True, help_text='Unité de mesure (%, heures, appels, etc.)')
    valeur_cible = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

class Ressource(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='ressources')
    nom = models.CharField(max_length=255)
    fichier = models.FileField(upload_to='missions/ressources/', blank=True, null=True)
    type = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    def __str__(self):
        return self.nom
