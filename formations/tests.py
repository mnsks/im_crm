from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import CentreAppels, EntrepriseDonneuseOrdre
from missions.models import Mission
from .models import Formation, Participation

class FormationsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Créer une entreprise donneuse d'ordre
        self.entreprise = EntrepriseDonneuseOrdre.objects.create(
            nom='Entreprise Test',
            description='Description test'
        )
        # Créer un centre d'appels
        self.centre = CentreAppels.objects.create(
            nom='Centre Test',
            entreprise=self.entreprise
        )
        # Créer un utilisateur admin
        User = get_user_model()
        self.admin = User.objects.create_user(
            username='admin@test.com',
            email='admin@test.com',
            password='testpass123',
            role='admin'
        )
        # Créer un utilisateur agent
        self.agent = User.objects.create_user(
            username='agent@test.com',
            email='agent@test.com',
            password='testpass123',
            role='agent'
        )
        # Lier l'agent au centre
        self.agent.parent_centre = self.centre
        self.agent.save()
        # Créer une mission
        self.mission = Mission.objects.create(
            titre='Mission Test',
            description='Description test',
            type='commercial',
            status='en_cours',
            objectifs='Objectifs test',
            entreprise=self.entreprise,
            centre=self.centre,
            date_debut='2025-07-01'
        )
        # Créer une formation
        self.formation = Formation.objects.create(
            titre='Formation Test',
            description='Description test',
            date='2025-07-01',
            duree=8,
            centre=self.centre
        )
        self.formation.missions.add(self.mission)

    def test_formations_list_view(self):
        """Test de la vue liste des formations"""
        # Connecter l'agent
        self.client.login(username='agent@test.com', password='testpass123')
        # Accéder à la liste des formations
        response = self.client.get(reverse('formations:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'formations/formations_list.html')
        self.assertContains(response, 'Formation Test')

    def test_formation_create_view(self):
        """Test de la vue création de formation"""
        # Connecter l'admin
        self.client.login(username='admin@test.com', password='testpass123')
        # Tester l'accès à la page
        response = self.client.get(reverse('formations:formation_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'formations/formation_form.html')
        # Tester la création d'une formation
        data = {
            'titre': 'Nouvelle Formation',
            'description': 'Description nouvelle formation',
            'date': '2025-08-01',
            'duree': 4,
            'centre': self.centre.id,
            'missions': [self.mission.id]
        }
        response = self.client.post(reverse('formations:formation_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirection après succès
        self.assertTrue(Formation.objects.filter(titre='Nouvelle Formation').exists())

    def test_inscription_formation_view(self):
        """Test de la vue inscription à une formation"""
        # Connecter l'agent
        self.client.login(username='agent@test.com', password='testpass123')
        # Tester l'accès à la page
        url = reverse('formations:inscription_formation', args=[self.formation.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'formations/inscription_formation.html')
        # Tester l'inscription
        data = {
            'commentaire': 'Test inscription'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirection après succès
        self.assertTrue(
            Participation.objects.filter(
                formation=self.formation,
                agent=self.agent
            ).exists()
        )

    def test_inscriptions_list_view(self):
        """Test de la vue liste des inscriptions"""
        # Créer une participation
        Participation.objects.create(
            formation=self.formation,
            agent=self.agent,
            commentaire='Test participation'
        )
        # Connecter l'admin
        self.client.login(username='admin@test.com', password='testpass123')
        # Tester l'accès à la page
        response = self.client.get(reverse('formations:inscriptions_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'formations/inscriptions_list.html')
        self.assertContains(response, 'Test participation')

    def test_mission_assign_view(self):
        """Test de la vue assignation d'agents à une mission"""
        # Créer une participation validée
        participation = Participation.objects.create(
            formation=self.formation,
            agent=self.agent,
            commentaire='Test participation',
            statut='validee'
        )
        # Connecter l'admin
        self.client.login(username='admin@test.com', password='testpass123')
        # Tester l'accès à la page
        url = reverse('formations:mission_assign', args=[self.mission.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'formations/mission_assign.html')
        # Tester l'assignation
        data = {
            'agents': [self.agent.id]
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirection après succès
        self.mission.refresh_from_db()
        self.assertIn(self.agent, self.mission.agents.all())
