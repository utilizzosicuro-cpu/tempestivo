import os
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup
from datetime import datetime

def verifica_internal_linking():
    cartella_corrente = os.getcwd()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"=== SCANSIONE RICORSIVA INTERNAL LINKING ===")
    print(f"Cartella di partenza: {cartella_corrente}\n")
    
    # 1. Trova tutti i file HTML nella cartella e sottocartelle
    file_html = {}
    for root, dirs, files in os.walk(cartella_corrente):
        # Esclude cartelle di sistema o ambienti virtuali comuni
        dirs[:] = [d for d in dirs if d not in {'.git', '.vscode', '__pycache__', 'venv', 'node_modules'}]
        
        for file in files:
            if file.lower().endswith(('.html', '.htm')):
                percorso_assoluto = os.path.join(root, file)
                percorso_relativo = os.path.relpath(percorso_assoluto, cartella_corrente)
                file_html[percorso_relativo.replace('\\', '/')] = percorso_assoluto

    if not file_html:
        print("Nessun file HTML trovato nella cartella corrente o nelle sottocartelle.")
        return

    print(f"Trovati {len(file_html)} file HTML in totale. Analisi dei link in corso...\n")

    totale_link_interni = 0
    link_corretti = 0
    link_errati = 0
    dettaglio_report = []

    # 2. Analisi dettagliata di ogni file HTML
    for rel_path, abs_path in file_html.items():
        try:
            with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            soup = BeautifulSoup(content, 'html.parser')
        except Exception as e:
            msg_err = f"[ERRORE LETTURA] Impossibile leggere il file {rel_path}: {e}"
            print(msg_err)
            dettaglio_report.append(msg_err)
            continue

        tag_a = soup.find_all('a', href=True)
        
        for tag in tag_a:
            href = tag['href'].strip()
            
            # Salta ancore interne (#), mailto, tel, javascript
            if not href or href.startswith(('#', 'mailto:', 'tel:', 'javascript:')):
                continue
            
            parsed_url = urlparse(href)
            # Salta link esterni assoluti (http, https, ftp)
            if parsed_url.scheme in ('http', 'https', 'ftp'):
                continue

            totale_link_interni += 1

            percorso_pulito = parsed_url.path
            if not percorso_pulito:
                # È probabilmente un link vuoto o solo con query/fragment
                continue
            
            percorso_pulito = unquote(percorso_pulito)

            # Risoluzione del percorso assoluto sul disco
            dir_file_corrente = os.path.dirname(abs_path)
            if percorso_pulito.startswith('/'):
                # Percorso assoluto rispetto alla root del progetto
                target_assoluto = os.path.normpath(os.path.join(cartella_corrente, percorso_pulito.lstrip('/')))
            else:
                # Percorso relativo rispetto al file HTML corrente
                target_assoluto = os.path.normpath(os.path.join(dir_file_corrente, percorso_pulito))

            # Verifica se la risorsa (file o cartella index implicita) esiste sul disco
            # Nota: se punta a una cartella senza specificare index.html, verifichiamo se esiste un index dentro quella cartella
            risorsa_esistente = False
            if os.path.exists(target_assoluto):
                if os.path.isfile(target_assoluto):
                    risorsa_esistente = True
                elif os.path.isdir(target_assoluto):
                    # Se punta a una cartella, controlliamo se esiste un index.html al suo interno
                    if os.path.exists(os.path.join(target_assoluto, 'index.html')):
                        risorsa_esistente = True

            if risorsa_esistente:
                link_corretti += 1
            else:
                link_errati += 1
                testo_ancora = tag.get_text(strip=True) or "[Immagine/Senza Testo]"
                riga_errore = (
                    f"LINK ROTTO:\n"
                    f"  - Pagina sorgente: {rel_path}\n"
                    f"  - Testo ancora:    '{testo_ancora}'\n"
                    f"  - Href trovato:    '{href}'\n"
                    f"  - Percorso atteso: {os.path.relpath(target_assoluto, cartella_corrente)}\n"
                )
                print(riga_errore)
                dettaglio_report.append(riga_errore)

    # 3. Creazione del Report Finale
    report_linee = [
        "=" * 60,
        "REPORT DETTAGLIATO INTERNAL LINKING",
        f"Data e Ora: {timestamp}",
        f"Cartella analizzata: {cartella_corrente}",
        "=" * 60,
        f"File HTML analizzati: {len(file_html)}",
        f"Collegamenti interni totali esaminati: {totale_link_interni}",
        f"Collegamenti corretti e funzionanti: {link_corretti}",
        f"Collegamenti rotti o errati trovati: {link_errati}",
        "=" * 60,
        "\nDETTAGLIO ERRORI RILEVATI:" if link_errati > 0 else "\nNessun link rotto trovato! Ottimo lavoro."
    ]

    report_linee.extend(dettaglio_report)
    
    output_report_path = os.path.join(cartella_corrente, "report_internal_linking.txt")
    with open(output_report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_linee))

    print("\n" + "=" * 40)
    print("VERIFICA COMPLETATA CON SUCCESSO")
    print(f"Collegamenti corretti: {link_corretti}")
    print(f"Collegamenti rotti: {link_errati}")
    print(f"Report dettagliato salvato in: {output_report_path}")
    print("=" * 40)

if __name__ == '__main__':
    verifica_internal_linking()