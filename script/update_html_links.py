import os
import re
import pandas as pd
from bs4 import BeautifulSoup

# Mappatura delle regole (testo del link -> nuovo href con slash /)
RULES = [
    # NAVBAR & LOGO
    {"regex": r"^chi\s*siamo$", "href": "/Chi-siamo.html"},
    {"regex": r"^servizi$", "href": "/servizi.html"},
    {"regex": r"^zone\s*coperte$", "href": "/mappa-zone.html"},
    {"regex": r"^ristrutturazioni\s*complete$", "href": "/landing-ristrutturazioni.html"},
    {"regex": r"^area\s*business$", "href": "/soluzioni-business-palermo-trapani.html"},

    # FOOTER
    {"regex": r"^ristrutturazioni$", "href": "/ristrutturazioni-palermo-trapani.html"},
    {"regex": r"^pronto\s*intervento\s*h24$", "href": "/pronto-intervento-palermo-trapani.html"},
    {"regex": r"^soluzioni\s*business$", "href": "/soluzioni-business-palermo-trapani.html"},
    {"regex": r"^mappa\s*delle\s*zone$", "href": "/mappa-zone.html"},
    {"regex": r"^privacy\s*policy$", "href": "/privacy.html"},
]

def process_html_file(file_path):
    """
    Legge un file HTML, aggiorna gli href corrispettivi per Logo, Navbar e Footer,
    e sovrascrive il file se ci sono state modifiche.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Errore durante la lettura di {file_path}: {e}")
        return False

    soup = BeautifulSoup(content, 'html.parser')
    modified = False

    # 1. Modifica Logo (classe .logo o .navbar-brand)
    logo_links = soup.select('a.logo, .logo a, a.navbar-brand')
    for link in logo_links:
        if link.get('href') != '/index.html':
            link['href'] = '/index.html'
            modified = True

    # 2. Modifica in base al testo visibile del link (Navbar e Footer)
    for a_tag in soup.find_all('a'):
        text = a_tag.get_text(strip=True)
        if not text:
            continue

        for rule in RULES:
            if re.match(rule["regex"], text, re.IGNORECASE):
                if a_tag.get('href') != rule["href"]:
                    a_tag['href'] = rule["href"]
                    modified = True
                break

    # Se il file è stato modificato, salva le modifiche
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        print(f"  [MODIFICATO] {file_path}")
        return True
    else:
        print(f"  [INVARIATO]  {file_path}")
        return False

def main():
    csv_filename = 'citta.csv'
    
    if not os.path.exists(csv_filename):
        print(f"Errore: File '{csv_filename}' non trovato nella cartella corrente.")
        return

    # Legge il CSV con Pandas prendendo la colonna degli slug/cartelle
    df = pd.read_csv(csv_filename)
    
    if 'slug' not in df.columns:
        print("Errore: La colonna 'slug' non è presente nel file CSV.")
        return

    citta_folders = df['slug'].dropna().unique().tolist()

    total_files = 0
    modified_files = 0

    print("=== INIZIO ELABORAZIONE PAGINE HTML ===")
    
    for city in citta_folders:
        folder_path = os.path.join(os.getcwd(), str(city))

        if not os.path.exists(folder_path):
            print(f"\n[SALTATA] Cartella non trovata: {city}")
            continue

        print(f"\n--- Scansione cartella città: {city} ---")

        # Cerca ricorsivamente tutti i file .html nella cartella della città
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(root, file)
                    total_files += 1
                    if process_html_file(file_path):
                        modified_files += 1

    print("\n==========================================")
    print(f"Elaborazione completata!")
    print(f"File HTML analizzati: {total_files}")
    print(f"File HTML aggiornati: {modified_files}")
    print("==========================================")

if __name__ == '__main__':
    main()