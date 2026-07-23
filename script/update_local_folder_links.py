import os
import re
from bs4 import BeautifulSoup
from datetime import datetime

REPORT_FILENAME = "report_aggiornamento_cartella_locale.txt"

# Mappa dei comuni per indirizzare le "Zone Servite" alle rispettive pagine index
CITY_SLUGS = [
    "palermo", "alcamo", "carini", "castellammare", "monreale", 
    "partinico", "terrasini", "cinisi", "isola-delle-femmine", 
    "capaci", "trappeto", "balestrate", "trapani"
]

def update_local_html_files():
    # Prende SOLO la cartella corrente in cui si trova lo script
    current_dir = os.getcwd()
    
    # Filtra solo i file .html presenti direttamente nella cartella corrente (esclude sottocartelle)
    local_html_files = [f for f in os.listdir(current_dir) if os.path.isfile(os.path.join(current_dir, f)) and f.endswith('.html')]

    modified_files_count = 0
    total_links_updated = 0
    logs = []

    print(f"=== INIZIO AGGIORNAMENTO FILE HTML NELLA CARTELLA CORRENTE ===")
    print(f"Trovati {len(local_html_files)} file HTML da analizzare in: {current_dir}\n")

    for file_name in local_html_files:
        file_path = os.path.join(current_dir, file_name)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logs.append(f"[ERRORE LETTURA] {file_name}: {e}")
            continue

        soup = BeautifulSoup(content, 'html.parser')
        file_modified = False

        # --- REGOLE DI AGGIORNAMENTO DEI LINK ---
        for a_tag in soup.find_all('a'):
            anchor_text = a_tag.get_text(strip=True).lower()
            current_href = a_tag.get('href', '')

            # 1. Riferimenti a TRAPANI e Provincia -> linka a /trapani/index.html
            if "trapani" in anchor_text or "soluzioni-business-palermo-trapani" in current_href:
                new_href = "/trapani/index.html"
                if current_href != new_href:
                    a_tag['href'] = new_href
                    file_modified = True
                    total_links_updated += 1
                    logs.append(f"[AGGIORNATO] {file_name} -> Trapani/Provincia linkato a: {new_href}")

            # 2. Riferimenti a ZONE DI INTERVENTO -> linka a /landing-ristrutturazioni.html
            elif "zone di intervento" in anchor_text or "zona di intervento" in anchor_text:
                new_href = "/landing-ristrutturazioni.html"
                if current_href != new_href:
                    a_tag['href'] = new_href
                    file_modified = True
                    total_links_updated += 1
                    logs.append(f"[AGGIORNATO] {file_name} -> Zone di Intervento linkato a: {new_href}")

            # 3. Riferimenti alle ZONE SERVITE -> linka alla index della città corrispondente
            else:
                parent_text = ""
                if a_tag.parent:
                    parent_text = a_tag.parent.get_text().lower()

                # Se si trova in un contesto di "Zone Servite" o cita un comune specifico
                if "zone servite" in parent_text or "zona servita" in parent_text or any(city in anchor_text for city in CITY_SLUGS):
                    for city in CITY_SLUGS:
                        if city in anchor_text or city in current_href.lower():
                            new_href = f"/{city}/index.html"
                            if current_href != new_href:
                                a_tag['href'] = new_href
                                file_modified = True
                                total_links_updated += 1
                                logs.append(f"[AGGIORNATO] {file_name} -> Comune '{city}' linkato a: {new_href}")
                            break

        # Salva le modifiche solo se ci sono stati aggiornamenti
        if file_modified:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                modified_files_count += 1
            except Exception as e:
                logs.append(f"[ERRORE SCRITTURA] {file_name}: {e}")

    # --- GENERAZIONE DEL FILE DI REPORT ---
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report_lines = [
        "=================================================================",
        "     REPORT AGGIORNAMENTO LINK LOCALI (CARTELLA CORRENTE)",
        "=================================================================",
        f"Data Esecuzione          : {now_str}",
        f"Percorso Cartella        : {current_dir}",
        f"File HTML Scansionati    : {len(local_html_files)}",
        f"File HTML Modificati     : {modified_files_count}",
        f"Link Totali Aggiornati   : {total_links_updated}",
        "=================================================================\n",
        "DETTAGLIO DELLE MODIFICHE APPLICATE:\n"
    ]

    if logs:
        report_lines.extend(logs)
    else:
        report_lines.append("✅ Tutti i link nella cartella corrente risultavano già corretti.")

    report_content = "\n".join(report_lines)

    report_path = os.path.join(current_dir, REPORT_FILENAME)
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"\n[COMPLETATO] Report salvato con successo in: {REPORT_FILENAME}")
    except Exception as e:
        print(f"\n[ERRORE] Impossibile salvare il file di report: {e}")

    print(f"File analizzati: {len(local_html_files)} | File modificati: {modified_files_count} | Link aggiornati: {total_links_updated}")


if __name__ == "__main__":
    update_local_html_files()