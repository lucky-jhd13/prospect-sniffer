"""
Moteur de Prospection Locale, Scraping Multi-Sources & Audit Technique.
Interroge le Registre National des Entreprises (data.gouv.fr), détecte les sites officiels,
extrait les coordonnées réelles et valide chaque email avec vérification DNS MX.
"""

import re
import time
import requests
import subprocess
import base64
from urllib.parse import urlparse, urljoin, parse_qs
from bs4 import BeautifulSoup
from config import DIRECTORY_DOMAINS, USER_PORTFOLIO, USER_NAME

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def clean_phone_number(raw_phone: str) -> str:
    """Nettoie et formate un numéro de téléphone français standard (10 chiffres)."""
    cleaned = re.sub(r"[^\d+]", "", raw_phone)
    if cleaned.startswith("+33"):
        cleaned = "0" + cleaned[3:]
    if len(cleaned) == 10 and cleaned.startswith("0"):
        return " ".join([cleaned[i:i+2] for i in range(0, 10, 2)])
    return raw_phone.strip()

def has_valid_mx(email: str) -> bool:
    """Vérifie la syntaxe et la présence d'un serveur de messagerie actif (DNS MX)."""
    if not email or "@" not in email:
        return False
    parts = email.strip().split("@")
    if len(parts) != 2:
        return False
    user, domain = parts[0].lower(), parts[1].lower()
    
    # Exclure les faux positifs / placeholders
    junk_domains = ["example.com", "domain.com", "wix.com", "wixpress.com", "sentry.io", "wordpress.com", "yoursite.com", "mysite.com"]
    if any(j in domain for j in junk_domains):
        return False
    if any(ext in domain for ext in [".png", ".jpg", ".jpeg", ".svg", ".css", ".js"]):
        return False
    if not (2 <= len(domain.split(".")[-1]) <= 10):
        return False

    try:
        out = subprocess.check_output(["dig", "+short", "MX", domain], timeout=2).decode().strip()
        return bool(out)
    except Exception:
        return False

def search_companies_data_gouv(trade: str, postal_code: str, city_name: str, limit: int = 10) -> list:
    """
    Récupère les entreprises enregistrées actives via l'API publique data.gouv.fr.
    100% gratuit, officiel et sans clé d'API.
    """
    url = "https://recherche-entreprises.api.gouv.fr/search"
    dept = postal_code[:2] if len(postal_code) >= 2 else "13"
    params = {
        "q": trade,
        "code_postal": postal_code,
        "departement": dept,
        "per_page": limit,
        "etat_administratif": "A"  # Uniquement entreprises actives
    }
    
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=8)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            companies = []
            for item in results:
                siege = item.get("siege", {})
                cp = siege.get("code_postal", "")
                
                # S'assurer que le code postal correspond au département
                if cp and not cp.startswith(dept):
                    continue
                    
                dirigeants = item.get("dirigeants", [])
                dirigeant_str = ""
                if dirigeants:
                    d = dirigeants[0]
                    prenom = d.get("prenom", "").strip().capitalize()
                    nom = d.get("nom", "").strip().upper()
                    if nom:
                        dirigeant_str = f"{prenom} {nom}".strip()
                
                commune_nom = siege.get("libelle_commune") or city_name
                companies.append({
                    "name": item.get("nom_complet", "").title(),
                    "siren": item.get("siren", ""),
                    "address": siege.get("adresse", ""),
                    "postal_code": cp or postal_code,
                    "city": commune_nom.title(),
                    "trade": trade,
                    "manager": dirigeant_str,
                    "activity_code": item.get("activite_principale", "")
                })
            return companies
    except Exception as e:
        print(f"[-] Erreur data.gouv ({trade} à {city_name}): {e}")
    return []

