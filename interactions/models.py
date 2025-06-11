from django.db import models
from core.models import ClientFinal, User
from missions.models import Mission

class Interaction(models.Model):
    TYPE_CHOICES = [
        ('appel_entrant', 'Appel entrant'),
        ('appel_sortant', 'Appel sortant'),
        ('email', 'Email'),
        ('chat', 'Chat'),
        ('sms', 'SMS'),
        ('autre', 'Autre'),
    ]
    client = models.ForeignKey(ClientFinal, on_delete=models.CASCADE, related_name='interactions')
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='interactions')
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='interactions')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    date = models.DateTimeField(auto_now_add=True)
    contenu = models.TextField(blank=True)
    resultat = models.CharField(max_length=255, blank=True)
    def __str__(self):
        return f"{self.type} - {self.client.nom} ({self.date})"
