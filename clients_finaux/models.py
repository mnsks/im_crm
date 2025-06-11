from django.db import models
from django.conf import settings
from missions.models import Mission

class HistoriqueAppel(models.Model):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='historique_appels')
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='historique_appels')
    date_appel = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=50)
    commentaire = models.TextField(blank=True)
    duree = models.DurationField(null=True, blank=True)
    prochain_contact = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date_appel']
        verbose_name = 'Historique d\'appel'
        verbose_name_plural = 'Historique des appels'

    def __str__(self):
        return f'Appel {self.client} - {self.mission} ({self.date_appel})'

class Requete(models.Model):
    STATUT_CHOICES = [
        ('nouvelle', 'Nouvelle'),
        ('en_cours', 'En cours'),
        ('resolue', 'Résolue'),
        ('annulee', 'Annulée')
    ]

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requetes')
    titre = models.CharField(max_length=200)
    description = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='nouvelle')
    priorite = models.IntegerField(default=0)

    class Meta:
        ordering = ['-date_creation']
        verbose_name = 'Requête'
        verbose_name_plural = 'Requêtes'

    def __str__(self):
        return f'{self.titre} ({self.client})'

class PreferenceContact(models.Model):
    client = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='preferences_contact')
    horaires_preferes = models.CharField(max_length=200, help_text='Ex: 9h-12h, 14h-17h')
    jours_exclus = models.CharField(max_length=200, blank=True, help_text='Ex: Lundi, Mercredi')
    mode_contact_prefere = models.CharField(max_length=50, default='telephone')
    numero_telephone = models.CharField(max_length=20)
    email_contact = models.EmailField()
    ne_pas_deranger = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Préférence de contact'
        verbose_name_plural = 'Préférences de contact'

    def __str__(self):
        return f'Préférences de {self.client}'

# Create your models here.
