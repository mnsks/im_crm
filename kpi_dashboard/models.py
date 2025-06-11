from django.db import models
from core.models import EntrepriseDonneuseOrdre, CentreAppels
from missions.models import Mission

class KPI(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='kpis')
    centre = models.ForeignKey(CentreAppels, on_delete=models.CASCADE, related_name='kpis')
    entreprise = models.ForeignKey(EntrepriseDonneuseOrdre, on_delete=models.CASCADE, related_name='kpis')
    nom = models.CharField(max_length=255)
    valeur = models.FloatField()
    date = models.DateField(auto_now_add=True)
    def __str__(self):
        return f"{self.nom} - {self.valeur} ({self.date})"
