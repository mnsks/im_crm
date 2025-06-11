from django.urls import path
from . import views

app_name = 'scripts'

urlpatterns = [
    path('', views.scripts_list, name='script_list'),
    path('nouveau/', views.script_create, name='script_create'),
    path('<int:pk>/', views.script_detail, name='script_detail'),
    path('<int:pk>/modifier/', views.script_update, name='script_update'),
    path('<int:pk>/version/', views.script_new_version, name='script_new_version'),
]
