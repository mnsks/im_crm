from django.urls import path
from . import views

app_name = 'kpis'

urlpatterns = [
    path('', views.kpis_list, name='list'),
    path('export/', views.kpis_export, name='export'),
]
