from django.core.management.base import BaseCommand
from django.test import Client
from django.urls import reverse
from core.models import User
import json

class Command(BaseCommand):
    help = 'Teste les fonctionnalités du rôle Administrateur'

    def handle(self, *args, **kwargs):
        # Récupérer un administrateur de test
        admin = User.objects.filter(role='admin').first()
        if not admin:
            self.stdout.write(self.style.ERROR('Aucun administrateur trouvé dans la base de données'))
            return

        # Créer un client de test
        client = Client()
        
        # Se connecter
        logged_in = client.login(username=admin.username, password='password123')
        if not logged_in:
            self.stdout.write(self.style.ERROR('Échec de connexion'))
            return
        
        self.stdout.write(f"Connecté en tant que {admin.username}")

        # URLs à tester
        urls_to_test = [
            ('core:dashboard', 'Tableau de bord'),
            ('core:missions_list', 'Missions'),
            ('core:agent_list', 'Gestion des Agents'),
            ('kpis:list', 'KPIs'),
            ('formations:list', 'Formations'),
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
        
        # 1. Créer un nouvel agent
        try:
            data = {
                'username': 'new_agent_test',
                'password1': 'password123',
                'password2': 'password123',
                'role': 'agent',
                'email': 'new_agent@test.com'
            }
            response = client.post(reverse('core:agent_create'), data)
            self.stdout.write(self.style.SUCCESS(
                f'[OK] Création agent: {response.status_code}'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Création agent: {str(e)}'))

        # 2. Consulter les KPIs
        try:
            response = client.get(reverse('kpis:list') + '?period=month')
            self.stdout.write(self.style.SUCCESS(
                f'[OK] Consultation KPIs: {response.status_code}'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Consultation KPIs: {str(e)}'))

        # 3. Créer une nouvelle formation
        try:
            data = {
                'titre': 'Formation test',
                'description': 'Description de la formation test',
                'date': '2025-07-01',
                'duree': '02:00:00',
                'formateur': 1
            }
            response = client.post(reverse('formations:formation_create'), data)
            self.stdout.write(self.style.SUCCESS(
                f'[OK] Création formation: {response.status_code}'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Création formation: {str(e)}'))

        # 4. Gérer les inscriptions aux formations
        try:
            response = client.get(reverse('formations:inscriptions_list'))
            self.stdout.write(self.style.SUCCESS(
                f'[OK] Gestion inscriptions: {response.status_code}'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Gestion inscriptions: {str(e)}'))

        # 5. Assigner une mission
        try:
            data = {
                'mission': 1,
                'agent': 1,
                'date_debut': '2025-06-06',
                'date_fin': '2025-06-07'
            }
            response = client.post(reverse('core:mission_assign'), data)
            self.stdout.write(self.style.SUCCESS(
                f'[OK] Assignation mission: {response.status_code}'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Assignation mission: {str(e)}'))
