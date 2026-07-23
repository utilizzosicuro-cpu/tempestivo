import os
import csv
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# URL base per simulare o verificare link assoluti
BASE_URL = "https://tempestivo.it"

def get_city_slugs(csv_path):
    """Legge la lista delle città dal CSV"""
    slugs = []
    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'slug' in row and row['slug']:
                    slugs.append(row['slug'].strip())
    except Exception as e:
        print(f"Errore nella lettura del CSV {csv_path}: {e}")
    return slugs

def update_footer_and_pages(current_dir, city_slugs):
    """Esegue tutte le modifiche e aggiornamenti ai link HTML richiesti"""
    updated_files = 0

    print("=== 1. APPLICAZIONE MODIFICHE AI LINK HTML ===")

    for root, _, files in os.walk(current_dir):
        for file in files:
            if not file.endswith('.html'):
                continue

            file_path = os.path.join(root, file)
            rel_file_path = os.path.relpath(file_path, current_dir).replace("\\", "/")

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"Errore lettura file {file_path}: {e}")
                continue

            soup = BeautifulSoup(content, 'html.parser')
            modified = False

            # --- A. MODIFICHE FOOTER (in tutte le pagine) ---
            footer = soup.find('footer')
            if footer:
                for a in footer.find_all('a'):
                    text = a.get_text(strip=True).lower()
                    
                    # 1. Ristrutturazioni
                    if "ristrutturazion" in text and "landing-ristrutturazioni.html" not in a.get('href', ''):
                        a['href'] = "/landing-ristrutturazioni.html"
                        modified = True

                    # 2. Pronto Intervento H24
                    elif "pronto intervento" in text and "pronto-intervento-palermo-trapani.html" not in a.get('href', ''):
                        a['href'] = "/pronto-intervento-palermo-trapani.html"
                        modified = True

                    # 3. Impianti Idraulici & Impianti Elettrici
                    elif ("idraulic" in text or "elettric" in text) and "servizi.html" not in a.get('href', ''):
                        a['href'] = "/servizi.html"
                        modified = True

                    # 4. Zone Principali nel Footer -> link alle index delle città
                    for slug in city_slugs:
                        if slug in text or slug.replace('-', ' ') in text:
                            # Se il testo si riferisce a una città del CSV, assegna il link /slug/index.html
                            target_href = f"/{slug}/index.html"
                            if a.get('href') != target_href:
                                a['href'] = target_href
                                modified = True

            # --- B. MODIFICHE PER PAGINE SPECIFICHE ---

            # Page: landing-ristrutturazioni.html (Zone servite)
            if file == "landing-ristrutturazioni.html":
                # Cerca contenitori/sezioni che contengono "zone servite"
                for container in soup.find_all(['section', 'div', 'ul']):
                    if "zone servite" in container.get_text().lower():
                        for a in container.find_all('a'):
                            a_text = a.get_text(strip=True).lower()
                            for slug in city_slugs:
                                if slug in a_text or slug.replace('-', ' ') in a_text:
                                    a['href'] = f"/{slug}/index.html"
                                    modified = True

            # Page: mappa-zone.html (Elenco Completo dei Comuni Serviti)
            if file == "mappa-zone.html":
                for container in soup.find_all(['section', 'div', 'ul']):
                    if "elenco completo dei comuni serviti" in container.get_text().lower() or "comuni serviti" in container.get_text().lower():
                        for a in container.find_all('a'):
                            a_text = a.get_text(strip=True).lower()
                            for slug in city_slugs:
                                if slug in a_text or slug.replace('-', ' ') in a_text:
                                    a['href'] = f"/{slug}/index.html"
                                    modified = True

            # Page: servizi.html (Dove operiamo)
            if file == "servizi.html":
                for container in soup.find_all(['section', 'div', 'ul']):
                    if "dove operiamo" in container.get_text().lower():
                        for a in container.find_all('a'):
                            a_text = a.get_text(strip=True).lower()
                            for slug in city_slugs:
                                if slug in a_text or slug.replace('-', ' ') in a_text:
                                    a['href'] = f"/{slug}/index.html"
                                    modified = True

            # Salva le modifiche se il file è stato alterato
            if modified:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(str(soup))
                    print(f"  [AGGIORNATO] {rel_file_path}")
                    updated_files += 1
                except Exception as e:
                    print(f"Errore scrittura {file_path}: {e}")

    print(f"\nModifiche completate su {updated_files} file HTML.\n")


