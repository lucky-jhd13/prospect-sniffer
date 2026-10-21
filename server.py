#!/usr/bin/env python3
"""
Serveur local d'outreach automatique et API pour Prospect Sniffer.
Permet d'envoyer les emails en 1 clic directement en tâche de fond via Apple Mail macOS
et d'interagir avec les données des prospects.
"""

import http.server
import socketserver
import json
import subprocess
import webbrowser
import os
from urllib.parse import urlparse

from config import SERVER_PORT, SERVER_HOST, DATA_DIR, CSV_PATH
from database import get_all_prospects

PORT = SERVER_PORT

def send_via_apple_mail(to_email: str, subject: str, body: str):
    """Envoie un email directement en tâche de fond via Apple Mail macOS."""
    safe_subject = subject.replace('\\', '\\\\').replace('"', '\\"')
    safe_body = body.replace('\\', '\\\\').replace('"', '\\"')
    safe_to = to_email.replace('\\', '\\\\').replace('"', '\\"')

    applescript = f'''
    tell application "Mail"
        set newMessage to make new outgoing message with properties {{subject:"{safe_subject}", content:"{safe_body}", visible:false}}
        tell newMessage
            make new to recipient at end of to recipients with properties {{address:"{safe_to}"}}
        end tell
        send newMessage
        return "OK"
    end tell
    '''
    try:
        proc = subprocess.run(["osascript", "-e", applescript], capture_output=True, text=True, timeout=12)
        if proc.returncode == 0:
            return True, "Email envoyé avec succès via Apple Mail"
        else:
            return False, f"Erreur AppleScript : {proc.stderr.strip()}"
    except Exception as e:
        return False, str(e)

class OutreachHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/send_email':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                payload = json.loads(post_data.decode('utf-8'))
                to_email = payload.get('to', '').strip()
                subject = payload.get('subject', '').strip()
                body = payload.get('body', '').strip()

                if not to_email or '@' not in to_email:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": False, "error": "Email destinataire invalide"}).encode('utf-8'))
                    return

                success, msg = send_via_apple_mail(to_email, subject, body)
                
                self.send_response(200 if success else 500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": success, "message": msg}).encode('utf-8'))

            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/prospects':
            prospects = get_all_prospects()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(prospects, ensure_ascii=False).encode('utf-8'))
            return

        # Servir dashboard.html par défaut si racine
        if self.path == '/' or self.path == '':
            self.path = '/dashboard.html'
        return super().do_GET()

def start_server(open_browser: bool = True):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), OutreachHandler) as httpd:
        url = f"http://localhost:{PORT}/dashboard.html"
        print("=" * 65)
        print(f"🚀 Serveur actif sur : {url}")
        print("⚡ Envoi en 1-clic direct via Apple Mail activé !")
        print("=" * 65)
        if open_browser:
            webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nArrêt du serveur.")

if __name__ == "__main__":
    start_server(open_browser=True)