def find_official_website(company_name: str, city: str, postal_code: str) -> str:
    """Cherche le site internet officiel d'une entreprise via moteur de recherche."""
    query = f"{company_name} {city} {postal_code}"
    search_url = "https://lite.duckduckgo.com/lite/"
    
    try:
        response = requests.post(search_url, data={"q": query}, headers=HEADERS, timeout=7)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.find_all("a", class_="result-link")
            
            for link in links[:8]:
                raw_url = link.get("href", "").strip()
                if not raw_url:
                    continue
                
                # Si DuckDuckGo redirige via uddg=
                if "duckduckgo.com" in raw_url and "uddg=" in raw_url:
                    parsed_link = urlparse(raw_url)
                    qs = parse_qs(parsed_link.query)
                    if "uddg" in qs:
                        raw_url = qs["uddg"][0]
                elif raw_url.startswith("//"):
                    raw_url = "https:" + raw_url
                
                if not raw_url.startswith("http"):
                    continue
                
                parsed_res = urlparse(raw_url)
                domain = parsed_res.netloc.lower()
                path = parsed_res.path.lower()
                if domain.startswith("www."):
                    domain = domain[4:]
                
                # Vérifier si ce n'est pas un annuaire d'entreprises ou plateforme de mise en relation
                is_directory = (
                    any(d in domain for d in DIRECTORY_DOMAINS)
                    or domain.startswith("entreprises.")
                    or domain.startswith("annuaire.")
                    or any(w in domain for w in ["annuaire", "societe", "pagesjaunes", "economique", "starofservice", "travaux", "habitat", "topexemples", "manageo", "pappers", "infogreffe", "verif", "bilansgratuits", "kompass", "pages-", "mesdepanneurs", "allovoisins", "bing.", "google.", "duckduckgo.", "gazette", "e-pro.", "omizi."])
                )
                is_aggregator_path = any(path.startswith(p) for p in ["/professionnel/", "/professionnels/", "/entreprise/", "/entreprises/", "/societe/", "/siret/", "/annuaire/", "/pros/", "/artisans/"])
                
                if not is_directory and not is_aggregator_path and "." in domain:
                    return raw_url
    except Exception:
        pass
    return None

def search_directory_contacts(company_name: str, city: str, postal_code: str) -> tuple:
    """Recherche les coordonnées publiques (téléphone, email) sur les fiches annuaires publiques."""
    clean_name = re.sub(r"\b(SARL|SAS|SASU|EURL|EI|SA|SOCIETE)\b", "", company_name, flags=re.IGNORECASE).strip()
    query = f"{clean_name} {city} telephone"
    search_url = "https://lite.duckduckgo.com/lite/"
    
    phones = []
    emails = []
    try:
        response = requests.post(search_url, data={"q": query}, headers=HEADERS, timeout=7)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text()
            
            # Téléphones français réels (01 à 09)
            phone_matches = re.findall(r"(?:(?:\+|00)33[\s.-]{0,3}(?:\(0\)[\s.-]{0,3})?|0)[1-9](?:[\s.-]?\d{2}){4}", text)
            seen_p = set()
            for p in phone_matches:
                clean = clean_phone_number(p)
                # Éviter les faux numéros d'annuaires payants ou SIRET partiels
                if clean not in seen_p and not clean.startswith("08") and not clean.startswith("01 55"):
                    seen_p.add(clean)
                    phones.append(clean)
                    
            # Emails
            raw_emails = set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text))
            for em in raw_emails:
                if has_valid_mx(em):
                    emails.append(em)
    except Exception:
        pass
        
    # Prioriser portables 06/07 puis fixes régionaux 04
    phones.sort(key=lambda x: 0 if x.startswith("06") or x.startswith("07") else (1 if x.startswith("04") else 2))
    return emails[:2], phones[:2]

def decode_cloudflare_email(cf_hex: str) -> str:
    """Décode les emails masqués par Cloudflare email protection."""
    try:
        r = int(cf_hex[:2], 16)
        email = "".join([chr(int(cf_hex[i:i+2], 16) ^ r) for i in range(2, len(cf_hex), 2)])
        return email
    except Exception:
        return ""

def extract_contacts_from_html(html_text: str) -> tuple:
    """Extrait et valide les emails et téléphones d'une page HTML."""
    soup = BeautifulSoup(html_text, "html.parser")
    raw_emails = set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", html_text))
    
    # Liens mailto:
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.lower().startswith("mailto:"):
            mail_part = href.split("?")[0].replace("mailto:", "").strip()
            if "@" in mail_part:
                raw_emails.add(mail_part)
                
    # Emails masqués Joomla (base64)
    for hidden_tag in soup.find_all("joomla-hidden-mail"):
        for attr in ["text", "first"]:
            val = hidden_tag.get(attr, "")
            try:
                decoded = base64.b64decode(val).decode("utf-8")
                if "@" in decoded:
                    raw_emails.add(decoded)
            except Exception:
                pass
                
    # Emails masqués Cloudflare
    for cf in soup.find_all(attrs={"data-cfemail": True}):
        dec = decode_cloudflare_email(cf["data-cfemail"])
        if "@" in dec:
            raw_emails.add(dec)

    # Filtrer et valider chaque adresse via DNS MX
    verified_emails = []
    for email in raw_emails:
        if has_valid_mx(email):
            verified_emails.append(email)
            
    # Prioriser les boîtes directes contact / devis
    verified_emails.sort(key=lambda x: 0 if any(k in x.lower() for k in ["contact", "devis", "direction", "admin"]) else 1)
                
    # Téléphones
    phone_matches = re.findall(r"(?:(?:\+|00)33[\s.-]{0,3}(?:\(0\)[\s.-]{0,3})?|0)[1-9](?:[\s.-]?\d{2}){4}", html_text)
    cleaned_phones = []
    seen_phones = set()
    for p in phone_matches:
        formatted = clean_phone_number(p)
        if formatted not in seen_phones and not formatted.startswith("01 55") and not formatted.startswith("08"):
            seen_phones.add(formatted)
            cleaned_phones.append(formatted)
            
    cleaned_phones.sort(key=lambda x: 0 if x.startswith("06") or x.startswith("07") else (1 if x.startswith("04") else 2))
    
    return verified_emails[:3], cleaned_phones[:2]

