import os
import time
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build

JSON_KEY_FILE = "chiave_google.json"
DOMAIN = DOMAIN = "https://tempestivo.it/carini"
PAGES_DIR = "."   # root da cui far partire la ricerca ricorsiva

SCOPES = ["https://www.googleapis.com/auth/indexing"]
credentials = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEY_FILE, scopes=SCOPES)
service = build("indexing", "v3", credentials=credentials)

# File di log
FILE_INVIATI = "inviati.txt"
FILE_FALLITI = "falliti.txt"

# Cartelle da ignorare durante la scansione
IGNORED_DIRS = {'.git', 'venv', 'env', '__pycache__', '.vscode'}

# Carica gli URL già inviati
if os.path.exists(FILE_INVIATI):
    with open(FILE_INVIATI, "r", encoding="utf-8") as f:
        inviati = set(line.strip() for line in f.readlines())
else:
    inviati = set()

def registra(file, url):
    with open(file, "a", encoding="utf-8") as f:
        f.write(url + "\n")

def invia_url(url):
    body = {"url": url, "type": "URL_UPDATED"}
    try:
        response = service.urlNotifications().publish(body=body).execute()
        print(f"✔ Inviato: {url}")
        registra(FILE_INVIATI, url)
    except Exception as e:
        print(f"❌ Errore per {url}: {e}")
        registra(FILE_FALLITI, url)

# --- CONFIGURAZIONE BATCH E PAUSE ---
batch_size = 10
pause_seconds = 120  # 2 minuti

# --- GENERAZIONE LISTA URL RICORSIVA ---
urls = []

# os.walk naviga la root e TUTTE le sottocartelle
for current_root, dirs, files in os.walk(PAGES_DIR):
    # Ignora cartelle di sistema/ambiente virtuale per evitare invii errati
    dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

    for filename in files:
        if filename.endswith(".html"):
            # Costruisce il percorso completo del file
            full_path = os.path.join(current_root, filename)
            
            # Calcola il percorso relativo rispetto alla root e normalizza gli slash per gli URL Web
            rel_path = os.path.relpath(full_path, PAGES_DIR).replace("\\", "/")
            
            # Gestione del prefisso /
            if rel_path.startswith("./"):
                rel_path = rel_path[2:]
            
            url = f"{DOMAIN}/{rel_path}"
            
            # Evita il reinvio se già presente in inviati.txt
            if url not in inviati:
                urls.append(url)

print(f"URL totali trovati nelle cartelle da inviare: {len(urls)}")

# --- INVIO IN BATCH ---
if urls:
    for i in range(0, len(urls), batch_size):
        batch = urls[i:i+batch_size]
        print(f"\n=== INVIO BATCH {i//batch_size + 1} ({len(batch)} URL) ===")
        for url in batch:
            invia_url(url)
            
        # Fai la pausa solo se ci sono ancora batch da inviare
        if i + batch_size < len(urls):
            print(f"⏳ Pausa {pause_seconds} secondi per evitare limiti di quota...")
            time.sleep(pause_seconds)

print("\n=== COMPLETATO ===")