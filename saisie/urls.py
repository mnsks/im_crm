from django.urls import path
from . import views

app_name = 'saisie'

urlpatterns = [
    path('', views.saisie_list, name='saisie_list'),
    path('nouvelle/', views.saisie_create, name='saisie_create'),
    path('<int:pk>/', views.saisie_detail, name='saisie_detail'),
    path('<int:pk>/modifier/', views.saisie_update, name='saisie_update'),
    path('mission/<int:mission_id>/', views.mission_saisies, name='mission_saisies'),
    path('agent/<int:agent_id>/', views.agent_saisies, name='agent_saisies'),
]
