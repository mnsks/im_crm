from django.db.models import Avg, Count, F, Q, Case, When, FloatField
from django.utils import timezone
from formations.models import Formation, Participation
from agents.models import Agent
from kpis.models import KPI
import logging

logger = logging.getLogger(__name__)

class TrainingAnalytics:
    """Classe pour l'analyse des données de formation"""

    def get_global_metrics(self):
        """Récupère les métriques globales sur les formations"""
        now = timezone.now()
        six_months_ago = now - timezone.timedelta(days=180)

        inscriptions = Participation.objects.filter(
            date_inscription__gte=six_months_ago
        )

        total_agents = Agent.objects.count()
        agents_inscrits = Agent.objects.filter(user__participations__date_inscription__gte=six_months_ago).distinct().count()

        metrics = {
            'taux_participation': (agents_inscrits / total_agents * 100) if total_agents > 0 else 0,
            'score_moyen': inscriptions.filter(statut='validee').aggregate(Avg('score'))['score__avg'] or 0,
            'satisfaction_moyenne': inscriptions.aggregate(Avg('satisfaction'))['satisfaction__avg'] or 0,
        }

        # Calculer l'impact sur la performance
        agents = Agent.objects.filter(user__participations__in=inscriptions).distinct()
        
        kpis_avant = KPI.objects.filter(
            agent__in=agents,
            date__lt=F('agent__user__participations__date_inscription'),
            type='performance'
        ).values('agent').annotate(avg_before=Avg('valeur'))

        kpis_apres = KPI.objects.filter(
            agent__in=agents,
            date__gt=F('agent__user__participations__date_inscription'),
            type='performance'
        ).values('agent').annotate(avg_after=Avg('valeur'))

        # Calculer la différence moyenne de performance
        total_diff = 0
        count_diff = 0
        
        for kpi_avant in kpis_avant:
            agent_id = kpi_avant['agent']
            kpi_apres = next((k for k in kpis_apres if k['agent'] == agent_id), None)
            
            if kpi_apres:
                diff = kpi_apres['avg_after'] - kpi_avant['avg_before']
                total_diff += diff
                count_diff += 1

        metrics['impact_performance'] = (total_diff / count_diff * 100) if count_diff > 0 else 0

        return metrics

    def get_top_formations(self, limit=5):
        """Récupère les formations les plus efficaces"""
        formations = Formation.objects.annotate(
            score_moyen=Avg('participations__score'),
            satisfaction_moyenne=Avg('participations__satisfaction'),
            nombre_participants=Count('participations')
        ).filter(
            date__gte=timezone.now().date(),
            nombre_participants__gt=0
        )

        top_formations = []
        for formation in formations:
            # Calculer l'impact sur la performance
            impact = self._calculate_formation_impact(formation)
            
            top_formations.append({
                'titre': formation.titre,
                'score': formation.score_moyen or 0,
                'satisfaction': formation.satisfaction_moyenne or 0,
                'impact': impact
            })

        # Trier par impact et score
        top_formations.sort(key=lambda x: (x['impact'], x['score']), reverse=True)
        return top_formations[:limit]

    def get_formation_types_analysis(self):
        """Analyse les performances par type de formation"""
        types_formation = Formation.objects.values('type').annotate(
            nombre=Count('id'),
            participation=Avg(
                Case(
                    When(participations__statut='validee', then=1),
                    default=0,
                    output_field=FloatField(),
                )
            ) * 100,
            score=Avg('participations__score'),
            satisfaction=Avg('participations__satisfaction')
        ).filter(type__isnull=False)

        for type_f in types_formation:
            formations = Formation.objects.filter(type=type_f['type'])
            type_f['impact'] = sum(self._calculate_formation_impact(f) for f in formations) / formations.count()

        return types_formation

    def get_recommendations(self):
        """Génère des recommandations d'amélioration"""
        metrics = self.get_global_metrics()
        types_analysis = self.get_formation_types_analysis()

        recommendations = []

        # Analyser le taux de participation
        if metrics['taux_participation'] < 50:
            recommendations.append({
                'titre': 'Améliorer la participation',
                'description': 'Le taux de participation est faible. Envisager des incitations ou une meilleure communication.'
            })

        # Analyser la satisfaction
        if metrics['satisfaction_moyenne'] < 3.5:
            recommendations.append({
                'titre': 'Améliorer la satisfaction',
                'description': 'La satisfaction moyenne est basse. Revoir le contenu et la qualité des formations.'
            })

        # Analyser l'impact sur la performance
        if metrics['impact_performance'] < 5:
            recommendations.append({
                'titre': 'Renforcer l\'impact',
                'description': 'L\'impact sur la performance est limité. Adapter le contenu aux besoins opérationnels.'
            })

        # Analyser les types de formation
        low_performing_types = [t for t in types_analysis if t['score'] < 3.0]
        if low_performing_types:
            recommendations.append({
                'titre': 'Types de formation à améliorer',
                'description': f"Les types suivants ont des scores faibles : {', '.join(t['type'] for t in low_performing_types)}"
            })

        return recommendations

    def _calculate_formation_impact(self, formation):
        """Calcule l'impact d'une formation sur la performance des agents"""
        participations = formation.participations.filter(statut='validee')
        
        total_impact = 0
        count_impact = 0
        
        for participation in participations:
            agent = Agent.objects.get(user=participation.agent)
            kpis_avant = KPI.objects.filter(
                agent=agent,
                date__lt=participation.date_inscription,
                type='performance'
            ).order_by('-date')[:3]

            kpis_apres = KPI.objects.filter(
                agent=agent,
                date__gt=participation.date_inscription,
                type='performance'
            ).order_by('date')[:3]

            if kpis_avant.exists() and kpis_apres.exists():
                avg_avant = sum(k.valeur for k in kpis_avant) / len(kpis_avant)
                avg_apres = sum(k.valeur for k in kpis_apres) / len(kpis_apres)
                
                if avg_avant > 0:
                    impact = ((avg_apres - avg_avant) / avg_avant * 100)
                    total_impact += impact
                    count_impact += 1

        return total_impact / count_impact if count_impact > 0 else 0
