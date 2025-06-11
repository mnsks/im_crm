from django.db import models
from missions.models import Mission

class Script(models.Model):
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='scripts')
    version = models.CharField(max_length=10)
    est_actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_modification']
    
    def __str__(self):
        return f"{self.titre} (v{self.version})"
