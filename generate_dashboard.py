import json
import csv
from urllib.parse import quote

def get_lead_action_category(prospect):
    """Détermine le besoin précis et l'offre commerciale à proposer."""
    audit = prospect.get("audit", {})
    issues = audit.get("issues", [])
    trade = (prospect.get("trade") or "").lower()
    issues_str = " ".join(issues).lower()
    url = audit.get("url")
    if url == "AUCUN" or not url:
        url = None
    
    if "agence" in trade or "communication" in trade:
        return {
            "key": "agency",
            "label": "Sous-traitance Dev",
            "icon": "fa-handshake",
            "color": "indigo",
            "badge_class": "bg-indigo-500/10 text-indigo-400 border-indigo-500/20",
            "offer": "Renfort dev / Intégration maquettes",
            "price": "250 € - 350 € / jour"
        }
    elif not url or "aucun site" in issues_str:
        return {
            "key": "create_site",
            "label": "Création de site web",
            "icon": "fa-hammer",
            "color": "amber",
            "badge_class": "bg-amber-500/10 text-amber-400 border-amber-500/20",
            "offer": "Landing page vitrine clé en main",
            "price": "600 € - 1 000 €"
        }
    elif (url and url.startswith("http://")) or "http" in issues_str or "ssl" in issues_str or "sécurisé" in issues_str:
        return {
            "key": "security",
            "label": "Sécurité HTTPS & Refonte",
            "icon": "fa-shield-halved",
            "color": "rose",
            "badge_class": "bg-rose-500/10 text-rose-400 border-rose-500/20",
            "offer": "Passage HTTPS & Modernisation",
            "price": "350 € - 500 €"
        }
    else:
        return {
            "key": "redesign",
            "label": "Refonte Vitesse & Mobile",
            "icon": "fa-bolt",
            "color": "cyan",
            "badge_class": "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
            "offer": "Optimisation vitesse & conversion mobile",
            "price": "450 € - 700 €"
        }

def export_csv(prospects: list, filename: str = "prospects.csv"):
    """Exporte les résultats dans un fichier CSV facile à ouvrir sur Excel / Sheets."""
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Nom", "Métier", "Ville", "Code Postal", "Dirigeant", "Site Web",
            "Besoin / Action", "Offre Conseillée", "Tarif Indicatif", "Anomalies",
            "Email Principal", "Téléphone Principal", "Statut Prospection", 
            "Dernier Démarchage", "Canal de Contact", "Nombre de Contacts",
            "Objet Email", "Corps Email"
        ])
        for p in prospects:
            audit = p.get("audit", {})
            pitch = p.get("pitch", {})
            cat = get_lead_action_category(p)
            writer.writerow([
                p.get("name"),
                p.get("trade"),
                p.get("city"),
                p.get("postal_code"),
                p.get("manager"),
                audit.get("url") or "AUCUN",
                cat["label"],
                cat["offer"],
                cat["price"],
                " | ".join(audit.get("issues", [])),
                p.get("primary_email"),
                p.get("primary_phone"),
                p.get("status", "À contacter"),
                p.get("contacted_at", "Jamais"),
                p.get("last_channel", "Aucun"),
                p.get("contact_count", 0),
                pitch.get("subject"),
                pitch.get("body")
            ])

