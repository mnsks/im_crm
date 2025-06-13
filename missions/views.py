from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Mission
from core.models import User

@login_required
def missions_list(request):
    # Filtrer les missions selon le rôle de l'utilisateur
    if request.user.role == 'agent':
        missions = Mission.objects.select_related('entreprise', 'centre').filter(agents=request.user)
    elif request.user.role == 'centre':
        missions = Mission.objects.select_related('entreprise', 'centre').filter(centre=request.user.parent_centre)
    elif request.user.role == 'donneur_ordre':
        missions = Mission.objects.select_related('entreprise', 'centre').filter(entreprise=request.user.parent_entreprise)
    elif request.user.role == 'admin':
        missions = Mission.objects.select_related('entreprise', 'centre').all()
    else:
        missions = Mission.objects.none()
    
    # Filtres
    status = request.GET.get('status')
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    filter_type = request.GET.get('filter_type', 'overlap')  # overlap, start, end
    
    if status:
        missions = missions.filter(status=status)
    
    if date_debut and date_fin:
        if filter_type == 'start':
            # Missions qui commencent dans la période
            missions = missions.filter(
                date_debut__gte=date_debut,
                date_debut__lte=date_fin
            )
        elif filter_type == 'end':
            # Missions qui se terminent dans la période
            missions = missions.filter(
                date_fin__gte=date_debut,
                date_fin__lte=date_fin
            )
        else:  # overlap - missions qui chevauchent la période
            missions = missions.filter(
                date_debut__lte=date_fin,
                date_fin__gte=date_debut
            )
    
    # Pagination
    paginator = Paginator(missions.order_by('-date_debut'), 10)
    page = request.GET.get('page')
    missions = paginator.get_page(page)
    
    context = {
        'missions': missions,
        'status_choices': Mission.STATUS_CHOICES,
    }
    
    return render(request, 'missions/missions_list.html', context)

@login_required
def mission_detail(request, pk):
    mission = get_object_or_404(Mission, pk=pk)
    
    # Vérifier les permissions
    if request.user.role == 'agent' and request.user not in mission.agents.all():
        return redirect('missions:list')
    elif request.user.role == 'centre' and mission.centre != request.user.parent_centre:
        return redirect('missions:list')
    elif request.user.role == 'donneur_ordre' and mission.entreprise != request.user.parent_entreprise:
        return redirect('missions:list')
    
    context = {
        'mission': mission,
    }
    
    return render(request, 'missions/mission_detail.html', context)

@login_required
def mission_create(request):
    if request.user.role not in ['admin', 'donneur_ordre']:
        return redirect('missions:list')
    
    if request.method == 'POST':
        # TODO: Implémenter la création de mission
        pass
    
    context = {
        'centres': User.objects.filter(role='centre'),
    }
    
    return render(request, 'missions/mission_form.html', context)

@login_required
def mission_update(request, pk):
    mission = get_object_or_404(Mission, pk=pk)
    
    # Vérifier les permissions
    if request.user.role == 'admin':
        pass
    elif request.user.role == 'donneur_ordre' and mission.entreprise != request.user.parent_entreprise:
        return redirect('missions:list')
    else:
        return redirect('missions:list')
    
    if request.method == 'POST':
        # TODO: Implémenter la mise à jour de mission
        pass
    
    context = {
        'mission': mission,
        'centres': User.objects.filter(role='centre'),
    }
    
    return render(request, 'missions/mission_form.html', context)

@login_required
def mission_delete(request, pk):
    mission = get_object_or_404(Mission, pk=pk)
    
    # Vérifier les permissions
    from django.contrib import messages
    if request.user.role == 'admin':
        pass
    elif request.user.role == 'donneur_ordre' and mission.entreprise != request.user.parent_entreprise:
        messages.error(request, "Vous n'avez pas le droit de supprimer cette mission.")
        return redirect('core:access_denied')
    elif request.user.role == 'centre' and mission.centre != request.user.parent_centre:
        messages.error(request, "Vous n'avez pas le droit de supprimer cette mission.")
        return redirect('core:access_denied')
    elif request.user.role == 'centre' and mission.centre == request.user.parent_centre:
        pass
    else:
        messages.error(request, "Vous n'avez pas le droit de supprimer cette mission.")
        return redirect('core:access_denied')
    
    if request.method == 'POST':
        mission.delete()
        return redirect('missions:mission_list')
    
    context = {
        'mission': mission,
    }
    
    return render(request, 'missions/mission_confirm_delete.html', context)
