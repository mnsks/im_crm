from django.db import models
from django.utils import timezone
from core.models import EntrepriseDonneuseOrdre, CentreAppels, User, ClientFinal
from missions.models import Mission

class Discussion(models.Model):
    titre = models.CharField(max_length=255)
    mission = models.ForeignKey(Mission, on_delete=models.SET_NULL, null=True, blank=True, related_name='discussions')
    centre = models.ForeignKey(CentreAppels, on_delete=models.SET_NULL, null=True, blank=True, related_name='discussions')
    entreprise = models.ForeignKey(EntrepriseDonneuseOrdre, on_delete=models.SET_NULL, null=True, blank=True, related_name='discussions')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.titre

class Message(models.Model):
    expediteur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='messages_envoyes')
    destinataire = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='messages_recus')
    objet = models.CharField(max_length=255)
    contenu = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_envoi']

    def __str__(self):
        return f"{self.expediteur} -> {self.destinataire} : {self.objet}"

class Notification(models.Model):
    TYPES = [
        ('mission', 'Mission'),
        ('message', 'Message'),
        ('formation', 'Formation'),
        ('feedback', 'Feedback'),
        ('system', 'Système')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True)
    icon_class = models.CharField(max_length=50, default='fas fa-bell')
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user}"

    def mark_as_read(self):
        if not self.read:
            self.read = True
            self.save()
