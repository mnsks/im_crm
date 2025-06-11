from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Script
from .forms import ScriptForm

@login_required
def scripts_list(request):
    # Récupérer les scripts selon le rôle de l'utilisateur
    if request.user.role == 'admin':
        # L'admin voit tous les scripts
        scripts = Script.objects.filter(est_actif=True)
    elif request.user.role == 'centre':
        # Le centre voit les scripts de ses missions
        scripts = Script.objects.filter(mission__centre=request.user.centre, est_actif=True)
    elif request.user.role == 'agent':
        # L'agent voit les scripts des missions sur lesquelles il a des interactions
        scripts = Script.objects.filter(mission__resultats_saisie__agent=request.user, est_actif=True).distinct()
    else:
        # Les autres rôles ne voient aucun script
        scripts = Script.objects.none()
    
    return render(request, 'scripts/scripts_list.html', {'scripts': scripts})

@login_required
def script_create(request):
    if not request.user.role in ['admin', 'centre']:
        messages.error(request, 'Accès non autorisé.')
        return redirect('scripts_list')
    
    if request.method == 'POST':
        form = ScriptForm(request.POST)
        if form.is_valid():
            script = form.save(commit=False)
            script.version = '1.0'
            script.save()
            messages.success(request, 'Script créé avec succès.')
            return redirect('scripts_list')
    else:
        form = ScriptForm()
    
    return render(request, 'scripts/script_form.html', {'form': form, 'action': 'Créer'})

@login_required
def script_detail(request, pk):
    # Récupérer le script selon le rôle de l'utilisateur
    if request.user.role == 'admin':
        script = get_object_or_404(Script, pk=pk)
    elif request.user.role == 'centre':
        script = get_object_or_404(Script, pk=pk, mission__centre=request.user.centre)
    elif request.user.role == 'agent':
        script = get_object_or_404(Script, pk=pk, mission__resultats_saisie__agent=request.user)
    else:
        messages.error(request, 'Accès non autorisé.')
        return redirect('scripts_list')
    
    return render(request, 'scripts/script_detail.html', {'script': script})

@login_required
def script_update(request, pk):
    if not request.user.role in ['admin', 'centre']:
        messages.error(request, 'Accès non autorisé.')
        return redirect('scripts_list')
    
    script = get_object_or_404(Script, pk=pk)
    
    if request.method == 'POST':
        form = ScriptForm(request.POST, instance=script)
        if form.is_valid():
            form.save()
            messages.success(request, 'Script mis à jour avec succès.')
            return redirect('script_detail', pk=pk)
    else:
        form = ScriptForm(instance=script)
    
    return render(request, 'scripts/script_form.html', {
        'form': form,
        'script': script,
        'action': 'Modifier'
    })

@login_required
def script_new_version(request, pk):
    if not request.user.role in ['admin', 'centre']:
        messages.error(request, 'Accès non autorisé.')
        return redirect('scripts_list')
    
    old_script = get_object_or_404(Script, pk=pk)
    
    if request.method == 'POST':
        form = ScriptForm(request.POST)
        if form.is_valid():
            # Désactiver l'ancienne version
            old_script.est_actif = False
            old_script.save()
            
            # Créer la nouvelle version
            new_script = form.save(commit=False)
            version = float(old_script.version) + 0.1
            new_script.version = f"{version:.1f}"
            new_script.mission = old_script.mission
            new_script.save()
            
            messages.success(request, f'Nouvelle version {new_script.version} créée avec succès.')
            return redirect('script_detail', pk=new_script.pk)
    else:
        form = ScriptForm(initial={
            'titre': old_script.titre,
            'contenu': old_script.contenu
        })
    
    return render(request, 'scripts/script_form.html', {
        'form': form,
        'script': old_script,
        'action': 'Nouvelle version'
    })
