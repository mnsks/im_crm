from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from core.models import User, CentreAppels
from django.db.models import Q
from .forms import AgentCreationForm, AgentChangeForm

def is_admin(user):
    return user.role == 'admin'

@login_required
@user_passes_test(is_admin)
def agent_list(request):
    agents = User.objects.filter(role='agent')
    if request.GET.get('search'):
        search = request.GET.get('search')
        agents = agents.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    return render(request, 'agents/agent_list.html', {'agents': agents})

@login_required
@user_passes_test(is_admin)
def agent_create(request):
    if request.method == 'POST':
        form = AgentCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Agent créé avec succès.')
            return redirect('agents:list')
    else:
        form = AgentCreationForm()
    return render(request, 'agents/agent_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def agent_detail(request, pk):
    agent = get_object_or_404(User, pk=pk, role='agent')
    return render(request, 'agents/agent_detail.html', {'agent': agent})

@login_required
@user_passes_test(is_admin)
def agent_edit(request, pk):
    agent = get_object_or_404(User, pk=pk, role='agent')
    if request.method == 'POST':
        form = AgentChangeForm(request.POST, instance=agent)
        if form.is_valid():
            form.save()
            messages.success(request, 'Agent modifié avec succès.')
            return redirect('agents:detail', pk=agent.pk)
    else:
        form = AgentChangeForm(instance=agent)
    return render(request, 'agents/agent_form.html', {'form': form, 'agent': agent})

@login_required
@user_passes_test(is_admin)
def agent_delete(request, pk):
    agent = get_object_or_404(User, pk=pk, role='agent')
    if request.method == 'POST':
        agent.delete()
        messages.success(request, 'Agent supprimé avec succès.')
        return redirect('agents:list')
    return render(request, 'agents/agent_confirm_delete.html', {'agent': agent})
