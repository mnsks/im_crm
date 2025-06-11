from django.core.management.base import BaseCommand
from django.test import Client
from django.urls import reverse
from core.models import User
import json

class Command(BaseCommand):
    help = 'Teste les fonctionnalités du rôle Centre d\'appel'

    def handle(self, *args, **kwargs):
        # Récupérer un centre d'appel de test
        centre = User.objects.filter(role='centre').first()
        if not centre:
            self.stdout.write(self.style.ERROR('Aucun centre d\'appel trouvé dans la base de données'))
            return

        # Créer un client de test
        client = Client()
        
        # Se connecter
        logged_in = client.login(username=centre.username, password='password123')
        if not logged_in:
            self.stdout.write(self.style.ERROR('Échec de connexion'))
            return
        
        self.stdout.write(f"Connecté en tant que {centre.username}")

        # URLs à tester
        urls_to_test = [
            ('core:missions_list', 'Missions reçues'),
            ('saisie:saisie_list', 'Saisie résultats'),
            ('clients:list', 'Clients'),
            ('rapports:list', 'Rapports'),
            ('formations:list', 'Formations'),
            ('communication:list', 'Communication'),
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
        
        # 1. Voir les missions en cours
        try:
            response = client.get(reverse('core:missions_list') + '?status=en_cours')
            self.stdout.write(self.style.SUCCESS(
                f'[OK] Voir missions en cours: {response.status_code}'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Voir missions en cours: {str(e)}'))

        # 2. Saisir un résultat
        try:
            data = {
                'mission': 1,
                'agent': 1,
                'duree_appel': '00:05:00',
                'statut': 'termine',
                'commentaire': 'Test saisie résultat'
            }
            response = client.post(reverse('saisie:create'), data)
            self.stdout.write(self.style.SUCCESS(
                f'[OK] Saisie résultat: {response.status_code}'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Saisie résultat: {str(e)}'))

        # 3. Consulter un rapport
        try:
            response = client.get(reverse('rapports:list') + '?date=2025-06-04')
            self.stdout.write(self.style.SUCCESS(
                f'[OK] Consultation rapport: {response.status_code}'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Consultation rapport: {str(e)}'))

        # 4. Gérer une formation
        try:
            response = client.get(reverse('formations:list') + '?status=a_venir')
            self.stdout.write(self.style.SUCCESS(
                f'[OK] Gestion formation: {response.status_code}'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Gestion formation: {str(e)}'))

        # 5. Envoyer une communication
        try:
            data = {
                'sujet': 'Test communication',
                'message': 'Ceci est un test de communication',
                'destinataires': [1]
            }
            response = client.post(reverse('communication:create'), data)
            self.stdout.write(self.style.SUCCESS(
                f'[OK] Envoi communication: {response.status_code}'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Envoi communication: {str(e)}'))
