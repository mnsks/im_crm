from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from .models import Document
from .forms import DocumentForm

@login_required
def documents_list(request):
    # Afficher les informations de l'utilisateur pour le débogage
    print(f"User: {request.user.username}")
    print(f"Role: {request.user.role}")
    print(f"Parent entreprise: {request.user.parent_entreprise}")
    
    # Vérifier que l'utilisateur est une entreprise donneuse d'ordre
    if request.user.role != 'entreprise':
        return HttpResponseForbidden(f"Accès non autorisé. Seules les entreprises peuvent accéder aux documents. Votre rôle : {request.user.role}")
    
    # Récupérer l'entreprise de l'utilisateur connecté
    entreprise = request.user.parent_entreprise
    if not entreprise:
        # Créer une entreprise pour l'utilisateur si c'est une entreprise donneuse d'ordre
        from core.models import EntrepriseDonneuseOrdre
        entreprise = EntrepriseDonneuseOrdre.objects.create(
            nom=f"Entreprise de {request.user.username}",
            description="Entreprise créée automatiquement"
        )
        request.user.parent_entreprise = entreprise
        request.user.save()
        print(f"Nouvelle entreprise créée: {entreprise}")
    
    # Récupérer tous les documents de l'entreprise
    documents = Document.objects.filter(entreprise=entreprise)
    
    # Grouper les documents par type
    documents_par_type = {}
    for doc_type, _ in Document.TYPE_CHOICES:
        documents_par_type[doc_type] = documents.filter(type=doc_type)
    
    # Formulaire pour ajouter un nouveau document
    form = DocumentForm()

    context = {
        'documents': documents,
        'documents_par_type': documents_par_type,
        'entreprise': entreprise,
        'form': form,
        'document_types': Document.TYPE_CHOICES,
    }
    return render(request, 'documents/documents_list.html', context)

@login_required
def document_create(request):
    if request.user.role != 'entreprise':
        return HttpResponseForbidden("Accès non autorisé.")

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.entreprise = request.user.parent_entreprise
            document.save()
            messages.success(request, 'Document ajouté avec succès.')
            return redirect('documents:document_list')
    else:
        form = DocumentForm()

    return render(request, 'documents/document_form.html', {
        'form': form,
        'title': 'Nouveau document'
    })
