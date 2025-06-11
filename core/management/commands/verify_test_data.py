from django.core.management.base import BaseCommand
from django.db.models import Count, Avg
from core.models import User, EntrepriseDonneuseOrdre, CentreAppels
from clients.models import Client
from missions.models import Mission
from saisie.models import SaisieResultat
from formations.models import Formation, Participation
from communication.models import Message
from scripts.models import Script
from feedback.models import Feedback

class Command(BaseCommand):
    help = 'Vérifie l\'intégrité des données de test'

    def handle(self, *args, **kwargs):
        # Vérification des utilisateurs par rôle
        user_roles = User.objects.values('role').annotate(count=Count('id'))
        self.stdout.write("=== Utilisateurs par rôle ===")
        for role_count in user_roles:
            self.stdout.write(f"{role_count['role']}: {role_count['count']}")

        # Vérification des entreprises et centres
        self.stdout.write("\n=== Entreprises et Centres ===")
        self.stdout.write(f"Entreprises: {EntrepriseDonneuseOrdre.objects.count()}")
        self.stdout.write(f"Centres d'appels: {CentreAppels.objects.count()}")
        
        # Vérification des missions
        missions_count = Mission.objects.count()
        missions_with_scripts = Mission.objects.filter(scripts__isnull=False).distinct().count()
        self.stdout.write("\n=== Missions ===")
        self.stdout.write(f"Total missions: {missions_count}")
        self.stdout.write(f"Missions avec scripts: {missions_with_scripts}")

        # Vérification des saisies
        saisies = SaisieResultat.objects.all()
        self.stdout.write("\n=== Saisies ===")
        self.stdout.write(f"Total saisies: {saisies.count()}")
        self.stdout.write(f"Saisies par status: {dict(saisies.values_list('status').annotate(count=Count('id')))}")

        # Vérification des formations
        formations = Formation.objects.all()
        participations = Participation.objects.all()
        self.stdout.write("\n=== Formations ===")
        self.stdout.write(f"Total formations: {formations.count()}")
        self.stdout.write(f"Total participations: {participations.count()}")
        self.stdout.write(f"Participations avec score: {participations.exclude(score__isnull=True).count()}")

        # Vérification des feedbacks
        feedbacks = Feedback.objects.all()
        self.stdout.write("\n=== Feedbacks ===")
        self.stdout.write(f"Total feedbacks: {feedbacks.count()}")
        self.stdout.write(f"Notes moyennes: {feedbacks.aggregate(avg_note=Avg('note'))['avg_note']:.2f}")

        # Vérification des messages
        messages = Message.objects.all()
        self.stdout.write("\n=== Messages ===")
        self.stdout.write(f"Total messages: {messages.count()}")
        self.stdout.write(f"Messages lus: {messages.filter(lu=True).count()}")
