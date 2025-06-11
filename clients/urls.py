from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    path('', views.clients_list, name='client_list'),
    path('ajouter/', views.client_create, name='client_create'),
    path('<int:pk>/', views.client_detail, name='client_detail'),
    path('<int:pk>/modifier/', views.client_update, name='client_update'),
]
