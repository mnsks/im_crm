from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.db import models
from core.models import User
from missions.models import Mission
from saisie.models import SaisieResultat
from datetime import datetime, timedelta
import csv

def is_admin(user):
    return user.role == 'admin'

@login_required
@user_passes_test(is_admin)
def kpis_list(request):
    period = request.GET.get('period', 'month')
    
    if period == 'month':
        start_date = datetime.now() - timedelta(days=30)
    elif period == 'week':
        start_date = datetime.now() - timedelta(days=7)
    else:  # year
        start_date = datetime.now() - timedelta(days=365)
    
    # Statistiques sur les missions
    total_missions = Mission.objects.filter(created_at__gte=start_date).count()
    missions_terminees = Mission.objects.filter(
        created_at__gte=start_date,
        status='terminee'
    ).count()
    
    # Statistiques sur les agents
    agents_actifs = User.objects.filter(
        role='agent',
        last_login__gte=start_date
    ).count()
    
    # Statistiques sur les saisies
    total_saisies = SaisieResultat.objects.filter(date_appel__gte=start_date).count()
    duree_moyenne = SaisieResultat.objects.filter(
        date_appel__gte=start_date
    ).aggregate(avg_duree=models.Avg('duree_appel'))['avg_duree']
    
    context = {
        'period': period,
        'total_missions': total_missions,
        'missions_terminees': missions_terminees,
        'taux_completion': (missions_terminees / total_missions * 100) if total_missions > 0 else 0,
        'agents_actifs': agents_actifs,
        'total_saisies': total_saisies,
        'duree_moyenne': duree_moyenne
    }
    
    return render(request, 'kpis/kpis_list.html', context)

@login_required
@user_passes_test(is_admin)
def kpis_export(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="kpis_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Indicateur', 'Valeur'])
    
    # Même logique que dans kpis_list
    period = request.GET.get('period', 'month')
    if period == 'month':
        start_date = datetime.now() - timedelta(days=30)
    elif period == 'week':
        start_date = datetime.now() - timedelta(days=7)
    else:
        start_date = datetime.now() - timedelta(days=365)
    
    total_missions = Mission.objects.filter(created_at__gte=start_date).count()
    missions_terminees = Mission.objects.filter(
        created_at__gte=start_date,
        status='terminee'
    ).count()
    
    writer.writerow(['Total missions', total_missions])
    writer.writerow(['Missions terminées', missions_terminees])
    writer.writerow(['Taux de complétion', f'{(missions_terminees/total_missions*100):.2f}%' if total_missions > 0 else '0%'])
    
    return response
