# Rapport de Stage - Développement Web E-Commerce

**Étudiant:** Marie Dupont  
**Entreprise:** TechStart Solutions  
**Durée:** 6 mois (Février - Juillet 2024)  
**Encadrant:** M. Jean Martin, Lead Developer

## 1. Objectifs du stage

### Objectifs principaux
- Développer une application web e-commerce responsive et moderne
- Intégrer une API REST pour la gestion des produits et commandes
- Mettre en place un système d'authentification sécurisé avec JWT
- Optimiser les performances et le SEO

### Objectifs secondaires
- Apprendre les bonnes pratiques de développement web
- Travailler en équipe selon la méthodologie Agile
- Contribuer à l'architecture technique du projet

## 2. Contexte de l'entreprise

TechStart Solutions est une startup de 25 employés spécialisée dans le développement d'applications web pour PME. L'entreprise utilise des technologies modernes comme React, Node.js et MongoDB.

## 3. Méthodologie utilisée

### Approche Agile Scrum
Nous avons utilisé la méthode Agile avec des sprints de 2 semaines:
- Daily stand-up meetings de 15 minutes
- Sprint planning chaque lundi
- Sprint review et retrospective chaque vendredi
- Utilisation de Jira pour le suivi des tâches

### Architecture technique
- **Frontend:** React.js 18 avec hooks et Context API pour la gestion d'état
- **Styling:** TailwindCSS pour un design responsive et moderne
- **Backend:** Node.js avec Express.js pour créer l'API REST
- **Base de données:** MongoDB avec Mongoose pour l'ODM
- **Authentification:** JWT (JSON Web Tokens) avec bcrypt pour le hashage des mots de passe

## 4. Réalisations techniques

### Module de gestion des produits
J'ai développé un système CRUD complet permettant:
- L'ajout de produits avec images multiples
- La modification et suppression de produits
- Un système de filtrage par catégorie et prix
- Une recherche en temps réel avec debouncing

### Système d'authentification
Implémentation complète incluant:
- Inscription avec validation d'email
- Connexion sécurisée avec tokens JWT
- Gestion des sessions avec refresh tokens
- Middleware de protection des routes

### Panier d'achat
Développement d'un panier persistant avec:
- Ajout/suppression d'articles
- Calcul automatique des totaux et taxes
- Sauvegarde dans localStorage
- Synchronisation avec le backend

## 5. Défis rencontrés

### Optimisation des performances
Problème: Le chargement initial prenait 8 secondes.
Solution: Mise en place de code splitting et lazy loading, réduisant le temps à 2.5 secondes.

### Gestion de l'état global
Défi: Synchronisation de l'état entre composants.
Solution: Migration vers Context API avec useReducer pour une meilleure organisation.

## 6. Résultats et métriques

- **Performance:** Score Lighthouse de 92/100
- **Responsive:** Compatible mobile, tablette, desktop
- **Tests:** 85% de couverture de code avec Jest
- **Livraison:** 2 jours d'avance sur le planning initial

## 7. Conclusions principales

Le projet a été un succès total. Nous avons livré l'application dans les délais avec toutes les fonctionnalités demandées. L'équipe a excellemment collaboré et la méthodologie Agile a permis une grande flexibilité face aux changements de requirements.

### Compétences acquises
- Maîtrise de React.js et des hooks
- Architecture d'API REST professionnelle
- Travail en équipe Agile
- Débogage et optimisation de performances

### Perspectives
Le site e-commerce est maintenant en production et génère déjà 1000 visites par jour. L'entreprise envisage de m'embaucher après mes études.