from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.template.loader import render_to_string
from weasyprint import HTML
from saisie.models import SaisieResultat
from missions.models import Mission
from .models import Rapport, Feedback
from .forms import FeedbackForm, SaisieResultatForm
from datetime import datetime, timedelta
import json

@login_required
def rapports_list(request):
    # Par défaut, afficher les rapports du mois en cours
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    mission_id = request.GET.get('mission')
    
    if not date_debut:
        # Premier jour du mois en cours
        date_debut = datetime.now().replace(day=1).strftime('%Y-%m-%d')
    if not date_fin:
        # Dernier jour du mois en cours
        date_fin = (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        date_fin = date_fin.strftime('%Y-%m-%d')
    
    # Filtrer les saisies selon le rôle de l'utilisateur
    if request.user.role == 'admin':
        saisies = SaisieResultat.objects.all()
        missions = Mission.objects.all()
    elif request.user.role == 'centre':
        saisies = SaisieResultat.objects.filter(mission__centre=request.user.parent_centre)
        missions = Mission.objects.filter(centre=request.user.parent_centre)
    else:
        saisies = SaisieResultat.objects.none()
        missions = Mission.objects.none()
    
    # Appliquer les filtres
    saisies = saisies.filter(date_appel__date__range=[date_debut, date_fin])
    if mission_id:
        saisies = saisies.filter(mission_id=mission_id)
    
    # Statistiques
    total_appels = saisies.count()
    succes = saisies.filter(status='success').count()
    echecs = saisies.filter(status='failure').count()
    rappels = saisies.filter(status='callback').count()
    indisponibles = saisies.filter(status='unavailable').count()
    
    # Taux de succès
    taux_succes = (succes / total_appels * 100) if total_appels > 0 else 0
    
    # Durée moyenne des appels
    duree_moyenne = saisies.aggregate(avg_duration=models.Avg('duree_appel'))['avg_duration']
    
    context = {
        'saisies': saisies,
        'missions': missions,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'mission_id': mission_id,
        'statistiques': {
            'total_appels': total_appels,
            'succes': succes,
            'echecs': echecs,
            'rappels': rappels,
            'indisponibles': indisponibles,
            'taux_succes': round(taux_succes, 2),
            'duree_moyenne': duree_moyenne
        }
    }
    
    return render(request, 'rapports/rapports_list.html', context)

@login_required
def daily_report(request):
    # Obtenir la date du jour
    today = datetime.now().date()
    
    # Filtrer les saisies selon le rôle de l'utilisateur
    if request.user.role == 'agent':
        saisies = SaisieResultat.objects.filter(
            agent=request.user,
            date_appel__date=today
        )
    else:
        saisies = SaisieResultat.objects.none()
    
    # Statistiques journalières
    total_appels = saisies.count()
    succes = saisies.filter(status='success').count()
    echecs = saisies.filter(status='failure').count()
    rappels = saisies.filter(status='callback').count()
    indisponibles = saisies.filter(status='unavailable').count()
    
    # Taux de succès
    taux_succes = (succes / total_appels * 100) if total_appels > 0 else 0
    
    # Durée moyenne des appels
    duree_moyenne = saisies.aggregate(avg_duration=models.Avg('duree_appel'))['avg_duration']
    
    context = {
        'saisies': saisies,
        'date': today,
        'statistiques': {
            'total_appels': total_appels,
            'succes': succes,
            'echecs': echecs,
            'rappels': rappels,
            'indisponibles': indisponibles,
            'taux_succes': round(taux_succes, 2),
            'duree_moyenne': duree_moyenne
        }
    }
    
    return render(request, 'rapports/daily_report.html', context)

@login_required
def generer_rapport_pdf(request, rapport_id):
    rapport = get_object_or_404(Rapport, id=rapport_id)
    
    # Vérifier les permissions
    if request.user.role not in ['admin', 'entreprise'] and request.user.parent_entreprise != rapport.entreprise:
        return HttpResponseForbidden()
    
    # Contexte pour le template PDF
    context = {
        'rapport': rapport,
        'statistiques': json.loads(rapport.statistiques) if rapport.statistiques else {},
        'saisies': rapport.saisies.all().order_by('-date'),
        'feedbacks': rapport.feedbacks.all().order_by('-date')
    }
    
    # Générer le HTML
    html_string = render_to_string('rapports/rapport_pdf.html', context)
    
    # Convertir en PDF
    html = HTML(string=html_string)
    pdf = html.write_pdf()
    
    # Envoyer le PDF
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'filename=rapport_{rapport.id}.pdf'
    return response

@login_required
def saisie_resultats(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id)
    
    # Vérifier que l'utilisateur est un agent assigné à la mission
    if request.user.role != 'agent' or request.user.parent_centre != mission.centre:
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        form = SaisieResultatForm(request.POST)
        if form.is_valid():
            saisie = form.save(commit=False)
            saisie.mission = mission
            saisie.agent = request.user
            saisie.save()
            
            # Mettre à jour ou créer le rapport
            rapport, created = Rapport.objects.get_or_create(
                mission=mission,
                centre=mission.centre,
                entreprise=mission.entreprise,
                date=datetime.now().date()
            )
            
            # Mettre à jour les statistiques
            stats = json.loads(rapport.statistiques) if rapport.statistiques else {}
            indicateur = form.cleaned_data['indicateur']
            valeur = form.cleaned_data['valeur']
            
            if indicateur not in stats:
                stats[indicateur] = []
            stats[indicateur].append(valeur)
            
            rapport.statistiques = json.dumps(stats)
            rapport.save()
            
            messages.success(request, 'Résultat saisi avec succès')
            return redirect('missions:mission_detail', mission_id=mission_id)
    else:
        form = SaisieResultatForm()
    
    context = {
        'form': form,
        'mission': mission,
        'saisies_recentes': SaisieResultat.objects.filter(
            mission=mission,
            agent=request.user
        ).order_by('-date')[:5]
    }
    
    return render(request, 'rapports/saisie_form.html', context)
