from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from .models import HistoriqueAppel, Requete, PreferenceContact
from feedback.models import Feedback
from documents.models import Document
from missions.models import Mission

def is_client_final(user):
    return user.is_authenticated and user.role == 'client'

@login_required
def redirect_if_not_client(request):
    if not is_client_final(request.user):
        messages.error(request, "Accès réservé aux clients finaux.")
        return redirect('core:dashboard')
    
    # Vérifier si l'utilisateur a un ClientFinal associé
    from core.models import ClientFinal, EntrepriseDonneuseOrdre
    try:
        client = ClientFinal.objects.get(email=request.user.email)
    except ClientFinal.DoesNotExist:
        # Récupérer l'entreprise associée si elle existe
        entreprise = None
        if request.user.parent_client_entreprise:
            entreprise = request.user.parent_client_entreprise
        else:
            # Prendre la première entreprise par défaut si aucune n'est associée
            entreprise = EntrepriseDonneuseOrdre.objects.first()
            if not entreprise:
                messages.error(request, "Aucune entreprise disponible. Contactez l'administrateur.")
                return redirect('core:dashboard')
        
        # Créer un nouveau ClientFinal
        try:
            client = ClientFinal.objects.create(
                nom=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                email=request.user.email,
                telephone=request.user.username,
                entreprise=entreprise
            )
            messages.success(request, "Votre profil client a été créé avec succès.")
        except Exception as e:
            messages.error(request, f"Erreur lors de la création du profil client : {str(e)}")
            return redirect('core:dashboard')
    
    return None

@login_required
def historique_appels(request):
    redirect_response = redirect_if_not_client(request)
    if redirect_response:
        return redirect_response

    # Récupérer les appels pour l'utilisateur connecté
    appels = HistoriqueAppel.objects.filter(
        client=request.user
    ).select_related('mission').order_by('-date_appel')
    
    return render(request, 'clients_finaux/historique_appels.html', {'appels': appels})

@login_required
def detail_appel(request, appel_id):
    redirect_response = redirect_if_not_client(request)
    if redirect_response:
        return redirect_response
    
    appel = get_object_or_404(HistoriqueAppel, id=appel_id, client=request.user)
    return render(request, 'clients_finaux/detail_appel.html', {'appel': appel})

@login_required
def liste_requetes(request):
    redirect_response = redirect_if_not_client(request)
    if redirect_response:
        return redirect_response

    # Récupérer les requêtes de l'utilisateur connecté
    requetes = Requete.objects.filter(
        client=request.user
    ).order_by('-date_creation')

    return render(request, 'clients_finaux/liste_requetes.html', {'requetes': requetes})

@login_required
def nouvelle_requete(request):
    redirect_response = redirect_if_not_client(request)
    if redirect_response:
        return redirect_response
    if request.method == 'POST':
        # Traitement du formulaire
        titre = request.POST.get('titre')
        description = request.POST.get('description')
        priorite = request.POST.get('priorite', 0)
        
        requete = Requete.objects.create(
            client=request.user,
            titre=titre,
            description=description,
            priorite=priorite
        )
        messages.success(request, 'Votre requête a été créée avec succès.')
        return redirect('clients_finaux:detail_requete', requete_id=requete.id)
        
    return render(request, 'clients_finaux/nouvelle_requete.html')

@login_required
def detail_requete(request, requete_id):
    redirect_response = redirect_if_not_client(request)
    if redirect_response:
        return redirect_response
    requete = get_object_or_404(Requete, id=requete_id, client=request.user)
    return render(request, 'clients_finaux/detail_requete.html', {'requete': requete})

@login_required
def modifier_requete(request, requete_id):
    redirect_response = redirect_if_not_client(request)
    if redirect_response:
        return redirect_response
    requete = get_object_or_404(Requete, id=requete_id, client=request.user)
    if request.method == 'POST':
        # Traitement du formulaire
        requete.titre = request.POST.get('titre')
        requete.description = request.POST.get('description')
        requete.priorite = request.POST.get('priorite', 0)
        requete.save()
        messages.success(request, 'Votre requête a été mise à jour avec succès.')
        return redirect('clients_finaux:detail_requete', requete_id=requete.id)
    return render(request, 'clients_finaux/modifier_requete.html', {'requete': requete})

