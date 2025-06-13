from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.documents_list, name='document_list'),
    path('create/', views.document_create, name='document_create'),
    path('<int:document_id>/edit/', views.document_edit, name='document_edit'),
    path('<int:document_id>/delete/', views.document_delete, name='document_delete'),
]
