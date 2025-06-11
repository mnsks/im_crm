from django.shortcuts import render
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Aggregate, Q, Count
from django.utils import timezone
from core.models import User
from missions.models import Mission
from formations.models import Formation

class AvgDurationField(Aggregate):
    function = 'AVG'
    name = 'avg_duration'

    def convert_value(self, value, expression, connection):
        if value is None:
            return 0
        if isinstance(value, timedelta):
            return value.total_seconds()
        return 0

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden, HttpResponseServerError
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import redirect, render
from django.utils import timezone
from django.db.models import Count, Avg, Sum
from django.db.models.functions import TruncDate
import json
import traceback
from missions.models import Mission
from saisie.models import SaisieResultat
from datetime import datetime, timedelta
from formations.models import Formation
from core.models import User

@login_required
def profile(request):
    """Vue pour afficher et modifier le profil utilisateur"""
    if request.method == 'POST':
        # Mise à jour des informations de profil
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        messages.success(request, 'Profil mis à jour avec succès')
    
    context = {
        'user': request.user
    }
    return render(request, 'core/profile.html', context)

@login_required
def change_password(request):
    """Vue pour changer le mot de passe"""
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        # Vérification de l'ancien mot de passe
        if not request.user.check_password(old_password):
            messages.error(request, 'Ancien mot de passe incorrect')
            return redirect('core:profile')
        
        # Vérification que les nouveaux mots de passe correspondent
        if new_password1 != new_password2:
            messages.error(request, 'Les nouveaux mots de passe ne correspondent pas')
            return redirect('core:profile')
        
        # Changement du mot de passe
        request.user.set_password(new_password1)
        request.user.save()
        messages.success(request, 'Mot de passe changé avec succès')
        
        # Mise à jour de la session pour éviter la déconnexion
        update_session_auth_hash(request, request.user)
        
        return redirect('core:profile')
    
    return redirect('core:profile')
from django.shortcuts import render
from django.db import models

from missions.models import Mission
from core.models import User
from feedback.models import Feedback
from kpis.models import KPI
from saisie.models import SaisieResultat
from formations.models import Formation
from rapports.models import Rapport


def access_denied(request):
    """Vue affichant une page d'accès refusé professionnelle."""
    return render(request, 'access_denied.html')

@login_required
def guide_utilisateur(request):
    """Affiche le guide utilisateur pour tous les rôles."""
    return render(request, 'guide_utilisateur.html')

@login_required
def dashboard(request):
    logger.info('\n' + '='*100)
    logger.info('ACCÈS AU DASHBOARD PRINCIPAL')
    logger.info('='*100)
    logger.info(f'Session ID: {request.session.session_key}')
    logger.info(f'Utilisateur connecté : {request.user.username} (ID: {request.user.id})')
    logger.info(f'Rôle utilisateur : {request.user.role}')
    logger.info(f'Parent entreprise : {request.user.parent_entreprise}')
    logger.info(f'Méthode HTTP : {request.method}')
    logger.info(f'URL complète : {request.build_absolute_uri()}')
    logger.info('='*100)

    try:
        if not request.user.is_authenticated:
            logger.info('ERREUR: Utilisateur non authentifié')
            return redirect('login')

        # Afficher les informations de l'utilisateur pour le débogage
        logger.info('\nInformations utilisateur :')
        logger.info(f'Username: {request.user.username}')
        logger.info(f'Rôle: {request.user.role}')
        logger.info(f'Rôles disponibles: {dict(User.ROLE_CHOICES)}')

        # Rediriger selon le rôle
        if request.user.role == 'admin':
            logger.info('Redirection vers admin_dashboard')
            return redirect('core:admin_dashboard')
        elif request.user.role in ['donneur_ordre', 'entreprise']:
            logger.info('Redirection vers donneur_ordre_dashboard')
            return redirect('core:donneur_ordre_dashboard')
        elif request.user.role == 'centre':  # Correction ici
            logger.info('Redirection vers centre_dashboard')
            return redirect('core:centre_dashboard')
        elif request.user.role == 'agent':
            logger.info('Redirection vers agent_dashboard')
            return redirect('core:agent_dashboard')
        else:
            logger.info(f'ERREUR: Rôle non reconnu : {request.user.role}')
            logger.info('Rôles valides:', dict(User.ROLE_CHOICES))
            return HttpResponseForbidden("Vous n'avez pas accès au tableau de bord.")
    except Exception as e:
        logger.info('ERREUR lors de la redirection:', str(e))
        logger.info('Traceback:', traceback.format_exc())
        return HttpResponseServerError('Une erreur est survenue lors de la redirection.')

import logging
logger = logging.getLogger(__name__)