def audit_website(url: str) -> dict:
    """Analyse technique d'un site web (SSL, vitesse, responsive) et extraction des contacts."""
    if not url.startswith("http"):
        url = "http://" + url
        
    audit_data = {
        "url": url,
        "is_accessible": False,
        "is_https": False,
        "load_time": None,
        "is_mobile_responsive": True,
        "emails": [],
        "phones": [],
        "issues": []
    }
    
    start_time = time.time()
    try:
        res = requests.get(url, headers=HEADERS, timeout=7, allow_redirects=True)
        audit_data["load_time"] = round(time.time() - start_time, 2)
        audit_data["is_accessible"] = True
        audit_data["url"] = res.url
        audit_data["is_https"] = res.url.startswith("https://")
        
        if not audit_data["is_https"]:
            audit_data["issues"].append("Pas de certificat SSL (Site non sécurisé HTTP)")
        if audit_data["load_time"] > 3.0:
            audit_data["issues"].append(f"Site très lent sur mobile ({audit_data['load_time']}s)")
        elif audit_data["load_time"] > 1.8:
            audit_data["issues"].append(f"Vitesse améliorable ({audit_data['load_time']}s)")
            
        soup = BeautifulSoup(res.text, "html.parser")
        has_viewport = bool(soup.find("meta", attrs={"name": "viewport"}))
        audit_data["is_mobile_responsive"] = has_viewport
        if not has_viewport:
            audit_data["issues"].append("Non adapté aux smartphones (balise viewport manquante)")
            
        # Contacts page d'accueil
        emails, phones = extract_contacts_from_html(res.text)
        audit_data["emails"].extend(emails)
        audit_data["phones"].extend(phones)
        
        # Si pas d'email, visiter la page contact / mentions légales
        if not audit_data["emails"]:
            contact_links = []
            for a in soup.find_all("a", href=True):
                href = a["href"].lower()
                if any(k in href for k in ["contact", "mention", "propos", "legal", "devis"]):
                    full_link = urljoin(res.url, a["href"])
                    if urlparse(full_link).netloc == urlparse(res.url).netloc:
                        contact_links.append(full_link)
            
            for c_link in contact_links[:2]:
                try:
                    c_res = requests.get(c_link, headers=HEADERS, timeout=5)
                    c_emails, c_phones = extract_contacts_from_html(c_res.text)
                    audit_data["emails"].extend(c_emails)
                    audit_data["phones"].extend(c_phones)
                    if audit_data["emails"]:
                        break
                except Exception:
                    pass
                    
        audit_data["emails"] = list(set(audit_data["emails"]))
        audit_data["phones"] = list(set(audit_data["phones"]))
        
    except requests.exceptions.SSLError:
        audit_data["issues"].append("Erreur de certificat SSL (alerte de sécurité sur navigateur)")
    except Exception as e:
        audit_data["issues"].append(f"Site inaccessible ou erreur technique ({type(e).__name__})")
        
    return audit_data

