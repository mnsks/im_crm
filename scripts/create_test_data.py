import os
import django
import sys

# Chemin vers le dossier du projet (là où se trouve manage.py)
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_PATH)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_externalisation.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from core.models import EntrepriseDonneuseOrdre, CentreAppels, User
from missions.models import Mission
from feedback.models import Feedback
from datetime import date, timedelta

User = get_user_model()

@transaction.atomic
def create_test_data():
    try:
        # Nettoyage des anciennes données de test
        Feedback.objects.filter(commentaire__startswith="Feedback test pour la mission").delete()
        Mission.objects.filter(titre__startswith="Mission test").delete()
        User.objects.filter(username__in=["donneur_test", "agent_test"]).delete()
        CentreAppels.objects.filter(nom="Centre Test").delete()
        EntrepriseDonneuseOrdre.objects.filter(nom="Entreprise Test").delete()

        # 1. Créer une entreprise donneuse d'ordre
        entreprise = EntrepriseDonneuseOrdre.objects.create(
            nom="Entreprise Test",
            description="Entreprise de test pour les feedbacks"
        )
        print(f"[OK] Entreprise créée: {entreprise}")

        # 2. Créer un utilisateur donneur d'ordre
        donneur_ordre = User.objects.create_user(
            username="donneur_test",
            email="donneur@test.com",
            password="testpass123",
            first_name="Jean",
            last_name="Test",
            role="donneur_ordre",
            parent_entreprise=entreprise
        )
        print(f"[OK] Donneur d'ordre créé: {donneur_ordre}")

        # 3. Créer un centre d'appel
        centre = CentreAppels.objects.create(
            nom="Centre Test",
            is_external=True,
            entreprise=entreprise
        )
        print(f"[OK] Centre d'appel créé: {centre}")

        # 4. Créer un agent
        agent = User.objects.create_user(
            username="agent_test",
            email="agent@test.com",
            password="testpass123",
            first_name="Pierre",
            last_name="Agent",
            role="agent",
            parent_centre=centre
        )
        print(f"[OK] Agent créé: {agent}")

        # 5. Créer des missions
        missions = []
        today = date.today()
        for i in range(1, 4):
            mission = Mission.objects.create(
                titre=f"Mission test {i}",
                description=f"Description de la mission test {i}",
                type="commercial",  # Champ obligatoire
                status="en_cours",
                entreprise=entreprise,
                centre=centre,
                date_debut=today,
                date_fin=today + timedelta(days=30)
            )
            missions.append(mission)
            print(f"[OK] Mission créée: {mission}")

        # 6. Créer des feedbacks
        for mission in missions:
            feedback = Feedback.objects.create(
                mission=mission,
                agent=agent,
                evaluateur=donneur_ordre,
                note=4,
                commentaire=f"Feedback test pour la mission {mission.titre}"
            )
            print(f"[OK] Feedback créé: {feedback}")

        print("\nDonnées de test créées avec succès!")
        print(f"Identifiants donneur d'ordre: donneur_test / testpass123")
        print(f"ID entreprise: {entreprise.id}")
        print(f"Nombre de missions créées: {len(missions)}")
        print(f"Nombre de feedbacks créés: {Feedback.objects.filter(mission__entreprise=entreprise).count()}")

    except Exception as e:
        print(f"\nErreur lors de la création des données de test: {str(e)}")
        raise

if __name__ == "__main__":
    create_test_data()
