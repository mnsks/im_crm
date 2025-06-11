from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Client
from .forms import ClientForm

@login_required
def clients_list(request):
    # Récupérer les clients selon le rôle de l'utilisateur
    if request.user.role == 'admin':
        # L'admin voit tous les clients
        clients = Client.objects.all()
    elif request.user.role == 'centre':
        # Le centre d'appel voit les clients associés à ses missions via les saisies
        clients = Client.objects.filter(interactions_saisie__mission__centre=request.user.parent_centre).distinct()
    elif request.user.role == 'agent':
        # L'agent voit les clients associés à ses missions via les saisies
        clients = Client.objects.filter(interactions_saisie__agent=request.user).distinct()
    elif request.user.role == 'donneur_ordre':
        # Le donneur d'ordre voit ses propres clients
        clients = Client.objects.filter(entreprise=request.user.entreprise)
    else:
        # Par défaut, aucun client n'est visible
        clients = Client.objects.none()
    
    return render(request, 'clients/clients_list.html', {'clients': clients})

@login_required
def client_create(request):
    # Seuls les donneurs d'ordre peuvent créer des clients
    if request.user.role != 'donneur_ordre':
        messages.error(request, 'Vous n\'avez pas la permission de créer des clients.')
        return redirect('clients:list')
        
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.entreprise = request.user.entreprise
            client.save()
            messages.success(request, 'Client créé avec succès.')
            return redirect('clients:list')
    else:
        form = ClientForm()
    
    return render(request, 'clients/client_form.html', {'form': form, 'action': 'Créer'})

@login_required
def client_detail(request, pk):
    # Récupérer le client selon le rôle de l'utilisateur
    if request.user.role == 'admin':
        client = get_object_or_404(Client, pk=pk)
    elif request.user.role == 'centre':
        client = get_object_or_404(Client, pk=pk, interactions_saisie__mission__centre=request.user.parent_centre)
    elif request.user.role == 'agent':
        client = get_object_or_404(Client, pk=pk, interactions_saisie__agent=request.user)
    elif request.user.role == 'donneur_ordre':
        client = get_object_or_404(Client, pk=pk, entreprise=request.user.entreprise)
    else:
        messages.error(request, 'Vous n\'avez pas accès à ce client.')
        return redirect('clients:client_list')
    
    # Préparer les données filtrées pour le template
    rappels = client.interactions_saisie.filter(status='callback', rappel_prevu__isnull=False)
    appels_reussis = client.interactions_saisie.filter(status='success').count()
    rappels_necessaires = client.interactions_saisie.filter(status='callback').count()
    
    return render(request, 'clients/client_detail.html', {
        'client': client,
        'rappels': rappels,
        'appels_reussis': appels_reussis,
        'rappels_necessaires': rappels_necessaires,
    })

@login_required
def client_update(request, pk):
    # Seuls les donneurs d'ordre et l'admin peuvent modifier les clients
    if request.user.role not in ['donneur_ordre', 'admin']:
        messages.error(request, 'Vous n\'avez pas la permission de modifier ce client.')
        return redirect('clients:client_list')
    
    # Récupérer le client
    if request.user.role == 'admin':
        client = get_object_or_404(Client, pk=pk)
    else:
        client = get_object_or_404(Client, pk=pk, entreprise=request.user.entreprise)
    
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Client mis à jour avec succès.')
            return redirect('client_detail', pk=pk)
    else:
        form = ClientForm(instance=client)
    
    return render(request, 'clients/client_form.html', {
        'form': form,
        'client': client,
        'action': 'Modifier'
    })
