import re
import time
import requests
from urllib.parse import urlparse, urljoin, quote
from bs4 import BeautifulSoup
from config import DIRECTORY_DOMAINS, USER_PORTFOLIO, USER_NAME

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def clean_phone_number(raw_phone):
    """Nettoie et formate un numéro de téléphone français."""
    cleaned = re.sub(r"[^\d+]", "", raw_phone)
    if cleaned.startswith("+33"):
        cleaned = "0" + cleaned[3:]
    if len(cleaned) == 10 and cleaned.startswith("0"):
        return " ".join([cleaned[i:i+2] for i in range(0, 10, 2)])
    return raw_phone.strip()

def search_companies_data_gouv(trade: str, postal_code: str, city_name: str, limit: int = 10):
    """
    Récupère les entreprises enregistrées via l'API publique data.gouv.fr.
    100% gratuit, sans clé d'API.
    """
    url = "https://recherche-entreprises.api.gouv.fr/search"
    params = {
        "q": trade,
        "code_postal": postal_code,
        "per_page": limit,
        "etat_administratif": "A"  # Uniquement entreprises actives
    }
    
    try:
        # L'API recherche-entreprises supporte le filtre departement et code_postal
        dept = postal_code[:2] if len(postal_code) >= 2 else "13"
        params["departement"] = dept
        
        response = requests.get(url, params=params, headers=HEADERS, timeout=8)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            companies = []
            for item in results:
                siege = item.get("siege", {})
                cp = siege.get("code_postal", "")
                
                # Filtrer pour s'assurer que le siège est bien dans le département
                if cp and not cp.startswith(dept):
                    continue
                    
                dirigeants = item.get("dirigeants", [])
                
                # Récupération propre du dirigeant principal
                dirigeant_str = ""
                if dirigeants:
                    d = dirigeants[0]
                    prenom = d.get("prenom", "").strip().capitalize()
                    nom = d.get("nom", "").strip().upper()
                    if nom:
                        dirigeant_str = f"{prenom} {nom}".strip()
                
                companies.append({
                    "name": item.get("nom_complet", "").title(),
                    "siren": item.get("siren", ""),
                    "address": siege.get("adresse", ""),
                    "postal_code": cp or postal_code,
                    "city": siege.get("commune", city_name).title(),
                    "trade": trade,
                    "manager": dirigeant_str,
                    "activity_code": item.get("activite_principale", "")
                })
            return companies
    except Exception as e:
        print(f"[-] Erreur data.gouv pour {trade} à {city_name}: {e}")
    return []

import base64

def find_official_website(company_name: str, city: str, postal_code: str):
    """
    Cherche si l'entreprise possède un site internet officiel
    via DuckDuckGo Lite POST (fiable et non bloqué).
    """
    query = f"{company_name} {city} {postal_code}"
    search_url = "https://lite.duckduckgo.com/lite/"
    
    try:
        response = requests.post(search_url, data={"q": query}, headers=HEADERS, timeout=7)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.find_all("a", class_="result-link")
            
            for link in links[:5]:
                raw_url = link.get("href", "").strip()
                if not raw_url.startswith("http"):
                    continue
                
                domain = urlparse(raw_url).netloc.lower()
                if domain.startswith("www."):
                    domain = domain[4:]
                
                # Vérifier si ce n'est pas un annuaire
                is_directory = any(d in domain for d in DIRECTORY_DOMAINS)
                if not is_directory and "." in domain:
                    return raw_url
    except Exception:
        pass
    return None

def decode_cloudflare_email(cf_hex: str):
    """Décode les emails masqués par Cloudflare email protection."""
    try:
        r = int(cf_hex[:2], 16)
        email = "".join([chr(int(cf_hex[i:i+2], 16) ^ r) for i in range(2, len(cf_hex), 2)])
        return email
    except Exception:
        return ""

