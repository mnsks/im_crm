from django.db import models
from django.utils import timezone
from agents.models import Agent

class KPI(models.Model):
    TYPE_CHOICES = [
        ('satisfaction', 'Satisfaction client'),
        ('performance', 'Performance'),
        ('qualite', 'Qualité'),
        ('formation', 'Formation')
    ]

    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='kpis')
    nom = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    valeur = models.FloatField()
    unite = models.CharField(max_length=20)
    date = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'KPI'
        verbose_name_plural = 'KPIs'
        ordering = ['-date']

    def __str__(self):
        return f"{self.nom}: {self.valeur}{self.unite}"
