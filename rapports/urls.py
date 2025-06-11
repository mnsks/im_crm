from django.urls import path
from . import views

app_name = 'rapports'

urlpatterns = [
    path('', views.rapports_list, name='rapports_list'),
    path('daily/', views.daily_report, name='daily_report'),
    path('saisie/<int:mission_id>/', views.saisie_resultats, name='saisie_resultats'),
    path('pdf/<int:rapport_id>/', views.generer_rapport_pdf, name='generer_pdf'),
]
