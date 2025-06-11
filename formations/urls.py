from django.urls import path
from . import views

app_name = 'formations'

urlpatterns = [
    path('', views.formations_list, name='formation_list'),
    path('create/', views.formation_create, name='formation_create'),
    path('inscription/<int:formation_id>/', views.inscription_formation, name='inscription_formation'),
    path('inscriptions/', views.inscriptions_list, name='inscriptions_list'),
    path('mission/<int:mission_id>/assign/', views.mission_assign, name='mission_assign'),
]