@login_required
@user_passes_test(lambda u: u.role == 'admin', login_url='/')
def admin_dashboard(request):
    logger.info("=== TEST DEBUG ADMIN DASHBOARD ===")
    """Dashboard pour les administrateurs"""
    try:
        logger.info('\n' + '='*100)
        logger.info('Vérification de l\'utilisateur admin :')
        logger.info(f'Username: {request.user.username}')
        logger.info(f'Role: {request.user.role}')
        logger.info(f'Is authenticated: {request.user.is_authenticated}')
        logger.info('='*100)
        logger.info('\n' + '='*100)
        logger.info('ACCÈS AU DASHBOARD ADMIN')
        logger.info('='*100)

        # Vérification complète de la base de données
        logger.info('\nAnalyse de la base de données :')
        
        # Liste tous les utilisateurs avec leurs rôles
        all_users = User.objects.all()
        logger.info('\nTous les utilisateurs :')
        for user in all_users:
            logger.info(f'- {user.username} (role: {user.role})')
        
        # Liste toutes les missions avec leurs statuts
        all_missions = Mission.objects.all()
        logger.info('\nToutes les missions :')
        for mission in all_missions:
            logger.info(f'- {mission.titre} (status: {mission.status})')
        
        # Comptage par type
        logger.info('\nComptage par type :')
        
        # Correction : utiliser les modèles dédiés pour les compteurs
        from .models import EntrepriseDonneuseOrdre, CentreAppels
        nb_entreprises = EntrepriseDonneuseOrdre.objects.count()
        nb_centres = CentreAppels.objects.count()
        nb_agents = User.objects.filter(role='agent', is_active=True).count()
        nb_missions = Mission.objects.filter(status='en_cours').count()
        logger.info(f'Entreprises (total): {nb_entreprises}')
        logger.info(f'Centres (total): {nb_centres}')
        logger.info(f'Agents (total): {nb_agents}')
        logger.info(f'Missions en cours (total): {nb_missions}')

        # Pour les stats détaillées, on garde la logique existante
        status_missions = {
            'en_cours': 0,
            'terminee': 0,
            'en_attente': 0,
            'annulee': 0
        }
        missions_stats = Mission.objects.values('status').annotate(count=Count('id'))
        for stat in missions_stats:
            status = stat['status']
            count = stat['count']
            if status in status_missions:
                status_missions[status] = count
        missions_en_cours = status_missions['en_cours']
        missions_terminees = status_missions['terminee']
        missions_en_attente = status_missions['en_attente']
        missions_annulees = status_missions['annulee']

        # Missions récentes (optionnel, à adapter si besoin)
        recent_missions = Mission.objects.order_by('-date_debut')[:5]

        # Formations data (à adapter selon logique projet)
        formations_data = [0, 0, 0, 0, 0, 0]

        # Préparer les données pour le template
        context = {
            'nb_entreprises': nb_entreprises,
            'nb_centres': nb_centres,
            'nb_agents': nb_agents,
            'nb_missions': nb_missions,
            'missions_en_cours': missions_en_cours,
            'missions_terminees': missions_terminees,
            'missions_en_attente': missions_en_attente,
            'missions_annulees': missions_annulees,
            'recent_missions': recent_missions,
            'formations_data': json.dumps(formations_data)
        }
        logger.info('\nDonnées envoyées au template :')
        logger.info('Statistiques générales :')
        logger.info(f'- Entreprises: {context["nb_entreprises"]}')
        logger.info(f'- Centres: {context["nb_centres"]}')
        logger.info(f'- Agents: {context["nb_agents"]}')
        logger.info(f'- Missions: {context["nb_missions"]}')
        logger.info(f'- En cours: {context["missions_en_cours"]}')
        logger.info(f'- Terminées: {context["missions_terminees"]}')
        logger.info(f'- En attente: {context["missions_en_attente"]}')
        logger.info(f'- Annulées: {context["missions_annulees"]}')
        logger.info(f'- Missions récentes: {context["recent_missions"]}')
        logger.info(f'- Formations data: {context["formations_data"]}')
        logger.info('\nContexte préparé avec succès')
        return render(request, 'dashboard/admin.html', context)

        
        logger.info('Statistiques de base :')
        logger.info(f'Entreprises: {nb_entreprises}')
        logger.info(f'Centres: {nb_centres}')
        logger.info(f'Agents: {nb_agents}')
        logger.info(f'Missions: {nb_missions}')
        
        # État des missions avec valeurs par défaut
        status_missions = {
            'en_cours': 0,
            'terminee': 0,
            'en_attente': 0,
            'annulee': 0
        }
        
        # Récupération des stats des missions
        missions_stats = Mission.objects.values('status').annotate(count=Count('id'))
        logger.info('\nStatistiques des missions par statut :')
        for stat in missions_stats:
            status = stat['status']
            count = stat['count']
            logger.info(f'- {status}: {count}')
            if status in status_missions:
                status_missions[status] = count
        
        # Assignation des variables pour le template
        missions_en_cours = status_missions['en_cours']
        missions_terminees = status_missions['terminee']
        missions_en_attente = status_missions['en_attente']
        missions_annulees = status_missions['annulee']

        logger.info('\nStatistiques des missions :')
        logger.info(f'En cours: {missions_en_cours}')
        logger.info(f'Terminées: {missions_terminees}')
        logger.info(f'En attente: {missions_en_attente}')
        logger.info(f'Annulées: {missions_annulees}')

        # Récupérer les missions récentes
        recent_missions = Mission.objects.order_by('-date_debut')[:5]
        logger.info('\nMissions récentes:', [m.titre for m in recent_missions])

        # Données des formations sur 6 mois
        today = timezone.now()
        six_months_ago = today - timedelta(days=180)
        
        logger.info('\nPériode des formations :')
        logger.info(f'De {six_months_ago.date()} à {today.date()}')
        
        # Formations par mois avec valeurs par défaut
        formations_data = [0] * 6
        month_names = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                      'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
        
        # Récupérer toutes les formations des 6 derniers mois
        formations = Formation.objects.filter(
            date_debut__gte=six_months_ago
        ).values('date_debut__month').annotate(
            count=Count('id')
        ).order_by('date_debut__month')
        
        logger.info('\nFormations trouvées par mois :')
        for f in formations:
            month = f['date_debut__month']
            count = f['count']
            month_idx = (month - today.month) % 12
            if month_idx < 6:
                formations_data[month_idx] = count
                logger.info(f'- {month_names[month-1]}: {count} formations')

        logger.info('\nDonnées des formations:', formations_data)
    
        # Préparer les données pour le template
        context = {
            'nb_entreprises': nb_entreprises,
            'nb_centres': nb_centres,
            'nb_agents': nb_agents,
            'nb_missions': nb_missions,
            'missions_en_cours': missions_en_cours,
            'missions_terminees': missions_terminees,
            'missions_en_attente': missions_en_attente,
            'missions_annulees': missions_annulees,
            'recent_missions': recent_missions,
            'formations_data': json.dumps(formations_data)
        }
        
        logger.info('\nDonnées envoyées au template :')
        logger.info('Statistiques générales :')
        logger.info(f'- Entreprises: {context["nb_entreprises"]}')
        logger.info(f'- Centres: {context["nb_centres"]}')
        logger.info(f'- Agents: {context["nb_agents"]}')
        logger.info(f'- Missions: {context["nb_missions"]}')
        
        logger.info('\nStatistiques des missions :')
        logger.info(f'- En cours: {context["missions_en_cours"]}')
        logger.info(f'- Terminées: {context["missions_terminees"]}')
        logger.info(f'- En attente: {context["missions_en_attente"]}')
        logger.info(f'- Annulées: {context["missions_annulees"]}')
        
        logger.info('\nMissions récentes :')
        for mission in context['recent_missions']:
            logger.info(f'- {mission.titre} ({mission.status})')
        
        logger.info('\nDonnées des formations :')
        logger.info(f'- {context["formations_data"]}')

        logger.info('\nContexte préparé avec succès')
        logger.info('Données des formations:', formations_data)
        return render(request, 'dashboard/admin.html', context)

    except Exception as e:
        logger.info('ERREUR dans admin_dashboard:', str(e))
        logger.info('Traceback:', traceback.format_exc())
        return render(request, 'dashboard/admin.html', {
            'nb_entreprises': 0,
            'nb_centres': 0,
            'nb_agents': 0,
            'nb_missions': 0,
            'missions_en_cours': 0,
            'missions_terminees': 0,
            'missions_en_attente': 0,
            'missions_annulees': 0,
            'recent_missions': [],
            'formations_data': json.dumps([0, 0, 0, 0, 0, 0])
        })

