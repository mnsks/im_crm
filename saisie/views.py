from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import SaisieResultat
from .forms import SaisieResultatForm
from missions.models import Mission
from core.models import User

@login_required
def saisie_list(request):
    # Filtrer les saisies selon le rôle de l'utilisateur
    if request.user.role == 'agent':
        saisies = SaisieResultat.objects.filter(agent=request.user)
    elif request.user.role == 'centre':
        saisies = SaisieResultat.objects.filter(mission__centre=request.user.parent_centre)
    else:
        saisies = SaisieResultat.objects.filter(mission__entreprise=request.user.entreprise)
    
    return render(request, 'saisie/saisie_list.html', {'saisies': saisies})

@login_required
def saisie_create(request):
    if request.method == 'POST':
        form = SaisieResultatForm(request.POST)
        if form.is_valid():
            saisie = form.save(commit=False)
            saisie.agent = request.user
            saisie.save()
            messages.success(request, 'Résultat enregistré avec succès.')
            
            # Rediriger vers la saisie suivante si c'est un rappel
            if saisie.status == 'callback' and saisie.rappel_prevu:
                messages.info(request, f'Rappel programmé pour le {saisie.rappel_prevu}')
            
            return redirect('saisie:saisie_list')
    else:
        # Pré-remplir avec la mission si spécifiée
        initial = {}
        if 'mission_id' in request.GET:
            initial['mission'] = get_object_or_404(Mission, pk=request.GET['mission_id'])
        form = SaisieResultatForm(initial=initial)
    
    return render(request, 'saisie/saisie_form.html', {'form': form})

@login_required
def saisie_detail(request, pk):
    saisie = get_object_or_404(SaisieResultat, pk=pk)
    
    # Vérifier les permissions
    if request.user.role == 'agent' and saisie.agent != request.user:
        messages.error(request, 'Accès non autorisé.')
        return redirect('saisie_list')
    
    return render(request, 'saisie/saisie_detail.html', {'saisie': saisie})

@login_required
def saisie_update(request, pk):
    saisie = get_object_or_404(SaisieResultat, pk=pk)
    
    # Vérifier les permissions
    if request.user.role == 'agent' and saisie.agent != request.user:
        messages.error(request, 'Accès non autorisé.')
        return redirect('saisie_list')
    
    if request.method == 'POST':
        form = SaisieResultatForm(request.POST, instance=saisie)
        if form.is_valid():
            form.save()
            messages.success(request, 'Résultat mis à jour avec succès.')
            return redirect('saisie_detail', pk=pk)
    else:
        form = SaisieResultatForm(instance=saisie)
    
    return render(request, 'saisie/saisie_form.html', {
        'form': form,
        'saisie': saisie
    })

@login_required
def mission_saisies(request, mission_id):
    mission = get_object_or_404(Mission, pk=mission_id)
    
    # Vérifier les permissions
    if request.user.role == 'agent' and not mission.agents.filter(id=request.user.id).exists():
        messages.error(request, 'Accès non autorisé.')
        return redirect('saisie_list')
    
    saisies = SaisieResultat.objects.filter(mission=mission)
    return render(request, 'saisie/mission_saisies.html', {
        'mission': mission,
        'saisies': saisies
    })

@login_required
def agent_saisies(request, agent_id):
    agent = get_object_or_404(User, pk=agent_id, role='agent')
    
    # Vérifier les permissions
    if request.user.role == 'agent' and request.user.id != agent_id:
        messages.error(request, 'Accès non autorisé.')
        return redirect('saisie_list')
    
    saisies = SaisieResultat.objects.filter(agent=agent)
    return render(request, 'saisie/agent_saisies.html', {
        'agent': agent,
        'saisies': saisies
    })
