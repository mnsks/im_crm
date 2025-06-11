from django.urls import path
from . import views

app_name = 'kpis'

urlpatterns = [
    path('export/csv/', views.kpi_export_csv, name='kpi_export_csv'),
    path('', views.kpi_list, name='kpi_list'),
    path('nouveau/', views.kpi_create, name='kpi_create'),
    path('<int:kpi_id>/modifier/', views.kpi_update, name='kpi_update'),
    path('<int:kpi_id>/supprimer/', views.kpi_delete, name='kpi_delete'),
]
