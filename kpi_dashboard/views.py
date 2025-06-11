from django.shortcuts import render

from django.contrib.auth.decorators import login_required, user_passes_test
from .models import KPI

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

@login_required
@user_passes_test(is_admin)
def kpi_export_csv(request):
    import csv
    from django.http import HttpResponse
    from core.models import CentreAppels, EntrepriseDonneuseOrdre
    from missions.models import Mission
    kpis = KPI.objects.select_related('mission', 'centre', 'entreprise').all()
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    centre_id = request.GET.get('centre')
    mission_id = request.GET.get('mission')
    entreprise_id = request.GET.get('entreprise')
    if date_debut:
        kpis = kpis.filter(date__gte=date_debut)
    if date_fin:
        kpis = kpis.filter(date__lte=date_fin)
    if centre_id:
        kpis = kpis.filter(centre_id=centre_id)
    if mission_id:
        kpis = kpis.filter(mission_id=mission_id)
    if entreprise_id:
        kpis = kpis.filter(entreprise_id=entreprise_id)
    kpis = kpis.order_by('-date')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="kpis.csv"'
    writer = csv.writer(response)
    writer.writerow(['Nom', 'Valeur', 'Date', 'Mission', 'Centre d\'appels', 'Entreprise'])
    for kpi in kpis:
        writer.writerow([
            kpi.nom,
            kpi.valeur,
            kpi.date,
            kpi.mission.nom if kpi.mission else '',
            kpi.centre.nom if kpi.centre else '',
            kpi.entreprise.nom if kpi.entreprise else '',
        ])
    return response

@login_required
@user_passes_test(is_admin)
def kpi_list(request):
    from datetime import datetime
    from core.models import CentreAppels, EntrepriseDonneuseOrdre
    from missions.models import Mission
    kpis = KPI.objects.select_related('mission', 'centre', 'entreprise').all()
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    centre_id = request.GET.get('centre')
    mission_id = request.GET.get('mission')
    entreprise_id = request.GET.get('entreprise')
    if date_debut:
        kpis = kpis.filter(date__gte=date_debut)
    if date_fin:
        kpis = kpis.filter(date__lte=date_fin)
    if centre_id:
        kpis = kpis.filter(centre_id=centre_id)
    if mission_id:
        kpis = kpis.filter(mission_id=mission_id)
    if entreprise_id:
        kpis = kpis.filter(entreprise_id=entreprise_id)
    kpis = kpis.order_by('-date')
    centres = CentreAppels.objects.all().order_by('nom')
    missions = Mission.objects.all().order_by('titre')
    entreprises = EntrepriseDonneuseOrdre.objects.all().order_by('nom')
    # Préparation des données pour le graphique
    from collections import defaultdict, OrderedDict
    import json
    kpis_by_name = defaultdict(list)
    all_dates = set()
    for kpi in kpis.order_by('date'):
        kpis_by_name[kpi.nom].append({'date': kpi.date.strftime('%Y-%m-%d'), 'valeur': kpi.valeur})
        all_dates.add(kpi.date.strftime('%Y-%m-%d'))
    all_dates = sorted(all_dates)
    # Pour chaque nom de KPI, associer la valeur pour chaque date (None si absent)
    chart_data = {}
    for nom, values in kpis_by_name.items():
        values_by_date = {v['date']: v['valeur'] for v in values}
        chart_data[nom] = [values_by_date.get(date, None) for date in all_dates]
    from django.core.paginator import Paginator
    paginator = Paginator(kpis, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'kpi_list.html', {
        'kpis': page_obj.object_list,
        'centres': centres,
        'missions': missions,
        'entreprises': entreprises,
        'kpi_chart_labels': json.dumps(all_dates),
        'kpi_chart_data': json.dumps(chart_data, ensure_ascii=False),
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': page_obj.has_other_pages(),
    })

@login_required
@user_passes_test(is_admin)
def kpi_create(request):
    from .forms import KPIForm
    from django.contrib import messages
    if request.method == 'POST':
        form = KPIForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "KPI créé avec succès.")
            return redirect('kpi_list')
    else:
        form = KPIForm()
    return render(request, 'kpi_form.html', {'form': form, 'action': 'Créer'})

@login_required
@user_passes_test(is_admin)
def kpi_update(request, kpi_id):
    from .forms import KPIForm
    from django.contrib import messages
    from django.shortcuts import get_object_or_404
    kpi = get_object_or_404(KPI, pk=kpi_id)
    if request.method == 'POST':
        form = KPIForm(request.POST, instance=kpi)
        if form.is_valid():
            form.save()
            messages.success(request, "KPI modifié avec succès.")
            return redirect('kpi_list')
    else:
        form = KPIForm(instance=kpi)
    return render(request, 'kpi_form.html', {'form': form, 'action': 'Modifier'})

@login_required
@user_passes_test(is_admin)
def kpi_delete(request, kpi_id):
    from django.contrib import messages
    from django.shortcuts import get_object_or_404, redirect
    kpi = get_object_or_404(KPI, pk=kpi_id)
    if request.method == 'POST':
        kpi.delete()
        messages.success(request, "KPI supprimé avec succès.")
        return redirect('kpi_list')
    return render(request, 'kpi_confirm_delete.html', {'kpi': kpi})
