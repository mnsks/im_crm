from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.documents_list, name='document_list'),
    path('create/', views.document_create, name='document_create'),
]