def export_html_dashboard(prospects: list, filename: str = "dashboard.html"):
    """Génère un tableau de bord HTML interactif avec filtrage par besoin ET suivi précis du démarchage."""
    for p in prospects:
        p["action_cat"] = get_lead_action_category(p)
        if not p.get("status"):
            p["status"] = "À contacter"
        if "contacted_at" not in p:
            p["contacted_at"] = None
        if "last_channel" not in p:
            p["last_channel"] = None
        if "contact_count" not in p:
            p["contact_count"] = 0
            
    total = len(prospects)
    need_create = len([p for p in prospects if p["action_cat"]["key"] == "create_site"])
    need_redesign = len([p for p in prospects if p["action_cat"]["key"] == "redesign"])
    need_security = len([p for p in prospects if p["action_cat"]["key"] == "security"])
    need_agency = len([p for p in prospects if p["action_cat"]["key"] == "agency"])
    
    prospects_json = json.dumps(prospects, ensure_ascii=False)
    
    html = f"""<!DOCTYPE html>
<html lang="fr" class="h-full bg-slate-950 text-slate-100">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Prospect Sniffer — Suivi de Démarchage & Besoins (Aix-Marseille)</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    .glass {{
      background: rgba(15, 23, 42, 0.85);
      backdrop-filter: blur(14px);
      border: 1px solid rgba(255, 255, 255, 0.08);
    }}
    .custom-scrollbar::-webkit-scrollbar {{
      width: 6px;
      height: 6px;
    }}
    .custom-scrollbar::-webkit-scrollbar-thumb {{
      background: #334155;
      border-radius: 4px;
    }}
    .privacy-blur {{
      filter: blur(4px);
      user-select: none;
      transition: filter 0.2s ease-in-out;
    }}
    .privacy-blur:hover {{
      filter: blur(1px);
    }}
  </style>
</head>
<body class="h-full flex flex-col font-sans antialiased text-slate-200">

  <!-- Top Navbar -->
  <header class="glass sticky top-0 z-40 border-b border-slate-800 px-6 py-4 flex flex-wrap items-center justify-between gap-4">
    <div class="flex items-center gap-3">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white shadow-lg shadow-blue-500/25">
        <i class="fa-solid fa-radar text-lg"></i>
      </div>
      <div>
        <h1 class="text-lg font-bold text-white tracking-tight flex items-center gap-2">
          Prospect Sniffer <span class="text-xs px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">Aix-Marseille</span>
        </h1>
        <p class="text-xs text-slate-400">Suivi en direct du démarchage (horodatage, relances J+3, 1-clic mail)</p>
      </div>
    </div>

    <div class="flex items-center gap-3">
      <button onclick="togglePrivacyMode()" id="btnPrivacyToggle" class="px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-rose-300 flex items-center gap-1.5 border border-slate-700 transition" title="Masquer / Flouter les emails et téléphones pour captures d'écran et réseaux sociaux">
        <i class="fa-solid fa-eye-slash text-rose-400" id="privacyIcon"></i> <span id="privacyLabel">Mode Démo (Masqué)</span>
      </button>
      <button onclick="resetToVerifiedData()" class="px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-amber-300 flex items-center gap-1.5 border border-slate-700 transition" title="Réinitialiser avec les adresses vérifiées (serveurs MX actifs)">
        <i class="fa-solid fa-rotate text-amber-400"></i> Actualiser contacts réels
      </button>
      <button onclick="downloadLiveCsv()" class="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 flex items-center gap-2 border border-slate-700 transition">
        <i class="fa-solid fa-file-csv text-emerald-400"></i> Exporter CSV
      </button>
      <a href="https://joahdabidat.vercel.app" target="_blank" class="px-3.5 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white flex items-center gap-2 shadow-lg shadow-blue-600/25 transition">
        <i class="fa-solid fa-arrow-up-right-from-square"></i> Mon Portfolio (Johad)
      </a>
    </div>
  </header>

  <!-- Main Content -->
  <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-8">
    
    <!-- KPI Funnel de Prospection & Suivi -->
    <div class="glass p-5 rounded-2xl border border-slate-800 mb-8 shadow-xl">
      <div class="flex flex-wrap items-center justify-between gap-4 mb-4">
        <div>
          <span class="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
            <i class="fa-solid fa-chart-pie text-blue-400"></i> Pipeline de Démarchage en direct
          </span>
          <div class="text-sm font-semibold text-white mt-0.5">
            Progression : <span id="kpiProgressText" class="text-emerald-400">0 / {total} entreprises démarchées (0%)</span>
          </div>
        </div>

        <div class="flex flex-wrap items-center gap-3">
          <div class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs">
            <span class="w-2.5 h-2.5 rounded-full bg-slate-500"></span>
            <span class="text-slate-400">À démarcher :</span>
            <span id="kpiTodo" class="font-bold text-white">0</span>
          </div>
          <div class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-blue-500/10 border border-blue-500/20 text-xs">
            <span class="w-2.5 h-2.5 rounded-full bg-blue-400"></span>
            <span class="text-blue-300">Contactés :</span>
            <span id="kpiContacted" class="font-bold text-blue-200">0</span>
          </div>
          <div class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs">
            <span class="w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse"></span>
            <span class="text-amber-300">À relancer :</span>
            <span id="kpiFollowup" class="font-bold text-amber-200">0</span>
          </div>
          <div class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs">
            <span class="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
            <span class="text-emerald-300">RDV Fixés :</span>
            <span id="kpiWon" class="font-bold text-emerald-200">0</span>
          </div>
        </div>
      </div>

      <!-- Barre de progression visuelle -->
      <div class="w-full bg-slate-900 h-2.5 rounded-full overflow-hidden border border-slate-800 flex">
        <div id="barContacted" class="bg-blue-500 h-full transition-all duration-500" style="width: 0%"></div>
        <div id="barFollowup" class="bg-amber-500 h-full transition-all duration-500" style="width: 0%"></div>
        <div id="barWon" class="bg-emerald-500 h-full transition-all duration-500" style="width: 0%"></div>
      </div>
    </div>

    <!-- Stat Cards par Besoin Métier -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
      <div onclick="filterCategory('create_site')" class="cursor-pointer glass p-4 rounded-xl border border-amber-500/30 bg-amber-500/10 hover:border-amber-400 transition">
        <div class="flex items-center justify-between text-amber-400 text-xs font-semibold mb-1">
          <span>CRÉER UN SITE (0 EXISTANT)</span>
          <i class="fa-solid fa-hammer text-amber-400"></i>
        </div>
        <div class="text-2xl font-extrabold text-amber-300" id="statNeedCreate">{need_create}</div>
        <div class="text-[11px] text-amber-400/80 mt-0.5">Landing pages (600€-1000€)</div>
      </div>

      <div onclick="filterCategory('redesign')" class="cursor-pointer glass p-4 rounded-xl border border-cyan-500/20 bg-cyan-500/5 hover:border-cyan-400 transition">
        <div class="flex items-center justify-between text-cyan-400 text-xs font-semibold mb-1">
          <span>REFONTE & VITESSE</span>
          <i class="fa-solid fa-bolt text-cyan-400"></i>
        </div>
        <div class="text-2xl font-extrabold text-cyan-300" id="statNeedRedesign">{need_redesign}</div>
        <div class="text-[11px] text-slate-400 mt-0.5">Sites lents ou inadaptés mobile</div>
      </div>

      <div onclick="filterCategory('security')" class="cursor-pointer glass p-4 rounded-xl border border-rose-500/20 bg-rose-500/5 hover:border-rose-400 transition">
        <div class="flex items-center justify-between text-rose-400 text-xs font-semibold mb-1">
          <span>SÉCURITÉ HTTPS</span>
          <i class="fa-solid fa-shield-halved text-rose-400"></i>
        </div>
        <div class="text-2xl font-extrabold text-rose-300" id="statNeedSecurity">{need_security}</div>
        <div class="text-[11px] text-slate-400 mt-0.5">Sites non sécurisés HTTP</div>
      </div>

      <div onclick="filterCategory('agency')" class="cursor-pointer glass p-4 rounded-xl border border-indigo-500/20 bg-indigo-500/5 hover:border-indigo-400 transition">
        <div class="flex items-center justify-between text-indigo-400 text-xs font-semibold mb-1">
          <span>SOUS-TRAITANCE AGENCES</span>
          <i class="fa-solid fa-handshake text-indigo-400"></i>
        </div>
        <div class="text-2xl font-extrabold text-indigo-300" id="statNeedAgency">{need_agency}</div>
        <div class="text-[11px] text-slate-400 mt-0.5">Renfort dev (250€-350€/j)</div>
      </div>
    </div>

    <!-- Double Barre de Filtrage : Besoins & Statut Suivi -->
    <div class="glass p-4 rounded-xl mb-6 space-y-3 border border-slate-800">
      
      <!-- Ligne 1 : Filtre de Suivi / Pipeline -->
      <div class="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800/80">
        <div class="flex flex-wrap items-center gap-2">
          <span class="text-xs font-bold text-slate-400 flex items-center gap-1.5 mr-1">
            <i class="fa-solid fa-filter text-blue-400"></i> Suivi :
          </span>
          <button onclick="filterTracking('all')" id="btn-track-all" class="track-btn px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 text-white transition">
            Tous les statuts ({total})
          </button>
          <button onclick="filterTracking('todo')" id="btn-track-todo" class="track-btn px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition">
            ⏳ À démarcher (<span id="countTrackTodo">0</span>)
          </button>
          <button onclick="filterTracking('contacted')" id="btn-track-contacted" class="track-btn px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-blue-400 border border-slate-700 transition">
            ✉️ Déjà démarchés (<span id="countTrackContacted">0</span>)
          </button>
          <button onclick="filterTracking('ready_followup')" id="btn-track-ready_followup" class="track-btn px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-amber-400 border border-slate-700 transition">
            🔔 À relancer (<span id="countTrackFollowup">0</span>)
          </button>
          <button onclick="filterTracking('won')" id="btn-track-won" class="track-btn px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-emerald-400 border border-slate-700 transition">
            🎯 RDV Fixés (<span id="countTrackWon">0</span>)
          </button>
        </div>

        <div class="flex items-center gap-2">
          <button onclick="startBatchCampaign()" id="btnBatchCampaign" class="px-3.5 py-1.5 rounded-lg text-xs font-bold bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-lg shadow-emerald-600/20 flex items-center gap-1.5 transition">
            <i class="fa-solid fa-bolt"></i> Démarcher les prospects non contactés en 1 clic
          </button>
        </div>
      </div>

      <!-- Ligne 2 : Filtre Besoins & Recherche -->
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div class="flex flex-wrap items-center gap-2">
          <span class="text-xs font-bold text-slate-400 flex items-center gap-1.5 mr-1">
            <i class="fa-solid fa-briefcase text-amber-400"></i> Besoin :
          </span>
          <button onclick="filterCategory('all')" id="btn-cat-all" class="cat-btn px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 text-white transition">
            Tous les besoins
          </button>
          <button onclick="filterCategory('create_site')" id="btn-cat-create_site" class="cat-btn px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-amber-400 border border-slate-700 transition">
            🏗️ Créer un site ({need_create})
          </button>
          <button onclick="filterCategory('redesign')" id="btn-cat-redesign" class="cat-btn px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-cyan-400 border border-slate-700 transition">
            ⚡ Refonte ({need_redesign})
          </button>
          <button onclick="filterCategory('security')" id="btn-cat-security" class="cat-btn px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-rose-400 border border-slate-700 transition">
            🔒 Sécurité ({need_security})
          </button>
          <button onclick="filterCategory('agency')" id="btn-cat-agency" class="cat-btn px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-indigo-400 border border-slate-700 transition">
            🤝 Agences ({need_agency})
          </button>
        </div>

        <div class="flex flex-wrap items-center gap-2">
          <div class="flex items-center gap-1.5 text-xs text-slate-400">
            <i class="fa-solid fa-arrow-down-wide-short text-slate-500"></i>
            <span>Trier :</span>
            <select id="sortSelect" onchange="applySorting(this.value)" class="bg-slate-900 border border-slate-800 text-xs text-slate-200 rounded-lg px-2.5 py-1.5 outline-none cursor-pointer">
              <option value="default">Besoin prioritaire</option>
              <option value="status_todo">À démarcher en premier</option>
              <option value="last_contacted_desc">Démarché récemment</option>
              <option value="name_asc">Entreprise (A - Z)</option>
              <option value="city_asc">Ville (A - Z)</option>
            </select>
          </div>

          <!-- Recherche Textuelle -->
          <div class="relative w-56">
            <i class="fa-solid fa-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 text-xs"></i>
            <input type="text" id="searchInput" oninput="renderTable()" placeholder="Rechercher nom, ville..." 
                   class="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition">
          </div>
        </div>

      </div>

    </div>

    <!-- Bannière de Progression Campagne Automatique -->
    <div id="campaignBanner" class="hidden glass p-4 rounded-xl mb-6 border border-emerald-500/30 bg-emerald-500/10 flex flex-col gap-3">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2.5">
          <div class="w-3 h-3 rounded-full bg-emerald-400 animate-ping"></div>
          <span class="text-xs font-bold text-emerald-300" id="campaignStatusText">Campagne automatique en cours...</span>
        </div>
        <button onclick="stopCampaign()" class="px-2.5 py-1 rounded bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 text-[11px] font-semibold border border-rose-500/30 transition">
          Arrêter la campagne
        </button>
      </div>
      <div class="w-full bg-slate-900 h-2 rounded-full overflow-hidden border border-slate-800">
        <div id="campaignProgressBar" class="bg-gradient-to-r from-emerald-500 to-teal-400 h-full w-0 transition-all duration-300"></div>
      </div>
    </div>

    <!-- Prospects List Table -->
    <div class="glass rounded-2xl border border-slate-800 overflow-hidden shadow-2xl">
      <div class="overflow-x-auto custom-scrollbar">
        <table class="w-full text-left text-xs border-collapse">
          <thead>
            <tr class="border-b border-slate-800 bg-slate-900/70 text-slate-400 font-semibold uppercase tracking-wider">
              <th class="py-3.5 px-4">Entreprise & Ville</th>
              <th class="py-3.5 px-4">Besoin Exact & Prestation</th>
              <th class="py-3.5 px-4">Email & Téléphone</th>
              <th class="py-3.5 px-4">Suivi & Horodatage</th>
              <th class="py-3.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody id="prospectsTableBody" class="divide-y divide-slate-800/60 font-normal">
            <!-- Rendu dynamique par JS -->
          </tbody>
        </table>
      </div>
    </div>

  </main>

  <!-- Modal Preview Contact & Sequences -->
  <div id="emailModal" class="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm hidden flex items-center justify-center p-4">
    <div class="glass w-full max-w-2xl rounded-2xl border border-slate-700 p-6 shadow-2xl flex flex-col gap-4">
      
      <!-- Modal Header -->
      <div class="flex items-center justify-between border-b border-slate-800 pb-3">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-blue-500/20 text-blue-400 flex items-center justify-center text-sm">
            <i class="fa-solid fa-paper-plane"></i>
          </div>
          <div>
            <h3 class="text-sm font-bold text-white" id="modalCompanyName">Entreprise</h3>
            <p class="text-xs text-slate-400" id="modalCompanyInfo">Métier • Ville</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <a id="btnGoogleSearch" href="#" target="_blank" class="px-2.5 py-1.5 rounded-lg text-xs font-medium bg-slate-900 border border-slate-700 text-amber-400 hover:text-white flex items-center gap-1.5 transition">
            <i class="fa-brands fa-google text-[11px]"></i> Trouver sur Google
          </a>
          <button onclick="closeModal()" class="text-slate-400 hover:text-white p-1.5 transition">
            <i class="fa-solid fa-xmark text-base"></i>
          </button>
        </div>
      </div>

      <!-- Bandeau Horodatage / Suivi dans la modale -->
      <div id="modalTrackingBanner" class="p-3 rounded-xl border border-slate-800 bg-slate-900/80 flex flex-wrap items-center justify-between gap-2 text-xs">
        <div class="flex items-center gap-2">
          <span id="modalTrackingIcon"><i class="fa-solid fa-clock text-slate-500"></i></span>
          <span id="modalTrackingText" class="text-slate-300 font-medium">Jamais démarché</span>
        </div>
        <div class="flex items-center gap-1.5">
          <button onclick="markQuickActionFromModal('phone')" class="px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-indigo-500/20 text-indigo-300 hover:bg-indigo-500/30 border border-indigo-500/30 transition">
            <i class="fa-solid fa-phone text-[10px]"></i> Appel passé
          </button>
          <button onclick="markQuickActionFromModal('email')" class="px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30 border border-emerald-500/30 transition">
            <i class="fa-solid fa-envelope text-[10px]"></i> Email envoyé
          </button>
          <button onclick="markQuickActionFromModal('won')" class="px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-emerald-600 text-white hover:bg-emerald-500 transition">
            <i class="fa-solid fa-handshake text-[10px]"></i> RDV Fixé !
          </button>
        </div>
      </div>

      <!-- Encadré du Besoin & Offre Conseillée -->
      <div id="modalActionBox" class="p-3 rounded-xl border flex items-center justify-between gap-3">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg flex items-center justify-center text-sm" id="modalActionIcon">
            <i class="fa-solid fa-hammer"></i>
          </div>
          <div>
            <div class="text-xs font-bold" id="modalActionLabel">Création de site web</div>
            <div class="text-[11px] text-slate-400" id="modalActionOffer">Landing page vitrine clé en main</div>
          </div>
        </div>
        <div class="text-right">
          <div class="text-[10px] uppercase font-semibold text-slate-500">Tarif conseillé</div>
          <div class="text-xs font-bold text-white" id="modalActionPrice">600 € - 1 000 €</div>
        </div>
      </div>

      <!-- Séquence de prospection : 1er Message vs Relance 1 vs Relance 2 -->
      <div class="p-2.5 rounded-xl bg-slate-900 border border-slate-800 flex flex-wrap items-center justify-between gap-2">
        <div class="text-xs font-semibold text-slate-300 flex items-center gap-2">
          <i class="fa-solid fa-arrows-split-up-and-left text-blue-400"></i>
          <span>Étape de contact :</span>
        </div>
        <div class="flex items-center gap-1.5">
          <button onclick="setSequenceStep('initial')" id="stepBtnInitial" class="seq-btn px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-blue-600 text-white transition">
            1. Premier Message
          </button>
          <button onclick="setSequenceStep('followup1')" id="stepBtnFollowup1" class="seq-btn px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-slate-800 text-slate-400 hover:text-white transition">
            2. Relance J+3
          </button>
          <button onclick="setSequenceStep('followup2')" id="stepBtnFollowup2" class="seq-btn px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-slate-800 text-slate-400 hover:text-white transition">
            3. Relance Ultime J+7
          </button>
        </div>
      </div>

      <!-- Dual Contact Fields -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 p-3 rounded-xl bg-slate-900/60 border border-slate-800/80">
        <div>
          <label class="text-[11px] font-semibold uppercase text-emerald-400 tracking-wider flex items-center gap-1.5 mb-1">
            <i class="fa-solid fa-envelope"></i> Adresse Email
          </label>
          <input type="email" id="modalTargetEmailInput" oninput="onContactInfoChanged()" placeholder="Renseigner ou modifier l'email..."
                 class="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-emerald-500 font-mono">
        </div>
        <div>
          <label class="text-[11px] font-semibold uppercase text-indigo-400 tracking-wider flex items-center gap-1.5 mb-1">
            <i class="fa-solid fa-mobile-screen"></i> Téléphone Portable / Fixe
          </label>
          <input type="text" id="modalTargetPhoneInput" oninput="onContactInfoChanged()" placeholder="Renseigner ou modifier le tél..."
                 class="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500 font-mono">
        </div>
      </div>

      <!-- Tabs : Email vs SMS -->
      <div class="flex items-center gap-2 border-b border-slate-800 pb-2">
        <button onclick="switchTab('email')" id="tabEmail" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 text-white flex items-center gap-2 transition">
          <i class="fa-solid fa-envelope"></i> Message Email
        </button>
        <button onclick="switchTab('sms')" id="tabSms" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:text-white flex items-center gap-2 transition">
          <i class="fa-solid fa-comment-sms text-emerald-400"></i> Message SMS / WhatsApp
        </button>
      </div>

      <!-- View Email -->
      <div id="viewEmail" class="space-y-3">
        <div>
          <label class="text-[11px] font-semibold uppercase text-slate-400 tracking-wider">Objet de l'email</label>
          <div id="modalSubject" class="mt-1 p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-xs font-semibold text-slate-200"></div>
        </div>

        <div>
          <label class="text-[11px] font-semibold uppercase text-slate-400 tracking-wider">Corps du message</label>
          <pre id="modalBody" class="mt-1 p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300 font-sans whitespace-pre-wrap max-h-40 overflow-y-auto custom-scrollbar"></pre>
        </div>

        <div class="flex items-center justify-between pt-2 border-t border-slate-800">
          <button onclick="copyEmailText()" id="btnCopyText" class="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 flex items-center gap-2 transition">
            <i class="fa-regular fa-copy"></i> Copier le texte
          </button>
          <div class="flex items-center gap-2">
            <button onclick="recordContactNow(currentModalIndex, 'email')" class="px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 transition">
              ✓ Marquer Contacté (Maintenant)
            </button>
            <a id="btnMailtoSend" href="#" onclick="onMailtoClicked()" class="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white flex items-center gap-2 shadow-lg shadow-blue-600/30 transition">
              <i class="fa-solid fa-envelope"></i> Ouvrir Mail
            </a>
          </div>
        </div>
      </div>

      <!-- View SMS -->
      <div id="viewSms" class="space-y-3 hidden">
        <div>
          <label class="text-[11px] font-semibold uppercase text-slate-400 tracking-wider">Message court (SMS / WhatsApp)</label>
          <pre id="modalSmsBody" class="mt-1 p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300 font-sans whitespace-pre-wrap"></pre>
        </div>

        <div class="flex items-center justify-between pt-2 border-t border-slate-800">
          <div class="flex items-center gap-2">
            <button onclick="copySmsText()" id="btnCopySmsText" class="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 flex items-center gap-2 transition">
              <i class="fa-regular fa-copy"></i> Copier SMS
            </button>
            <a id="modalPhoneCall" href="#" onclick="recordContactNow(currentModalIndex, 'phone')" class="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-indigo-400 flex items-center gap-1.5 transition">
              <i class="fa-solid fa-phone"></i> Appeler
            </a>
          </div>
          <a id="btnWhatsAppSend" href="#" onclick="recordContactNow(currentModalIndex, 'sms')" target="_blank" class="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-xs font-semibold text-white flex items-center gap-2 shadow-lg shadow-emerald-600/30 transition">
            <i class="fa-brands fa-whatsapp text-sm"></i> Ouvrir WhatsApp / SMS
          </a>
        </div>
      </div>

    </div>
  </div>

  <script>
    let initialData = {prospects_json};
    let savedData = null;
    try {{
      // Récupérer uniquement les données de suivi vérifiées v7
      const stored = localStorage.getItem('saved_prospects_data_v7_verified');
      if (stored) savedData = JSON.parse(stored);
    }} catch(e) {{}}

    const data = initialData.map((item, idx) => {{
      const saved = (savedData && savedData[idx]) ? savedData[idx] : {{}};
      return {{
        ...item,
        status: saved.status || item.status || 'À contacter',
        // Conserver les coordonnées réelles certifiées de initialData en priorité
        primary_email: (saved.primary_email && saved.primary_email.includes('@')) ? saved.primary_email : (item.primary_email || ''),
        primary_phone: saved.primary_phone || item.primary_phone || '',
        contacted_at: saved.contacted_at || item.contacted_at || null,
        last_channel: saved.last_channel || item.last_channel || null,
        contact_count: saved.contact_count !== undefined ? saved.contact_count : (item.contact_count || 0)
      }};
    }});

    function resetToVerifiedData() {{
      if (confirm("Réinitialiser l'affichage avec la liste des emails et téléphones 100% réels et vérifiés ?\\n(Efface l'ancien cache contenant les adresses invalides)")) {{
        try {{
          localStorage.removeItem('saved_prospects_data_v4');
          localStorage.removeItem('saved_prospects_data_v5');
          localStorage.removeItem('saved_prospects_data_v7_verified');
        }} catch(e) {{}}
        window.location.reload();
      }}
    }}

    let isPrivacyMode = true; // Actif par défaut pour captures d'écran et démos publiques

    function togglePrivacyMode() {{
      isPrivacyMode = !isPrivacyMode;
      const label = document.getElementById('privacyLabel');
      const icon = document.getElementById('privacyIcon');
      const btn = document.getElementById('btnPrivacyToggle');
      if (isPrivacyMode) {{
        label.textContent = "Mode Démo (Masqué)";
        icon.className = "fa-solid fa-eye-slash text-rose-400";
        btn.className = "px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-rose-300 flex items-center gap-1.5 border border-slate-700 transition";
      }} else {{
        label.textContent = "Contacts visibles";
        icon.className = "fa-solid fa-eye text-emerald-400";
        btn.className = "px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-emerald-300 flex items-center gap-1.5 border border-slate-700 transition";
      }}
      renderTable();
    }}

    function maskEmail(email) {{
      if (!email || !email.includes('@')) return email;
      const parts = email.split('@');
      const user = parts[0];
      const domainParts = parts[1].split('.');
      const maskedUser = user.length > 2 ? user.slice(0, 2) + '••••' : user[0] + '••••';
      const ext = domainParts.pop();
      return `${{maskedUser}}@•••••.${{ext}}`;
    }}

    function maskPhone(phone) {{
      if (!phone) return phone;
      const clean = phone.trim();
      if (clean.length < 8) return '•• •• •• ••';
      return clean.slice(0, 5) + ' •• •• ••';
    }}

    let currentCategory = 'all';
    let currentTracking = 'all';
    let currentSort = 'default';
    let currentModalItem = null;
    let currentModalIndex = null;
    let currentTab = 'email';
    let currentSequenceStep = 'initial';

    function formatRelativeDate(isoString) {{
      if (!isoString) return null;
      const d = new Date(isoString);
      if (isNaN(d.getTime())) return null;
      const now = new Date();
      const diffMs = now - d;
      const diffSec = Math.floor(diffMs / 1000);
      const diffMin = Math.floor(diffSec / 60);
      const diffHours = Math.floor(diffMin / 60);
      const diffDays = Math.floor(diffHours / 24);

      const pad = (n) => String(n).padStart(2, '0');
      const timeStr = `${{pad(d.getHours())}}:${{pad(d.getMinutes())}}`;
      const dateStr = `${{pad(d.getDate())}}/${{pad(d.getMonth() + 1)}}`;

      if (diffMin < 2) return "À l'instant";
      if (diffMin < 60) return `Il y a ${{diffMin}} min`;
      if (diffHours < 24 && d.getDate() === now.getDate()) return `Aujourd'hui à ${{timeStr}}`;
      if (diffDays === 1 || (diffHours < 48 && d.getDate() === now.getDate() - 1)) return `Hier à ${{timeStr}}`;
      if (diffDays < 7) return `Il y a ${{diffDays}} jours (${{dateStr}})`;
      return `Le ${{dateStr}} à ${{timeStr}}`;
    }}

    function getDaysElapsed(isoString) {{
      if (!isoString) return 999;
      const d = new Date(isoString);
      if (isNaN(d.getTime())) return 999;
      return Math.floor((new Date() - d) / (1000 * 60 * 60 * 24));
    }}

    function getFollowUpAlert(item) {{
      if (!item.contacted_at) return null;
      const days = getDaysElapsed(item.contacted_at);
      
      if (item.status === 'Contacté' && days >= 3) {{
        return {{
          step: 'followup1',
          badgeText: `🔔 Relance J+3 (${{days}}j écoulés)`,
          buttonText: 'Relancer J+3'
        }};
      }}
      if (item.status === 'Relancé 1' && days >= 4) {{ // 4j après relance 1 = J+7
        return {{
          step: 'followup2',
          badgeText: `🔔 Relance finale J+7 (${{days}}j écoulés)`,
          buttonText: 'Relance J+7'
        }};
      }}
      return null;
    }}

    function filterCategory(cat) {{
      currentCategory = cat;
      document.querySelectorAll('.cat-btn').forEach(btn => {{
        btn.classList.remove('bg-blue-600', 'text-white');
        btn.classList.add('bg-slate-800');
      }});
      const activeBtn = document.getElementById('btn-cat-' + cat);
      if (activeBtn) {{
        activeBtn.classList.add('bg-blue-600', 'text-white');
        activeBtn.classList.remove('bg-slate-800');
      }}
      renderTable();
    }}

    function filterTracking(trackKey) {{
      currentTracking = trackKey;
      document.querySelectorAll('.track-btn').forEach(btn => {{
        btn.classList.remove('bg-blue-600', 'text-white');
        btn.classList.add('bg-slate-800');
      }});
      const activeBtn = document.getElementById('btn-track-' + trackKey);
      if (activeBtn) {{
        activeBtn.classList.add('bg-blue-600', 'text-white');
        activeBtn.classList.remove('bg-slate-800');
      }}
      renderTable();
    }}

    function applySorting(sortVal) {{
      currentSort = sortVal;
      renderTable();
    }}

    function recordContactNow(index, channel = 'email') {{
      if (index === null || index === undefined || !data[index]) return;
      const item = data[index];
      
      item.contacted_at = new Date().toISOString();
      item.last_channel = channel;
      item.contact_count = (item.contact_count || 0) + 1;

      if (item.status === 'À contacter') {{
        item.status = 'Contacté';
      }} else if (item.status === 'Contacté') {{
        item.status = 'Relancé 1';
      }} else if (item.status === 'Relancé 1') {{
        item.status = 'Relancé 2';
      }}

      saveLocalData();
      renderTable();
      if (currentModalIndex === index) {{
        refreshModalTrackingView();
      }}
    }}

    function markStatus(index, newStatus) {{
      data[index].status = newStatus;
      if (!data[index].contacted_at && (newStatus === 'Contacté' || newStatus === 'Relancé 1' || newStatus === 'Relancé 2' || newStatus === 'RDV Fixé')) {{
        data[index].contacted_at = new Date().toISOString();
        data[index].last_channel = data[index].last_channel || 'email';
        data[index].contact_count = (data[index].contact_count || 0) + 1;
      }}
      saveLocalData();
      renderTable();
    }}

    function quickFollowup(index, step) {{
      openModal(index);
      setSequenceStep(step);
    }}

    function markQuickActionFromModal(action) {{
      if (currentModalIndex === null) return;
      if (action === 'phone') {{
        recordContactNow(currentModalIndex, 'phone');
      }} else if (action === 'email') {{
        recordContactNow(currentModalIndex, 'email');
      }} else if (action === 'won') {{
        data[currentModalIndex].status = 'RDV Fixé';
        if (!data[currentModalIndex].contacted_at) data[currentModalIndex].contacted_at = new Date().toISOString();
        saveLocalData();
        renderTable();
        refreshModalTrackingView();
      }}
    }}

    function onMailtoClicked() {{
      if (currentModalIndex !== null) {{
        recordContactNow(currentModalIndex, 'email');
      }}
    }}

    function saveLocalData() {{
      try {{
        localStorage.setItem('saved_prospects_data_v7_verified', JSON.stringify(data));
      }} catch(e) {{}}
    }}

    function renderTable() {{
      // Calcul des métriques de Suivi Global
      let countTodo = 0;
      let countContacted = 0;
      let countFollowup = 0;
      let countWon = 0;

      data.forEach(item => {{
        const alert = getFollowUpAlert(item);
        if (alert) countFollowup++;

        if (item.status === 'RDV Fixé') {{
          countWon++;
          countContacted++;
        }} else if (item.status === 'Contacté' || item.status === 'Relancé 1' || item.status === 'Relancé 2' || item.contacted_at) {{
          countContacted++;
        }} else {{
          countTodo++;
        }}
      }});

      // Mise à jour des compteurs Pipeline
      const elKpiTodo = document.getElementById('kpiTodo');
      const elKpiContacted = document.getElementById('kpiContacted');
      const elKpiFollowup = document.getElementById('kpiFollowup');
      const elKpiWon = document.getElementById('kpiWon');
      const elProgressText = document.getElementById('kpiProgressText');

      if (elKpiTodo) elKpiTodo.textContent = countTodo;
      if (elKpiContacted) elKpiContacted.textContent = countContacted;
      if (elKpiFollowup) elKpiFollowup.textContent = countFollowup;
      if (elKpiWon) elKpiWon.textContent = countWon;

      const pct = Math.round((countContacted / data.length) * 100);
      if (elProgressText) {{
        elProgressText.textContent = `${{countContacted}} / ${{data.length}} entreprises démarchées (${{pct}}%)`;
      }}

      // Barre de progression
      const barContacted = document.getElementById('barContacted');
      const barFollowup = document.getElementById('barFollowup');
      const barWon = document.getElementById('barWon');
      if (barContacted) barContacted.style.width = `${{Math.max(0, ((countContacted - countFollowup - countWon) / data.length) * 100)}}%`;
      if (barFollowup) barFollowup.style.width = `${{Math.max(0, (countFollowup / data.length) * 100)}}%`;
      if (barWon) barWon.style.width = `${{Math.max(0, (countWon / data.length) * 100)}}%`;

      // Compteurs sur les boutons de suivi
      const countTrackTodo = document.getElementById('countTrackTodo');
      const countTrackContacted = document.getElementById('countTrackContacted');
      const countTrackFollowup = document.getElementById('countTrackFollowup');
      const countTrackWon = document.getElementById('countTrackWon');
      if (countTrackTodo) countTrackTodo.textContent = countTodo;
      if (countTrackContacted) countTrackContacted.textContent = countContacted;
      if (countTrackFollowup) countTrackFollowup.textContent = countFollowup;
      if (countTrackWon) countTrackWon.textContent = countWon;

      // Compteurs par besoin
      const countCreate = data.filter(p => p.action_cat?.key === 'create_site').length;
      const countRedesign = data.filter(p => p.action_cat?.key === 'redesign').length;
      const countSecurity = data.filter(p => p.action_cat?.key === 'security').length;
      const countAgency = data.filter(p => p.action_cat?.key === 'agency').length;

      const elCreate = document.getElementById('statNeedCreate');
      const elRedesign = document.getElementById('statNeedRedesign');
      const elSecurity = document.getElementById('statNeedSecurity');
      const elAgency = document.getElementById('statNeedAgency');

      if (elCreate) elCreate.textContent = countCreate;
      if (elRedesign) elRedesign.textContent = countRedesign;
      if (elSecurity) elSecurity.textContent = countSecurity;
      if (elAgency) elAgency.textContent = countAgency;

      const tbody = document.getElementById('prospectsTableBody');
      const search = document.getElementById('searchInput').value.toLowerCase();
      tbody.innerHTML = '';

      // Filtrage
      let filtered = data.filter(item => {{
        // Filtre Besoin
        const catKey = item.action_cat?.key || 'create_site';
        if (currentCategory !== 'all' && catKey !== currentCategory) return false;

        // Filtre Suivi
        const alert = getFollowUpAlert(item);
        const isContacted = item.status !== 'À contacter' || !!item.contacted_at;
        
        if (currentTracking === 'todo' && isContacted) return false;
        if (currentTracking === 'contacted' && !isContacted) return false;
        if (currentTracking === 'ready_followup' && !alert) return false;
        if (currentTracking === 'won' && item.status !== 'RDV Fixé') return false;

        // Recherche texte
        if (search) {{
          const fullText = (item.name + ' ' + item.city + ' ' + item.trade + ' ' + (item.manager || '') + ' ' + (item.primary_email || '') + ' ' + (item.primary_phone || '') + ' ' + (item.action_cat?.label || '')).toLowerCase();
          if (!fullText.includes(search)) return false;
        }}
        return true;
      }});

      // Tri
      filtered.sort((a, b) => {{
        if (currentSort === 'name_asc') return (a.name || '').localeCompare(b.name || '');
        if (currentSort === 'city_asc') return (a.city || '').localeCompare(b.city || '');
        if (currentSort === 'status_todo') {{
          const aDone = (a.status !== 'À contacter' || a.contacted_at) ? 1 : 0;
          const bDone = (b.status !== 'À contacter' || b.contacted_at) ? 1 : 0;
          return aDone - bDone;
        }}
        if (currentSort === 'last_contacted_desc') {{
          const timeA = a.contacted_at ? new Date(a.contacted_at).getTime() : 0;
          const timeB = b.contacted_at ? new Date(b.contacted_at).getTime() : 0;
          return timeB - timeA;
        }}
        // Default : Prioriser la création de site
        const scoreA = a.action_cat?.key === 'create_site' ? 0 : 1;
        const scoreB = b.action_cat?.key === 'create_site' ? 0 : 1;
        return scoreA - scoreB;
      }});

      if (filtered.length === 0) {{
        tbody.innerHTML = `<tr><td colspan="5" class="py-12 text-center text-slate-500">
          <i class="fa-solid fa-inbox text-3xl mb-2 text-slate-600 block"></i>
          Aucune entreprise trouvée avec ces critères.
        </td></tr>`;
        return;
      }}

      filtered.forEach((item) => {{
        const realIndex = data.indexOf(item);
        const cat = item.action_cat || {{ label: 'Création de site', icon: 'fa-hammer', color: 'amber', badge_class: 'bg-amber-500/10 text-amber-400 border-amber-500/20', offer: 'Landing page vitrine', price: '600€-1000€' }};

        // Contact info column avec support du Mode Démo / Confidentialité
        const emailDisplay = isPrivacyMode ? maskEmail(item.primary_email) : item.primary_email;
        const phoneDisplay = isPrivacyMode ? maskPhone(item.primary_phone) : item.primary_phone;
        const blurStyle = isPrivacyMode ? 'privacy-blur' : '';

        let contactHtml = '<div class="space-y-1">';
        if (item.primary_email) {{
          contactHtml += `<div class="text-[11px] text-emerald-400 flex items-center gap-1.5 font-medium truncate max-w-[200px]" title="${{isPrivacyMode ? 'Coordonnée masquée pour démo' : item.primary_email}}">
            <i class="fa-solid fa-envelope text-[10px] text-emerald-400"></i> <span class="${{blurStyle}}">${{emailDisplay}}</span>
          </div>`;
        }} else {{
          contactHtml += `<div class="text-[10px] text-slate-500 hover:text-emerald-400 cursor-pointer flex items-center gap-1 transition" onclick="openModal(${{realIndex}}, 'email')">
            <i class="fa-solid fa-plus text-[9px]"></i> Ajouter email
          </div>`;
        }}

        if (item.primary_phone) {{
          contactHtml += `<div class="text-[11px] text-indigo-400 flex items-center gap-1.5 font-medium">
            <i class="fa-solid fa-mobile-screen text-[10px] text-indigo-400"></i> <span class="${{blurStyle}}">${{phoneDisplay}}</span>
          </div>`;
        }} else {{
          contactHtml += `<div class="text-[10px] text-slate-500 hover:text-indigo-400 cursor-pointer flex items-center gap-1 transition" onclick="openModal(${{realIndex}}, 'sms')">
            <i class="fa-solid fa-plus text-[9px]"></i> Ajouter tél
          </div>`;
        }}
        contactHtml += '</div>';

        // Suivi & Horodatage column
        const statusColors = {{
          'À contacter': 'text-slate-400 bg-slate-900 border-slate-800',
          'Contacté': 'text-blue-400 bg-blue-500/10 border-blue-500/30 font-semibold',
          'Relancé 1': 'text-amber-400 bg-amber-500/10 border-amber-500/30 font-semibold',
          'Relancé 2': 'text-purple-400 bg-purple-500/10 border-purple-500/30 font-semibold',
          'RDV Fixé': 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30 font-bold',
          'Pas intéressé': 'text-rose-400 bg-rose-500/10 border-rose-500/30'
        }};
        const currentStyle = statusColors[item.status] || statusColors['À contacter'];

        // Suivi text
        let trackingDetails = '';
        const formattedDate = formatRelativeDate(item.contacted_at);
        const channelIcon = item.last_channel === 'phone' ? 'fa-phone text-indigo-400' : (item.last_channel === 'sms' ? 'fa-comment-sms text-emerald-400' : 'fa-envelope text-blue-400');
        const channelLabel = item.last_channel === 'phone' ? 'Par téléphone' : (item.last_channel === 'sms' ? 'Par SMS' : 'Par email');

        if (item.contacted_at) {{
          trackingDetails = `
            <div class="flex items-center gap-1.5 text-[11px] text-slate-300 font-medium mt-1">
              <i class="fa-solid ${{channelIcon}} text-[10px]"></i>
              <span>Démarché : <strong class="text-white">${{formattedDate}}</strong></span>
            </div>
            <div class="text-[10px] text-slate-500">
              ${{channelLabel}} • ${{item.contact_count || 1}} contact(s)
            </div>
          `;
        }} else {{
          trackingDetails = `
            <div class="flex items-center gap-1.5 text-[11px] text-slate-500 mt-1">
              <span class="w-2 h-2 rounded-full bg-slate-600"></span>
              <span>Jamais démarché</span>
              <button onclick="recordContactNow(${{realIndex}}, 'email')" class="text-[10px] text-blue-400 hover:underline ml-1">+ Fait</button>
            </div>
          `;
        }}

        // Alerte relance
        const alert = getFollowUpAlert(item);
        let alertHtml = '';
        if (alert) {{
          alertHtml = `
            <div class="mt-1.5">
              <button onclick="quickFollowup(${{realIndex}}, '${{alert.step}}')" class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40 hover:bg-amber-500/30 animate-pulse transition">
                <i class="fa-solid fa-bell"></i> ${{alert.badgeText}}
              </button>
            </div>
          `;
        }}

        const tr = document.createElement('tr');
        tr.className = "hover:bg-slate-900/40 transition";
        tr.innerHTML = `
          <td class="py-4 px-4">
            <div class="font-bold text-slate-100">${{item.name}}</div>
            <div class="text-[11px] text-slate-500 flex items-center gap-1 mt-0.5">
              <i class="fa-solid fa-location-dot text-[10px]"></i> ${{item.city}} (${{item.postal_code}})
            </div>
            <div class="text-[11px] text-slate-400 mt-1 capitalize">${{item.trade}}</div>
          </td>
          <td class="py-4 px-4">
            <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold border ${{cat.badge_class}}">
              <i class="fa-solid ${{cat.icon}} text-[10px]"></i> ${{cat.label}}
            </span>
            <div class="text-[11px] text-slate-300 font-medium mt-1">${{cat.offer}}</div>
            <div class="text-[10px] text-slate-500">${{cat.price}}</div>
          </td>
          <td class="py-4 px-4">
            ${{contactHtml}}
          </td>
          <td class="py-4 px-4">
            <div class="space-y-1">
              <select onchange="markStatus(${{realIndex}}, this.value)" class="text-xs rounded-lg px-2.5 py-1 font-semibold border outline-none cursor-pointer transition ${{currentStyle}}">
                <option value="À contacter" ${{item.status === 'À contacter' ? 'selected' : ''}}>⏳ À contacter</option>
                <option value="Contacté" ${{item.status === 'Contacté' ? 'selected' : ''}}>📨 Contacté</option>
                <option value="Relancé 1" ${{item.status === 'Relancé 1' ? 'selected' : ''}}>🔄 Relancé 1 (J+3)</option>
                <option value="Relancé 2" ${{item.status === 'Relancé 2' ? 'selected' : ''}}>⌛ Relancé 2 (J+7)</option>
                <option value="RDV Fixé" ${{item.status === 'RDV Fixé' ? 'selected' : ''}}>🎯 RDV Fixé !</option>
                <option value="Pas intéressé" ${{item.status === 'Pas intéressé' ? 'selected' : ''}}>❌ Pas intéressé</option>
              </select>
              ${{trackingDetails}}
              ${{alertHtml}}
            </div>
          </td>
          <td class="py-4 px-4 text-right">
            <div class="flex items-center justify-end gap-1.5">
              ${{item.primary_email ? `
                <button onclick="sendDirect1Click(${{realIndex}}, this)" class="px-2.5 py-1.5 rounded-lg bg-emerald-600/90 hover:bg-emerald-500 text-white font-semibold text-xs flex items-center gap-1 shadow-sm transition" title="Envoyer directement en 1 clic sans ouvrir d'interface">
                  <i class="fa-solid fa-bolt text-[10px]"></i> 1-Clic
                </button>
              ` : ''}}
              <button onclick="openModal(${{realIndex}})" class="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs flex items-center gap-1 border border-slate-700 transition" title="Voir la fiche, relances et messages">
                <i class="fa-solid fa-pen text-[10px] text-slate-400"></i> Fiche
              </button>
            </div>
          </td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    function switchTab(tab) {{
      currentTab = tab;
      const tabEmail = document.getElementById('tabEmail');
      const tabSms = document.getElementById('tabSms');
      const viewEmail = document.getElementById('viewEmail');
      const viewSms = document.getElementById('viewSms');

      if (tab === 'email') {{
        tabEmail.classList.add('bg-blue-600', 'text-white');
        tabEmail.classList.remove('bg-slate-800', 'text-slate-300');
        tabSms.classList.remove('bg-blue-600', 'text-white');
        tabSms.classList.add('bg-slate-800', 'text-slate-300');
        viewEmail.classList.remove('hidden');
        viewSms.classList.add('hidden');
      }} else {{
        tabSms.classList.add('bg-blue-600', 'text-white');
        tabSms.classList.remove('bg-slate-800', 'text-slate-300');
        tabEmail.classList.remove('bg-blue-600', 'text-white');
        tabEmail.classList.add('bg-slate-800', 'text-slate-300');
        viewEmail.classList.add('hidden');
        viewSms.classList.remove('hidden');
      }}
    }}

    function setSequenceStep(step) {{
      currentSequenceStep = step;
      document.querySelectorAll('.seq-btn').forEach(btn => {{
        btn.classList.remove('bg-blue-600', 'text-white');
        btn.classList.add('bg-slate-800', 'text-slate-400');
      }});

      if (step === 'initial') {{
        document.getElementById('stepBtnInitial').classList.add('bg-blue-600', 'text-white');
        document.getElementById('stepBtnInitial').classList.remove('bg-slate-800', 'text-slate-400');
      }} else if (step === 'followup1') {{
        document.getElementById('stepBtnFollowup1').classList.add('bg-blue-600', 'text-white');
        document.getElementById('stepBtnFollowup1').classList.remove('bg-slate-800', 'text-slate-400');
      }} else if (step === 'followup2') {{
        document.getElementById('stepBtnFollowup2').classList.add('bg-blue-600', 'text-white');
        document.getElementById('stepBtnFollowup2').classList.remove('bg-slate-800', 'text-slate-400');
      }}

      updateMessageContent();
    }}

    function updateMessageContent() {{
      if (!currentModalItem) return;
      const item = currentModalItem;
      const greeting = item.manager ? `Bonjour ${{item.manager}},` : 'Bonjour,';
      const cat = item.action_cat || {{}};

      let subject = '';
      let body = '';
      let smsBody = '';

      if (currentSequenceStep === 'initial') {{
        if (cat.key === 'agency') {{
          subject = `Renfort développement web freelance sur Aix-Marseille`;
          body = `${{greeting}}

Je me permets de vous contacter car j'apprécie beaucoup les projets et l'identité de ${{item.name}}.

Développeur web basé dans la région, j'interviens régulièrement en sous-traitance auprès d'agences de communication pour coder des maquettes Figma, intégrer des landing pages ultra-rapides (React / Next.js / Tailwind) ou ajouter des fonctionnalités sur-mesure lors de vos pics d'activité.

Vous pouvez découvrir mon profil et mes réalisations ici :
👉 https://joahdabidat.vercel.app

Seriez-vous ouvert à un rapide échange de 5 minutes cette semaine pour voir si nous pourrions collaborer sur de futurs projets clients ?

Bien cordialement,
Johad`;
          smsBody = `${{greeting}} Johad (développeur web freelance). J'aide les agences de la région en renfort technique (intégration maquettes / dev). Dispo 2 min par tél pour échanger ? Portfolio : https://joahdabidat.vercel.app`;
        }} else if (cat.key === 'create_site') {{
          subject = `Visibilité web de ${{item.name}} à ${{item.city}}`;
          body = `${{greeting}}

J'ai remarqué votre activité de ${{item.trade}} à ${{item.city}}. En faisant quelques recherches sur les entreprises de votre secteur dans la région, j'ai constaté que votre fiche d'établissement n'est reliée à aucun site internet officiel.

Aujourd'hui, plus de 80 % des clients de la région recherchent et comparent sur leur smartphone avant de demander un devis ou d'appeler. Sans site vitrine dédié, ces demandes partent directement chez vos concurrents.

Je suis développeur web basé dans la région et je conçois des landing pages ultra-rapides, modernes et optimisées pour le référencement local, prêtes en quelques jours seulement.

Vous pouvez consulter mes réalisations ici :
👉 https://joahdabidat.vercel.app

Seriez-vous ouvert à un rapide échange de 5 minutes cette semaine pour voir ce qu'on pourrait mettre en place simplement ?

Bien cordialement,
Johad`;
          smsBody = `${{greeting}} Johad d'Aix-Marseille (développeur web).
J'ai vu votre fiche de ${{item.trade}} à ${{item.city}}, mais vous n'avez pas de site web relié.
Je conçois des pages web rapides pour les artisans locaux : https://joahdabidat.vercel.app
Seriez-vous dispo pour un échange de 2 min par téléphone cette semaine ?`;
        }} else {{
          subject = `Optimisation du site internet de ${{item.name}}`;
          body = `${{greeting}}

Je me permets de vous contacter au sujet du site web de ${{item.name}} (${{item.audit?.url || ''}}).

En analysant la présence en ligne des entreprises de ${{item.city}}, j'ai relevé quelques points techniques qui pénalisent actuellement votre visibilité sur Google et votre conversion de clients :
${{(item.audit?.issues || []).map(i => '- ' + i).join('\\n')}}

Sur smartphone, chaque seconde de lenteur ou défaut d'affichage fait fuir un prospect cherchant un professionnel fiable.

Développeur web dans la région Aix-Marseille, j'aide les entreprises locales à moderniser leur présence en ligne avec des sites vitrines ultra-rapides, sécurisés et pensés pour convertir les visiteurs en appels et devis.

Vous pouvez découvrir mes projets ici :
👉 https://joahdabidat.vercel.app

Avez-vous 5 minutes d'ici la fin de semaine pour en discuter rapidement par téléphone ?

Bien cordialement,
Johad`;
          smsBody = `${{greeting}} Johad (développeur web). J'ai repéré quelques lenteurs sur le site de ${{item.name}} sur smartphone. Je peux vous l'optimiser pour booster vos appels. Dispo 2 min par tél ? Portfolio : https://joahdabidat.vercel.app`;
        }}

      }} else if (currentSequenceStep === 'followup1') {{
        subject = `Re: Visibilité web de ${{item.name}} à ${{item.city}}`;
        body = `${{greeting}}

Je me permets de faire remonter rapidement mon précédent message dans votre boîte mail.

Avez-vous eu l'occasion d'y jeter un œil concernant ${{cat.label.toLowerCase()}} pour ${{item.name}} sur ${{item.city}} ?

Pour rappel, vous pouvez voir quelques exemples de pages modernes et ultra-rapides que je réalise ici :
👉 https://joahdabidat.vercel.app

Seriez-vous disponible pour un échange rapide de 5 minutes par téléphone cette semaine ?

Bien cordialement,
Johad`;
        smsBody = `${{greeting}} Johad (développeur web). Je vous avais envoyé un message concernant ${{item.name}} sur ${{item.city}}. Seriez-vous disponible 2 min pour un échange rapide cette semaine ? (Portfolio : https://joahdabidat.vercel.app)`;

      }} else if (currentSequenceStep === 'followup2') {{
        subject = `Dernière tentative - Site internet ${{item.name}}`;
        body = `${{greeting}}

Je n'ai pas eu de retour à mes précédents messages, je suppose donc que ${{cat.label.toLowerCase()}} n'est pas votre priorité pour le moment.

Je ne vous relancerai plus pour ne pas encombrer votre messagerie.

Si toutefois le besoin se présente d'ici quelques mois pour développer vos demandes de devis sur ${{item.city}}, vous pouvez garder mon portfolio sous la main :
👉 https://joahdabidat.vercel.app

Je vous souhaite une excellente continuation dans vos projets !

Bien cordialement,
Johad`;
        smsBody = `${{greeting}} Johad. Je suppose que le site web n'est pas d'actualité pour ${{item.name}}, je ne vous relance plus. Je vous laisse mon contact si besoin : https://joahdabidat.vercel.app - Bonne continuation !`;
      }}

      document.getElementById('modalSubject').textContent = subject;
      document.getElementById('modalBody').textContent = body;
      document.getElementById('modalSmsBody').textContent = smsBody;

      updateActionButtons();
    }}

    function refreshModalTrackingView() {{
      if (!currentModalItem) return;
      const item = currentModalItem;
      const formattedDate = formatRelativeDate(item.contacted_at);
      const textEl = document.getElementById('modalTrackingText');
      const iconEl = document.getElementById('modalTrackingIcon');

      if (item.contacted_at) {{
        const channelLabel = item.last_channel === 'phone' ? 'Téléphone' : (item.last_channel === 'sms' ? 'SMS' : 'Email');
        iconEl.innerHTML = `<i class="fa-solid fa-circle-check text-emerald-400"></i>`;
        textEl.innerHTML = `Démarché : <strong class="text-white">${{formattedDate}}</strong> via ${{channelLabel}} (${{item.contact_count || 1}} prise(s) de contact)`;
      }} else {{
        iconEl.innerHTML = `<i class="fa-solid fa-clock text-slate-500"></i>`;
        textEl.textContent = "Jamais démarché pour le moment";
      }}
    }}

    function openModal(index, defaultTab = null) {{
      const item = data[index];
      currentModalItem = item;
      currentModalIndex = index;
      
      const cat = item.action_cat || {{}};
      document.getElementById('modalCompanyName').textContent = item.name;
      document.getElementById('modalCompanyInfo').textContent = (item.trade || '') + ' • ' + (item.city || '') + (item.manager ? ' • Gérant : ' + item.manager : '');
      
      // Encadré de l'action conseillée
      document.getElementById('modalActionLabel').textContent = cat.label || 'Action recommandée';
      document.getElementById('modalActionOffer').textContent = cat.offer || 'Prestation sur-mesure';
      document.getElementById('modalActionPrice').textContent = cat.price || 'Sur devis';
      
      const actionBox = document.getElementById('modalActionBox');
      const actionIcon = document.getElementById('modalActionIcon');
      actionBox.className = `p-3 rounded-xl border flex items-center justify-between gap-3 ${{cat.badge_class}}`;
      actionIcon.innerHTML = `<i class="fa-solid ${{cat.icon || 'fa-bolt'}}"></i>`;

      const gQuery = encodeURIComponent(item.name + ' ' + item.city + ' contact');
      document.getElementById('btnGoogleSearch').href = `https://www.google.com/search?q=${{gQuery}}`;

      document.getElementById('modalTargetEmailInput').value = item.primary_email || '';
      document.getElementById('modalTargetPhoneInput').value = item.primary_phone || '';

      refreshModalTrackingView();

      if (item.status === 'Contacté') {{
        setSequenceStep('followup1');
      }} else if (item.status === 'Relancé 1') {{
        setSequenceStep('followup2');
      }} else {{
        setSequenceStep('initial');
      }}

      if (defaultTab) {{
        switchTab(defaultTab);
      }} else if (item.primary_email) {{
        switchTab('email');
      }} else if (item.primary_phone) {{
        switchTab('sms');
      }} else {{
        switchTab('email');
      }}

      document.getElementById('emailModal').classList.remove('hidden');
    }}

    function onContactInfoChanged() {{
      if (!currentModalItem) return;
      const newEmail = document.getElementById('modalTargetEmailInput').value.trim();
      const newPhone = document.getElementById('modalTargetPhoneInput').value.trim();

      currentModalItem.primary_email = newEmail;
      currentModalItem.primary_phone = newPhone;

      saveLocalData();
      updateActionButtons();
      renderTable();
    }}

    function updateActionButtons() {{
      if (!currentModalItem) return;
      const email = document.getElementById('modalTargetEmailInput').value.trim();
      const phone = document.getElementById('modalTargetPhoneInput').value.trim();
      const subject = encodeURIComponent(document.getElementById('modalSubject').textContent);
      const body = encodeURIComponent(document.getElementById('modalBody').textContent);
      const smsBody = encodeURIComponent(document.getElementById('modalSmsBody').textContent);

      const btnEmail = document.getElementById('btnMailtoSend');
      btnEmail.href = `mailto:${{email}}?subject=${{subject}}&body=${{body}}`;

      const btnWhatsApp = document.getElementById('btnWhatsAppSend');
      const phoneCall = document.getElementById('modalPhoneCall');
      if (phone) {{
        const cleanPhone = phone.replace(/[^0-9]/g, '');
        const intlPhone = cleanPhone.startsWith('0') ? '33' + cleanPhone.slice(1) : cleanPhone;
        btnWhatsApp.href = `https://wa.me/${{intlPhone}}?text=${{smsBody}}`;
        phoneCall.href = `tel:${{cleanPhone}}`;
        phoneCall.classList.remove('hidden');
      }} else {{
        btnWhatsApp.href = document.getElementById('btnGoogleSearch').href;
        phoneCall.classList.add('hidden');
      }}
    }}

    function closeModal() {{
      document.getElementById('emailModal').classList.add('hidden');
    }}

    function copyEmailText() {{
      const subject = document.getElementById('modalSubject').textContent;
      const body = document.getElementById('modalBody').textContent;
      const text = (subject ? "Objet: " + subject + "\\n\\n" : "") + body;
      navigator.clipboard.writeText(text).then(() => {{
        const btn = document.getElementById('btnCopyText');
        const oldHtml = btn.innerHTML;
        btn.innerHTML = `<i class="fa-solid fa-check text-emerald-400"></i> Copié !`;
        setTimeout(() => {{ btn.innerHTML = oldHtml; }}, 2000);
      }});
    }}

    function copySmsText() {{
      const body = document.getElementById('modalSmsBody').textContent;
      navigator.clipboard.writeText(body).then(() => {{
        const btn = document.getElementById('btnCopySmsText');
        const oldHtml = btn.innerHTML;
        btn.innerHTML = `<i class="fa-solid fa-check text-emerald-400"></i> Copié !`;
        setTimeout(() => {{ btn.innerHTML = oldHtml; }}, 2000);
      }});
    }}

    let isCampaignRunning = false;

    async function sendDirect1Click(index, btnElement) {{
      const item = data[index];
      if (!item.primary_email) {{
        alert("Aucun email renseigné pour cette entreprise.");
        return;
      }}

      const originalHtml = btnElement.innerHTML;
      btnElement.disabled = true;
      btnElement.innerHTML = `<i class="fa-solid fa-spinner fa-spin text-[10px]"></i>`;

      const greeting = item.manager ? `Bonjour ${{item.manager}},` : 'Bonjour,';
      const cat = item.action_cat || {{}};
      let subject = item.pitch?.subject || `Visibilité web de ${{item.name}} à ${{item.city}}`;
      let body = item.pitch?.body || '';

      if (cat.key === 'agency') {{
        subject = `Renfort développement web freelance sur Aix-Marseille`;
        body = `${{greeting}}\\n\\nJe me permets de vous contacter car j'apprécie beaucoup les projets et l'identité de ${{item.name}}.\\n\\n👉 https://joahdabidat.vercel.app\\n\\nBien cordialement,\\nJohad`;
      }}

      try {{
        const response = await fetch('http://localhost:8088/api/send_email', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            to: item.primary_email,
            subject: subject,
            body: body
          }})
        }});

        if (response.ok) {{
          btnElement.className = "px-2.5 py-1.5 rounded-lg bg-emerald-600 text-white font-semibold text-xs flex items-center gap-1 shadow-sm";
          btnElement.innerHTML = `<i class="fa-solid fa-check text-[10px]"></i> Envoyé`;
          recordContactNow(index, 'email');
        }} else {{
          throw new Error('Erreur serveur');
        }}
      }} catch (err) {{
        btnElement.innerHTML = originalHtml;
        btnElement.disabled = false;
        if (confirm("Le serveur d'envoi rapide n'est pas encore actif.\\n\\nVoulez-vous ouvrir Apple Mail en mode classique pour ce prospect ?\\n(Pour l'envoi 1-clic direct en tâche de fond sans ouvrir Mail, lancez simplement './server.py' dans le terminal).")) {{
          const mailtoUrl = `mailto:${{item.primary_email}}?subject=${{encodeURIComponent(subject)}}&body=${{encodeURIComponent(body)}}`;
          window.location.href = mailtoUrl;
          recordContactNow(index, 'email');
        }}
      }}
    }}

    async function startBatchCampaign() {{
      const filteredTodo = data.filter(item => {{
        const catKey = item.action_cat?.key || 'create_site';
        if (currentCategory !== 'all' && catKey !== currentCategory) return false;
        // Cibler uniquement les non contactés avec email
        const isAlreadyContacted = item.status !== 'À contacter' || !!item.contacted_at;
        return item.primary_email && !isAlreadyContacted;
      }});

      if (filteredTodo.length === 0) {{
        alert("Aucun prospect non contacté avec email disponible dans cette sélection.");
        return;
      }}

      if (!confirm(`Lancer la campagne automatique sur les ${{filteredTodo.length}} entreprises NON CONTACTÉES sélectionnées ?\\n\\nLes emails seront envoyés directement en tâche de fond l'un après l'autre via Apple Mail et chaque entreprise sera automatiquement horodatée.`)) {{
        return;
      }}

      isCampaignRunning = true;
      const banner = document.getElementById('campaignBanner');
      const progressBar = document.getElementById('campaignProgressBar');
      const statusText = document.getElementById('campaignStatusText');
      banner.classList.remove('hidden');

      let sentCount = 0;
      for (const item of filteredTodo) {{
        if (!isCampaignRunning) break;
        const index = data.indexOf(item);
        sentCount++;

        statusText.textContent = `Envoi en cours [${{sentCount}}/${{filteredTodo.length}}] : ${{item.name}} (${{item.primary_email}})...`;
        progressBar.style.width = `${{Math.round((sentCount / filteredTodo.length) * 100)}}%`;

        const greeting = item.manager ? `Bonjour ${{item.manager}},` : 'Bonjour,';
        const cat = item.action_cat || {{}};
        let subject = item.pitch?.subject || `Visibilité web de ${{item.name}} à ${{item.city}}`;
        let body = item.pitch?.body || '';

        try {{
          await fetch('http://localhost:8088/api/send_email', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
              to: item.primary_email,
              subject: subject,
              body: body
            }})
          }});
          recordContactNow(index, 'email');
        }} catch(e) {{
          console.error("Erreur envoi", item.name, e);
        }}

        if (sentCount < filteredTodo.length && isCampaignRunning) {{
          statusText.textContent = `Pause de sécurité anti-spam (15s) avant le prochain prospect [${{sentCount}}/${{filteredTodo.length}}]...`;
          await new Promise(r => setTimeout(r, 15000));
        }}
      }}

      statusText.textContent = `🎉 Campagne terminée ! ${{sentCount}} entreprises démarchées et horodatées avec succès.`;
      setTimeout(() => {{
        banner.classList.add('hidden');
      }}, 6000);
      isCampaignRunning = false;
    }}

    function stopCampaign() {{
      isCampaignRunning = false;
      document.getElementById('campaignStatusText').textContent = "Campagne interrompue.";
      setTimeout(() => {{
        document.getElementById('campaignBanner').classList.add('hidden');
      }}, 2000);
    }}

    function downloadLiveCsv() {{
      let csvContent = "data:text/csv;charset=utf-8,";
      csvContent += "Nom,Métier,Ville,Code Postal,Dirigeant,Email,Téléphone,Besoin,Offre,Tarif,Statut,Dernier Demarchage,Canal,Nombre Contacts\\n";
      data.forEach(p => {{
        const row = [
          `"${{(p.name || '').replace(/"/g, '""')}}"`,
          `"${{(p.trade || '').replace(/"/g, '""')}}"`,
          `"${{(p.city || '').replace(/"/g, '""')}}"`,
          `"${{(p.postal_code || '').replace(/"/g, '""')}}"`,
          `"${{(p.manager || '').replace(/"/g, '""')}}"`,
          `"${{(p.primary_email || '').replace(/"/g, '""')}}"`,
          `"${{(p.primary_phone || '').replace(/"/g, '""')}}"`,
          `"${{(p.action_cat?.label || '').replace(/"/g, '""')}}"`,
          `"${{(p.action_cat?.offer || '').replace(/"/g, '""')}}"`,
          `"${{(p.action_cat?.price || '').replace(/"/g, '""')}}"`,
          `"${{(p.status || 'À contacter').replace(/"/g, '""')}}"`,
          `"${{(p.contacted_at || 'Jamais').replace(/"/g, '""')}}"`,
          `"${{(p.last_channel || 'Aucun').replace(/"/g, '""')}}"`,
          `"${{p.contact_count || 0}}"`
        ];
        csvContent += row.join(",") + "\\n";
      }});
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      link.setAttribute("download", "prospects_avec_suivi.csv");
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }}

    document.addEventListener('DOMContentLoaded', () => {{
      renderTable();
    }});
  </script>
</body>
</html>
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
