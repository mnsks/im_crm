from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import CentreAppels, User, EntrepriseDonneuseOrdre
from formations.models import Formation, Participation, Quiz
from agents.models import Agent
from ai_tools.training_analytics import TrainingAnalytics
import datetime

class Command(BaseCommand):
    help = 'Crée une formation test et exécute le workflow complet'

    def handle(self, *args, **kwargs):
        # 1. Créer une entreprise donneuse d'ordre et un centre d'appels
        entreprise, _ = EntrepriseDonneuseOrdre.objects.get_or_create(
            nom="Entreprise Test",
            defaults={
                "description": "Entreprise de test pour le workflow de formation"
            }
        )
        
        centre, created = CentreAppels.objects.get_or_create(
            nom="Centre Test",
            defaults={
                "entreprise": entreprise,
                "is_external": True
            }
        )
        self.stdout.write(self.style.SUCCESS(f'Centre créé: {centre.nom}'))

        # 2. Créer une formation
        formation = Formation.objects.create(
            titre="Formation Test Compétences Relationnelles",
            centre=centre,
            date=timezone.now().date() + datetime.timedelta(days=7),
            duree=8,
            description="Formation sur la gestion de la relation client et la communication",
            type="soft_skills"
        )
        self.stdout.write(self.style.SUCCESS(f'Formation créée: {formation.titre}'))

        # 3. Ajouter des quiz
        quiz1 = Quiz.objects.create(
            formation=formation,
            question="Quelle est la première étape d'une communication efficace ?",
            reponse="L'écoute active"
        )
        quiz2 = Quiz.objects.create(
            formation=formation,
            question="Comment gérer un client mécontent ?",
            reponse="Rester calme et empathique"
        )
        self.stdout.write(self.style.SUCCESS('Quiz créés'))

        # 4. Créer des agents test
        agents_created = []
        for i in range(3):
            username = f"agent_test_{i}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@example.com",
                    "first_name": f"Agent{i}",
                    "last_name": "Test"
                }
            )
            if created:
                user.set_password("test123!")
                user.save()
            
            agent, created = Agent.objects.get_or_create(
                user=user,
                defaults={
                    "centre_appel": centre,
                    "date_embauche": timezone.now().date(),
                    "niveau_competence": 1,
                    "specialites": ["relation_client"]
                }
            )
            agents_created.append(agent)
            self.stdout.write(self.style.SUCCESS(f'Agent créé: {agent.user.username}'))

        # 5. Inscrire les agents à la formation
        for agent in agents_created:
            participation = Participation.objects.create(
                formation=formation,
                agent=agent.user,
                statut="en_attente"
            )
            self.stdout.write(self.style.SUCCESS(f'Inscription créée pour {agent.user.username}'))

        # 6. Simuler la validation d'une participation
        if agents_created:
            participation = Participation.objects.filter(agent=agents_created[0].user).first()
            if participation:
                participation.statut = "validee"
                participation.score = 0.85
                participation.satisfaction = 0.9
                participation.commentaire = "Formation très enrichissante"
                participation.save()
                self.stdout.write(self.style.SUCCESS(f'Participation validée pour {agents_created[0].user.username}'))

        # 7. Tester les analytics
        analytics = TrainingAnalytics()
        metrics = analytics.get_global_metrics()
        self.stdout.write("\nMétriques globales :")
        self.stdout.write(str(metrics))

        try:
            recommendations = analytics.get_recommendations()
            self.stdout.write("\nRecommandations :")
            for rec in recommendations:
                self.stdout.write(f"- {rec['titre']}: {rec['description']}")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Impossible de générer les recommandations : {str(e)}"))

        self.stdout.write(self.style.SUCCESS('Test du workflow de formation terminé avec succès'))
