from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'ai_tools'

# Configuration du routeur DRF
router = DefaultRouter()
router.register(r'analyse-sentiment', views.AnalyseSentimentViewSet)
router.register(r'prediction-performance', views.PredictionPerformanceViewSet)
router.register(r'recommandation-formation', views.RecommandationFormationViewSet)
router.register(r'optimisation-planning', views.OptimisationPlanningViewSet)

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Vue du tableau de bord
    path('', views.DashboardAIView.as_view(), name='dashboard'),
    
    # Vues pour les agents
    path('recommendations/', views.RecommandationFormationListView.as_view(), name='recommendations'),
    path('performance-prediction/', views.PredictionPerformanceListView.as_view(), name='performance_prediction'),
    
    # Vues pour les centres d'appel
    path('team-performance/', views.TeamPerformanceView.as_view(), name='team_performance'),
    path('schedule-optimization/', views.ScheduleOptimizationView.as_view(), name='schedule_optimization'),
    path('sentiment-analysis/', views.SentimentAnalysisView.as_view(), name='sentiment_analysis'),
    
    # Vues pour les administrateurs
    path('global-analytics/', views.GlobalAnalyticsView.as_view(), name='global_analytics'),
    path('predictive-alerts/', views.PredictiveAlertsView.as_view(), name='predictive_alerts'),
    path('training-analytics/', views.TrainingAnalyticsView.as_view(), name='training_analytics'),
]
