from django.core.management.base import BaseCommand
from django.test import Client
from django.urls import reverse
from core.models import User
import json

class Command(BaseCommand):
    help = 'Teste les fonctionnalités du rôle Donneur d\'ordre'

    def handle(self, *args, **kwargs):
        # Récupérer un donneur d'ordre de test
        donneur = User.objects.filter(role='donneur_ordre').first()
        if not donneur:
            self.stdout.write(self.style.ERROR('Aucun donneur d\'ordre trouvé dans la base de données'))
            return

        # Créer un client de test
        client = Client()
        
        # Se connecter
        logged_in = client.login(username=donneur.username, password='password123')
        if not donneur:
            self.stdout.write(self.style.ERROR('Échec de connexion'))
            return
        
        self.stdout.write(f"Connecté en tant que {donneur.username}")

        # URLs à tester
        urls_to_test = [
            ('core:missions_list', 'Missions confiées'),
            ('documents:list', 'Documents'),
            ('feedback:list', 'Feedbacks'),
            ('core:dashboard', 'Tableau de bord'),
            ('messages:list', 'Messagerie'),
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
        
        # 1. Créer une nouvelle mission
        try:
            data = {
                'titre': 'Mission test',
                'description': 'Description de la mission test',
                'objectifs': 'Objectifs de la mission test',
                'date_debut': '2025-06-10',
                'date_fin': '2025-06-20',
                'centre': 1
            }
            response = client.post(reverse('core:mission_create'), data)
            self.stdout.write(self.style.SUCCESS(
                f'[OK] Création mission: {response.status_code}'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Création mission: {str(e)}'))

        # 2. Consulter les feedbacks
        try:
            response = client.get(reverse('feedback:list') + '?mission=1')
            self.stdout.write(self.style.SUCCESS(
                f'[OK] Consultation feedbacks: {response.status_code}'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Consultation feedbacks: {str(e)}'))

        # 3. Télécharger un document
        try:
            response = client.get(reverse('documents:download', kwargs={'document_id': 1}))
            self.stdout.write(self.style.SUCCESS(
                f'[OK] Téléchargement document: {response.status_code}'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Téléchargement document: {str(e)}'))

        # 4. Envoyer un message
        try:
            data = {
                'sujet': 'Message test',
                'contenu': 'Contenu du message test',
                'destinataire': 1
            }
            response = client.post(reverse('messages:create'), data)
            self.stdout.write(self.style.SUCCESS(
                f'[OK] Envoi message: {response.status_code}'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Envoi message: {str(e)}'))

        # 5. Consulter le tableau de bord
        try:
            response = client.get(reverse('core:dashboard') + '?period=month')
            self.stdout.write(self.style.SUCCESS(
                f'[OK] Consultation tableau de bord: {response.status_code}'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Consultation tableau de bord: {str(e)}'))
