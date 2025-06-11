from django.test import TestCase
from ai_tools.sentiment_analysis import SentimentAnalyzer
from ai_tools.models import AnalyseSentiment

class TestSentimentAnalyzer(TestCase):
    def setUp(self):
        self.analyzer = SentimentAnalyzer()

    def test_analyze_positive_sentiment(self):
        """Test l'analyse d'un feedback positif"""
        feedback = "Excellent service, très satisfait de la qualité du support!"
        result = self.analyzer.analyze_sentiment(feedback)
        
        self.assertGreater(result['score'], 0.6)
        self.assertEqual(result['sentiment'], 'positif')
        self.assertGreater(result['confidence'], 0.5)
        
        # Vérifier que l'analyse a été sauvegardée
        analyse = AnalyseSentiment.objects.last()
        self.assertEqual(analyse.texte_feedback, feedback)
        self.assertEqual(analyse.sentiment, 'positif')
        self.assertEqual(analyse.score_sentiment, result['score'])
        self.assertEqual(analyse.confiance, result['confidence'])

    def test_analyze_negative_sentiment(self):
        """Test l'analyse d'un feedback négatif"""
        feedback = "Service médiocre, très déçu de la réponse!"
        result = self.analyzer.analyze_sentiment(feedback)
        
        self.assertLess(result['score'], 0.4)
        self.assertEqual(result['sentiment'], 'négatif')
        self.assertGreater(result['confidence'], 0.5)
        
        # Vérifier que l'analyse a été sauvegardée
        analyse = AnalyseSentiment.objects.last()
        self.assertEqual(analyse.texte_feedback, feedback)
        self.assertEqual(analyse.sentiment, 'négatif')
        self.assertEqual(analyse.score_sentiment, result['score'])
        self.assertEqual(analyse.confiance, result['confidence'])

    def test_analyze_neutral_sentiment(self):
        """Test l'analyse d'un feedback neutre"""
        feedback = "Le service était correct."
        result = self.analyzer.analyze_sentiment(feedback)
        
        self.assertGreaterEqual(result['score'], 0.4)
        self.assertLessEqual(result['score'], 0.6)
        self.assertEqual(result['sentiment'], 'neutre')
        self.assertGreater(result['confidence'], 0.5)
