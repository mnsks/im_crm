# CRM Externalisation

Application web Django pour la gestion de la communication et du pilotage entre Entreprise Donneuse d'Ordre, Centres d'Appels (internes/externes) et Clients finaux.

## Modules inclus
- **core** : gestion des utilisateurs, rôles, permissions, entreprises, centres
- **missions** : gestion des missions, ressources, documents
- **interactions** : gestion des appels, emails, SMS, historique
- **rapports** : génération et suivi des rapports de mission
- **formations** : gestion des formations et quiz
- **communication** : messagerie interne sécurisée
- **kpi_dashboard** : tableaux de bord dynamiques
- **ai_tools** : outils d'IA (exemple : analyse de sentiment sur interactions)

## Démarrage rapide
1. Installer les dépendances : `pip install -r requirements.txt`
2. Configurer la base de données MySQL dans `settings.py`
3. Lancer les migrations : `python manage.py migrate`
4. Créer un superutilisateur : `python manage.py createsuperuser`
5. Démarrer le serveur : `python manage.py runserver`

## Stack technique
- Django
- Django REST Framework
- MySQL
- (Optionnel) Librairies IA : transformers, textblob, etc.

## Structure recommandée
```
crm_externalisation/
├── core/
├── missions/
├── interactions/
├── rapports/
├── formations/
├── communication/
├── kpi_dashboard/
├── ai_tools/
├── manage.py
├── requirements.txt
└── README.md
```

---
Pour toute question ou évolution, n'hésitez pas à demander !
