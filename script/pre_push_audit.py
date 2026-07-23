import os
import re
from bs4 import BeautifulSoup, FeatureNotFound
from datetime import datetime

REPORT_FILENAME = "report_audit_pre_push.txt"

# Estensioni file da analizzare
HTML_EXTENSIONS = ('.html', '.htm')

# Pattern per la ricerca di possibili secret/chiavi esposte
SENSITIVE_PATTERNS = [
    (r'(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|password)\s*=\s*[\'"][^\'"]+[\'"]', "Possibile API Key o Token visibile"),
    (r'AIzaSy[a-zA-Z0-9_\-]{33}', "Chiave API Google Firebase/Maps visibile"),
    (r'ghp_[a-zA-Z0-9]{36}', "GitHub Personal Access Token visibile")
]

def check_html_syntax(content):
    """
    Verifica anomalie sintattiche elementari analizzando il bilanciamento dei tag principali
    e l'eventuale presenza di marcatori di conflitto Git (<<<<<<< / >>>>>>>).
    """
    errors = []
    
    # 1. Verifica conflitti Git non risolti
    if "<<<<<<< " in content or ">>>>>>> " in content:
        errors.append("Trovati marcatori di conflitto Git (<<<<<<< / >>>>>>>) nel file!")

    # 2. Controllo tag fondamentali
    lower_content = content.lower()
    if "<html" in lower_content and "</html>" not in lower_content:
        errors.append("Tag <html> aperto ma non chiuso correttamente.")
    if "<body" in lower_content and "</body>" not in lower_content:
        errors.append("Tag <body> aperto ma non chiuso correttamente.")
    if "<head" in lower_content and "</head>" not in lower_content:
        errors.append("Tag <head> aperto ma non chiuso correttamente.")
        
    return errors

def check_sensitive_data(content):
    """
    Cerca pattern di chiavi private, token o credenziali nei file HTML.
    """
    issues = []
    for pattern, desc in SENSITIVE_PATTERNS:
        if re.search(pattern, content):
            issues.append(desc)
    return issues

def audit_pre_push():
    root_dir = os.getcwd()
    total_files = 0
    total_links_checked = 0
    issues_found = []

    print("=== INIZIO AUDIT INTEGRALE PRE-PUSH GITHUB ===")

    for current_root, _, files in os.walk(root_dir):
        # Ignora la cartella di Git ed eventuali ambienti virtuali
        if '.git' in current_root or 'venv' in current_root or '__pycache__' in current_root:
            continue

        for file in files:
            if not file.endswith(HTML_EXTENSIONS):
                continue

            total_files += 1
            file_path = os.path.join(current_root, file)
            rel_file_path = os.path.relpath(file_path, root_dir).replace("\\", "/")

            # --- VERIFICA 1: Codifica UTF-8 ---
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                issues_found.append({
                    'file': rel_file_path,
                    'type': 'CODIFICA',
                    'detail': 'Il file non è salvato in UTF-8 valido (possibili caratteri accentati corrotti).'
                })
                continue
            except Exception as e:
                issues_found.append({
                    'file': rel_file_path,
                    'type': 'LETTURA',
                    'detail': f"Impossibile leggere il file: {e}"
                })
                continue

            # --- VERIFICA 2: Sintassi HTML ---
            syntax_errors = check_html_syntax(content)
            for err in syntax_errors:
                issues_found.append({
                    'file': rel_file_path,
                    'type': 'SINTASSI HTML',
                    'detail': err
                })

            # --- VERIFICA 3: Dati Sensibili / Secret ---
            sens_issues = check_sensitive_data(content)
            for issue in sens_issues:
                issues_found.append({
                    'file': rel_file_path,
                    'type': 'SICUREZZA',
                    'detail': issue
                })

            # Parser BeautifulSoup con html.parser per analisi collegamenti e asset
            try:
                soup = BeautifulSoup(content, 'html.parser')
            except Exception as e:
                issues_found.append({
                    'file': rel_file_path,
                    'type': 'PARSING',
                    'detail': f"Errore nel parsing HTML: {e}"
                })
                continue

            # --- VERIFICA 4: Audit Link (`<a href="...">`) ---
            for a_tag in soup.find_all('a', href=True):
                total_links_checked += 1
                href = a_tag['href'].strip()

                # Ignora link vuoti, javascript o ancore di pagina
                if not href or href == '#' or href.startswith(('mailto:', 'tel:', 'javascript:')):
                    continue

                # Controllo link esterni o assoluti
                if href.startswith(('http://', 'https://')):
                    # Se punta al dominio locale tempestivo.it
                    if 'tempestivo.it' in href:
                        # Estrae il percorso locale dall'URL
                        clean_path = re.sub(r'https?://[^/]+', '', href).split('#')[0].split('?')[0]
                        target_disk_path = os.path.normpath(os.path.join(root_dir, clean_path.lstrip('/')))
                        if os.path.isdir(target_disk_path):
                            target_disk_path = os.path.join(target_disk_path, "index.html")
                        if not os.path.exists(target_disk_path):
                            issues_found.append({
                                'file': rel_file_path,
                                'type': 'LINK ROTTO (404)',
                                'detail': f"Link assoluto interno verso risorsa inesistente: '{href}'"
                            })
                else:
                    # Link Relativo o con /
                    clean_href = href.split('#')[0].split('?')[0]
                    if clean_href:
                        if clean_href.startswith('/'):
                            target_path = os.path.normpath(os.path.join(root_dir, clean_href.lstrip('/')))
                        else:
                            target_path = os.path.normpath(os.path.join(os.path.dirname(file_path), clean_href))

                        if os.path.isdir(target_path):
                            target_path = os.path.join(target_path, "index.html")

                        if not os.path.exists(target_path):
                            issues_found.append({
                                'file': rel_file_path,
                                'type': 'LINK ROTTO (404)',
                                'detail': f"Link locale non trovato sul disco: '{href}' -> '{target_path}'"
                            })

            # --- VERIFICA 5: Asset Mancanti (Immagini e CSS) ---
            for img in soup.find_all('img', src=True):
                src = img['src'].strip()
                if src and not src.startswith(('http://', 'https://', 'data:')):
                    clean_src = src.split('#')[0].split('?')[0]
                    if clean_src.startswith('/'):
                        img_path = os.path.normpath(os.path.join(root_dir, clean_src.lstrip('/')))
                    else:
                        img_path = os.path.normpath(os.path.join(os.path.dirname(file_path), clean_src))

                    if not os.path.exists(img_path):
                        issues_found.append({
                            'file': rel_file_path,
                            'type': 'IMMAGINE MANCANTE',
                            'detail': f"Immagine non trovata sul disco: '{src}'"
                        })

    # --- GENERAZIONE DEL REPORT ---
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report_lines = [
        "=================================================================",
        "        REPORT AUDIT INTEGRALE PRE-PUSH GITHUB",
        "=================================================================",
        f"Data Esecuzione          : {now_str}",
        f"Cartella Principale      : {root_dir}",
        f"File HTML Analizzati     : {total_files}",
        f"Link Totali Verificati   : {total_links_checked}",
        f"Anomalie / Criticità     : {len(issues_found)}",
        "=================================================================\n"
    ]

    if issues_found:
        report_lines.append("DETTAGLIO CRITICITÀ E ANOMALIE RISCONTRATE:\n")
        for idx, item in enumerate(issues_found, start=1):
            report_lines.append(f"[{idx}] File: {item['file']}")
            report_lines.append(f"    ├─ Categoria Errore : {item['type']}")
            report_lines.append(f"    └─ Descrizione     : {item['detail']}")
            report_lines.append("-" * 65)
    else:
        report_lines.append("✅ NESSUN PROBLEMA RISCONTRATO! Il progetto è pronto per il push su GitHub.")

    report_content = "\n".join(report_lines)

    report_path = os.path.join(root_dir, REPORT_FILENAME)
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"\n[COMPLETATO] Report salvato con successo in: {REPORT_FILENAME}")
    except Exception as e:
        print(f"\n[ERRORE] Impossibile salvare il file di report: {e}")

    print(f"\nFile analizzati: {total_files} | Link controllati: {total_links_checked}")
    if issues_found:
        print(f"⚠️ TROVATE {len(issues_found)} CRITICITÀ! Apri '{REPORT_FILENAME}' per i dettagli.")
    else:
        print("✅ Tutto perfetto! Puoi procedere al commit e git push.")

if __name__ == "__main__":
    audit_pre_push()