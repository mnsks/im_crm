from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden
from .forms import FormationForm, InscriptionFormationForm, ParticipationForm
from .models import Formation, Participation
from missions.models import Mission

@login_required
def formations_list(request):
    # Récupérer toutes les formations disponibles pour l'agent
    agent = request.user
    
    # Si l'agent est rattaché à un centre, montrer les formations de ce centre
    if agent.parent_centre:
        formations = Formation.objects.filter(centre=agent.parent_centre).order_by('date')
    # Si c'est un admin, montrer toutes les formations
    elif agent.role == 'admin':
        formations = Formation.objects.all().order_by('date')
    # Sinon, aucune formation
    else:
        formations = Formation.objects.none()
    
    # Participations de l'agent
    participations = Participation.objects.filter(agent=agent)
    formations_suivies = [p.formation_id for p in participations]
    
    context = {
        'formations': formations,
        'formations_suivies': formations_suivies,
    }
    return render(request, 'formations/formations_list.html', context)

def inscription_formation(request, formation_id):
    formation = get_object_or_404(Formation, pk=formation_id)
    if request.method == 'POST':
        form = ParticipationForm(request.POST)
        if form.is_valid():
            participation = form.save(commit=False)
            participation.formation = formation
            participation.agent = request.user
            participation.save()
            messages.success(request, "Inscription enregistrée avec succès.")
            return redirect('formations:formation_list')
    else:
        form = ParticipationForm()
    return render(request, 'formations/inscription_formation.html', {'form': form, 'formation': formation})

@login_required
@user_passes_test(lambda u: u.role == 'admin')
def formation_create(request):
    if request.method == 'POST':
        form = FormationForm(request.POST)
        if form.is_valid():
            formation = form.save()
            messages.success(request, "Formation créée avec succès.")
            return redirect('formations:formation_list')
    else:
        form = FormationForm()
    return render(request, 'formations/formation_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.role == 'admin')
def inscriptions_list(request):
    inscriptions = Participation.objects.select_related('agent', 'formation').order_by('-date_inscription')
    return render(request, 'formations/inscriptions_list.html', {'inscriptions': inscriptions})

@login_required
@user_passes_test(lambda u: u.role == 'admin')
def mission_assign(request, mission_id):
    mission = get_object_or_404(Mission, pk=mission_id)
    if request.method == 'POST':
        agent_ids = request.POST.getlist('agents')
        if agent_ids:
            # Assigner les agents à la mission
            mission.agents.set(agent_ids)
            messages.success(request, "Agents assignés avec succès à la mission.")
            return redirect('missions:mission_detail', pk=mission.id)
        else:
            messages.error(request, "Veuillez sélectionner au moins un agent.")
    
    # Récupérer les agents formés pour cette mission
    agents_formes = [p.agent for p in Participation.objects.filter(
        formation__missions=mission,
        statut='validee'
    ).select_related('agent')]
    
    return render(request, 'formations/mission_assign.html', {
        'mission': mission,
        'agents_formes': agents_formes
    })
