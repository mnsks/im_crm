from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta
from core.models import User, EntrepriseDonneuseOrdre, CentreAppels, ClientFinal
from missions.models import Mission
from saisie.models import SaisieResultat
from formations.models import Formation, Participation
from communication.models import Message
from scripts.models import Script
from feedback.models import Feedback
import random

class Command(BaseCommand):
    help = 'Crée des données de test pour toutes les tables'

    def handle(self, *args, **kwargs):
        # Création des entreprises
        entreprises = []
        for i in range(1, 4):
            entreprise = EntrepriseDonneuseOrdre.objects.create(
                nom=f"Entreprise {i}",
                adresse=f"Adresse Entreprise {i}",
                telephone=f"+33{i}11223344",
                email=f"contact@entreprise{i}.com"
            )
            entreprises.append(entreprise)

        # Création des centres d'appels
        centres = []
        for i in range(1, 6):
            centre = CentreAppels.objects.create(
                nom=f"Centre d'appels {i}",
                adresse=f"Adresse Centre {i}",
                telephone=f"+33{i}99887766",
                email=f"contact@centre{i}.com",
                entreprise=random.choice(entreprises)
            )
            centres.append(centre)

        # Création des utilisateurs avec différents rôles
        users = []
        roles = ['admin', 'centre', 'agent']
        for i in range(1, 21):
            role = roles[i % len(roles)]
            user = User.objects.create(
                username=f"user{i}",
                email=f"user{i}@example.com",
                password=make_password('password123'),
                first_name=f"Prénom{i}",
                last_name=f"Nom{i}",
                role=role,
                parent_centre=random.choice(centres) if role in ['centre', 'agent'] else None
            )
            users.append(user)

        # Création des clients
        clients = []
        for i in range(1, 31):
            client = ClientFinal.objects.create(
                nom=f"Client {i}",
                prenom=f"Prénom Client {i}",
                telephone=f"+33{i}12345678",
                email=f"client{i}@example.com",
                adresse=f"Adresse Client {i}",
                entreprise=random.choice(entreprises)
            )
            clients.append(client)

        # Création des missions
        missions = []
        statuts = ['en_cours', 'terminee', 'planifiee']
        for i in range(1, 16):
            mission = Mission.objects.create(
                titre=f"Mission {i}",
                description=f"Description de la mission {i}",
                entreprise=random.choice(entreprises),
                centre=random.choice(centres),
                date_debut=datetime.now() - timedelta(days=random.randint(1, 30)),
                date_fin=datetime.now() + timedelta(days=random.randint(1, 30)),
                statut=random.choice(statuts)
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

        # Création des saisies
        resultats = ['succes', 'echec', 'rappel']
        for i in range(1, 51):
            SaisieResultat.objects.create(
                agent=random.choice([u for u in users if u.role == 'agent']),
                client=random.choice(clients),
                mission=random.choice(missions),
                resultat=random.choice(resultats),
                commentaire=f"Commentaire saisie {i}",
                duree_appel=random.randint(30, 600)
            )

        # Création des formations
        formations = []
        for i in range(1, 11):
            formation = Formation.objects.create(
                titre=f"Formation {i}",
                description=f"Description de la formation {i}",
                date=datetime.now() + timedelta(days=random.randint(-10, 30))
            )
            formations.append(formation)

        # Création des participations aux formations
        for i in range(1, 31):
            Participation.objects.create(
                agent=random.choice([u for u in users if u.role == 'agent']),
                formation=random.choice(formations),
                date_inscription=datetime.now() - timedelta(days=random.randint(1, 10)),
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

        # Création des feedbacks
        notes = [1, 2, 3, 4, 5]
        for i in range(1, 26):
            Feedback.objects.create(
                client=random.choice(clients),
                agent=random.choice([u for u in users if u.role == 'agent']),
                mission=random.choice(missions),
                note=random.choice(notes),
                commentaire=f"Commentaire feedback {i}"
            )

        self.stdout.write(self.style.SUCCESS('Données de test créées avec succès!'))
