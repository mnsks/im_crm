from django.urls import path
from . import views

app_name = 'missions'

urlpatterns = [
    path('', views.missions_list, name='mission_list'),
    path('nouvelle/', views.mission_create, name='mission_create'),
    path('<int:pk>/', views.mission_detail, name='mission_detail'),
    path('<int:pk>/modifier/', views.mission_update, name='mission_update'),
    path('<int:pk>/supprimer/', views.mission_delete, name='mission_delete'),
]