@login_required
@user_passes_test(lambda u: u.role == 'entreprise')
def entreprise_dashboard(request):
    """Dashboard pour les entreprises donneuses d'ordre"""
    from django.db.models import Count, Avg
    from django.utils import timezone
    import json
    import logging
    from django.contrib import messages
    from django.shortcuts import redirect

    entreprise = getattr(request.user, 'parent_entreprise', None)
    if not entreprise:
        logging.warning(f"Utilisateur sans parent_entreprise : {request.user.username} (ID: {request.user.id})")
        messages.error(request, "Votre profil entreprise est incomplet. Merci de contacter l'administrateur.")
        return redirect('dashboard')

    today = timezone.now()
    thirty_days_ago = today - timedelta(days=30)
    
    # Statistiques de base
    nb_missions = Mission.objects.filter(entreprise=entreprise).count()
    nb_centres = CentreAppels.objects.filter(missions__entreprise=entreprise).distinct().count()
    
    # Statistiques des appels sur les 30 derniers jours
    appels_stats = SaisieResultat.objects.filter(
        mission__entreprise=entreprise,
        date_appel__gte=thirty_days_ago
    ).values('date_appel__date').annotate(
        nb_appels=Count('id')
    ).order_by('date_appel__date')

    dates = []
    nb_appels = []
    for stat in appels_stats:
        dates.append(stat['date_appel__date'].strftime('%Y-%m-%d'))
        nb_appels.append(stat['nb_appels'])

    # Taux de succès par jour
    taux_succes_stats = SaisieResultat.objects.filter(
        mission__entreprise=entreprise,
        date_appel__gte=thirty_days_ago
    ).values('date_appel__date').annotate(
        total=Count('id'),
        succes=Count('id', filter=models.Q(status='succes'))
    ).order_by('date_appel__date')

    taux_succes_data = []
    for stat in taux_succes_stats:
        if stat['total'] > 0:
            taux = (stat['succes'] / stat['total']) * 100
            taux_succes_data.append(round(taux, 1))
        else:
            taux_succes_data.append(0)

    # Performance des centres d'appels
    centres_performance = CentreAppels.objects.filter(
        missions__entreprise=entreprise
    ).annotate(
        nb_appels=Count('missions__resultats_saisie', filter=models.Q(
            missions__resultats_saisie__date_appel__gte=thirty_days_ago
        )),
        nb_succes=Count('missions__resultats_saisie', filter=models.Q(
            missions__resultats_saisie__date_appel__gte=thirty_days_ago,
            missions__resultats_saisie__status='success'
        ))
    ).values('nom', 'nb_appels', 'nb_succes')

    for centre in centres_performance:
        if centre['nb_appels'] > 0:
            centre['taux_succes'] = round((centre['nb_succes'] / centre['nb_appels']) * 100, 1)
        else:
            centre['taux_succes'] = 0

    # Statistiques des feedbacks
    feedbacks_stats = {
        'nb_feedbacks': Feedback.objects.filter(
            mission__entreprise=entreprise,
            date_creation__gte=thirty_days_ago
        ).count(),
        'note_moyenne': Feedback.objects.filter(
            mission__entreprise=entreprise,
            date_creation__gte=thirty_days_ago
        ).aggregate(Avg('note'))['note__avg']
    }

    # Distribution des notes
    notes_distribution = Feedback.objects.filter(
        mission__entreprise=entreprise,
        date_creation__gte=thirty_days_ago
    ).values('note').annotate(count=Count('id'))

    notes_data = [0] * 5  # Pour les notes de 1 à 5
    for note in notes_distribution:
        if 1 <= note['note'] <= 5:
            notes_data[note['note']-1] = note['count']

    # Missions en cours et récentes
    missions_en_cours = Mission.objects.filter(
        entreprise=entreprise,
        status='en_cours'
    ).select_related('centre').order_by('-date_debut')[:5]

    recent_missions = Mission.objects.filter(
        entreprise=entreprise
    ).select_related('centre').order_by('-date_debut')[:5]

    return render(request, 'dashboard/entreprise.html', {
        'entreprise': entreprise,
        'nb_missions': nb_missions,
        'nb_centres': nb_centres,
        'dates': json.dumps(dates),
        'nb_appels': json.dumps(nb_appels),
        'taux_succes_data': json.dumps(taux_succes_data),
        'centres_performance': centres_performance,
        'nb_feedbacks': feedbacks_stats['nb_feedbacks'],
        'note_moyenne': round(feedbacks_stats['note_moyenne'], 1) if feedbacks_stats['note_moyenne'] else 0,
        'notes_distribution': json.dumps(notes_data),
        'missions_en_cours': missions_en_cours,
        'recent_missions': recent_missions,
    })

