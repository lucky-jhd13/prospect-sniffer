# 🎯 Prospect Sniffer — Prospection B2B Locale & Outreach Automatisé

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![macOS Apple Mail](https://img.shields.io/badge/macOS_Mail-AppleScript-000000?style=for-the-badge&logo=apple&logoColor=white)](https://apple.com)
[![Zero Budget](https://img.shields.io/badge/Budget-0_%E2%82%AC-success?style=for-the-badge)](https://joahdabidat.vercel.app)
[![Location](https://img.shields.io/badge/Zone-Aix--Marseille-orange?style=for-the-badge)](https://joahdabidat.vercel.app)

> **Système tout-en-un de prospection locale pour développeurs web et freelances.**  
> Détecte automatiquement les besoins techniques d'entreprises locales (absence de site, lenteur mobile, failles SSL), qualifie les contacts et déclenche l'envoi d'emails personnalisés en 1 clic via Apple Mail en tâche de fond.

---

## ⚡ Démarrage Rapide en 1 Clic

### 1. Cloner et Lancer
```bash
# Rendre le script exécutable (première fois)
chmod +x start.sh

# Lancer l'application
./start.sh
```
Le script configure automatiquement l'environnement virtuel, installe les dépendances, démarre le serveur local et ouvre le tableau de bord sur **`http://localhost:8088/dashboard.html`**.

### 2. Commandes CLI (`main.py`)
Le projet dispose d'un point d'entrée unique et modulaire :
```bash
python main.py              # Lance le serveur et ouvre le dashboard (par défaut)
python main.py --build      # Régénère la base de données certifiée et les exports
python main.py --scan       # Lance un scan en direct sur les API d'entreprises locales
python main.py --verify     # Valide les serveurs de messagerie (enregistrements DNS MX)
```

---

## 🌟 Fonctionnalités Clés

### 1. 🎯 Segmentation Intelligente par Besoin Client
Fini le démarchage générique à froid. Chaque prospect est classé selon son **opportunité commerciale exacte** :
- **🏗️ Création de site web (0 existant)** : entreprises avec fiche Google sans aucun site web relié ➡️ *Offre Landing Page vitrine (600 € - 1 000 €)*.
- **⚡ Refonte & Vitesse** : sites lents (> 3s sur smartphone) ou non responsives ➡️ *Offre Optimisation mobile (450 € - 700 €)*.
- **🔒 Sécurité HTTPS** : sites encore en HTTP sans certificat SSL ➡️ *Offre Passage HTTPS & Modernisation (350 € - 500 €)*.
- **🤝 Sous-traitance Agences** : agences de communication locales ➡️ *Offre Renfort dev / Intégration front (250 € - 350 € / jour)*.

### 2. 🚀 Envoi 1-Clic Direct en Tâche de Fond (macOS)
- Intégration directe avec **Apple Mail** via AppleScript silencieux.
- **Zéro mot de passe SMTP** à configurer : utilise directement le compte déjà configuré sur votre Mac.
- Mode campagne automatique groupée avec temporisation anti-spam de sécurité (15s).

### 3. 📊 Pipeline & Suivi de Démarchage en Temps Réel
- **Horodatage automatique** : enregistre la date et l'heure exactes de chaque contact (`Démarché Aujourd'hui à 14:15`, `Il y a 3 jours`).
- **Canal utilisé** : Email, Téléphone, SMS ou WhatsApp.
- **Alertes Relances automatiques** : badge dynamique clignotant dès qu'une entreprise a été contactée il y a plus de 3 jours sans réponse pour déclencher la **Relance J+3** ou la **Relance finale J+7**.
- **Filtres de statut** : isolez en 1 clic les entreprises `⏳ À démarcher`, `✉️ Déjà démarchées`, `🔔 À relancer` ou `🎯 RDV Fixés`.

### 4. 🔒 Mode Démo / Confidentialité (Screenshot-Friendly)
- Un bouton **`Mode Démo`** permet de flouter et masquer instantanément tous les emails et numéros de téléphone (`c•••••@••••.fr` et `04 91 •• •• ••`).
- Idéal pour partager des captures d'écran sur **LinkedIn**, **Twitter/X** ou son **portfolio** sans enfreindre le RGPD ni exposer les coordonnées de prospects.

---

## 📁 Architecture du Dépôt

```
.
├── start.sh                  # ⚡ Script de lancement clé en main (macOS/Linux)
├── main.py                   # 🎛️ Point d'entrée CLI central
├── server.py                 # 🖥️ Serveur HTTP local & API Apple Mail (Port 8088)
├── config.py                 # ⚙️ Configuration (Freelance, Villes, Métiers, Port)
├── database.py               # 🗄️ Base de données qualifiée (52 entreprises réelles)
├── prospector.py             # 🔍 Module d'audit technique, SSL, PageSpeed & Pitch
├── generate_dashboard.py     # 🎨 Générateur du dashboard interactif
├── dashboard.html            # 🌐 Interface Web Glassmorphism (Tailwind CSS)
├── requirements.txt          # 📦 Dépendances Python minimales
├── .gitignore                # 🛡️ Protection des fichiers venv, logs et cache
└── data/
    └── prospects.csv         # 📊 Données exportées avec horodatage et suivi
```

---

## ⚙️ Personnalisation

Éditez le fichier `config.py` pour adapter l'outil à votre profil :
```python
USER_NAME = "Votre Nom"
USER_ROLE = "Développeur Web & Spécialiste Landing Pages"
USER_PORTFOLIO = "https://votre-portfolio.vercel.app"
SERVER_PORT = 8088

# Vos villes cibles
DEFAULT_CITIES = [
    {"name": "Aix-en-Provence", "postal_code": "13100"},
    {"name": "Marseille", "postal_code": "13001"},
    ...
]
```

---

## 👨‍💻 Auteur

Développé par **Johad** — Développeur Web Freelance (Aix-Marseille).  
- **Portfolio :** [joahdabidat.vercel.app](https://joahdabidat.vercel.app)
- **Spécialités :** React, Next.js, Tailwind CSS, Python Automation, Landing Pages Haute Vitesse.

---

## 📄 Licence

Ce projet est sous licence MIT — vous êtes libre de l'utiliser, le modifier et l'adapter pour votre propre activité de prospection freelance.
