from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import (
    AnalyseSentiment,
    PredictionPerformance,
    RecommandationFormation,
    OptimisationPlanning
)
from .predictive_analytics import PredictiveAnalytics
from .training_recommender import TrainingRecommender
from .schedule_optimizer import ScheduleOptimizer
from agents.models import Agent

@shared_task
def analyser_sentiments_periodique():
    """Analyse les sentiments des interactions récentes"""
    from interactions.models import Interaction
    
    # Récupérer les interactions des dernières 24h sans analyse
    hier = timezone.now() - timedelta(days=1)
    interactions = Interaction.objects.filter(
        date_creation__gte=hier,
        analyse_sentiment__isnull=True
    )
    
    for interaction in interactions:
        # TODO: Implémenter l'analyse de sentiment
        AnalyseSentiment.objects.create(
            interaction=interaction,
            polarite=0.0,  # À remplacer par l'analyse réelle
            subjectivite=0.0,  # À remplacer par l'analyse réelle
            resultat="NEUTRE"
        )

@shared_task
def predire_performances_agents():
    """Prédit les performances futures des agents"""
    analyzer = PredictiveAnalytics()
    agents = Agent.objects.filter(disponible=True)
    
    for agent in agents:
        prediction = analyzer.predict_performance(agent.id)
        if prediction:
            PredictionPerformance.objects.create(
                agent=agent,
                kpi_predit=prediction['kpi'],
                confiance=prediction['confiance'],
                alerte=prediction['alerte']
            )

@shared_task
def mettre_a_jour_recommandations():
    """Met à jour les recommandations de formation pour tous les agents"""
    recommender = TrainingRecommender()
    agents = Agent.objects.filter(disponible=True)
    
    for agent in agents:
        recommandations = recommender.get_recommendations(agent.id)
        for rec in recommandations:
            RecommandationFormation.objects.create(
                agent=agent,
                formation_id=rec['formation_id'],
                score=rec['score']
            )

@shared_task
def optimiser_planning_hebdomadaire():
    """Optimise le planning pour la semaine à venir"""
    optimizer = ScheduleOptimizer()
    debut = timezone.now()
    fin = debut + timedelta(days=7)
    
    resultat = optimizer.optimize_schedule(debut, fin)
    if resultat:
        OptimisationPlanning.objects.create(
            score_optimisation=resultat['score'],
            nombre_agents=resultat['nb_agents'],
            nombre_missions=resultat['nb_missions'],
            details=resultat['details']
        )
