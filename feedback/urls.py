from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    path('', views.feedback_list, name='feedback_list'),
    path('nouveau/', views.feedback_create, name='feedback_create'),
    path('<int:pk>/', views.feedback_detail, name='feedback_detail'),
    path('agent/<int:agent_id>/', views.agent_feedback_list, name='agent_feedback_list'),
    path('mission/<int:mission_id>/', views.mission_feedback_list, name='mission_feedback_list'),
]
