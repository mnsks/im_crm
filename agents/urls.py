from django.urls import path
from . import views

app_name = 'agents'

urlpatterns = [
    path('', views.agent_list, name='agent_list'),
    path('create/', views.agent_create, name='create'),
    path('<int:pk>/', views.agent_detail, name='detail'),
    path('<int:pk>/edit/', views.agent_edit, name='edit'),
    path('<int:pk>/delete/', views.agent_delete, name='delete'),
]
