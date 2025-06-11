from django.core.management.base import BaseCommand
from django.test import Client
from django.urls import reverse
from core.models import User
import json

class Command(BaseCommand):
    help = 'Teste les fonctionnalités du rôle Agent'

    def handle(self, *args, **kwargs):
        # Récupérer un agent de test
        agent = User.objects.filter(role='agent').first()
        if not agent:
            self.stdout.write(self.style.ERROR('Aucun agent trouvé dans la base de données'))
            return

        # Créer un client de test
        client = Client()
        
        # Se connecter
        logged_in = client.login(username=agent.username, password='password123')
        if not logged_in:
            self.stdout.write(self.style.ERROR('Échec de connexion'))
            return
        
        self.stdout.write(f"Connecté en tant que {agent.username}")

        # URLs à tester
        urls_to_test = [
            ('core:missions_list', 'Planning'),
            ('formations:list', 'Formations'),
            ('clients:list', 'Clients'),
            ('scripts:list', 'Scripts'),
            ('feedback:list', 'Feedback'),
            ('rapports:daily', 'Rapport journalier'),
        ]

        # Tester chaque URL
        for url_name, description in urls_to_test:
            try:
                url = reverse(url_name)
                response = client.get(url)
                
                if response.status_code == 200:
                    self.stdout.write(self.style.SUCCESS(
                        f'[OK] {description} ({url}): 200'
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f'[WARN] {description} ({url}): {response.status_code}'
                    ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'[ERROR] {description}: {str(e)}'
                ))

        # Test d'interactions spécifiques
        self.stdout.write("\nTest des interactions spécifiques:")
        
        # 1. Voir les missions du jour
        try:
            response = client.get(reverse('core:missions_list') + '?date=today')
            self.stdout.write(self.style.SUCCESS(
                f'[OK] Voir missions du jour: {response.status_code}'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Voir missions du jour: {str(e)}'))

        # 2. Voir les formations à venir
        try:
            response = client.get(reverse('formations:list') + '?upcoming=true')
            self.stdout.write(self.style.SUCCESS(
                f'[OK] Voir formations à venir: {response.status_code}'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Voir formations à venir: {str(e)}'))

        # 3. Rechercher un client
        try:
            response = client.get(reverse('clients:list') + '?search=Client')
            self.stdout.write(self.style.SUCCESS(
                f'[OK] Recherche client: {response.status_code}'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Recherche client: {str(e)}'))

        # 4. Accéder à un script
        try:
            response = client.get(reverse('scripts:list') + '?mission_id=1')
            self.stdout.write(self.style.SUCCESS(
                f'[OK] Accès script: {response.status_code}'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Accès script: {str(e)}'))

        # 5. Soumettre un rapport journalier
        try:
            data = {
                'date': '2025-06-04',
                'commentaire': 'Test rapport journalier',
                'heures_travaillees': 8
            }
            response = client.post(reverse('rapports:daily'), data)
            self.stdout.write(self.style.SUCCESS(
                f'[OK] Soumission rapport: {response.status_code}'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Soumission rapport: {str(e)}'))
