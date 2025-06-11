import os
from celery import Celery
from celery.schedules import crontab

# Définir les variables d'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_externalisation.settings')

# Créer l'instance Celery
app = Celery('crm_externalisation')

# Configuration depuis Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Chargement automatique des tâches depuis les applications
app.autodiscover_tasks()

# Configuration des tâches périodiques
app.conf.beat_schedule = {
    'analyse-sentiments-quotidienne': {
        'task': 'ai_tools.tasks.analyser_sentiments_periodique',
        'schedule': crontab(hour='*/1'),  # Toutes les heures
    },
    'prediction-performances-quotidienne': {
        'task': 'ai_tools.tasks.predire_performances_agents',
        'schedule': crontab(hour='0', minute='0'),  # Une fois par jour à minuit
    },
    'recommandations-formations-hebdo': {
        'task': 'ai_tools.tasks.mettre_a_jour_recommandations',
        'schedule': crontab(day_of_week='1', hour='1', minute='0'),  # Lundi à 1h du matin
    },
    'optimisation-planning-hebdo': {
        'task': 'ai_tools.tasks.optimiser_planning_hebdomadaire',
        'schedule': crontab(day_of_week='6', hour='2', minute='0'),  # Samedi à 2h du matin
    },
}
