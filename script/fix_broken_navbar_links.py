import os
from bs4 import BeautifulSoup
from datetime import datetime

# Mappatura delle regole per testo del link
# (La chiave è il testo/parola chiave, i valori sono l'URL per sottocartella e l'URL per la root)
REPAIR_MAP = {
    "ristrutturazioni complete e veloci": {
        "sub": "/landing-ristrutturazioni.html",
        "root": "landing-ristrutturazioni.html"
    },
    "ristrutturazioni": {
        "sub": "/landing-ristrutturazioni.html",
        "root": "landing-ristrutturazioni.html"
    },
    "pronto intervento h24": {
        "sub": "/pronto-intervento-palermo-trapani.html",
        "root": "pronto-intervento-palermo-trapani.html"
    },
    "pronto intervento": {
        "sub": "/pronto-intervento-palermo-trapani.html",
        "root": "pronto-intervento-palermo-trapani.html"
    },
    "vedi tutte le zone": {
        "sub": "/mappa-zone.html",
        "root": "mappa-zone.html"
    },
    "zone coperte": {
        "sub": "/mappa-zone.html",
        "root": "mappa-zone.html"
    },
    "chi siamo": {
        "sub": "/chi-siamo.html",
        "root": "chi-siamo.html"
    }
}

REPORT_FILENAME = "report_correzioni_navbar.txt"


def is_link_broken(href, current_file_path, root_dir):
    """Verifica se un link della navbar è rotto, vuoto o punta a una destinazione inesistente."""
    href = href.strip()

    # Link vuoti, non validi o generici
    if href in ["", "#", "/", "http://", "https://"] or href.endswith("undefined") or "null" in href:
        return True, "Link vuoto, non valido o ancoraggio generico"

    # Ignora link a telefono, email o funzioni script
    if href.startswith(("mailto:", "tel:", "javascript:")):
        return False, "Ok (link speciale)"

    clean_href = href.split('#')[0].split('?')[0]

    if not clean_href:
        return True, "Link vuoto o solo ancoraggio"

    # Risoluzione del percorso locale
    if clean_href.startswith('/'):
        target_path = os.path.join(root_dir, clean_href.lstrip('/'))
    else:
        target_path = os.path.normpath(os.path.join(os.path.dirname(current_file_path), clean_href))

    # Controllo se il file o la cartella target esistono realmente sul disco
    if os.path.isdir(target_path):
        target_index = os.path.join(target_path, "index.html")
        if not os.path.exists(target_index):
            return True, "La cartella di destinazione non contiene index.html"
    elif not os.path.exists(target_path):
        return True, "File di destinazione non trovato (404 locale)"

    return False, "Ok"


def find_navbar_element(soup):
    """Individua l'elemento nav/navbar all'interno della pagina HTML."""
    # 1. Cerca il tag standard <nav>
    nav = soup.find('nav')
    if nav:
        return nav

    # 2. Cerca elementi div/header con classi o id tipo 'navbar' o 'menu'
    for tag in soup.find_all(['header', 'div', 'section']):
        classes = tag.get('class', [])
        tag_id = tag.get('id', '')
        
        class_str = ' '.join(classes).lower() if isinstance(classes, list) else str(classes).lower()
        if 'navbar' in class_str or 'menu' in class_str or 'navbar' in str(tag_id).lower():
            return tag

    return None


def process_and_fix_navbars():
    root_dir = os.getcwd()
    total_files_scanned = 0
    modified_files_count = 0
    logs = []

    print("=== INIZIO VERIFICA E CORREZIONE LINK NAVBAR ===")

    for current_root, _, files in os.walk(root_dir):
        for file in files:
            if not file.endswith('.html'):
                continue

            total_files_scanned += 1
            file_path = os.path.join(current_root, file)
            rel_file_path = os.path.relpath(file_path, root_dir).replace("\\", "/")

            # Stabilisce se il file si trova nella ROOT o in una SOTTOCARTELLA
            is_in_root = (os.path.dirname(file_path) == root_dir)

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                logs.append(f"[ERRORE LETTURA] {rel_file_path}: {e}")
                continue

            soup = BeautifulSoup(content, 'html.parser')
            navbar = find_navbar_element(soup)

            # Se non trova una navbar/menu nel file, passa al successivo
            if not navbar:
                continue

            file_modified = False

            for a_tag in navbar.find_all('a', href=True):
                href = a_tag['href']
                text = a_tag.get_text(strip=True).lower()

                # Verifica se il link della navbar risulta rotto
                broken, reason = is_link_broken(href, file_path, root_dir)

                if broken:
                    new_href = None

                    # Identifica la regola di riparazione corretta in base al testo dell'ancora
                    for key, target_urls in REPAIR_MAP.items():
                        if key in text:
                            # Assegna il link senza '/' se in root, oppure con '/' se in sottocartella
                            new_href = target_urls["root"] if is_in_root else target_urls["sub"]
                            break

                    if new_href:
                        a_tag['href'] = new_href
                        file_modified = True
                        location_type = "ROOT (senza /)" if is_in_root else "SOTTOCARTELLA (con /)"
                        logs.append(
                            f"[CORRETTO] {rel_file_path} [{location_type}]\n"
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

            # Salva il file solo se ci sono state modifiche
            if file_modified:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(str(soup))
                    modified_files_count += 1
                except Exception as e:
                    logs.append(f"[ERRORE SCRITTURA] {rel_file_path}: {e}")

    # --- GENERAZIONE DEL REPORT SU FILE ---
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report_lines = [
        "=================================================================",
        "        REPORT VERIFICA E CORREZIONE LINK NAVBAR",
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
        report_lines.append("✅ Nessun link rotto riscontrato nelle navbar del sito!")

    report_content = "\n\n".join(report_lines)

    report_path = os.path.join(root_dir, REPORT_FILENAME)
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"\n[COMPLETATO] Report generato con successo: {REPORT_FILENAME}")
    except Exception as e:
        print(f"\n[ERRORE] Impossibile salvare il file di report: {e}")

    print(f"Pagine analizzate: {total_files_scanned} | Pagine con navbar aggiornate: {modified_files_count}")


if __name__ == "__main__":
    process_and_fix_navbars()