from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta
import random
import uuid

from core.models import User, EntrepriseDonneuseOrdre, CentreAppels
from clients.models import Client
from missions.models import Mission
from saisie.models import SaisieResultat
from formations.models import Formation, Participation
from communication.models import Message
from scripts.models import Script
from feedback.models import Feedback

class Command(BaseCommand):
    help = 'Crée des données de test pour toutes les tables'

    def handle(self, *args, **kwargs):
        # Nettoyage des données existantes
        self.stdout.write("Nettoyage des données existantes...")
        Feedback.objects.all().delete()
        Message.objects.all().delete()
        Participation.objects.all().delete()
        Formation.objects.all().delete()
        SaisieResultat.objects.all().delete()
        Script.objects.all().delete()
        Mission.objects.all().delete()
        Client.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        CentreAppels.objects.all().delete()
        EntrepriseDonneuseOrdre.objects.all().delete()
        self.stdout.write("Nettoyage terminé.\n")

        # Création des entreprises
        entreprises = []
        for i in range(1, 4):
            entreprise = EntrepriseDonneuseOrdre.objects.create(
                nom=f"Entreprise {i}",
                description=f"Description de l'entreprise {i}"
            )
            entreprises.append(entreprise)

        # Création des centres d'appels
        centres = []
        for i in range(1, 6):
            centre = CentreAppels.objects.create(
                nom=f"Centre d'appels {i}",
                is_external=random.choice([True, False]),
                entreprise=random.choice(entreprises)
            )
            centres.append(centre)

        # Création des utilisateurs avec différents rôles
        users = []
        roles = ['admin', 'centre', 'agent', 'entreprise']
        centre = random.choice(centres)
        entreprise = random.choice(entreprises)
        for i in range(1, 21):
            role = roles[i % len(roles)]
            username = f"{role}_{uuid.uuid4().hex[:8]}"
            user = User.objects.create(
                username=username,
                password=make_password('password123'),
                email=f"{username}@example.com",
                first_name=f"Prénom {role} {i}",
                last_name=f"Nom {role} {i}",
                role=role,
                parent_centre=centre if role == 'agent' else None,
                parent_entreprise=entreprise if role == 'entreprise' else None
            )
            users.append(user)

        # Création des clients
        clients = []
        for i in range(1, 31):
            client = Client.objects.create(
                nom=f"Client {i}",
                email=f"client{i}@example.com",
                telephone=f"+33{i}12345678",
                entreprise=random.choice(entreprises),
                adresse=f"Adresse du client {i}",
                notes=f"Notes sur le client {i}"
            )
            clients.append(client)

        # Création des missions
        missions = []
        statuts = ['en_attente', 'en_cours', 'terminee', 'annulee']
        types = ['commercial', 'support', 'information']
        for i in range(1, 16):
            mission = Mission.objects.create(
                titre=f"Mission {i}",
                description=f"Description de la mission {i}",
                entreprise=random.choice(entreprises),
                centre=random.choice(centres),
                date_debut=timezone.now() - timedelta(days=random.randint(1, 30)),
                date_fin=timezone.now() + timedelta(days=random.randint(1, 30)),
                status=random.choice(statuts),
                type=random.choice(types),
                objectifs=f"Objectifs de la mission {i}..."
            )
            missions.append(mission)

        # Création des scripts
        scripts = []
        for i in range(1, 11):
            script = Script.objects.create(
                titre=f"Script {i}",
                contenu=f"Contenu du script {i}...",
                mission=random.choice(missions)
            )
            scripts.append(script)

        # Création des saisies avec données historiques
        start_date = timezone.now() - timedelta(days=90)  # 3 mois d'historique
        for day in range(90):
            current_date = start_date + timedelta(days=day)
            # Créer 10-20 saisies par jour
            for i in range(random.randint(10, 20)):
                SaisieResultat.objects.create(
                    agent=random.choice([u for u in users if u.role == 'agent']),
                    client=random.choice(clients),
                    mission=random.choice(missions),
                    status=random.choice(['success', 'failure', 'callback', 'unavailable']),
                    commentaire=f"Commentaire saisie du {current_date.strftime('%Y-%m-%d')} - {i}",
                    duree_appel=timedelta(seconds=random.randint(30, 600)),
                    date_appel=current_date
                )

        # Création des formations
        formations = []
        for i in range(1, 11):
            formation = Formation.objects.create(
                titre=f"Formation {i}",
                description=f"Description de la formation {i}",
                date=timezone.now() + timedelta(days=random.randint(1, 30)),
                centre=random.choice(centres)
            )
            formations.append(formation)

        # Création des participations aux formations
        for i in range(1, 31):
            Participation.objects.create(
                formation=random.choice(formations),
                agent=random.choice(users),
                score=random.randint(0, 100) if random.random() > 0.3 else None
            )

        # Création des messages
        sujets = [
            "Question sur la mission",
            "Demande d'information",
            "Rapport journalier",
            "Problème technique",
            "Mise à jour importante"
        ]
        for i in range(1, 41):
            Message.objects.create(
                expediteur=random.choice(users),
                destinataire=random.choice(users),
                objet=f"{random.choice(sujets)} - {i}",
                contenu=f"Contenu du message {i}...",
                lu=random.choice([True, False])
            )

        # Création des feedbacks avec historique
        notes = [1, 2, 3, 4, 5]
        start_date = timezone.now() - timedelta(days=90)  # 3 mois d'historique
        for day in range(90):
            current_date = start_date + timedelta(days=day)
            # Créer 2-5 feedbacks par jour
            for i in range(random.randint(2, 5)):
                agent = random.choice([u for u in users if u.role == 'agent'])
                Feedback.objects.create(
                    evaluateur=random.choice([u for u in users if u.role in ['admin', 'centre', 'entreprise']]),
                    agent=agent,
                    mission=random.choice(missions),
                    note=random.choice(notes),
                    commentaire=f"Commentaire feedback du {current_date.strftime('%Y-%m-%d')} - {i}",
                    date_creation=current_date
                )

        self.stdout.write(self.style.SUCCESS('Données de test créées avec succès!'))
