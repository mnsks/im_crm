from django.test import TestCase
from django.contrib.auth import get_user_model
from agents.models import Agent
from ai_tools.predictive_analytics import PredictiveAnalytics
from ai_tools.models import PredictionPerformance

class TestPredictiveAnalytics(TestCase):
    def setUp(self):
        self.analytics = PredictiveAnalytics()
        
        # Créer un agent de test
        User = get_user_model()
        user = User.objects.create_user(username='agent_test', password='test123')
        self.agent = Agent.objects.create(user=user, disponible=True)

    def test_predict_performance(self):
        """Test la prédiction de performance d'un agent"""
        result = self.analytics.predict_performance(self.agent.id)
        
        # Vérifier le format et les valeurs de la prédiction
        self.assertIn('prediction', result)
        self.assertIn('confidence', result)
        self.assertIn('alert', result)
        
        # Vérifier les plages de valeurs
        self.assertGreaterEqual(result['prediction'], 0.6)
        self.assertLessEqual(result['prediction'], 0.9)
        self.assertGreaterEqual(result['confidence'], 0.7)
        self.assertLessEqual(result['confidence'], 0.9)
        self.assertIsInstance(result['alert'], bool)
        
        # Vérifier que la prédiction a été sauvegardée
        prediction = PredictionPerformance.objects.last()
        self.assertEqual(prediction.agent_id, self.agent.id)
        self.assertEqual(prediction.kpi_predit, result['prediction'])
        self.assertEqual(prediction.confiance, result['confidence'])
        self.assertEqual(prediction.alerte, result['alert'])
