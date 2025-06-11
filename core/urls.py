from django.urls import path
from . import views

app_name = 'core'
from django.contrib.auth import views as auth_views

app_name = 'core'

urlpatterns = [
    path('dashboard/donneur-ordre/', views.donneur_ordre_dashboard, name='donneur_ordre_dashboard'),
    path('access-denied/', views.access_denied, name='access_denied'),
    # Authentification
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('change-password/', views.change_password, name='change_password'),

    # Dashboard et profil
    path('', views.dashboard, name='dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/centre/', views.centre_dashboard, name='centre_dashboard'),
    path('dashboard/agent/', views.agent_dashboard, name='agent_dashboard'),
    path('profile/', views.profile, name='profile'),
    path('notifications/', views.notifications, name='notifications'),

    # Gestion des missions
    path('missions/', views.missions_list, name='missions_list'),
    path('missions/nouvelle/', views.mission_create, name='mission_create'),
    path('missions/<int:mission_id>/', views.mission_detail, name='mission_detail'),
    path('missions/<int:mission_id>/modifier/', views.mission_update, name='mission_update'),

    # Gestion des feedbacks
    path('feedbacks/<int:feedback_id>/modifier/', views.feedback_update, name='feedback_update'),
    path('feedbacks/<int:feedback_id>/supprimer/', views.feedback_delete, name='feedback_delete'),

    # Gestion des agents
    path('agents/', views.agent_list, name='agent_list'),
    path('agents/nouveau/', views.agent_create, name='agent_create'),
    path('agents/<int:user_id>/', views.agent_detail, name='agent_detail'),
    path('agents/export/csv/', views.agent_export_csv, name='agent_export_csv'),
    path('agents/<int:user_id>/modifier/', views.agent_update, name='agent_update'),
    path('agents/<int:user_id>/supprimer/', views.agent_delete, name='agent_delete'),

    # Gestion des centres d'appels
    path('centres/<int:centre_id>/', views.centre_detail, name='centre_detail'),

    # Paramètres
    path('settings/', views.settings, name='settings'),
]
