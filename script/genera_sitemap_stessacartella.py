import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime

# 1. CONFIGURAZIONE
# Sostituisci con il dominio reale del tuo sito web
BASE_URL = "https://tempestivo.it"

# Scansiona la directory corrente (dove risiede lo script)
OUTPUT_DIR = "."

# Nome della sitemap finale
SITEMAP_FILENAME = "sitemap.xml"

# Nomi di cartelle o file da ignorare nella sitemap
EXCLUDE_FILES = {SITEMAP_FILENAME, "sitemap-index.xml"}
EXCLUDE_DIRS = {".git", ".vscode", "__pycache__", "venv", "node_modules"}


def generate_sitemap():
    root_path = os.path.abspath(OUTPUT_DIR)

    # Creazione elemento radice XML
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    
    total_urls = 0
    today_date = datetime.now().strftime("%Y-%m-%d")

    print(f"=== SCANSIONE DELLA CARTELLA CORRENTE ({root_path}) ===")

    # Scansione ricorsiva della directory corrente e sotto-cartelle
    for root, dirs, files in os.walk(root_path):
        # Ignora le cartelle nella lista di esclusione
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for file in files:
            if file.endswith('.html') and file not in EXCLUDE_FILES:
                file_path = os.path.join(root, file)
                
                # Ricava il percorso relativo rispetto alla cartella corrente
                rel_path = os.path.relpath(file_path, root_path).replace("\\", "/")

                # Gestione URL puliti:
                # - index.html -> /
                # - palermo/index.html -> /palermo/
                # - palermo/servizi.html -> /palermo/servizi.html
                if rel_path == "index.html":
                    page_path = ""
                elif rel_path.endswith("/index.html"):
                    page_path = rel_path[:-10]  # Rimuove "index.html" mantenendo lo slash finale
                else:
                    page_path = rel_path

                # Costruzione dell'URL finale
                if page_path:
                    url = f"{BASE_URL.rstrip('/')}/{page_path.lstrip('/')}"
                else:
                    url = f"{BASE_URL.rstrip('/')}/"

                # Creazione elemento <url> per la sitemap
                url_elem = ET.SubElement(urlset, "url")
                
                # <loc>
                loc_elem = ET.SubElement(url_elem, "loc")
                loc_elem.text = url

                # <lastmod>
                lastmod_elem = ET.SubElement(url_elem, "lastmod")
                lastmod_elem.text = today_date

                # <changefreq>
                changefreq_elem = ET.SubElement(url_elem, "changefreq")
                changefreq_elem.text = "monthly"

                # <priority>
                priority_elem = ET.SubElement(url_elem, "priority")
                if page_path == "" or page_path.count("/") == 0:
                    priority_elem.text = "1.0"
                else:
                    priority_elem.text = "0.8"

                total_urls += 1
                print(f"  [AGGIUNTO] {rel_path} -> {url}")

    # Formattazione XML pulita ed indentata
    xml_string = ET.tostring(urlset, encoding='utf-8')
    parsed_xml = minidom.parseString(xml_string)
    pretty_xml = parsed_xml.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")

    # Salva il file sitemap.xml nella cartella corrente
    output_sitemap_path = os.path.join(root_path, SITEMAP_FILENAME)
    
    with open(output_sitemap_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml)

    print("\n==========================================")
    print(f"SITEMAP GENERATA CON SUCCESSO!")
    print(f"Pagine HTML trovate e aggiunte: {total_urls}")
    print(f"File salvato in: {output_sitemap_path}")
    print("==========================================")


if __name__ == "__main__":
    generate_sitemap()