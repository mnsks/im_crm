from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ('donneur_ordre', "Entreprise Donneuse d'Ordre"),
        ('centre', "Centre d'Appels"),
        ('centre_appel', "Centre d'Appels (variante)"),
        ('agent', "Agent"),
        ('client', "Client Final"),
        ('admin', "Administrateur"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    # Pour rattacher à une entité (ex: agent -> centre)
    parent_centre = models.ForeignKey('CentreAppels', null=True, blank=True, on_delete=models.SET_NULL, related_name='agents')
    parent_entreprise = models.ForeignKey('EntrepriseDonneuseOrdre', null=True, blank=True, on_delete=models.SET_NULL, related_name='entreprise_users')
    # Pour les clients finaux, rattachement optionnel à une entreprise
    parent_client_entreprise = models.ForeignKey('EntrepriseDonneuseOrdre', null=True, blank=True, on_delete=models.SET_NULL, related_name='clients')

class EntrepriseDonneuseOrdre(models.Model):
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    espace_documents = models.FileField(upload_to='entreprises/documents/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.nom

class CentreAppels(models.Model):
    nom = models.CharField(max_length=255)
    is_external = models.BooleanField(default=False)
    entreprise = models.ForeignKey(EntrepriseDonneuseOrdre, on_delete=models.CASCADE, related_name='centres')
    espace_saisie = models.FileField(upload_to='centres/saisies/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.nom

class ClientFinal(models.Model):
    nom = models.CharField(max_length=255)
    email = models.EmailField()
    telephone = models.CharField(max_length=30, blank=True)
    entreprise = models.ForeignKey(EntrepriseDonneuseOrdre, on_delete=models.CASCADE, related_name='clients_final')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.nom
