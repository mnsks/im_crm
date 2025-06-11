from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from agents.models import Agent
from missions.models import Mission
from ai_tools.schedule_optimizer import ScheduleOptimizer
from ai_tools.models import OptimisationPlanning

class TestScheduleOptimizer(TestCase):
    def setUp(self):
        self.optimizer = ScheduleOptimizer()
        
        # Créer des agents de test
        User = get_user_model()
        self.agents = []
        for i in range(3):
            user = User.objects.create_user(username=f'agent_{i}', password='test123')
            agent = Agent.objects.create(user=user, disponible=True)
            self.agents.append(agent)
        
        # Créer des missions de test
        self.missions = []
        now = timezone.now()
        for i in range(5):
            mission = Mission.objects.create(
                titre=f'Mission {i}',
                description=f'Description {i}',
                date_debut=now + timedelta(days=i),
                date_fin=now + timedelta(days=i+1),
                statut='En attente'
            )
            self.missions.append(mission)

    def test_optimize_schedule(self):
        """Test l'optimisation du planning"""
        debut = timezone.now()
        fin = debut + timedelta(days=7)
        
        result = self.optimizer.optimize_schedule(debut, fin)
        
        # Vérifier le format du résultat
        self.assertIn('score', result)
        self.assertIn('nb_agents', result)
        self.assertIn('nb_missions', result)
        self.assertIn('details', result)
        self.assertIn('affectations', result['details'])
        
        # Vérifier les valeurs
        self.assertEqual(result['nb_agents'], len(self.agents))
        self.assertEqual(result['nb_missions'], len(self.missions))
        self.assertGreater(result['score'], 0)
        
        # Vérifier que l'optimisation a été sauvegardée
        optim = OptimisationPlanning.objects.last()
        self.assertEqual(optim.score_optimisation, result['score'])
        self.assertEqual(optim.nombre_agents, result['nb_agents'])
        self.assertEqual(optim.nombre_missions, result['nb_missions'])
        self.assertEqual(optim.details, result['details'])
        
        # Vérifier les affectations
        for affectation in result['details']['affectations']:
            self.assertIn('agent_id', affectation)
            self.assertIn('missions', affectation)
            self.assertIn(affectation['agent_id'], [a.id for a in self.agents])
            for mission_id in affectation['missions']:
                self.assertIn(mission_id, [m.id for m in self.missions])
