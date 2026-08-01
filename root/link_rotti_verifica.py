import os
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup

def verifica_collegamenti():
    cartella_corrente = os.getcwd()
    print(f"Scansione della cartella: {cartella_corrente}\n")
    
    # Trova tutti i file HTML nella cartella e sottocartelle
    file_html = {}
    for root, dirs, files in os.walk(cartella_corrente):
        for file in files:
            if file.lower().endswith(('.html', '.htm')):
                percorso_assoluto = os.path.join(root, file)
                percorso_relativo = os.path.relpath(percorso_assoluto, cartella_corrente)
                file_html[percorso_relativo.replace('\\', '/')] = percorso_assoluto

    if not file_html:
        print("Nessun file HTML trovato nella cartella corrente.")
        return

    print(f"Trovati {len(file_html)} file HTML. Analisi dei link in corso...\n")

    totale_link_interni = 0
    link_errati = 0

    # Analizza ogni file HTML
    for rel_path, abs_path in file_html.items():
        try:
            with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
        except Exception as e:
            print(f"[ERRORE LETTURA] Impossibile leggere il file {rel_path}: {e}")
            continue

        # Trova tutti i tag 'a' con attributo 'href'
        tag_a = soup.find_all('a', href=True)
        
        for tag in tag_a:
            href = tag['href'].strip()
            
            # Salta anchor interne (es. #sezione), mailto, tel e link esterni assoluti (http/https)
            if not href or href.startswith(('#', 'mailto:', 'tel:', 'javascript:')):
                continue
            
            parsed_url = urlparse(href)
            if parsed_url.scheme in ('http', 'https', 'ftp'):
                # È un link esterno, lo saltiamo dalla verifica locale
                continue

            totale_link_interni += 1

            # Rimuove eventuali parametri di query o frammenti (es. pagina.html?id=1#top)
            percorso_pulito = parsed_url.path
            if not percorso_pulito:
                continue
            
            percorso_pulito = unquote(percorso_pulito)

            # Risolve il percorso del link rispetto alla posizione del file HTML corrente
            dir_file_corrente = os.path.dirname(abs_path)
            if percorso_pulito.startswith('/'):
                # Percorso assoluto rispetto alla root del progetto
                target_assoluto = os.path.normpath(os.path.join(cartella_corrente, percorso_pulito.lstrip('/')))
            else:
                # Percorso relativo
                target_assoluto = os.path.normpath(os.path.join(dir_file_corrente, percorso_pulito))

            # Verifica se il file di destinazione esiste sul disco
            if not os.path.exists(target_assoluto) or not os.path.isfile(target_assoluto):
                link_errati += 1
                print(f"[LINK ROTTO] In '{rel_path}':")
                print(f"  -> Href trovato: '{href}'")
                print(f"  -> Destinazione mancante: {os.path.relpath(target_assoluto, cartella_corrente)}\n")

    print("=" * 40)
    print("REPORT FINALE VERIFICA LINK")
    print("=" * 40)
    print(f"File HTML analizzati: {len(file_html)}")
    print(f"Collegamenti interni totali esaminati: {totale_link_interni}")
    print(f"Collegamenti rotti o errati trovati: {link_errati}")
    if link_errati == 0:
        print("\nOttimo! Tutti i collegamenti interni puntano a file esistenti.")
    else:
        print(f"\nAttenzione: sono stati rilevati {link_errati} link non funzionanti.")

if __name__ == '__main__':
    verifica_collegamenti()