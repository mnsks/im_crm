from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.urls import reverse
from .models import Document
from .forms import DocumentForm

@login_required
def documents_list(request):
    # Afficher les informations de l'utilisateur pour le débogage
    print(f"User: {request.user.username}")
    print(f"Role: {request.user.role}")
    print(f"Parent entreprise: {request.user.parent_entreprise}")
    
    # Vérifier les permissions d'accès
    if request.user.role not in ['donneur_ordre', 'admin']:
        return HttpResponseForbidden(f"Accès non autorisé. Seuls les administrateurs et les entreprises peuvent accéder aux documents. Votre rôle : {request.user.role}")
    
    # Pour les administrateurs, montrer tous les documents
    if request.user.role == 'admin':
        documents = Document.objects.all()
        # Grouper les documents par entreprise et par type
        documents_par_type = {}
        for doc_type, _ in Document.TYPE_CHOICES:
            documents_par_type[doc_type] = documents.filter(type=doc_type)
        
        context = {
            'documents': documents,
            'documents_par_type': documents_par_type,
            'is_admin': True,
            'form': DocumentForm(),
            'document_types': Document.TYPE_CHOICES,
        }
        return render(request, 'documents/documents_list.html', context)
    
    # Pour les donneurs d'ordre, montrer uniquement leurs documents
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
    form = DocumentForm(is_admin=request.user.role == 'admin')

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
    if request.user.role not in ['donneur_ordre', 'admin']:
        return HttpResponseForbidden("Accès non autorisé.")

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, is_admin=request.user.role == 'admin')
        if form.is_valid():
            document = form.save(commit=False)
            # Si c'est un admin, utiliser l'entreprise sélectionnée dans le formulaire
            if request.user.role == 'admin':
                document.entreprise = form.cleaned_data.get('entreprise')
            else:
                document.entreprise = request.user.parent_entreprise
            document.save()
            messages.success(request, 'Document ajouté avec succès.')
            return redirect('documents:document_list')
    else:
        form = DocumentForm(is_admin=request.user.role == 'admin')

    return render(request, 'documents/document_form.html', {
        'form': form,
        'title': 'Nouveau document',
        'submit_label': 'Créer'
    })

@login_required
def document_edit(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    
    # Vérifier les permissions
    if request.user.role not in ['donneur_ordre', 'admin'] or \
       (request.user.role == 'donneur_ordre' and request.user.parent_entreprise != document.entreprise):
        return HttpResponseForbidden("Vous n'avez pas la permission de modifier ce document.")
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document, 
                          is_admin=request.user.role == 'admin')
        if form.is_valid():
            document = form.save(commit=False)
            if request.user.role == 'admin':
                document.entreprise = form.cleaned_data.get('entreprise')
            document.save()
            messages.success(request, 'Document modifié avec succès.')
            return redirect('documents:document_list')
    else:
        form = DocumentForm(instance=document, is_admin=request.user.role == 'admin')
    
    return render(request, 'documents/document_form.html', {
        'form': form,
        'document': document,
        'title': f'Modifier {document.titre}',
        'submit_label': 'Enregistrer'
    })

@login_required
def document_delete(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    
    # Vérifier les permissions
    if request.user.role not in ['donneur_ordre', 'admin'] or \
       (request.user.role == 'donneur_ordre' and request.user.parent_entreprise != document.entreprise):
        return HttpResponseForbidden("Vous n'avez pas la permission de supprimer ce document.")
    
    if request.method == 'POST':
        document.delete()
        messages.success(request, 'Document supprimé avec succès.')
    
    return redirect('documents:document_list')
