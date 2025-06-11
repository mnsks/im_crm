from django.db import models
from django.db.models import Avg
from django.utils import timezone
import logging
from agents.models import Agent
from formations.models import Formation
from ai_tools.models import RecommandationFormation
from kpis.models import KPI
# import tensorflow as tf - temporairement désactivé
import numpy as np

logger = logging.getLogger(__name__)

class RecommandationExplication:
    """Classe pour stocker les explications des recommandations"""
    def __init__(self, formation_id, score, raisons):
        self.formation_id = formation_id
        self.score = score
        self.raisons = raisons  # Liste de raisons avec leurs impacts

class TrainingRecommender:
    def __init__(self):
        self.model = None  # Temporairement désactivé en attendant TensorFlow

    def get_recommendations(self, agent_id, limit=5, avec_explications=False):
        """Génère des recommandations de formation pour un agent
        
        Args:
            agent_id: ID de l'agent
            limit: Nombre maximum de recommandations à retourner
            avec_explications: Si True, inclut les explications détaillées
        
        Returns:
            Liste de recommandations, chacune contenant:
            - formation_id: ID de la formation
            - score: Score de recommandation (0.5 à 1.0)
            - recommendation_id: ID de la recommandation créée
            - satisfaction_moyenne: Note moyenne de satisfaction
            - explications: (optionnel) Détails du calcul du score
        """
        logger.info(f"Génération de recommandations pour l'agent {agent_id}")
        
        agent = Agent.objects.get(id=agent_id)
        kpis = {'performance': 0.0, 'qualite': 0.0, 'satisfaction': 0.0, 'formation': 0.0}
        
        # Récupération des KPIs moyens récents
        for kpi_type in kpis.keys():
            type_kpis = agent.kpis.filter(type=kpi_type).order_by('-date')[:5]
            if type_kpis.exists():
                kpis[kpi_type] = sum(k.valeur for k in type_kpis) / len(type_kpis)
                logger.debug(f"KPI {kpi_type}: {kpis[kpi_type]:.2f}")
        
        # Supprimer les anciennes recommandations non appliquées
        RecommandationFormation.objects.filter(agent=agent, appliquee=False).delete()
        logger.info("Anciennes recommandations supprimées")
        
        # Récupérer les formations à venir du centre
        formations = Formation.objects.filter(
            centre=agent.centre_appel,
            date__gte=timezone.now().date()
        ).select_related('centre')
        logger.info(f"Nombre de formations disponibles: {formations.count()}")
        
        recommendations = []
        for formation in formations:
            score, explications = self._calculate_formation_score(formation, kpis, agent)
            rec = RecommandationFormation.objects.create(
                agent=agent,
                formation=formation,
                score=score,
                appliquee=False
            )
            
            recommendation = {
                'formation_id': formation.id,
                'score': score,
                'recommendation_id': rec.id,
                'satisfaction_moyenne': formation.get_satisfaction_moyenne()
            }
            
            if avec_explications:
                recommendation['explications'] = explications
            
            recommendations.append(recommendation)
            logger.debug(f"Formation {formation.titre}: score {score:.2f}")
        
        # Trier par score et limiter le nombre de résultats
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:limit]
    
    def _calculate_formation_score(self, formation, kpis, agent):
        """Calcule un score pour une formation basé sur les KPIs de l'agent et l'historique
        
        Returns:
            tuple: (score final, liste d'explications)
        """
        description = formation.description.lower()
        
        explications = []
        
        # Vérifier si c'est une formation performance
        is_performance = any(word in description for word in ['performance', 'productivité', 'efficacité'])
        
        # Si le KPI performance est faible et c'est une formation performance,
        # donner un score très élevé
        if is_performance and kpis['performance'] < 0.65:
            base_score = 0.9  # Score de base très élevé
            explications.append({
                'raison': 'KPI performance faible',
                'impact': '+0.9',
                'details': f"KPI performance: {kpis['performance']:.2f}"
            })
        else:
            # Pour les autres formations, calculer le score en fonction des KPIs
            base_score = 0.0
            if any(word in description for word in ['qualité', 'excellence', 'amélioration']):
                if kpis['qualite'] < 0.7:
                    score_qualite = 0.7 * (1 - kpis['qualite'])
                    base_score = max(base_score, score_qualite)
                    explications.append({
                        'raison': 'KPI qualité faible',
                        'impact': f'+{score_qualite:.2f}',
                        'details': f"KPI qualité: {kpis['qualite']:.2f}"
                    })
            
            if any(word in description for word in ['client', 'satisfaction', 'relation']):
                if kpis['satisfaction'] < 0.7:
                    score_satisfaction = 0.7 * (1 - kpis['satisfaction'])
                    base_score = max(base_score, score_satisfaction)
                    explications.append({
                        'raison': 'KPI satisfaction faible',
                        'impact': f'+{score_satisfaction:.2f}',
                        'details': f"KPI satisfaction: {kpis['satisfaction']:.2f}"
                    })
            
            # Score de base minimum
            if base_score < 0.5:
                base_score = 0.5
                explications.append({
                    'raison': 'Score minimum appliqué',
                    'impact': '0.5',
                    'details': 'Score de base minimum garanti'
                })
        
        # Vérifier l'historique des formations
        formations_suivies = agent.user.participations.filter(
            formation__centre=formation.centre,
            statut='validee'
        ).select_related('formation')
        
        # Pénaliser les formations similaires
        for participation in formations_suivies:
            formation_suivie = participation.formation
            mots_formation = set(formation.description.lower().split())
            mots_suivie = set(formation_suivie.description.lower().split())
            similarite = len(mots_formation.intersection(mots_suivie)) / len(mots_formation.union(mots_suivie))
            
            if similarite > 0.3:
                jours_depuis_formation = (timezone.now().date() - participation.date_inscription.date()).days
                if jours_depuis_formation < 180:  # 6 mois
                    # Pénalisation plus forte pour les formations similaires
                    penalite = similarite
                    score_avant = base_score
                    base_score *= (1 - penalite)
                    explications.append({
                        'raison': 'Formation similaire récente',
                        'impact': f'-{(score_avant - base_score):.2f}',
                        'details': f"Similarité: {similarite:.2f}, {jours_depuis_formation} jours"
                    })
        
        # Ajouter un bonus pour les formations bien notées
        satisfaction_moyenne = formation.get_satisfaction_moyenne()
        if satisfaction_moyenne:
            bonus = 0.1 * satisfaction_moyenne
            base_score += bonus
            explications.append({
                'raison': 'Bonus satisfaction',
                'impact': f'+{bonus:.2f}',
                'details': f"Satisfaction moyenne: {satisfaction_moyenne:.2f}"
            })
        
        # Garantir que le score reste entre 0.5 et 1.0
        score_final = max(0.5, min(1.0, base_score))
        
        if score_final != base_score:
            explications.append({
                'raison': 'Normalisation',
                'impact': f'={score_final:.2f}',
                'details': 'Score ajusté dans l\'intervalle [0.5, 1.0]'
            })
        
        return score_final, explications

    def build_model(self):
        """Construit le modèle de recommandation"""
        # Temporairement désactivé en attendant TensorFlow
        pass
        
    def prepare_training_data(self, agent_id):
        """Prépare les données pour l'entraînement"""
        agent = Agent.objects.get(id=agent_id)
        formations = Formation.objects.all()
        
        # TODO: Implémenter la préparation des données avec les KPIs de l'agent
        # et les caractéristiques des formations
        pass
        
    def train_model(self, X, y):
        """Entraîne le modèle de recommandation"""
        # Temporairement désactivé en attendant TensorFlow
        pass
        
    def update_recommendations(self, agent_id):
        """Met à jour les recommandations basées sur les nouvelles données"""
        return self.get_recommendations(agent_id)
