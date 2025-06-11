from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from ai_tools.training_recommender import TrainingRecommender
from formations.models import Formation, Participation
from agents.models import Agent
from core.models import CentreAppels, EntrepriseDonneuseOrdre
from kpis.models import KPI
from ai_tools.models import RecommandationFormation

class TestTrainingRecommender(TestCase):
    def setUp(self):
        self.recommender = TrainingRecommender()
        
        # Créer une entreprise de test
        self.entreprise = EntrepriseDonneuseOrdre.objects.create(
            nom='Entreprise Test',
            description='Description test'
        )
        
        # Créer un centre d'appels de test
        self.centre = CentreAppels.objects.create(
            nom='Centre Test',
            is_external=True,
            entreprise=self.entreprise
        )
        
        # Créer un agent de test
        User = get_user_model()
        user = User.objects.create_user(username='agent_test', password='test123')
        self.agent = Agent.objects.create(
            user=user,
            disponible=True,
            centre_appel=self.centre,
            date_embauche='2025-01-01'
        )
        
        # Créer quelques formations de test avec des descriptions ciblées
        formation_data = [
            {
                'titre': 'Formation Performance',
                'description': 'Améliorer la productivité et efficacité',
                'duree': 4,
                'date': '2025-06-15'
            },
            {
                'titre': 'Formation Qualité',
                'description': 'Excellence et amélioration continue',
                'duree': 4,
                'date': '2025-06-15'
            },
            {
                'titre': 'Formation Relation Client',
                'description': 'Satisfaction client et relation clientèle',
                'duree': 4,
                'date': '2025-06-15'
            },
            {
                'titre': 'Formation Similaire',
                'description': 'Améliorer la productivité des agents',  # Similaire à Formation Performance
                'duree': 4,
                'date': '2025-06-15'
            },
            {
                'titre': 'Formation Passée',
                'description': 'Formation expirée',
                'duree': 4,
                'date': '2025-01-01'  # Date passée
            }
        ]
        
        self.formations = []
        for data in formation_data:
            formation = Formation.objects.create(
                **data,
                centre=self.centre
            )
            self.formations.append(formation)
            
        # Créer des KPIs pour l'agent
        kpi_data = [
            {'type': 'performance', 'valeur': 0.6},  # Performance faible
            {'type': 'qualite', 'valeur': 0.8},      # Qualité bonne
            {'type': 'satisfaction', 'valeur': 0.7},  # Satisfaction moyenne
            {'type': 'formation', 'valeur': 0.9}      # Formation bonne
        ]
        
        for data in kpi_data:
            KPI.objects.create(
                agent=self.agent,
                nom=f'KPI {data["type"]}',
                **data,
                unite='%'
            )
            
        # Créer une participation passée à une formation similaire
        formation_similaire = self.formations[3]  # Formation Similaire
        Participation.objects.create(
            formation=formation_similaire,
            agent=self.agent.user,  # Utiliser le User associé à l'Agent
            date_inscription=timezone.now() - timedelta(days=30),
            statut='validee',
            satisfaction=0.8  # Bonne satisfaction
        )

    def test_get_recommendations(self):
        """Test les recommandations de formation pour un agent avec explications"""
        # Test avec explications activées
        recommender = TrainingRecommender()
        recommendations = recommender.get_recommendations(self.agent.id, avec_explications=True)

        # Vérifier que nous avons le bon nombre de recommandations
        formations_a_venir = Formation.objects.filter(
            date__gte=timezone.now().date()
        ).count()
        self.assertEqual(len(recommendations), min(formations_a_venir, 5))

        # Vérifier que chaque recommandation a les champs requis
        for rec in recommendations:
            self.assertIn('formation_id', rec)
            self.assertIn('score', rec)
            self.assertIn('recommendation_id', rec)
            self.assertIn('satisfaction_moyenne', rec)
            
            # Vérifier la présence et le format des explications
            self.assertIn('explications', rec)
            for explication in rec['explications']:
                self.assertIn('raison', explication)
                self.assertIn('impact', explication)
                self.assertIn('details', explication)
            self.assertTrue(0.5 <= rec['score'] <= 1.0)
            # Vérifier que la recommandation est sauvegardée
            recommandation = RecommandationFormation.objects.get(id=rec['recommendation_id'])
            self.assertEqual(recommandation.agent, self.agent)
            
            # Vérifier que la formation n'est pas expirée
            formation = Formation.objects.get(id=rec['formation_id'])
            self.assertGreaterEqual(formation.date, timezone.now().date())
        
        # Vérifier que les recommandations sont triées par score décroissant
        scores = [rec['score'] for rec in recommendations]
        self.assertEqual(scores, sorted(scores, reverse=True))
        
        # Vérifier que la formation Performance est recommandée en premier
        # car l'agent a un KPI performance faible
        first_rec = recommendations[0]
        first_formation = Formation.objects.get(id=first_rec['formation_id'])
        self.assertEqual(first_formation.titre, 'Formation Performance')
        
        # Vérifier que la formation similaire a un score plus bas
        # à cause de la similarité avec une formation déjà suivie
        for rec in recommendations:
            formation = Formation.objects.get(id=rec['formation_id'])
            if formation.titre == 'Formation Similaire':
                similar_score = rec['score']
                self.assertLess(
                    similar_score,
                    recommendations[0]['score'],
                    "La formation similaire devrait avoir un score plus bas"
                )
        
        # Vérifier que les explications sont cohérentes pour la formation performance
        first_rec = recommendations[0]
        first_explications = first_rec['explications']
        self.assertTrue(
            any(exp['raison'] == 'KPI performance faible' for exp in first_explications),
            "La formation performance devrait avoir une explication liée au KPI performance faible"
        )
        
        # Vérifier que la formation similaire a une pénalisation
        for rec in recommendations:
            formation = Formation.objects.get(id=rec['formation_id'])
            if formation.titre == 'Formation Similaire':
                explications = rec['explications']
                self.assertTrue(
                    any(exp['raison'] == 'Formation similaire récente' for exp in explications),
                    "La formation similaire devrait avoir une pénalisation de similarité"
                )
        
        # Vérifier que les anciennes recommandations sont supprimées
        result2 = recommender.get_recommendations(self.agent.id)
        self.assertEqual(
            RecommandationFormation.objects.count(),
            len(result2)
        )
        # Vérifier que les anciennes recommandations n'existent plus
        for rec in recommendations:
            self.assertFalse(
                RecommandationFormation.objects.filter(id=rec['recommendation_id']).exists()
            )
