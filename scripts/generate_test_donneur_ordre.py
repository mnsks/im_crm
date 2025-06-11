import os
import sys
import django
from datetime import datetime, timedelta
import random

# Configurer l'environnement Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_externalisation.settings')
django.setup()

from django.utils import timezone
from missions.models import Mission
from saisie.models import SaisieResultat
from clients.models import EntrepriseDonneuseOrdre, Client
from core.models import CentreAppels
from django.contrib.auth import get_user_model

User = get_user_model()

def generate_test_data():
    """Génère des données de test pour le donneur d'ordre"""
    try:
        # Récupérer le donneur d'ordre
        entreprise = EntrepriseDonneuseOrdre.objects.first()
        if not entreprise:
            print("Aucune entreprise donneuse d'ordre trouvée")
            return

        # Période de test : 30 derniers jours
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)

        # Créer des clients de test
        clients = []
        for i in range(20):
            client = Client.objects.create(
                entreprise=entreprise,
                nom=f"Client Test {i+1}",
                email=f"client{i+1}@test.com",
                telephone=f"0{random.randint(600000000, 699999999)}",
                adresse=f"Adresse test {i+1}, {random.randint(10000, 99999)} Ville test {i+1}",
                notes=f"Client de test créé le {timezone.now().strftime('%Y-%m-%d')}"
            )
            clients.append(client)

        # Statuts possibles pour les missions
        statuts_mission = ['en_cours', 'terminee', 'en_attente', 'annulee']
        
        # Créer des missions de test
        for i in range(10):
            mission = Mission.objects.create(
                entreprise=entreprise,
                titre=f"Mission test {i+1}",
                description=f"Description de la mission test {i+1}",
                type=random.choice(['commercial', 'support', 'information']),
                date_debut=start_date + timedelta(days=random.randint(0, 15)),
                date_fin=end_date - timedelta(days=random.randint(0, 5)),
                status=random.choice(statuts_mission),
                objectifs=f"Objectif : {random.randint(100, 500)} appels à réaliser"
            )

            # Vérifier si un centre d'appel est disponible
            centres = CentreAppels.objects.all()
            if centres.exists():
                # Assigner un centre aléatoire à la mission
                mission.centre = random.choice(centres)
                mission.save()

                # Récupérer les agents du centre
                agents = User.objects.filter(role='agent', parent_centre=mission.centre)
                if agents.exists():
                    # Générer des résultats d'appels pour cette mission
                    nb_appels = random.randint(50, 200)
                    for _ in range(nb_appels):
                        date_appel = mission.date_debut + timedelta(
                            days=random.randint(0, (mission.date_fin - mission.date_debut).days)
                        )
                        
                        SaisieResultat.objects.create(
                            mission=mission,
                            agent=random.choice(agents),
                            client=random.choice(clients),
                            date_appel=date_appel,
                            type_appel='sortant',
                            status=random.choice(['success', 'failure', 'callback', 'unavailable']),
                            duree_appel=timedelta(minutes=random.randint(1, 30)),
                            commentaire=f"Appel test du {date_appel.strftime('%Y-%m-%d')}"
                        )

        print(f"Données générées avec succès pour l'entreprise {entreprise.nom}")
        print(f"- {Mission.objects.filter(entreprise=entreprise).count()} missions créées")
        print(f"- {SaisieResultat.objects.filter(mission__entreprise=entreprise).count()} appels générés")

    except Exception as e:
        print(f"Erreur lors de la génération des données : {str(e)}")

if __name__ == '__main__':
    generate_test_data()
