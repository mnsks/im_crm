from django.db import models
from core.models import CentreAppels, User
from missions.models import Mission

class Formation(models.Model):
    TYPE_CHOICES = [
        ('technique', 'Technique'),
        ('soft_skills', 'Soft Skills'),
        ('produit', 'Produit'),
        ('process', 'Processus'),
        ('reglementaire', 'Réglementaire'),
    ]

    titre = models.CharField(max_length=255)
    centre = models.ForeignKey(CentreAppels, on_delete=models.CASCADE, related_name='formations')
    missions = models.ManyToManyField(Mission, blank=True, related_name='formations')
    date = models.DateField()
    duree = models.PositiveIntegerField(help_text='Durée en heures', default=1)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='technique')

    def get_satisfaction_moyenne(self):
        """Retourne la satisfaction moyenne des agents ayant suivi la formation"""
        participations = self.participations.filter(
            statut='validee',
            satisfaction__isnull=False
        )
        if not participations.exists():
            return None
        return sum(p.satisfaction for p in participations) / participations.count()

    def __str__(self):
        return self.titre

class Quiz(models.Model):
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name='quizs')
    question = models.CharField(max_length=255)
    reponse = models.CharField(max_length=255)
    def __str__(self):
        return self.question

class Participation(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('validee', 'Validée'),
        ('refusee', 'Refusée'),
    ]

    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name='participations')
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='participations')
    date_inscription = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    score = models.FloatField(null=True, blank=True)
    satisfaction = models.FloatField(null=True, blank=True, help_text='Note de satisfaction de 0 à 1')
    commentaire = models.TextField(blank=True)
    def __str__(self):
        return f"{self.agent} - {self.formation} ({self.date_inscription})"

class InscriptionFormation(models.Model):
    nom_prenom = models.CharField(max_length=255)
    email = models.EmailField()
    telephone = models.CharField(max_length=30)
    date_naissance = models.DateField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    num_edof = models.CharField(max_length=30, blank=True)
    formation = models.CharField(max_length=255)
    adresse_postale = models.TextField()
    date_saisie = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.nom_prenom} - {self.formation} ({self.date_saisie.date()})"
