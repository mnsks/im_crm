from django.test import TestCase, Client
from django.urls import reverse
from core.models import User, CentreAppels, EntrepriseDonneuseOrdre
from django.contrib.messages import get_messages

class AgentsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Créer une entreprise et un centre d'appels
        self.entreprise = EntrepriseDonneuseOrdre.objects.create(
            nom='Test Enterprise'
        )
        self.centre = CentreAppels.objects.create(
            nom='Test Centre',
            entreprise=self.entreprise
        )
        
        # Créer un utilisateur admin
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role='admin'
        )
        
        # Créer un agent de test
        self.agent = User.objects.create_user(
            username='agent1',
            email='agent1@test.com',
            password='testpass123',
            role='agent',
            parent_centre=self.centre
        )
        
        # Connecter l'admin
        self.client.login(username='admin', password='testpass123')
    
    def test_agent_list_view(self):
        response = self.client.get(reverse('agents:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'agents/agent_list.html')
        self.assertContains(response, self.agent.username)
    
    def test_agent_detail_view(self):
        response = self.client.get(reverse('agents:detail', kwargs={'pk': self.agent.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'agents/agent_detail.html')
        self.assertContains(response, self.agent.email)
    
    def test_agent_create_view(self):
        response = self.client.post(reverse('agents:create'), {
            'username': 'newagent',
            'email': 'newagent@test.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'parent_centre': self.centre.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newagent').exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Agent créé avec succès.')
    
    def test_agent_edit_view(self):
        response = self.client.post(
            reverse('agents:edit', kwargs={'pk': self.agent.pk}),
            {
                'username': self.agent.username,
                'email': 'updated@test.com',
                'parent_centre': self.centre.id
            }
        )
        self.assertEqual(response.status_code, 302)
        self.agent.refresh_from_db()
        self.assertEqual(self.agent.email, 'updated@test.com')
    
    def test_agent_delete_view(self):
        response = self.client.post(reverse('agents:delete', kwargs={'pk': self.agent.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(pk=self.agent.pk).exists())
    
    def test_non_admin_access(self):
        # Déconnecter l'admin
        self.client.logout()
        
        # Connecter un agent normal
        self.client.login(username='agent1', password='testpass123')
        
        # Tester l'accès aux vues
        urls = [
            reverse('agents:list'),
            reverse('agents:create'),
            reverse('agents:detail', kwargs={'pk': self.agent.pk}),
            reverse('agents:edit', kwargs={'pk': self.agent.pk}),
            reverse('agents:delete', kwargs={'pk': self.agent.pk})
        ]
        
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)  # Redirection vers login