def audit_links(current_dir):
    """Effettua una verifica globale di tutti i collegamenti ipertestuali (Audit 404 / Link tronchi)"""
    print("=== 2. VERIFICA E AUDIT DEI COLLEGAMENTI (LINK CHECKER) ===")
    
    broken_links = []
    total_links_checked = 0

    for root, _, files in os.walk(current_dir):
        for file in files:
            if not file.endswith('.html'):
                continue

            file_path = os.path.join(root, file)
            rel_source_file = os.path.relpath(file_path, current_dir).replace("\\", "/")

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')
            except Exception:
                continue

            for a in soup.find_all('a', href=True):
                href = a['href'].strip()
                total_links_checked += 1

                # Ignora ancore interne (#), mailto, tel e link javascript
                if href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:') or href.startswith('javascript:'):
                    continue

                # 1. Verifica Link Tronchi o Malformati
                if href in ["/", "http://", "https://", ""] or href.endswith("undefined") or "null" in href:
                    broken_links.append({
                        'source': rel_source_file,
                        'href': href,
                        'reason': 'Link tronco, vuoto o non valido'
                    })
                    continue

                # 2. Verifica Link Assoluti/Esterni
                if href.startswith("http://") or href.startswith("https://"):
                    # Se punta al proprio dominio ma con percorso inesistente
                    if BASE_URL in href:
                        parsed = urlparse(href)
                        local_target = parsed.path.lstrip('/')
                        target_full = os.path.join(current_dir, local_target)
                        if not os.path.exists(target_full) and not os.path.exists(target_full + ".html"):
                            broken_links.append({
                                'source': rel_source_file,
                                'href': href,
                                'reason': '404 - Pagina di destinazione non trovata sul server locale'
                            })
                    continue

                # 3. Verifica Link Relativi/Assoluti Locali (es. /palermo/index.html o palermo/index.html)
                clean_href = href.split('#')[0].split('?')[0]  # Rimuove query string e ancore
                
                if clean_href.startswith('/'):
                    target_path = os.path.join(current_dir, clean_href.lstrip('/'))
                else:
                    target_path = os.path.normpath(os.path.join(root, clean_href))

                # Se si tratta di una directory, controlla se esiste index.html al suo interno
                if os.path.isdir(target_path):
                    target_path_index = os.path.join(target_path, "index.html")
                    if not os.path.exists(target_path_index):
                        broken_links.append({
                            'source': rel_source_file,
                            'href': href,
                            'reason': '404 - La cartella non contiene un file index.html'
                        })
                elif not os.path.exists(target_path):
                    broken_links.append({
                        'source': rel_source_file,
                        'href': href,
                        'reason': '404 - File HTML non trovato'
                    })

    # --- STAMPA E REPORT FINALE ---
    print("\n==========================================")
    print("REPORT DI VERIFICA DEI COLLEGAMENTI (AUDIT)")
    print("==========================================")
    print(f"Link totali analizzati: {total_links_checked}")
    print(f"Link difettosi/rotti rilevati: {len(broken_links)}")
    print("------------------------------------------")

    if broken_links:
        print("\nELENCO DETTAGLIATO LINK DIFETTOSI/404:\n")
        for idx, item in enumerate(broken_links, start=1):
            print(f"{idx}. File d'origine: {item['source']}")
            print(f"   Link errato:    '{item['href']}'")
            print(f"   Motivo:         {item['reason']}")
            print("-" * 42)
    else:
        print("\n✅ Nessun link rotto o difettoso riscontrato! Tutti i collegamenti sono validi.")

def main():
    current_dir = os.getcwd()
    csv_path = 'citta_2.csv' if os.path.exists('citta_2.csv') else 'citta.csv'

    if not os.path.exists(csv_path):
        print(f"Errore: CSV delle città non trovato ('citta_2.csv' o 'citta.csv')!")
        return

    city_slugs = get_city_slugs(csv_path)

    # Step 1: Applica tutte le modifiche ai link
    update_footer_and_pages(current_dir, city_slugs)

    # Step 2: Audit e verifica dei link
    audit_links(current_dir)

if __name__ == '__main__':
    main()