def generate_pitch(company: dict, audit: dict) -> dict:
    """Rédige un email et un SMS personnalisés en fonction du besoin détecté."""
    name = company.get("name", "l'équipe")
    city = company.get("city", "")
    trade = company.get("trade", "votre activité")
    manager = company.get("manager", "")
    
    greeting = f"Bonjour {manager}," if manager else "Bonjour,"
    trade_lower = trade.lower()
    
    if "agence" in trade_lower or "communication" in trade_lower:
        opportunity_type = "SOUS-TRAITANCE AGENCES"
        subject = f"Renfort développement web freelance sur Aix-Marseille"
        body = f"""{greeting}

Je me permets de vous contacter car j'apprécie beaucoup les projets et l'identité de {name}.

Développeur web basé dans la région, j'interviens régulièrement en renfort auprès d'agences pour coder des maquettes Figma, intégrer des landing pages ultra-rapides (React / Next.js / Tailwind) ou ajouter des fonctionnalités sur-mesure lors de vos pics d'activité.

Vous pouvez découvrir mon profil et mes réalisations ici :
👉 {USER_PORTFOLIO}

Seriez-vous ouvert à un rapide échange de 5 minutes cette semaine pour voir si nous pourrions collaborer sur de futurs projets clients ?

Bien cordialement,
{USER_NAME}
"""
    elif not audit.get("url") or audit.get("url") == "AUCUN":
        opportunity_type = "OR (Création de site web)"
        subject = f"Visibilité web de {name} à {city}"
        body = f"""{greeting}

J'ai remarqué votre activité de {trade} à {city}. En faisant quelques recherches sur les entreprises de votre secteur dans la région, j'ai constaté que votre fiche d'établissement n'est reliée à aucun site internet officiel.

Aujourd'hui, plus de 80 % des clients de la région recherchent et comparent sur leur smartphone avant de demander un devis ou d'appeler. Sans site vitrine dédié, ces demandes partent directement chez vos concurrents.

Je suis développeur web basé dans la région et je conçois des landing pages ultra-rapides, modernes et optimisées pour le référencement local, prêtes en quelques jours seulement.

Vous pouvez consulter mes réalisations ici :
👉 {USER_PORTFOLIO}

Seriez-vous ouvert à un rapide échange de 5 minutes cette semaine pour voir ce qu'on pourrait mettre en place simplement ?

Bien cordialement,
{USER_NAME}
"""
    else:
        opportunity_type = "ARGENT (Refonte & Vitesse)"
        issues_formatted = "\n".join([f"- {i}" for i in audit.get("issues", [])]) or "- Vitesse de chargement mobile améliorable"
        subject = f"Optimisation du site internet de {name}"
        body = f"""{greeting}

Je me permets de vous contacter au sujet du site web de {name} ({audit.get('url')}).

En analysant la présence en ligne des entreprises de {city}, j'ai relevé quelques points techniques qui pénalisent actuellement votre visibilité sur Google et votre conversion de clients :
{issues_formatted}

Sur smartphone, chaque seconde de lenteur ou défaut d'affichage fait fuir un prospect cherchant un professionnel fiable.

Développeur web dans la région Aix-Marseille, j'aide les entreprises locales à moderniser leur présence en ligne avec des sites vitrines ultra-rapides, sécurisés et pensés pour convertir les visiteurs en appels et devis.

Vous pouvez découvrir mes projets ici :
👉 {USER_PORTFOLIO}

Avez-vous 5 minutes d'ici la fin de semaine pour en discuter rapidement par téléphone ?

Bien cordialement,
{USER_NAME}
"""
    return {
        "opportunity_type": opportunity_type,
        "subject": subject,
        "body": body
    }

def analyze_prospect(company: dict) -> dict:
    """Orchestre la recherche de site, le crawl, l'extraction de contacts et l'audit."""
    name = company["name"]
    city = company["city"]
    postal_code = company["postal_code"]
    
    # 1. Détecter site web officiel
    website = find_official_website(name, city, postal_code)
    
    emails = []
    phones = []
    
    if website:
        audit = audit_website(website)
        emails = audit.get("emails", [])
        phones = audit.get("phones", [])
    else:
        audit = {
            "url": "AUCUN",
            "is_accessible": False,
            "is_https": False,
            "issues": ["Aucun site web officiel relié à la fiche Google"],
            "score": 0
        }
        
    # 2. Si pas d'email ou pas de téléphone, fouiller les annuaires publics
    if not emails or not phones:
        d_emails, d_phones = search_directory_contacts(name, city, postal_code)
        if not emails:
            emails.extend(d_emails)
        if not phones:
            phones.extend(d_phones)
            
    # 3. Générer le pitch adapté
    pitch = generate_pitch(company, audit)
    
    primary_email = emails[0] if emails else ""
    primary_phone = phones[0] if phones else ""
    
    return {
        **company,
        "audit": audit,
        "pitch": pitch,
        "primary_email": primary_email,
        "primary_phone": primary_phone,
        "all_emails": emails,
        "all_phones": phones,
        "status": "À contacter",
        "contacted_at": None,
        "last_channel": None,
        "contact_count": 0
    }
