import os
import random
import datetime
import json
from datetime import timedelta
import numpy as np
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import CentreAppels, EntrepriseDonneuseOrdre
from agents.models import Agent
from missions.models import Mission, KPI, Ressource
from formations.models import Formation, Quiz, Participation
from interactions.models import Interaction
from core.models import ClientFinal
from django.db import transaction
from django.db.models import Count, Sum, Avg, F, Q
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth

User = get_user_model()

class Command(BaseCommand):
    help = 'Génère des données de test pour le rôle Agent'

    def handle(self, *args, **options):
        self.stdout.write("Début de la génération des données de test pour les agents...")
        
        # Vérifier et supprimer les données existantes
        if User.objects.filter(role='agent').exists():
            self.stdout.write(self.style.WARNING("Suppression des anciennes données d'agent..."))
            User.objects.filter(role='agent').delete()
            self.stdout.write(self.style.SUCCESS("Anciennes données d'agent supprimées avec succès."))
        
        # Créer un centre d'appels si nécessaire
        centre = CentreAppels.objects.first()
        if not centre:
            entreprise = EntrepriseDonneuseOrdre.objects.first()
            if not entreprise:
                entreprise = EntrepriseDonneuseOrdre.objects.create(
                    nom="Entreprise Test",
                    siret="12345678901234",
                    adresse="123 Rue Test, 75000 Paris",
                    email_contact="contact@test.com"
                )
            
            centre = CentreAppels.objects.create(
                nom="Centre d'appels principal",
                entreprise=entreprise,
                adresse="456 Avenue Test, 75000 Paris",
                email_contact="centre@test.com"
            )
        
        # Liste des prénoms et noms pour générer des utilisateurs réalistes
        prenoms = ["Jean", "Marie", "Pierre", "Sophie", "Thomas", "Julie", "Nicolas", "Camille", "Alexandre", "Laura"]
        noms = ["Dupont", "Martin", "Bernard", "Petit", "Durand", "Leroy", "Moreau", "Simon", "Laurent", "Michel"]
        
        # Créer 10 agents
        for i in range(1, 11):
            prenom = random.choice(prenoms)
            nom = random.choice(noms)
            # Ajouter un identifiant unique pour éviter les doublons
            username = f"{prenom.lower()}.{nom.lower()}{i}"
            email = f"{username}@test.com"
            
            # Créer l'utilisateur avec le modèle personnalisé
            user = User.objects.create_user(
                username=username,
                email=email,
                password="password123",
                first_name=prenom,
                last_name=nom,
                role='agent'
            )
            
            # Créer le profil agent
            date_embauche = timezone.now().date() - datetime.timedelta(days=random.randint(30, 1000))
            specialites = random.sample(["commercial", "support", "sav", "technique", "relation client"], k=random.randint(1, 3))
            
            Agent.objects.create(
                user=user,
                centre_appel=centre,
                niveau_competence=random.randint(1, 5),
                disponible=random.choice([True, False]),
                date_embauche=date_embauche,
                specialites=specialites
            )
            
            self.stdout.write(self.style.SUCCESS(f'Agent créé : {prenom} {nom}'))
        
        # Définir les attributs de classe pour les types d'interaction et les résultats
        self.types_interaction = [
            'appel_entrant', 'appel_sortant', 'email', 'chat', 'sms', 'autre'
        ]
        
        self.resultats = [
            "Client satisfait", "Rendez-vous pris", "Devis envoyé",
            "Rappel programmé", "Problème résolu", "Transféré au service technique",
            "Commande passée", "Information fournie", "Réclamation enregistrée"
        ]
        
        # Créer des KPIs plus détaillés
        kpis = [
            {"nom": "Temps moyen d'appel", "type": "temporel", "unite": "secondes", "valeur_cible": 180, "description": "Durée moyenne des appels réussis"},
            {"nom": "Taux de conversion", "type": "quantitatif", "unite": "%", "valeur_cible": 15, "description": "Pourcentage d'appels transformés en vente"},
            {"nom": "Satisfaction client", "type": "qualitatif", "unite": "/5", "valeur_cible": 4.5, "description": "Note moyenne de satisfaction client"},
            {"nom": "Nombre d'appels par jour", "type": "quantitatif", "unite": "appels", "valeur_cible": 50, "description": "Nombre moyen d'appels par jour ouvré"},
            {"nom": "Taux de résolution", "type": "quantitatif", "unite": "%", "valeur_cible": 85, "description": "Pourcentage de problèmes résolus au premier appel"},
            {"nom": "Temps d'attente moyen", "type": "temporel", "unite": "secondes", "valeur_cible": 30, "description": "Temps d'attente moyen avant prise d'appel"},
            {"nom": "Taux d'abandon", "type": "quantitatif", "unite": "%", "valeur_cible": 5, "description": "Pourcentage d'appels abandonnés avant réponse"},
            {"nom": "Taux de rappel", "type": "quantitatif", "unite": "%", "valeur_cible": 10, "description": "Pourcentage d'appels nécessitant un rappel"},
        ]
        
        kpi_objects = []
        for kpi_data in kpis:
            kpi = KPI.objects.create(
                nom=kpi_data["nom"],
                type=kpi_data["type"],
                unite=kpi_data["unite"],
                valeur_cible=kpi_data["valeur_cible"],
                description=f"Description du KPI {kpi_data['nom']}"
            )
            kpi_objects.append(kpi)
            self.stdout.write(self.style.SUCCESS(f'KPI créé : {kpi.nom}'))
        
        # Créer des missions plus variées
        missions_data = [
            {"titre": "Campagne commerciale été 2023", "type": "commercial", "status": "terminee", "description": "Promotion des produits phares de l'été"},
            {"titre": "Support technique produits électroniques", "type": "support", "status": "en_cours", "description": "Assistance technique pour la gamme électronique"},
            {"titre": "Enquête satisfaction client", "type": "information", "status": "en_attente", "description": "Évaluation de la satisfaction client post-achat"},
            {"titre": "Promotion produits hivernaux", "type": "commercial", "status": "en_cours", "description": "Mise en avant des produits pour l'hiver"},
            {"titre": "Fidélisation clientèle", "type": "commercial", "status": "en_cours", "description": "Programme de fidélisation des clients existants"},
            {"titre": "Enquête NPS", "type": "information", "status": "en_cours", "description": "Mesure du Net Promoter Score"},
            {"titre": "Formation nouveaux produits", "type": "formation", "status": "terminee", "description": "Formation sur la nouvelle gamme de produits"},
            {"titre": "Sondage tendances 2023", "type": "information", "status": "en_attente", "description": "Étude des tendances consommateur"},
        ]
        
        missions = []
        for i, mission_data in enumerate(missions_data):
            date_debut = timezone.now().date() - datetime.timedelta(days=30 - (i * 7))
            date_fin = date_debut + datetime.timedelta(days=14 + (i * 7))
            
            mission = Mission.objects.create(
                titre=mission_data["titre"],
                description=mission_data.get("description", f"Description détaillée de la mission '{mission_data['titre']}'"),
                type=mission_data["type"],
                status=mission_data["status"],
                objectifs=f"Objectifs de la mission '{mission_data['titre']}':\n- Atteindre un taux de satisfaction de 90%\n- Réaliser au moins 100 contacts\n- Maintenir un taux de conversion de 15%",
                entreprise=EntrepriseDonneuseOrdre.objects.first(),
                centre=centre,
                date_debut=date_debut,
                date_fin=date_fin if mission_data["status"] != "en_attente" else None
            )
            
            # Associer des KPIs à la mission
            mission.kpis.set(random.sample(kpi_objects, k=random.randint(1, 3)))
            
            # Créer des ressources pour la mission
            for j in range(random.randint(1, 3)):
                Ressource.objects.create(
                    mission=mission,
                    nom=f"Ressource {j+1} pour {mission.titre[:20]}",
                    type=random.choice(["document", "présentation", "script"]),
                    description=f"Description de la ressource {j+1} pour la mission {mission.titre}"
                )
            
            missions.append(mission)
            self.stdout.write(self.style.SUCCESS(f'Mission créée : {mission.titre}'))
        
        # Créer des formations plus variées
        formations_data = [
            {"titre": "Techniques de vente avancées", "type": "technique", "duree": 8, "description": "Maîtrise des techniques de vente complexes et gestion des objections"},
            {"titre": "Gestion des réclamations clients", "type": "soft_skills", "duree": 4, "description": "Apprendre à gérer efficacement les réclamations et à transformer les mécontents en ambassadeurs"},
            {"titre": "Nouveaux produits 2023", "type": "produit", "duree": 6, "description": "Présentation complète de la nouvelle gamme de produits et de leurs avantages concurrentiels"},
            {"titre": "Réglementation RGPD", "type": "reglementaire", "duree": 3, "description": "Mise à jour sur les obligations légales en matière de protection des données"},
            {"titre": "Communication efficace au téléphone", "type": "soft_skills", "duree": 4, "description": "Techniques pour une communication claire et efficace par téléphone"},
            {"titre": "Outils CRM avancés", "type": "technique", "duree": 6, "description": "Maîtrise des fonctionnalités avancées du CRM"},
            {"titre": "Gestion du stress et des émotions", "type": "soft_skills", "duree": 4, "description": "Techniques pour gérer le stress et les émotions en situation difficile"},
            {"titre": "Techniques de négociation", "type": "technique", "duree": 8, "description": "Apprendre les techniques de négociation gagnant-gagnant"},
        ]
        
        formations = []
        for formation_data in formations_data:
            formation = Formation.objects.create(
                titre=formation_data["titre"],
                centre=centre,
                date=timezone.now().date() - datetime.timedelta(days=random.randint(1, 60)),
                duree=formation_data["duree"],
                description=formation_data.get("description", f"Description de la formation {formation_data['titre']}"),
                type=formation_data["type"]
            )
            
            # Créer des quiz pour la formation
            for q in range(1, 6):
                Quiz.objects.create(
                    formation=formation,
                    question=f"Question {q} sur {formation.titre}",
                    reponse=f"Réponse à la question {q}"
                )
            
            formations.append(formation)
            self.stdout.write(self.style.SUCCESS(f'Formation créée : {formation.titre}'))
        
        # Créer des participations aux formations pour les agents
        agents = User.objects.filter(role='agent')
        for agent in agents:
            # Sélectionner 1 à 3 formations auxquelles l'agent participe
            formations_agent = random.sample(formations, k=random.randint(1, 3))
            
            for formation in formations_agent:
                statut = random.choices(
                    ['en_attente', 'validee', 'refusee'],
                    weights=[0.2, 0.7, 0.1],
                    k=1
                )[0]
                
                participation = Participation.objects.create(
                    formation=formation,
                    agent=agent,
                    statut=statut,
                    score=random.uniform(0, 20) if statut == 'validee' else None,
                    satisfaction=random.uniform(0, 1) if statut == 'validee' else None,
                    commentaire="Formation très utile" if statut == 'validee' else ""
                )
                
                self.stdout.write(self.style.SUCCESS(
                    f'Participation créée : {agent.first_name} {agent.last_name} - {formation.titre} ({statut})'
                ))
        
        # Assigner des agents aux missions de manière plus réaliste
        for mission in missions:
            # Entre 2 et 8 agents par mission, avec plus d'agents pour les missions en cours
            nb_agents = random.randint(2, 4) if mission.status != 'en_cours' else random.randint(3, 8)
            agents_mission = random.sample(list(agents), k=min(nb_agents, len(agents)))
            mission.agents.set(agents_mission)
            mission.save()
            
            # Générer des interactions pour cette mission
            self.generer_interactions_pour_mission(mission, agents_mission)
            
            self.stdout.write(self.style.SUCCESS(
                f'Agents assignés à la mission {mission.titre} : {len(agents_mission)} agents'
            ))
    
    def generer_interactions_pour_mission(self, mission, agents):
        """Génère des données d'interaction réalistes pour une mission et des agents donnés"""
        # Créer quelques clients pour les interactions
        clients = []
        for i in range(1, 21):  # 20 clients par mission
            client = ClientFinal.objects.create(
                nom=f"Client {i} {mission.titre[:10]}",
                email=f"client{i}@example.com",
                telephone=f"06{random.randint(10000000, 99999999)}",
                entreprise=mission.entreprise
            )
            clients.append(client)
        
        # Générer entre 50 et 200 interactions par mission
        nb_interactions = random.randint(50, 200)
        
        # Répartir les interactions sur les 30 derniers jours
        aujourd_hui = timezone.now()
        
        # Générer des interactions
        for _ in range(nb_interactions):
            agent = random.choice(agents)
            client = random.choice(clients)
            type_interaction = random.choice(self.types_interaction)
            date_interaction = aujourd_hui - timedelta(days=random.randint(0, 30))
            
            # Générer un contenu réaliste en fonction du type d'interaction
            if type_interaction in ['appel_entrant', 'appel_sortant']:
                duree = random.randint(30, 1800)  # Entre 30s et 30min
                contenu = f"Appel de {duree} secondes. "
                contenu += random.choice([
                    "Le client était satisfait.",
                    "Le client avait des questions techniques.",
                    "Le client souhaitait des informations supplémentaires.",
                    "Le client avait une réclamation.",
                    "Le client était intéressé par une offre."
                ])
            elif type_interaction == 'email':
                contenu = f"Email envoyé/requ au client. Sujet: "
                contenu += random.choice([
                    "Réponse à votre demande d'information",
                    "Confirmation de votre commande",
                    "Suite à notre échange téléphonique",
                    "Votre réclamation en cours",
                    "Questionnaire de satisfaction"
                ])
            elif type_interaction == 'chat':
                contenu = "Échange en chat avec le client. Points abordés: "
                contenu += ", ".join(random.sample([
                    "questions techniques", "prix", "disponibilité", "délais",
                    "paiement", "garantie", "retour produit", "problème de livraison"
                ], k=random.randint(1, 3)))
            else:
                contenu = random.choice([
                    "Interaction avec le client.",
                    "Échange concernant une demande client.",
                    "Suivi de la relation client.",
                    "Traitement d'une demande d'information.",
                    "Réponse à une réclamation."
                ])
            
            # Créer l'interaction
            interaction = Interaction.objects.create(
                client=client,
                mission=mission,
                agent=agent,
                type=type_interaction,
                date=date_interaction,
                contenu=contenu,
                resultat=random.choice(self.resultats) if random.random() > 0.2 else ""
            )
        
        self.stdout.write(self.style.SUCCESS(
            f'Généré {nb_interactions} interactions pour la mission {mission.titre}'
        ))
        
        self.stdout.write(self.style.SUCCESS('\nGénération des données de test terminée avec succès !'))
        agents = User.objects.filter(role='agent')
        missions = Mission.objects.all()
        formations = Formation.objects.all()
        kpis = KPI.objects.all()
        
        self.stdout.write(self.style.SUCCESS(f'- {agents.count()} agents crees'))
        self.stdout.write(self.style.SUCCESS(f'- {missions.count()} missions creees'))
        self.stdout.write(self.style.SUCCESS(f'- {formations.count()} formations creees'))
        self.stdout.write(self.style.SUCCESS(f'- {kpis.count()} KPIs crees'))
        self.stdout.write(self.style.SUCCESS('\nIdentifiants de connexion pour les agents :'))
        self.stdout.write(self.style.SUCCESS('\nIdentifiants de connexion pour les agents :'))
        agents = User.objects.filter(role='agent')
        for agent in agents:
            self.stdout.write(self.style.SUCCESS(f'- {agent.username} / password123'))
