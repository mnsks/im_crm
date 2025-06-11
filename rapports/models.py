from django.db import models
from core.models import EntrepriseDonneuseOrdre, CentreAppels, User
from missions.models import Mission

class Rapport(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='rapports')
    centre = models.ForeignKey(CentreAppels, on_delete=models.CASCADE, related_name='rapports')
    entreprise = models.ForeignKey(EntrepriseDonneuseOrdre, on_delete=models.CASCADE, related_name='rapports')
    date = models.DateField(auto_now_add=True)
    fichier = models.FileField(upload_to='rapports/', blank=True, null=True)
    statistiques = models.TextField(blank=True)
    def __str__(self):
        return f"Rapport {self.mission.titre} - {self.date}"

class Feedback(models.Model):
    rapport = models.ForeignKey(Rapport, on_delete=models.CASCADE, related_name='feedbacks')
    auteur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedbacks')
    texte = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Feedback {self.rapport} - {self.auteur}"

class SaisieResultat(models.Model):
    STATUS_CHOICES = [
        ('success', 'Réussi'),
        ('failure', 'Échec'),
        ('pending', 'En attente'),
    ]
    
    rapport = models.ForeignKey(Rapport, on_delete=models.CASCADE, related_name='saisies')
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='saisies')
    indicateur = models.CharField(max_length=255)
    valeur = models.CharField(max_length=255)
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.indicateur}: {self.valeur} ({self.rapport})"
