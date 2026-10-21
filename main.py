#!/usr/bin/env python3
"""
Prospect Sniffer — Point d'entrée principal.
Gère le lancement du serveur, la génération du dashboard, le scan de nouveaux prospects
et l'export des données.
"""

import sys
import os
import argparse
import time

from config import DEFAULT_CITIES, DEFAULT_TRADES, SERVER_PORT
from database import build_database, get_all_prospects
from generate_dashboard import export_csv, export_html_dashboard

def banner():
    print(r"""
========================================================================
   ____                                   __     ____        _ _____  
  / __ \_________  _________  ___  _____/ /_   / __/____   (_) __/ __/
 / /_/ / ___/ __ \/ ___/ __ \/ _ \/ ___/ __/  / /_/ ___/  / / /_/ /_  
/ ____/ /  / /_/ (__  ) /_/ /  __/ /__/ /_   / __/ /     / / __/ __/   
\/   /_/   \____/____/ .___/\___/\___/\__/  /_/ /_/     /_/_/ /_/      
                    /_/                                                
  Prospection B2B Locale & Audit Technique — Métropole Aix-Marseille
========================================================================
""")

def run_scanner(cities, trades, limit_per_search=6):
    """Scan en direct de nouvelles entreprises via les API publiques et audit technique."""
    from prospector import search_companies_data_gouv, analyze_prospect
    
    all_prospects = []
    total_searches = len(cities) * len(trades)
    current_search = 0
    
    print(f"\n🚀 Démarrage du scan sur {len(cities)} ville(s) et {len(trades)} métier(s)...")
    
    for city in cities:
        city_name = city["name"]
        postal_code = city["postal_code"]
        
        for trade in trades:
            current_search += 1
            print(f"[{current_search}/{total_searches}] 🔎 Recherche : {trade.upper()} à {city_name} ({postal_code})...")
            
            companies = search_companies_data_gouv(trade, postal_code, city_name, limit=limit_per_search)
            print(f"   -> {len(companies)} entreprise(s) trouvée(s).")
            
            for comp in companies:
                print(f"   ⚡ Audit de {comp['name']}...", end=" ", flush=True)
                prospect = analyze_prospect(comp)
                opp_type = prospect["pitch"]["opportunity_type"]
                print(f"[{opp_type}]")
                all_prospects.append(prospect)
                time.sleep(0.4)
                
    # Déduplication
    unique_prospects = []
    seen = set()
    for p in all_prospects:
        key = p.get("siren") or p.get("name")
        if key not in seen:
            seen.add(key)
            unique_prospects.append(p)
            
    print("\n" + "=" * 60)
    print(f"✅ Scan terminé : {len(unique_prospects)} prospects qualifiés !")
    export_csv(unique_prospects, "prospects.csv")
    export_csv(unique_prospects, "data/prospects.csv")
    export_html_dashboard(unique_prospects, "dashboard.html")
    print("📁 Données exportées vers prospects.csv et dashboard.html")
    print("=" * 60)
    return unique_prospects

def verify_emails():
    """Vérifie la validité DNS MX de toutes les adresses email en base."""
    import subprocess
    print("🔍 Vérification des serveurs de messagerie (enregistrements MX)...")
    prospects = get_all_prospects()
    valid = 0
    for p in prospects:
        email = p.get("primary_email", "")
        if "@" in email:
            domain = email.split("@")[1].strip()
            try:
                out = subprocess.check_output(["dig", "+short", "MX", domain], timeout=2).decode().strip()
                if out:
                    valid += 1
                else:
                    print(f"❌ Pas de MX : {p['name']} ({email})")
            except Exception:
                print(f"⚠️ Erreur DNS : {email}")
    print(f"✅ Résultat : {valid}/{len(prospects)} serveurs de messagerie actifs vérifiés.")

def main():
    banner()
    parser = argparse.ArgumentParser(description="Prospect Sniffer — Outil de Prospection Locale & Outreach B2B")
    parser.add_argument("--serve", action="store_true", help="Lancer le serveur web et ouvrir le dashboard (mode par défaut)")
    parser.add_argument("--build", action="store_true", help="Régénérer le dashboard et les exports CSV à partir de la base")
    parser.add_argument("--scan", action="store_true", help="Lancer un scan en direct sur de nouvelles entreprises")
    parser.add_argument("--verify", action="store_true", help="Vérifier la validité des adresses emails (DNS MX)")
    parser.add_argument("--port", type=int, default=SERVER_PORT, help=f"Port d'écoute du serveur (défaut : {SERVER_PORT})")
    parser.add_argument("--no-browser", action="store_true", help="Ne pas ouvrir automatiquement le navigateur")

    args = parser.parse_args()

    # Si action spécifique demandée
    if args.verify:
        verify_emails()
        return

    if args.build:
        build_database()
        return

    if args.scan:
        sample_cities = DEFAULT_CITIES[:2]
        sample_trades = ["plomberie", "electricite", "serrurerie"]
        run_scanner(sample_cities, sample_trades, limit_per_search=5)
        return

    # Mode par défaut : build si nécessaire et lancer le serveur
    if not os.path.exists("dashboard.html") or not os.path.exists("prospects.csv"):
        print("📦 Fichiers initiaux manquants, génération automatique de la base...")
        build_database()

    from server import start_server
    start_server(open_browser=not args.no_browser)

if __name__ == "__main__":
    main()
