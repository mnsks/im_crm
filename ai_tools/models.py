from django.db import models
from interactions.models import Interaction
from agents.models import Agent
from formations.models import Formation

class AnalyseSentiment(models.Model):
    texte_feedback = models.TextField()
    score_sentiment = models.FloatField()
    sentiment = models.CharField(max_length=50)
    confiance = models.FloatField()
    date_analyse = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ['-date_analyse']

    def __str__(self):
        return f"Analyse sentiment : {self.sentiment} (score: {self.score_sentiment:.2f})"

class PredictionPerformance(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='predictions_performance')
    date_prediction = models.DateTimeField(auto_now_add=True)
    kpi_predit = models.FloatField()
    confiance = models.FloatField()
    alerte = models.BooleanField(default=False)

    def __str__(self):
        return f"Prédiction KPI {self.agent.username} : {self.kpi_predit:.2f}"

class RecommandationFormation(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='recommandations_formation')
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE)
    score = models.FloatField()
    date_recommandation = models.DateTimeField(auto_now_add=True)
    appliquee = models.BooleanField(default=False)

    def __str__(self):
        return f"Recommandation {self.formation.titre} pour {self.agent.username}"

class OptimisationPlanning(models.Model):
    date_optimisation = models.DateTimeField(auto_now_add=True)
    score_optimisation = models.FloatField()
    nombre_agents = models.IntegerField()
    nombre_missions = models.IntegerField()
    details = models.JSONField(default=dict)

    def __str__(self):
        return f"Optimisation du {self.date_optimisation} - Score: {self.score_optimisation}"
