#!/usr/bin/env bash
# ==============================================================================
# Prospect Sniffer — Script de Démarrage en 1 Clic
# Métropole Aix-Marseille-Provence
# ==============================================================================

set -e

# Se placer dans le répertoire du script
cd "$(dirname "$0")"

echo "🚀 Préparation de Prospect Sniffer..."

# 1. Vérifier Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Erreur : Python 3 n'est pas installé sur ce système."
    exit 1
fi

# 2. Créer l'environnement virtuel si inexistant
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel (venv)..."
    python3 -m venv venv
fi

# 3. Activer le venv
source venv/bin/activate

# 4. Installer les dépendances
if [ -f "requirements.txt" ]; then
    echo "⬇️  Vérification des dépendances..."
    pip install -q -r requirements.txt
fi

# 5. Lancer l'application
echo "⚡ Démarrage du serveur et ouverture du dashboard..."
python main.py
