from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Feedback
from .forms import FeedbackForm
from missions.models import Mission
from core.models import User

@login_required
def feedback_list(request):
    # Filtrer les feedbacks selon le rôle de l'utilisateur
    if request.user.role == 'agent':
        feedbacks = Feedback.objects.filter(agent=request.user)
    elif request.user.role == 'centre':
        feedbacks = Feedback.objects.filter(mission__centre=request.user.parent_centre)
    elif request.user.role == 'donneur_ordre':
        # Récupérer tous les feedbacks des missions de l'entreprise du donneur d'ordre
        feedbacks = Feedback.objects.filter(mission__entreprise=request.user.parent_entreprise)

    else:
        feedbacks = Feedback.objects.none()
    
    debug = {}
    if request.user.role == 'donneur_ordre':
        debug = {
            'user_id': user_id,
            'parent_entreprise_id': parent_entreprise_id,
            'missions_ids': missions_ids,
            'feedbacks_ids': list(feedbacks.values_list('id', flat=True)),
        }
    return render(request, 'feedback/feedback_list.html', {'feedbacks': feedbacks, 'debug': debug})

@login_required
def feedback_create(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.evaluateur = request.user
            feedback.save()
            messages.success(request, 'Feedback envoyé avec succès.')
            return redirect('feedback:feedback_list')
    else:
        # Pré-remplir avec la mission et l'agent si spécifiés
        initial = {}
        if 'mission_id' in request.GET:
            initial['mission'] = get_object_or_404(Mission, pk=request.GET['mission_id'])
        if 'agent_id' in request.GET:
            initial['agent'] = get_object_or_404(User, pk=request.GET['agent_id'])
        form = FeedbackForm(initial=initial)
    
    return render(request, 'feedback/feedback_form.html', {'form': form})

@login_required
def feedback_detail(request, pk):
    feedback = get_object_or_404(Feedback, pk=pk)
    
    # Vérifier les permissions
    if request.user.role == 'agent' and feedback.agent != request.user:
        messages.error(request, 'Accès non autorisé.')
        return redirect('feedback:feedback_list')
    
    return render(request, 'feedback/feedback_detail.html', {'feedback': feedback})

@login_required
def agent_feedback_list(request, agent_id):
    agent = get_object_or_404(User, pk=agent_id, role='agent')
    
    # Vérifier les permissions
    if request.user.role == 'agent' and request.user.id != agent_id:
        messages.error(request, 'Accès non autorisé.')
        return redirect('feedback:feedback_list')
    
    feedbacks = Feedback.objects.filter(agent=agent)
    return render(request, 'feedback/agent_feedback_list.html', {
        'agent': agent,
        'feedbacks': feedbacks
    })

@login_required
def mission_feedback_list(request, mission_id):
    mission = get_object_or_404(Mission, pk=mission_id)
    
    # Vérifier les permissions
    if request.user.role == 'agent' and not mission.agents.filter(id=request.user.id).exists():
        messages.error(request, 'Accès non autorisé.')
        return redirect('feedback:feedback_list')
    
    feedbacks = Feedback.objects.filter(mission=mission)
    return render(request, 'feedback/mission_feedback_list.html', {
        'mission': mission,
        'feedbacks': feedbacks
    })
