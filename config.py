"""
Configuration globale pour Prospect Sniffer (Aix-Marseille).
Personnalise tes informations, tes offres et tes cibles géographiques.
"""

import os

# Informations Freelance
USER_NAME = "Johad"
USER_ROLE = "Développeur Web & Spécialiste Landing Pages"
USER_PORTFOLIO = "https://joahdabidat.vercel.app"

# Configuration Réseau & Serveur
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8088

# Chemins des données
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_PATH = os.path.join(DATA_DIR, "prospects.csv")
ROOT_CSV_PATH = os.path.join(BASE_DIR, "prospects.csv")
DASHBOARD_HTML_PATH = os.path.join(BASE_DIR, "dashboard.html")

# Villes cibles par défaut dans la métropole Aix-Marseille-Provence
DEFAULT_CITIES = [
    {"name": "Aix-en-Provence", "postal_code": "13100"},
    {"name": "Marseille", "postal_code": "13001"},
    {"name": "Aubagne", "postal_code": "13400"},
    {"name": "Salon-de-Provence", "postal_code": "13300"},
    {"name": "Martigues", "postal_code": "13500"},
    {"name": "Marignane", "postal_code": "13700"},
    {"name": "Vitrolles", "postal_code": "13127"},
    {"name": "Gardanne", "postal_code": "13120"}
]

# Métiers cibles recommandés (forte valeur par client, besoin crucial de visibilité locale)
DEFAULT_TRADES = [
    "plomberie",
    "electricite",
    "serrurerie",
    "climatisation",
    "menuiserie",
    "renovation",
    "paysagiste",
    "peinture batiment",
    "architecture",
    "agence communication"
]

# Domaines d'annuaires à exclure pour détecter le vrai site de l'entreprise
DIRECTORY_DOMAINS = [
    "pagesjaunes.fr",
    "societe.com",
    "infogreffe.fr",
    "annuaire-entreprises.data.gouv.fr",
    "verif.com",
    "manageo.fr",
    "facebook.com",
    "instagram.com",
    "linkedin.com",
    "google.com",
    "google.fr",
    "yelp.fr",
    "travaux.com",
    "starofservice.com",
    "habitatpresto.com",
    "mappy.com",
    "lefigaro.fr",
    "bilansgratuits.fr",
    "pappers.fr",
    "tousplombiers.fr",
    "artisanspresdechezvous.com",
    "ici-artisan.fr",
    "score3.fr",
    "mesdepanneurs.fr",
    "ou-serrurier.fr",
    "les-bons-artisans.fr",
    "allovoisins.com",
    "travauxbricolage.fr",
    "qualibat.com",
    "artisan-de-confiance.fr",
    "pages-entreprises.com"
]
