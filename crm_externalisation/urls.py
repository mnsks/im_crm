"""
URL configuration for crm_externalisation project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import guide_utilisateur

urlpatterns = [
    # URLs de l'application AI Tools
    path('ai/', include('ai_tools.urls', namespace='ai_tools')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('guide/', guide_utilisateur, name='guide_utilisateur'),
    path('', include('core.urls', namespace='core')),
    path('kpis/', include('kpis.urls', namespace='kpis')),
    path('missions/', include('missions.urls', namespace='missions')),
    path('formations/', include('formations.urls', namespace='formations')),
    path('agents/', include('agents.urls', namespace='agents')),
    path('documents/', include('documents.urls', namespace='documents')),
    path('clients/', include('clients.urls', namespace='clients')),
    path('scripts/', include('scripts.urls', namespace='scripts')),
    path('feedback/', include('feedback.urls', namespace='feedback')),
    path('saisie/', include('saisie.urls', namespace='saisie')),
    path('rapports/', include('rapports.urls', namespace='rapports')),
    path('communication/', include('communication.urls', namespace='communication')),
    path('client/', include('clients_finaux.urls')),  # URLs pour le client final
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) if settings.DEBUG else []