@login_required
def liste_documents(request):
    redirect_response = redirect_if_not_client(request)
    if redirect_response:
        return redirect_response

    # Récupérer les documents de l'entreprise de l'utilisateur
    if request.user.parent_client_entreprise:
        documents = Document.objects.filter(
            entreprise=request.user.parent_client_entreprise
        ).order_by('-date_modification')
    else:
        documents = Document.objects.none()
        messages.warning(request, "Aucune entreprise associée à votre compte.")

    return render(request, 'clients_finaux/liste_documents.html', {'documents': documents})

@login_required
def detail_document(request, document_id):
    redirect_response = redirect_if_not_client(request)
    if redirect_response:
        return redirect_response

    if not request.user.parent_client_entreprise:
        messages.error(request, "Aucune entreprise associée à votre compte.")
        return redirect('clients_finaux:liste_documents')

    document = get_object_or_404(
        Document,
        id=document_id,
        entreprise=request.user.parent_client_entreprise
    )
    return render(request, 'clients_finaux/detail_document.html', {'document': document})

@login_required
def preferences_contact(request):
    redirect_response = redirect_if_not_client(request)
    if redirect_response:
        return redirect_response
    preferences, created = PreferenceContact.objects.get_or_create(client=request.user)
    return render(request, 'clients_finaux/preferences.html', {'preferences': preferences})

@login_required
def modifier_preferences(request):
    redirect_response = redirect_if_not_client(request)
    if redirect_response:
        return redirect_response
    preferences, created = PreferenceContact.objects.get_or_create(client=request.user)
    if request.method == 'POST':
        # Traitement du formulaire
        preferences.horaires_preferes = request.POST.get('horaires_preferes')
        preferences.jours_exclus = request.POST.get('jours_exclus')
        preferences.mode_contact_prefere = request.POST.get('mode_contact_prefere')
        preferences.numero_telephone = request.POST.get('numero_telephone')
        preferences.email_contact = request.POST.get('email_contact')
        preferences.ne_pas_deranger = request.POST.get('ne_pas_deranger') == 'on'
        preferences.save()
        messages.success(request, 'Vos préférences ont été mises à jour avec succès.')
        return redirect('clients_finaux:preferences')
    return render(request, 'clients_finaux/modifier_preferences.html', {'preferences': preferences})

@login_required
def liste_feedback(request):
    redirect_response = redirect_if_not_client(request)
    if redirect_response:
        return redirect_response

    # Récupérer les feedbacks donnés par l'utilisateur
    feedbacks = Feedback.objects.filter(
        evaluateur=request.user
    ).select_related('mission', 'agent').order_by('-date_creation')

    return render(request, 'clients_finaux/liste_feedback.html', {'feedbacks': feedbacks})

@login_required
def nouveau_feedback(request):
    redirect_response = redirect_if_not_client(request)
    if redirect_response:
        return redirect_response

    # Récupérer les missions de l'entreprise du client
    if not request.user.parent_client_entreprise:
        messages.error(request, "Aucune entreprise associée à votre compte.")
        return redirect('clients_finaux:feedback')

    missions = Mission.objects.filter(
        entreprise=request.user.parent_client_entreprise
    ).select_related('agent').order_by('-date_creation')

    if request.method == 'POST':
        note = request.POST.get('note')
        commentaire = request.POST.get('commentaire')
        mission_id = request.POST.get('mission_id')
        
        try:
            mission = Mission.objects.get(
                id=mission_id,
                entreprise=request.user.parent_client_entreprise
            )
            
            # Créer le feedback
            feedback = Feedback.objects.create(
                mission=mission,
                evaluateur=request.user,  # Le client qui donne le feedback
                agent=mission.agent,      # L'agent qui a géré la mission
                note=note,
                commentaire=commentaire
            )
            
            messages.success(request, 'Votre feedback a été envoyé avec succès.')
            return redirect('clients_finaux:feedback')
            
        except Mission.DoesNotExist:
            messages.error(request, "Mission non trouvée ou non autorisée.")
    
    context = {
        'missions': missions,
        'rating_choices': Feedback.RATING_CHOICES
    }
    return render(request, 'clients_finaux/nouveau_feedback.html', context)
