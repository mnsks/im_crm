from django.urls import path
from . import views

app_name = 'clients_finaux'

urlpatterns = [
    # Historique des appels
    path('historique/', views.historique_appels, name='historique'),
    path('historique/<int:appel_id>/', views.detail_appel, name='detail_appel'),
    
    # Requêtes
    path('requetes/', views.liste_requetes, name='requetes'),
    path('requetes/nouvelle/', views.nouvelle_requete, name='nouvelle_requete'),
    path('requetes/<int:requete_id>/', views.detail_requete, name='detail_requete'),
    path('requetes/<int:requete_id>/modifier/', views.modifier_requete, name='modifier_requete'),
    
    # Documents
    path('documents/', views.liste_documents, name='documents'),
    path('documents/<int:document_id>/', views.detail_document, name='detail_document'),
    
    # Préférences
    path('preferences/', views.preferences_contact, name='preferences'),
    path('preferences/modifier/', views.modifier_preferences, name='modifier_preferences'),
    
    # Feedback
    path('feedback/', views.liste_feedback, name='feedback'),
    path('feedback/nouveau/', views.nouveau_feedback, name='nouveau_feedback'),
]