@login_required
@user_passes_test(lambda u: u.role == 'centre')
def centre_dashboard(request):
    """Dashboard pour les centres d'appels"""
    from django.db.models import Count, Avg
    from django.utils import timezone
    import json

    centre = request.user.parent_centre
    
    # Statistiques de base
    nb_agents = User.objects.filter(parent_centre=centre, role='agent').count()
    nb_missions_actives = Mission.objects.filter(centre=centre, status='en_cours').count()
    
    # Nombre de formations planifiées
    nb_formations = Formation.objects.filter(
        centre=centre,
        date__gte=timezone.now().date()
    ).count()
    
    # Statistiques des appels sur les 30 derniers jours
    today = timezone.now()
    thirty_days_ago = today - timedelta(days=30)
    appels_stats = SaisieResultat.objects.filter(
        mission__centre=centre,
        date_appel__gte=thirty_days_ago
    ).values('date_appel__date').annotate(
        nb_appels=Count('id'),
        duree_moyenne=AvgDurationField('duree_appel')
    ).order_by('date_appel__date')

    # Préparer les données pour le graphique
    dates = []
    nb_appels = []
    durees_moyennes = []
    for stat in appels_stats:
        dates.append(stat['date_appel__date'].strftime('%Y-%m-%d'))
        nb_appels.append(stat['nb_appels'])
        durees_moyennes.append(round(stat['duree_moyenne'], 1) if stat['duree_moyenne'] else 0)

    # Répartition des statuts d'appels
    status_stats = SaisieResultat.objects.filter(
        mission__centre=centre,
        date_appel__gte=thirty_days_ago
    ).values('status').annotate(count=Count('id'))

    status_data = {
        'succes': 0,
        'echec': 0,
        'rappel': 0,
        'indisponible': 0
    }
    for stat in status_stats:
        status_data[stat['status']] = stat['count']

    # Performance des agents
    agents_performance = User.objects.filter(
        parent_centre=centre,
        role='agent'
    ).annotate(
        nb_appels=Count('saisies_resultats', filter=models.Q(
            saisies_resultats__date_appel__gte=thirty_days_ago
        )),
        nb_succes=Count('saisies_resultats', filter=models.Q(
            saisies_resultats__date_appel__gte=thirty_days_ago,
            saisies_resultats__status='succes'
        ))
    ).values('username', 'nb_appels', 'nb_succes')

    for agent in agents_performance:
        if agent['nb_appels'] > 0:
            agent['taux_succes'] = round((agent['nb_succes'] / agent['nb_appels']) * 100, 1)
        else:
            agent['taux_succes'] = 0

    # Missions en cours
    current_missions = Mission.objects.filter(
        centre=centre,
        status='en_cours'
    ).order_by('-date_debut')[:5]

    # Calculer le nombre d'appels aujourd'hui
    nb_appels_jour = SaisieResultat.objects.filter(
        mission__centre=centre,
        date_appel__date=today.date()
    ).count()

    # Calculer les appels par type
    calls_incoming = SaisieResultat.objects.filter(
        mission__centre=centre,
        type_appel='entrant',
        date_appel__date=today.date()
    ).count()

    calls_outgoing = SaisieResultat.objects.filter(
        mission__centre=centre,
        type_appel='sortant',
        date_appel__date=today.date()
    ).count()

    calls_missed = SaisieResultat.objects.filter(
        mission__centre=centre,
        status='failure',
        date_appel__date=today.date()
    ).count()

    # Préparer les données pour les graphiques
    hourly_labels = [f'{h:02d}h' for h in range(24)]
    calls_data = [0] * 24

    # Agréger les appels par heure
    hourly_stats = SaisieResultat.objects.filter(
        mission__centre=centre,
        date_appel__date=today.date()
    ).extra({
        'hour': "EXTRACT(hour FROM date_appel)"
    }).values('hour').annotate(count=Count('id'))

    for stat in hourly_stats:
        hour = int(stat['hour'])
        if 0 <= hour < 24:  # Vérification de sécurité
            calls_data[hour] = stat['count']

    return render(request, 'dashboard/centre.html', {
        'centre': centre,
        'nb_agents': nb_agents,
        'nb_appels_jour': nb_appels_jour,
        'nb_missions_actives': nb_missions_actives,
        'hourly_labels': json.dumps(hourly_labels),
        'calls_data': json.dumps(calls_data),
        'calls_incoming': calls_incoming,
        'calls_outgoing': calls_outgoing,
        'calls_missed': calls_missed,
        'agents_performance': agents_performance,
        'current_missions': current_missions,
        'nb_formations': nb_formations,
    })

