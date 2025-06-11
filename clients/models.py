from django.db import models
from core.models import EntrepriseDonneuseOrdre

class Client(models.Model):
    nom = models.CharField(max_length=200)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    entreprise = models.ForeignKey('core.EntrepriseDonneuseOrdre', on_delete=models.CASCADE, related_name='clients_entreprise')
    adresse = models.TextField()
    notes = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom
