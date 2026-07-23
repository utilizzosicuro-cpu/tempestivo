import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime

# Mappatura delle regole di correzione per testo del link
REPAIR_MAP = {
    "ristrutturazioni": "/landing-ristrutturazioni.html",
    "pronto intervento h24": "/pronto-intervento-palermo-trapani.html",
    "pronto intervento": "/pronto-intervento-palermo-trapani.html",
    "vedi tutte le zone": "/mappa-zone.html",
    "chi siamo": "/chi-siamo.html",
    "mappa delle zone": "/mappa-zone.html"
}

REPORT_FILENAME = "report_correzioni_footer.txt"


def is_link_broken(href, current_file_path, root_dir):
    """
    Verifica se un link del footer è rotto, vuoto o punta a un file non esistente.
    """
    href = href.strip()

    # Link vuoti, tronchi o segnaposto
    if href in ["", "#", "/", "http://", "https://"] or href.endswith("undefined") or "null" in href:
        return True, "Link vuoto, non valido o ancoraggio generico"

    # Ignora protocolli speciali (telefono, email, script)
    if href.startswith(("mailto:", "tel:", "javascript:")):
        return False, "Ok (link speciale)"

    # Pulisce da parametri URL o ancore
    clean_href = href.split('#')[0].split('?')[0]

    if not clean_href:
        return True, "Link vuoto o solo ancoraggio"

    # Risoluzione del percorso locale
    if clean_href.startswith('/'):
        target_path = os.path.join(root_dir, clean_href.lstrip('/'))
    else:
        target_path = os.path.normpath(os.path.join(os.path.dirname(current_file_path), clean_href))

    # Controllo esistenza cartella o file
    if os.path.isdir(target_path):
        target_index = os.path.join(target_path, "index.html")
        if not os.path.exists(target_index):
            return True, "La cartella di destinazione non contiene index.html"
    elif not os.path.exists(target_path):
        return True, "File di destinazione non trovato (404 locale)"

    return False, "Ok"


def process_and_fix_footers():
    root_dir = os.getcwd()
    total_files_scanned = 0
    modified_files_count = 0
    logs = []

    print("=== INIZIO VERIFICA E CORREZIONE LINK FOOTER ===")

    for current_root, _, files in os.walk(root_dir):
        for file in files:
            if not file.endswith('.html'):
                continue

            total_files_scanned += 1
            file_path = os.path.join(current_root, file)
            rel_file_path = os.path.relpath(file_path, root_dir).replace("\\", "/")

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                logs.append(f"[ERRORE LETTURA] {rel_file_path}: {e}")
                continue

            soup = BeautifulSoup(content, 'html.parser')
            footer = soup.find('footer')

            # Se la pagina non ha un <footer>, passa oltre
            if not footer:
                continue

            file_modified = False

            for a_tag in footer.find_all('a', href=True):
                href = a_tag['href']
                text = a_tag.get_text(strip=True).lower()

                # 1. Verifica se il link è rotto
                broken, reason = is_link_broken(href, file_path, root_dir)

                # 2. Se è rotto, prova a correggerlo in base al testo dell'ancora
                if broken:
                    new_href = None

                    # Cerca una corrispondenza nelle regole di riparazione
                    for key, target_url in REPAIR_MAP.items():
                        if key in text:
                            new_href = target_url
                            break

                    if new_href:
                        a_tag['href'] = new_href
                        file_modified = True
                        logs.append(
                            f"[CORRETTO] {rel_file_path}\n"
                            f"   ├─ Testo Link : '{a_tag.get_text(strip=True)}'\n"
                            f"   ├─ Link Errato: '{href}' ({reason})\n"
                            f"   └─ Nuovo Link : '{new_href}'"
                        )
                    else:
                        logs.append(
                            f"[SEGNALATO ROTTO - NO REGOLA] {rel_file_path}\n"
                            f"   ├─ Testo Link : '{a_tag.get_text(strip=True)}'\n"
                            f"   └─ Link Errato: '{href}' ({reason})"
                        )

            # Salva le modifiche solo se ci sono state correzioni effettive
            if file_modified:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(str(soup))
                    modified_files_count += 1
                except Exception as e:
                    logs.append(f"[ERRORE SCRITTURA] {rel_file_path}: {e}")

    # --- GENERAZIONE FILE REPORT ---
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report_lines = [
        "=================================================================",
        "        REPORT VERIFICA E CORREZIONE LINK FOOTER",
        "=================================================================",
        f"Data Esecuzione          : {now_str}",
        f"Cartella Scansionata     : {root_dir}",
        f"Pagine HTML Scansionate  : {total_files_scanned}",
        f"Pagine HTML Modificate   : {modified_files_count}",
        "=================================================================\n",
        "DETTAGLIO AZIONI ED EVENTI:\n"
    ]

    if logs:
        report_lines.extend(logs)
    else:
        report_lines.append("✅ Nessun link rotto riscontrato nei footer del sito!")

    report_content = "\n\n".join(report_lines) if isinstance(logs, list) else "\n".join(report_lines)

    report_path = os.path.join(root_dir, REPORT_FILENAME)
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"\n[COMPLETATO] Report generato con successo: {REPORT_FILENAME}")
    except Exception as e:
        print(f"\n[ERRORE] Impossibile salvare il report: {e}")

    print(f"File analizzati: {total_files_scanned} | File con footer aggiornati: {modified_files_count}")


if __name__ == "__main__":
    process_and_fix_footers()