@login_required
@user_passes_test(lambda u: u.role == 'agent')
def agent_dashboard(request):
    """Dashboard pour les agents"""
    from django.db.models import Count, Avg
    from django.utils import timezone
    import json

    agent = request.user
    
    # Statistiques de base
    today = timezone.now()
    thirty_days_ago = today - timedelta(days=30)

    # Statistiques des appels
    appels_stats = SaisieResultat.objects.filter(
        mission__agents=agent,
        date_appel__gte=thirty_days_ago
    ).values('date_appel__date').annotate(
        nb_appels=Count('id'),
        duree_moyenne=Avg('duree_appel')
    ).order_by('date_appel__date')

    # Préparation des données pour les graphiques
    dates = []
    nb_appels = []
    durees_moyennes = []
    for stat in appels_stats:
        dates.append(stat['date_appel__date'].strftime('%Y-%m-%d'))
        nb_appels.append(stat['nb_appels'])
        durees_moyennes.append(round(stat['duree_moyenne'], 1) if stat['duree_moyenne'] else 0)

    # Statistiques globales
    all_appels = SaisieResultat.objects.filter(
        mission__agents=agent,
        date_appel__gte=thirty_days_ago
    )
    total_appels = all_appels.count()
    succes = all_appels.filter(status='succes').count()
    taux_succes = (succes / total_appels * 100) if total_appels > 0 else 0
    duree_moyenne = all_appels.aggregate(Avg('duree_appel'))['duree_appel__avg'] or 0
    duree_moyenne_minutes = duree_moyenne / 60 if duree_moyenne else 0

    # Distribution des statuts
    status_counts = all_appels.values('status').annotate(count=Count('id'))
    status_data = {}
    for status in status_counts:
        status_data[status['status']] = status['count']

    # Missions en cours
    current_missions = Mission.objects.filter(
        agents=agent,
        status='en_cours'
    ).order_by('-date_debut')[:5]

    # Formations à venir avec nombre de participants
    formations_a_venir = Formation.objects.filter(
        participations__agent=agent,
        participations__statut='validee',
        date__gt=today
    ).annotate(
        nb_participants=models.Count('participations', filter=models.Q(participations__statut='validee'))
    ).order_by('date')[:5]

    # Feedbacks récents
    recent_feedbacks = Feedback.objects.filter(
        mission__agents=agent
    ).select_related('agent', 'evaluateur', 'mission').order_by('-date_creation')[:5]

    # Nombre d'appels aujourd'hui
    appels_aujourdhui = SaisieResultat.objects.filter(
        mission__agents=agent,
        date_appel__date=today.date()
    ).count()

    # Nombre de formations complétées
    formations_completees = Formation.objects.filter(
        participations__agent=agent,
        participations__statut='terminee'
    ).count()

    return render(request, 'dashboard/agent.html', {
        'agent': agent,
        'dates': json.dumps(dates),
        'nb_appels': json.dumps(nb_appels),
        'durees_moyennes': json.dumps(durees_moyennes),
        'status_data': json.dumps(status_data),
        'taux_succes': round(taux_succes, 1),
        'duree_moyenne_minutes': round(duree_moyenne_minutes, 1),
        'current_missions': current_missions,
        'formations_a_venir': formations_a_venir,
        'recent_feedbacks': recent_feedbacks,
        'all_appels': all_appels,
        'appels_aujourdhui': appels_aujourdhui,
        'nb_formations_suivies': formations_completees,
        'centre': agent.parent_centre
    })

from django.http import Http404

from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from missions.forms import MissionForm
from rapports.forms import FeedbackForm # Ajout de l'import pour FeedbackForm
from .forms import AgentCreationForm, AgentUpdateForm # Ajout des formulaires Agent
from .models import User, CentreAppels # Ajout de CentreAppels


@login_required
def missions_list(request):
    from core.models import CentreAppels
    missions = Mission.objects.select_related('entreprise', 'centre').all()
    q = request.GET.get('q', '').strip()
    centre_id = request.GET.get('centre')
    if q:
        missions = missions.filter(
            models.Q(titre__icontains=q) |
            models.Q(objectifs__icontains=q) |
            models.Q(entreprise__nom__icontains=q)
        )
    if centre_id:
        missions = missions.filter(centre_id=centre_id)
    missions = missions.order_by('-date_debut')
    centres = CentreAppels.objects.all().order_by('nom')
    paginator = Paginator(missions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "missions/missions_list.html", {
        'missions': page_obj.object_list,
        'centres': centres,
        'paginator': paginator,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    })

def can_create_edit_mission(user):
    return user.is_authenticated and user.role in ['admin', 'entreprise_donneuse_ordre']

@user_passes_test(can_create_edit_mission)
@login_required
def mission_create(request):
    # La vérification du rôle est gérée par @user_passes_test
    # Si l'utilisateur n'a pas le bon rôle, il obtiendra une page 403 par défaut
    # ou sera redirigé vers la page de login s'il n'est pas connecté.
    # Pour un message personnalisé et redirection, il faudrait retirer le décorateur
    # et faire la vérification manuellement comme ci-dessous.

    # if not request.user.role in ['admin', 'entreprise_donneuse_ordre']:
    #     messages.error(request, "Vous n'avez pas les droits nécessaires pour créer une mission.")
    #     return redirect('missions:list') # ou une autre page appropriée

    if request.method == 'POST':
        form = MissionForm(request.POST)
        if form.is_valid():
            mission = form.save()
            messages.success(request, f"La mission '{mission.titre}' a été créée avec succès.")
            return redirect('missions:list')
    else:
        form = MissionForm()
    return render(request, 'missions/mission_form.html', {'form': form, 'action': 'Créer'})

@user_passes_test(can_create_edit_mission)
@login_required
def mission_update(request, mission_id):
    # La vérification du rôle est gérée par @user_passes_test
    # if not request.user.role in ['admin', 'entreprise_donneuse_ordre']:
    #     messages.error(request, "Vous n'avez pas les droits nécessaires pour modifier cette mission.")
    #     return redirect('missions:mission_detail', mission_id=mission_id)

    mission = get_object_or_404(Mission, pk=mission_id)
    if request.method == 'POST':
        form = MissionForm(request.POST, instance=mission)
        if form.is_valid():
            form.save()
            messages.success(request, f"La mission '{mission.titre}' a été modifiée avec succès.")
            return redirect('missions:mission_detail', mission_id=mission.id)
    else:
        form = MissionForm(instance=mission)
    return render(request, 'missions/mission_form.html', {'form': form, 'mission': mission, 'action': 'Modifier'})


