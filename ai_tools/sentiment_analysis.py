from django.db import models
from .models import AnalyseSentiment
from textblob import TextBlob
import numpy as np

class SentimentAnalyzer:
    def __init__(self):
        self.model = None  # Pour le moment, on utilise TextBlob

    def analyze_sentiment(self, feedback_text):
        """Analyse le sentiment d'un feedback client"""
        # Version simplifiée avec TextBlob
        analysis = TextBlob(feedback_text)
        
        # Ajuster la polarité en fonction des mots clés négatifs
        negative_words = ['médiocre', 'déçu', 'mauvais', 'insatisfait', 'nul']
        polarity = analysis.sentiment.polarity
        
        # Si des mots négatifs sont présents, réduire la polarité
        if any(word in feedback_text.lower() for word in negative_words):
            polarity = min(-0.3, polarity)
        
        # Normaliser le score entre 0 et 1
        sentiment_score = (polarity + 1) / 2
        
        # Déterminer le sentiment (positif > 0.6, négatif < 0.4)
        sentiment = 'positif' if sentiment_score > 0.6 else 'négatif' if sentiment_score < 0.4 else 'neutre'
        
        # Sauvegarder l'analyse
        analyse = AnalyseSentiment.objects.create(
            texte_feedback=feedback_text,
            score_sentiment=sentiment_score,
            sentiment=sentiment,
            confiance=np.random.uniform(0.7, 0.9)  # Pour le moment, confiance aléatoire
        )
        
        return {
            'score': sentiment_score,
            'sentiment': sentiment,
            'confidence': analyse.confiance
        }