def extract_contacts_from_html(html_text: str):
    """Extrait les emails et téléphones d'une page HTML, y compris ceux obfusqués en JS/Base64."""
    soup = BeautifulSoup(html_text, "html.parser")
    raw_emails = set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", html_text))
    
    # Détection des liens mailto:
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.lower().startswith("mailto:"):
            mail_part = href.split("?")[0].replace("mailto:", "").strip()
            if "@" in mail_part:
                raw_emails.add(mail_part)
                
    # Détection des emails masqués Joomla (base64)
    for hidden_tag in soup.find_all("joomla-hidden-mail"):
        for attr in ["text", "first"]:
            val = hidden_tag.get(attr, "")
            try:
                decoded = base64.b64decode(val).decode("utf-8")
                if "@" in decoded:
                    raw_emails.add(decoded)
            except Exception:
                pass
                
    # Détection des emails protégés par Cloudflare
    for cf in soup.find_all(attrs={"data-cfemail": True}):
        dec = decode_cloudflare_email(cf["data-cfemail"])
        if "@" in dec:
            raw_emails.add(dec)

    cleaned_emails = []
    for email in raw_emails:
        e = email.lower()
        if not any(e.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif", ".css", ".js"]):
            if "sentry" not in e and "wix" not in e and "example.com" not in e and "domain" not in e and "schema" not in e:
                cleaned_emails.append(email)
                
    cleaned_emails.sort(key=lambda x: 0 if any(k in x.lower() for k in ["contact", "info", "devis", "direction", "admin"]) else 1)
                
    # Numéros de téléphone français réels
    phone_matches = re.findall(r"(?:(?:\+|00)33[\s.-]{0,3}(?:\(0\)[\s.-]{0,3})?|0)[1-9](?:[\s.-]?\d{2}){4}", html_text)
    cleaned_phones = []
    seen_phones = set()
    for p in phone_matches:
        formatted = clean_phone_number(p)
        if formatted not in seen_phones and not formatted.startswith("01 55"):
            seen_phones.add(formatted)
            cleaned_phones.append(formatted)
            
    cleaned_phones.sort(key=lambda x: 0 if x.startswith("06") or x.startswith("07") else (1 if x.startswith("04") else 2))
    
    return cleaned_emails[:5], cleaned_phones[:3]

def audit_website(url: str):
    """
    Analyse technique d'un site : HTTPS, temps de réponse, responsive mobile,
    et scraping des emails/téléphones sur l'accueil et la page contact.
    """
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
            audit_data["issues"].append(f"Site très lent ({audit_data['load_time']}s)")
        elif audit_data["load_time"] > 1.8:
            audit_data["issues"].append(f"Vitesse améliorable ({audit_data['load_time']}s)")
            
        soup = BeautifulSoup(res.text, "html.parser")
        has_viewport = bool(soup.find("meta", attrs={"name": "viewport"}))
        audit_data["is_mobile_responsive"] = has_viewport
        if not has_viewport:
            audit_data["issues"].append("Non optimisé pour smartphone (manque balise viewport)")
            
        # Emails et téléphones page d'accueil
        emails, phones = extract_contacts_from_html(res.text)
        audit_data["emails"].extend(emails)
        audit_data["phones"].extend(phones)
        
        # Si pas d'email, fouiller la page contact ou mentions légales
        if not audit_data["emails"]:
            contact_links = []
            for a in soup.find_all("a", href=True):
                href = a["href"].lower()
                if any(k in href for k in ["contact", "mention", "propos", "legal"]):
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

def generate_pitch(company: dict, audit: dict):
    """
    Rédige un email personnalisé en fonction du diagnostic précis.
    """
    name = company.get("name", "l'équipe")
    city = company.get("city", "")
    trade = company.get("trade", "votre activité")
    manager = company.get("manager", "")
    
    greeting = f"Bonjour {manager}," if manager else "Bonjour,"
    
    if not audit.get("url"):
        # Cas 1 : Aucun site internet
        opportunity_type = "OR (Aucun site internet)"
        subject = f"Visibilité web de {name} à {city}"
        body = f"""{greeting}

J'ai remarqué votre activité de {trade} à {city}. En faisant quelques recherches sur vos concurrents dans la région, j'ai constaté que votre fiche d'entreprise n'est reliée à aucun site internet officiel.

Aujourd'hui, plus de 80 % des clients de la région recherchent et comparent sur leur smartphone avant de demander un devis ou d'appeler. Sans site vitrine dédié, ces demandes partent directement chez vos concurrents.

Je suis développeur web basé dans la région et je conçois des landing pages ultra-rapides, modernes et optimisées pour le référencement local, prêtes en quelques jours seulement.

Vous pouvez consulter mes réalisations et mon portfolio ici :
👉 {USER_PORTFOLIO}

Seriez-vous ouvert à un rapide échange de 5 minutes cette semaine pour voir ce qu'on pourrait mettre en place simplement ?

Bien cordialement,
{USER_NAME}
"""
    else:
        # Cas 2 : Site présent avec anomalies
        issues = audit.get("issues", [])
        opportunity_type = "ARGENT (Site améliorable)"
        subject = f"Optimisation du site internet de {name}"
        
        issue_bullets = ""
        if issues:
            issue_bullets = "\n".join([f"- {issue}" for issue in issues])
        else:
            issue_bullets = "- Temps de chargement et design sur mobile optimisables"
            
        body = f"""{greeting}

Je me permets de vous contacter au sujet du site web de {name} ({audit.get('url')}).

En analysant la présence en ligne des artisans et entreprises de {city}, j'ai relevé quelques points techniques qui pénalisent actuellement votre visibilité sur Google et votre conversion de clients :
{issue_bullets}

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

def enrich_missing_contacts(company_name: str, city: str):
    """
    Recherche les coordonnées publiques (téléphone, email) via les fiches d'annuaires
    quand l'entreprise n'a pas de site web propre.
    """
    phones = []
    emails = []
    query = f"{company_name} {city} telephone contact"
    url = "https://lite.duckduckgo.com/lite/"
    try:
        r = requests.post(url, data={"q": query}, headers=HEADERS, timeout=6)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            text = soup.get_text()
            
            # Recherche numéros de téléphone FR
            phone_matches = re.findall(r"(?:(?:\+|00)33[\s.-]{0,3}(?:\(0\)[\s.-]{0,3})?|0)[1-9](?:[\s.-]?\d{2}){4}", text)
            seen_p = set()
            for p in phone_matches:
                cleaned = clean_phone_number(p)
                # Éviter les faux positifs (numéros courts ou codes INSEE)
                if cleaned not in seen_p and not cleaned.startswith("01 55") and not cleaned.startswith("08"):
                    seen_p.add(cleaned)
                    phones.append(cleaned)
                    
            # Prioriser mobiles (06, 07) puis fixes régionaux (04)
            phones.sort(key=lambda x: 0 if x.startswith("06") or x.startswith("07") else (1 if x.startswith("04") else 2))
            
            # Recherche emails
            email_matches = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
            for e in set(email_matches):
                el = e.lower()
                if not any(el.endswith(ext) for ext in [".png", ".jpg", ".css", ".js", ".svg"]):
                    if "duckduckgo" not in el and "sentry" not in el and "example" not in el:
                        emails.append(e)
    except Exception:
        pass
        
    return phones[:3], emails[:2]

def analyze_prospect(company: dict):
    """Effectue l'analyse complète d'une entreprise."""
    website = find_official_website(company["name"], company["city"], company["postal_code"])
    
    if website:
        audit = audit_website(website)
    else:
        # Recherche approfondie des contacts sur les fiches locales
        ext_phones, ext_emails = enrich_missing_contacts(company["name"], company["city"])
        audit = {
            "url": None,
            "is_accessible": False,
            "is_https": False,
            "load_time": None,
            "is_mobile_responsive": False,
            "emails": ext_emails,
            "phones": ext_phones,
            "issues": ["Aucun site web officiel (Uniquement fiche annuaire / Google Maps)"]
        }
        
    pitch = generate_pitch(company, audit)
    
    return {
        **company,
        "audit": audit,
        "pitch": pitch,
        "primary_email": audit["emails"][0] if audit["emails"] else "",
        "primary_phone": audit["phones"][0] if audit["phones"] else "",
        "all_emails": audit["emails"],
        "all_phones": audit["phones"]
    }