@login_required
def feedback_update(request, feedback_id):
    feedback = get_object_or_404(Feedback, pk=feedback_id)
    mission_id = feedback.rapport.mission.id

    if not (request.user == feedback.auteur or request.user.role == 'admin'):
        messages.error(request, "Vous n'êtes pas autorisé à modifier ce feedback.")
        return redirect('mission_detail', mission_id=mission_id)

    if request.method == 'POST':
        form = FeedbackForm(request.POST, instance=feedback)
        if form.is_valid():
            form.save()
            messages.success(request, "Le feedback a été modifié avec succès.")
            return redirect('mission_detail', mission_id=mission_id)
    else:
        form = FeedbackForm(instance=feedback)
    
    return render(request, 'feedback_form.html', {'form': form, 'feedback': feedback, 'action': 'Modifier'})

@login_required
def feedback_delete(request, feedback_id):
    feedback = get_object_or_404(Feedback, pk=feedback_id)
    mission_id = feedback.rapport.mission.id

    if not (request.user == feedback.auteur or request.user.role == 'admin'):
        messages.error(request, "Vous n'êtes pas autorisé à supprimer ce feedback.")
        return redirect('mission_detail', mission_id=mission_id)

    if request.method == 'POST': # Confirmation de la suppression
        feedback.delete()
        messages.success(request, "Le feedback a été supprimé avec succès.")
        return redirect('mission_detail', mission_id=mission_id)
    
    # Si GET, on pourrait afficher une page de confirmation, 
    # mais pour simplifier, on peut aussi juste le faire via un POST depuis un bouton.
    # Pour une meilleure UX, une page de confirmation est recommandée.
    # Ici, on va supposer une confirmation via un petit formulaire/bouton dans le template.
    return render(request, 'feedback_confirm_delete.html', {'feedback': feedback})

# Vue détail centre d'appels
from django.contrib.auth import views as auth_views, authenticate, login
from django.shortcuts import redirect
from django.contrib.auth import logout, update_session_auth_hash, login, authenticate
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm

