from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    AnalyseSentiment,
    PredictionPerformance,
    RecommandationFormation,
    OptimisationPlanning
)
from .serializers import (
    AnalyseSentimentSerializer,
    PredictionPerformanceSerializer,
    RecommandationFormationSerializer,
    OptimisationPlanningSerializer
)
from .predictive_analytics import PredictiveAnalytics
from .training_analytics import TrainingAnalytics
from .training_recommender import TrainingRecommender
from .schedule_optimizer import ScheduleOptimizer

# Vues API
class AnalyseSentimentViewSet(viewsets.ModelViewSet):
    queryset = AnalyseSentiment.objects.all()
    serializer_class = AnalyseSentimentSerializer

    @action(detail=False, methods=['post'])
    def analyser_texte(self, request):
        texte = request.data.get('texte')
        if not texte:
            return Response({'error': 'Texte requis'}, status=status.HTTP_400_BAD_REQUEST)
        # TODO: Implémenter l'analyse de sentiment
        return Response({'message': 'Analyse en cours'})

class PredictionPerformanceViewSet(viewsets.ModelViewSet):
    queryset = PredictionPerformance.objects.all()
    serializer_class = PredictionPerformanceSerializer

    @action(detail=False, methods=['post'])
    def predire_performance(self, request):
        agent_id = request.data.get('agent_id')
        if not agent_id:
            return Response({'error': 'ID agent requis'}, status=status.HTTP_400_BAD_REQUEST)
        
        analyzer = PredictiveAnalytics()
        prediction = analyzer.predict_performance(agent_id)
        return Response(prediction)

class RecommandationFormationViewSet(viewsets.ModelViewSet):
    queryset = RecommandationFormation.objects.all()
    serializer_class = RecommandationFormationSerializer

    @action(detail=False, methods=['post'])
    def recommander_formations(self, request):
        agent_id = request.data.get('agent_id')
        if not agent_id:
            return Response({'error': 'ID agent requis'}, status=status.HTTP_400_BAD_REQUEST)
        
        recommender = TrainingRecommender()
        recommendations = recommender.get_recommendations(agent_id)
        return Response(recommendations)

class OptimisationPlanningViewSet(viewsets.ModelViewSet):
    queryset = OptimisationPlanning.objects.all()
    serializer_class = OptimisationPlanningSerializer

    @action(detail=False, methods=['post'])
    def optimiser_planning(self, request):
        date_debut = request.data.get('date_debut')
        date_fin = request.data.get('date_fin')
        if not date_debut or not date_fin:
            return Response({'error': 'Dates requises'}, status=status.HTTP_400_BAD_REQUEST)
        
        optimizer = ScheduleOptimizer()
        planning = optimizer.optimize_schedule(date_debut, date_fin)
        return Response(planning)

# Vues Template
@method_decorator(login_required, name='dispatch')
class DashboardAIView(LoginRequiredMixin, TemplateView):
    template_name = 'ai_tools/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['derniers_sentiments'] = AnalyseSentiment.objects.all()[:5]
        context['dernieres_predictions'] = PredictionPerformance.objects.all()[:5]
        context['dernieres_recommandations'] = RecommandationFormation.objects.all()[:5]
        context['dernieres_optimisations'] = OptimisationPlanning.objects.all()[:5]
        return context

@method_decorator(login_required, name='dispatch')
class AnalyseSentimentListView(ListView):
    model = AnalyseSentiment
    template_name = 'ai_tools/analyse_sentiment_list.html'
    context_object_name = 'analyses'
    paginate_by = 10

@method_decorator(login_required, name='dispatch')
class PredictionPerformanceListView(ListView):
    model = PredictionPerformance
    template_name = 'ai_tools/prediction_performance_list.html'
    context_object_name = 'predictions'
    paginate_by = 10

@method_decorator(login_required, name='dispatch')
class RecommandationFormationListView(ListView):
    model = RecommandationFormation
    template_name = 'ai_tools/recommandation_formation_list.html'
    context_object_name = 'recommandations'
    paginate_by = 10

@method_decorator(login_required, name='dispatch')
class OptimisationPlanningListView(ListView):
    model = OptimisationPlanning
    template_name = 'ai_tools/optimisation_planning_list.html'
    context_object_name = 'optimisations'
    paginate_by = 10

@method_decorator(login_required, name='dispatch')
class TeamPerformanceView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'ai_tools/team_performance.html'

    def test_func(self):
        return self.request.user.role == 'centre'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # TODO: Implémenter la logique d'analyse de performance d'équipe
        return context

@method_decorator(login_required, name='dispatch')
class ScheduleOptimizationView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'ai_tools/schedule_optimization.html'

    def test_func(self):
        return self.request.user.role == 'centre'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # TODO: Implémenter la logique d'optimisation des plannings
        return context

@method_decorator(login_required, name='dispatch')
class SentimentAnalysisView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'ai_tools/sentiment_analysis.html'

    def test_func(self):
        return self.request.user.role == 'centre'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # TODO: Implémenter la logique d'analyse des sentiments
        return context

@method_decorator(login_required, name='dispatch')
class GlobalAnalyticsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'ai_tools/global_analytics.html'

    def test_func(self):
        return self.request.user.role == 'admin'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # TODO: Implémenter la logique d'analytics global
        return context

@method_decorator(login_required, name='dispatch')
class PredictiveAlertsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'ai_tools/predictive_alerts.html'

    def test_func(self):
        return self.request.user.role == 'admin'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # TODO: Implémenter la logique des alertes prédictives
        return context

@method_decorator(login_required, name='dispatch')
class TrainingAnalyticsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'ai_tools/training_analytics.html'

    def test_func(self):
        return self.request.user.role == 'admin'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        analytics = TrainingAnalytics()

        # Récupérer les métriques globales
        metrics = analytics.get_global_metrics()
        context.update(metrics)

        # Récupérer les meilleures formations
        context['top_formations'] = analytics.get_top_formations()

        # Récupérer l'analyse par type de formation
        context['types_formation'] = analytics.get_formation_types_analysis()

        # Récupérer les recommandations
        context['recommandations'] = analytics.get_recommendations()

        return context
