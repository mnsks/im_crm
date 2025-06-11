from django.db import models
from core.models import User
from missions.models import Mission
from clients.models import Client

class SaisieResultat(models.Model):
    TYPE_APPEL_CHOICES = [
        ('entrant', 'Appel entrant'),
        ('sortant', 'Appel sortant'),
    ]

    STATUS_CHOICES = [
        ('success', 'Succès'),
        ('failure', 'Échec'),
        ('callback', 'Rappel nécessaire'),
        ('unavailable', 'Indisponible'),
    ]

    type_appel = models.CharField(max_length=10, choices=TYPE_APPEL_CHOICES, default='sortant')
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='resultats_saisie')
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saisies_resultats')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='interactions_saisie')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    commentaire = models.TextField()
    duree_appel = models.DurationField()
    date_appel = models.DateTimeField(auto_now_add=True)
    rappel_prevu = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-date_appel']
        verbose_name = 'Saisie de résultat'
        verbose_name_plural = 'Saisies de résultats'
    
    def __str__(self):
        return f"Appel {self.status} - {self.client} par {self.agent}"