def custom_login(request):
    """Vue de login personnalisée pour gérer la redirection selon le rôle"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    form = AuthenticationForm()
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenue, {user.username} !')
                
                # Rediriger selon le rôle
                if user.role == 'client':
                    return redirect('clients_finaux:historique')
                elif user.role in ['admin', 'donneur_ordre', 'agent', 'centre']:
                    return redirect('core:dashboard')
                else:
                    return redirect('core:dashboard')
        else:
            messages.error(request, 'Identifiants invalides. Veuillez réessayer.')
    
    # Afficher le formulaire de connexion
    return render(request, 'registration/login.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('login')

@login_required
def notifications(request):
    # Pour l'instant, juste une page simple
    return render(request, 'core/notifications.html', {
        'notifications': [] # À implémenter avec un vrai système de notifications
    })

@login_required
def profile(request):
    return render(request, 'core/profile.html', {
        'user': request.user
    })

@login_required
def settings(request):
    return render(request, 'core/settings.html', {
        'user': request.user
    })

def is_donneur_ordre(user):
    return user.is_authenticated and user.role in ['donneur_ordre', 'entreprise']

import traceback

@login_required
@user_passes_test(is_donneur_ordre)
def donneur_ordre_dashboard(request):
    logger.info('\n' + '='*100)
    logger.info('ACCÈS AU DASHBOARD DONNEUR ORDRE')
    logger.info('='*100)
    logger.info(f'Session ID: {request.session.session_key}')
    logger.info(f'Utilisateur connecté : {request.user.username} (ID: {request.user.id})')
    logger.info(f'Rôle utilisateur : {request.user.role}')
    logger.info(f'Méthode HTTP : {request.method}')
    logger.info(f'URL complète : {request.build_absolute_uri()}')
    logger.info('='*100)

    try:
        # Récupérer l'entreprise du donneur d'ordre
        entreprise = request.user.parent_entreprise
        if not entreprise:
            logger.info("ERREUR: Utilisateur sans entreprise associée")
            return HttpResponseForbidden("Vous n'êtes pas associé à une entreprise donneuse d'ordre.")
        
        logger.info(f'Entreprise trouvée : {entreprise.nom} (ID: {entreprise.id})')
    except Exception as e:
        logger.info('ERREUR lors de la récupération de l\'entreprise:', str(e))
        logger.info('Traceback:', traceback.format_exc())
        return HttpResponseServerError('Une erreur est survenue lors de la récupération de l\'entreprise.')
    
    # Date il y a 30 jours
    thirty_days_ago = timezone.now() - timedelta(days=30)
    default_mission_statuts = ['en_attente', 'en_cours', 'terminee', 'annulee']
    default_appel_statuts = ['success', 'failure', 'callback', 'unavailable']
    
    logger.info('Debug - Entreprise:', entreprise.id, entreprise.nom)
    logger.info('Debug - Date limite:', thirty_days_ago)

    # Initialiser les données
    dates = []
    nb_appels = []
    durees_moyennes = []
    missions_data = {status: 0 for status in default_mission_statuts}
    statuts_data = {status: 0 for status in default_appel_statuts}

    try:
        # Générer les dates sur 30 jours
        current_date = timezone.now().date()
        for i in range(30):
            date = current_date - timedelta(days=i)
            dates.insert(0, date.strftime('%Y-%m-%d'))
            nb_appels.insert(0, 0)
            durees_moyennes.insert(0, 0)

        # Récupérer les données des appels
        appels_stats = SaisieResultat.objects.filter(
            mission__entreprise=entreprise,
            date_appel__gte=thirty_days_ago
        ).annotate(
            date=TruncDate('date_appel')
        ).values('date').annotate(
            nb_appels=Count('id'),
            duree_moyenne=Avg('duree_appel')
        ).order_by('date')

        # Remplir les données des appels
        date_to_index = {date: idx for idx, date in enumerate(dates)}
        for stat in appels_stats:
            date_str = stat['date'].strftime('%Y-%m-%d')
            if date_str in date_to_index:
                idx = date_to_index[date_str]
                nb_appels[idx] = stat['nb_appels']
                if stat['duree_moyenne']:
                    duree = stat['duree_moyenne'].total_seconds() if isinstance(stat['duree_moyenne'], timedelta) else float(stat['duree_moyenne'])
                    durees_moyennes[idx] = round(duree, 1)

        # Récupérer les données des missions
        logger.info('\nDEBUG - Récupération des statuts de missions')
        missions_stats = Mission.objects.filter(
            entreprise=entreprise
        ).values('status').annotate(
            count=Count('id')
        )
        logger.info('SQL missions:', missions_stats.query)
        missions_stats = list(missions_stats)
        logger.info('Résultats missions:', missions_stats)

        for stat in missions_stats:
            if stat['status'] in missions_data:
                missions_data[stat['status']] = stat['count']
            else:
                logger.info(f'ATTENTION: Status de mission inconnu: {stat["status"]}')

        # Récupérer les données des statuts d'appels
        logger.info('\nDEBUG - Récupération des statuts d\'appels')
        statuts_stats = SaisieResultat.objects.filter(
            mission__entreprise=entreprise,
            date_appel__gte=thirty_days_ago
        ).values('status').annotate(
            count=Count('id')
        )
        logger.info('SQL appels:', statuts_stats.query)
        statuts_stats = list(statuts_stats)
        logger.info('Résultats appels:', statuts_stats)

        for stat in statuts_stats:
            if stat['status'] in statuts_data:
                statuts_data[stat['status']] = stat['count']
            else:
                logger.info(f'ATTENTION: Status d\'appel inconnu: {stat["status"]}')

        # Préparer les données finales
        missions_labels = list(missions_data.keys())
        missions_values = list(missions_data.values())
        statuts_labels = list(statuts_data.keys())
        statuts_values = list(statuts_data.values())

        logger.info('Debug - Données finales :')
        logger.info('Dates:', dates)
        logger.info('Nombre d\'appels:', nb_appels)
        logger.info('Durées moyennes:', durees_moyennes)
        logger.info('Missions labels:', missions_labels)
        logger.info('Missions values:', missions_values)
        logger.info('Statuts labels:', statuts_labels)
        logger.info('Statuts values:', statuts_values)
    except Exception as e:
        logger.info('ERREUR lors de la génération des données:', str(e))
        logger.info('Traceback:', traceback.format_exc())
        dates = [timezone.now().strftime('%Y-%m-%d')]
        nb_appels = [0]
        durees_moyennes = [0]
        missions_labels = default_mission_statuts
        missions_values = [0] * len(default_mission_statuts)
        statuts_labels = default_appel_statuts
        statuts_values = [0] * len(default_appel_statuts)
    
    logger.info('\nDEBUG - Données brutes avant formatage:')
    logger.info('Dates (type: %s):' % type(dates).__name__, dates)
    logger.info('Nb appels (type: %s):' % type(nb_appels).__name__, nb_appels)
    logger.info('Durées moyennes (type: %s):' % type(durees_moyennes).__name__, durees_moyennes)
    logger.info('Labels missions (type: %s):' % type(missions_labels).__name__, missions_labels)
    logger.info('Valeurs missions (type: %s):' % type(missions_values).__name__, missions_values)
    logger.info('Labels statuts (type: %s):' % type(statuts_labels).__name__, statuts_labels)
    logger.info('Valeurs statuts (type: %s):' % type(statuts_values).__name__, statuts_values)

    # Vérifier et nettoyer les données
    # S'assurer que toutes les valeurs sont des types simples (str, int, float)
    chart_data = {
        'dates': [str(d) for d in dates],
        'nbAppels': [int(n) for n in nb_appels],
        'dureesMoyennes': [float(d) for d in durees_moyennes],
        'missionsLabels': [str(l) for l in missions_labels],
        'missionsValues': [int(v) for v in missions_values],
        'statutsLabels': [str(l) for l in statuts_labels],
        'statutsValues': [int(v) for v in statuts_values]
    }

    logger.info('\nDEBUG - Données formatées pour JSON:')
    logger.info(json.dumps(chart_data, indent=2, ensure_ascii=False))

    # Sérialiser en JSON
    try:
        chart_json = json.dumps(chart_data, ensure_ascii=False)
        logger.info('\nDEBUG - JSON sérialisé avec succès')
    except Exception as e:
        logger.info('\nERREUR - Échec de la sérialisation JSON:', str(e))
        chart_json = json.dumps({
            'dates': [],
            'nbAppels': [],
            'dureesMoyennes': [],
            'missionsLabels': [],
            'missionsValues': [],
            'statutsLabels': [],
            'statutsValues': []
        })

    # Préparer le contexte
    context = {
        'chart_data': chart_json
    }

    try:
        # Ajouter les statistiques globales
        stats = {
            'total_missions': Mission.objects.filter(entreprise=entreprise).count(),
            'missions_en_cours': Mission.objects.filter(entreprise=entreprise, status='en_cours').count(),
            'total_appels': SaisieResultat.objects.filter(mission__entreprise=entreprise).count(),
            'appels_reussis': SaisieResultat.objects.filter(mission__entreprise=entreprise, status='success').count(),
        }
        context.update(stats)
        
        logger.info('Debug - Statistiques globales :')
        logger.info(stats)

    except Exception as e:
        logger.info('ERREUR lors du calcul des statistiques globales:', str(e))
        context.update({
            'total_missions': 0,
            'missions_en_cours': 0,
            'total_appels': 0,
            'appels_reussis': 0,
        })

    return render(request, 'dashboard/donneur_ordre.html', context)

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Votre mot de passe a été changé avec succès!')
            return redirect('core:profile')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
            return redirect('core:profile')


@login_required
def centre_detail(request, centre_id):
    centre = get_object_or_404(CentreAppels, pk=centre_id)
    agents = centre.agents.all().order_by('username')
    from missions.models import Mission
    from kpi_dashboard.models import KPI
    nb_missions = Mission.objects.filter(centre=centre).count()
    nb_kpis = KPI.objects.filter(centre=centre).count()
    return render(request, 'centre_detail.html', {
        'centre': centre,
        'agents': agents,
        'nb_missions': nb_missions,
        'nb_kpis': nb_kpis,
    })

# Vues pour la gestion des Agents

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

@login_required
@user_passes_test(is_admin)
def agent_export_csv(request):
    import csv
    from django.http import HttpResponse
    from .models import CentreAppels
    agents = User.objects.filter(role='agent')
    q = request.GET.get('q', '').strip()
    centre_id = request.GET.get('centre')
    if q:
        agents = agents.filter(
            models.Q(username__icontains=q) |
            models.Q(first_name__icontains=q) |
            models.Q(last_name__icontains=q) |
            models.Q(email__icontains=q)
        )
    if centre_id:
        agents = agents.filter(parent_centre_id=centre_id)
    agents = agents.order_by('username')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="agents.csv"'
    writer = csv.writer(response)
    writer.writerow(['Nom d\'utilisateur', 'Nom', 'Prénom', 'Email', 'Centre d\'appels', 'Actif'])
    for agent in agents:
        writer.writerow([
            agent.username,
            agent.last_name,
            agent.first_name,
            agent.email,
            agent.parent_centre.nom if agent.parent_centre else '',
            'Oui' if agent.is_active else 'Non',
        ])
    return response

@login_required
@user_passes_test(is_admin)
def agent_list(request):
    from .models import CentreAppels
    agents = User.objects.filter(role='agent')
    q = request.GET.get('q', '').strip()
    centre_id = request.GET.get('centre')
    if q:
        agents = agents.filter(
            models.Q(username__icontains=q) |
            models.Q(first_name__icontains=q) |
            models.Q(last_name__icontains=q) |
            models.Q(email__icontains=q)
        )
    if centre_id:
        agents = agents.filter(parent_centre_id=centre_id)
    agents = agents.order_by('username')
    centres = CentreAppels.objects.all().order_by('nom')
    from django.core.paginator import Paginator
    paginator = Paginator(agents, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'agents/agent_list.html', {
        'agents': page_obj.object_list,
        'centres': centres,
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': page_obj.has_other_pages(),
    })

@login_required
@user_passes_test(is_admin) # ou une permission plus fine plus tard
def agent_detail(request, user_id):
    agent = get_object_or_404(User, pk=user_id, role='agent')
    return render(request, 'agents/agent_detail.html', {'agent': agent})

@login_required
@user_passes_test(is_admin)
def agent_create(request):
    if request.method == 'POST':
        form = AgentCreationForm(request.POST)
        if form.is_valid():
            agent = form.save()
            messages.success(request, f"L'agent '{agent.username}' a été créé avec succès.")
            return redirect('agent_list')
    else:
        form = AgentCreationForm()
    return render(request, 'core/agent_form.html', {'form': form, 'action': 'Créer'})

@login_required
@user_passes_test(is_admin)
def agent_update(request, user_id):
    agent = get_object_or_404(User, pk=user_id, role='agent')
    if request.method == 'POST':
        form = AgentUpdateForm(request.POST, instance=agent)
        if form.is_valid():
            form.save()
            messages.success(request, f"L'agent '{agent.username}' a été modifié avec succès.")
            return redirect('agent_detail', user_id=agent.id)
    else:
        form = AgentUpdateForm(instance=agent)
    return render(request, 'agent_form.html', {'form': form, 'agent': agent, 'action': 'Modifier'})

@login_required
@user_passes_test(is_admin)
def agent_delete(request, user_id):
    agent = get_object_or_404(User, pk=user_id, role='agent')
    if request.method == 'POST': # Confirmation de la suppression
        # Plutôt que de supprimer, on pourrait désactiver l'agent
        # agent.is_active = False
        # agent.save()
        # messages.success(request, f"L'agent '{agent.username}' a été désactivé.")
        # Pour une suppression réelle :
        agent_username = agent.username
        agent.delete()
        messages.success(request, f"L'agent '{agent_username}' a été supprimé avec succès.")
        return redirect('agent_list')
    return render(request, 'agent_confirm_delete.html', {'agent': agent})

from saisie.models import SaisieResultat

@login_required
def mission_detail(request, mission_id):
    try:
        mission = Mission.objects.select_related('entreprise', 'centre').prefetch_related('ressources', 'kpis').get(pk=mission_id)
    except Mission.DoesNotExist:
        raise Http404('Mission non trouvée')

    # Ajout de feedback par formulaire POST
    feedback_error = None
    if request.method == 'POST' and request.POST.get('feedback_text'):
        note = request.POST.get('note')
        commentaire = request.POST.get('feedback_text')
        if note and commentaire:
            try:
                Feedback.objects.create(
                    mission=mission,
                    agent=None,  # À définir selon le contexte
                    evaluateur=request.user,
                    note=int(note),
                    commentaire=commentaire
                )
                return redirect('missions:mission_detail', mission_id=mission.id)
            except ValueError:
                feedback_error = "Note invalide."
        else:
            feedback_error = "Veuillez saisir une note et un commentaire."

    # Agents affectés à ce centre et mission
    agents = []
    if mission.centre:
        agents = User.objects.filter(parent_centre=mission.centre, role='agent')
    kpis = mission.kpis.all()
    # Résultats collectés (SaisieResultat) liés à la mission
    saisies = SaisieResultat.objects.filter(mission=mission).select_related('agent').order_by('-date_appel')
    # Feedbacks liés à la mission
    feedbacks = Feedback.objects.filter(mission=mission).select_related('agent', 'evaluateur').order_by('-date_creation')
    rapports = Rapport.objects.filter(mission=mission)
    return render(request, "missions/mission_detail.html", {
        'mission': mission,
        'agents': agents,
        'kpis': kpis,
        'saisies': saisies,
        'rapports': rapports,
        'feedbacks': feedbacks,
        'feedback_error': feedback_error,
    })
