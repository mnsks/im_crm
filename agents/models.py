from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    centre_appel = models.ForeignKey('core.CentreAppels', on_delete=models.CASCADE)
    niveau_competence = models.IntegerField(default=1)
    disponible = models.BooleanField(default=True)
    date_embauche = models.DateField()
    specialites = models.JSONField(default=list)

    def __str__(self):
        return f"Agent: {self.user.username}"

    class Meta:
        verbose_name = "Agent"
        verbose_name_plural = "Agents"
