from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from core.models import User
from .models import Message, Notification, Notification
from django.utils import timezone

@login_required
def message_list(request):
    # Récupérer les messages selon le rôle de l'utilisateur
    if request.user.role == 'admin':
        messages = Message.objects.all()
    elif request.user.role == 'centre':
        # Messages du centre et de ses agents
        messages = Message.objects.filter(
            Q(expediteur=request.user) | 
            Q(destinataire=request.user) |
            Q(expediteur__parent_centre=request.user.parent_centre) |
            Q(destinataire__parent_centre=request.user.parent_centre)
        )
    else:
        # Messages personnels uniquement
        messages = Message.objects.filter(
            Q(expediteur=request.user) | 
            Q(destinataire=request.user)
        )
    
    # Trier par date décroissante
    messages = messages.order_by('-date_envoi')
    
    # Pagination
    paginator = Paginator(messages, 25)
    page = request.GET.get('page')
    messages = paginator.get_page(page)
    
    return render(request, 'communication/message_list.html', {
        'messages': messages
    })

@login_required
def communication_list(request):
    # Récupérer les messages selon le rôle de l'utilisateur
    if request.user.role == 'admin':
        message_list = Message.objects.all()
        users = User.objects.all()
    elif request.user.role == 'centre':
        # Messages du centre et de ses agents
        message_list = Message.objects.filter(
            Q(expediteur=request.user) | 
            Q(destinataire=request.user) |
            Q(expediteur__parent_centre=request.user.parent_centre) |
            Q(destinataire__parent_centre=request.user.parent_centre)
        )
        users = User.objects.filter(parent_centre=request.user.parent_centre)
    else:
        # Messages personnels uniquement
        message_list = Message.objects.filter(
            Q(expediteur=request.user) | 
            Q(destinataire=request.user)
        )
        users = User.objects.filter(parent_centre=request.user.parent_centre)
    
    # Trier par date décroissante
    message_list = message_list.order_by('-date_envoi')
    
    # Pagination
    paginator = Paginator(message_list, 25)
    page = request.GET.get('page')
    message_list = paginator.get_page(page)
    
    context = {
        'communication_messages': message_list,
        'users': users,
    }
    
    return render(request, 'communication/communication_list.html', context)

@login_required
def message_create(request):
    if request.method == 'POST':
        destinataire = User.objects.get(id=request.POST.get('destinataire'))
        objet = request.POST.get('objet')
        contenu = request.POST.get('contenu')
        
        message = Message.objects.create(
            expediteur=request.user,
            destinataire=destinataire,
            objet=objet,
            contenu=contenu
        )
        
        messages.success(request, "Message envoyé avec succès.")
        return redirect('communication:communication_list')
    
    return redirect('communication:communication_list')

@login_required
def message_view(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    
    # Vérifier que l'utilisateur a le droit de voir ce message
    if request.user not in [message.expediteur, message.destinataire] and \
       not (request.user.role == 'centre' and message.expediteur.parent_centre == request.user.parent_centre) and \
       not (request.user.role == 'admin'):
        messages.error(request, "Vous n'avez pas accès à ce message.")
        return redirect('communication:communication_list')
    
    # Marquer comme lu si l'utilisateur est le destinataire
    if request.user == message.destinataire and not message.lu:
        message.lu = True
        message.date_lecture = timezone.now()
        message.save()
    
    return render(request, 'communication/message_view.html', {
        'message': message
    })

@login_required
def message_reply(request, message_id):
    original_message = get_object_or_404(Message, id=message_id)
    
    # Vérifier que l'utilisateur a le droit de répondre à ce message
    if request.user not in [original_message.expediteur, original_message.destinataire] and \
       not (request.user.role == 'centre' and original_message.expediteur.parent_centre == request.user.parent_centre):
        messages.error(request, "Vous n'avez pas accès à ce message.")
        return redirect('communication:communication_list')
    
    if request.method == 'POST':
        contenu = request.POST.get('contenu')
        if contenu:
            # Créer le message de réponse
            Message.objects.create(
                expediteur=request.user,
                destinataire=original_message.expediteur if request.user != original_message.expediteur else original_message.destinataire,
                objet=f'Re: {original_message.objet}',
                contenu=contenu
            )
            messages.success(request, "Réponse envoyée avec succès.")
            return redirect('communication:communication_list')
    
    return render(request, 'communication/message_reply.html', {
        'original_message': original_message
    })

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'communication/notification_list.html', {
        'notifications': notifications
    })

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    messages.success(request, 'Notification marquée comme lue.')
    return redirect('communication:notifications')

@login_required
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, read=False).update(read=True)
    messages.success(request, 'Toutes les notifications ont été marquées comme lues.')
    return redirect('communication:notifications')
