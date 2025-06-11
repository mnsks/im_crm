from django.db import models
from core.models import User
from missions.models import Mission

class Feedback(models.Model):
    RATING_CHOICES = [
        (1, '1 - Très insatisfait'),
        (2, '2 - Insatisfait'),
        (3, '3 - Neutre'),
        (4, '4 - Satisfait'),
        (5, '5 - Très satisfait'),
    ]

    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='feedbacks')
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks_recus')
    evaluateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks_donnes')
    note = models.IntegerField(choices=RATING_CHOICES)
    commentaire = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Feedback de {self.evaluateur} pour {self.agent} - Mission {self.mission}"
