import os
import csv
import xml.etree.ElementTree as ET
from xml.dom import minidom

# 1. IMPOSTA IL DOMINIO DEL TUO SITO WEB
BASE_URL = "https://tempestivo.it"

# Nome della sitemap indice da generare (verrà esclusa dalla scansione)
OUTPUT_FILENAME = "sitemap-index.xml"

def get_city_slugs(csv_path):
    """ Legge le città dalla colonna 'slug' del CSV """
    slugs = set()
    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'slug' in row and row['slug']:
                    slugs.add(row['slug'].strip())
    except Exception as e:
        print(f"Errore nella lettura del CSV {csv_path}: {e}")
    return list(slugs)

def generate_sitemap_index():
    current_dir = os.getcwd()
    
    # Creazione della radice XML conforme allo standard di Google per le Sitemap Index
    sitemapindex = ET.Element("sitemapindex", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    
    found_sitemaps = 0
    added_urls = set()  # Set per evitare sitemap duplicate

    def add_sitemap_url(file_path):
        nonlocal found_sitemaps
        # Calcola il percorso relativo
        rel_path = os.path.relpath(file_path, current_dir).replace("\\", "/")
        sitemap_url = f"{BASE_URL.rstrip('/')}/{rel_path}"

        if sitemap_url not in added_urls:
            added_urls.add(sitemap_url)
            sitemap_elem = ET.SubElement(sitemapindex, "sitemap")
            loc_elem = ET.SubElement(sitemap_elem, "loc")
            loc_elem.text = sitemap_url
            found_sitemaps += 1
            print(f"  [TROVATA] {rel_path} -> {sitemap_url}")

    print("=== SCANSIONE SITEMAP IN CORSO ===")

    # --- 1. RICERCA NELLA CARTELLA PRINCIPALE (ROOT) ---
    print("\n--- Scansione della cartella principale (Root) ---")
    for file in os.listdir(current_dir):
        file_path = os.path.join(current_dir, file)
        # Se è un file XML, contiene 'sitemap' nel nome e NON è l'indice stesso
        if os.path.isfile(file_path) and file.endswith('.xml') and 'sitemap' in file.lower() and file != OUTPUT_FILENAME:
            add_sitemap_url(file_path)

    # --- 2. RICERCA NELLE CARTELLE DEI COMUNI (DAL CSV) ---
    csv_path = 'citta_2.csv' if os.path.exists('citta_2.csv') else 'citta.csv'
    
    if os.path.exists(csv_path):
        city_slugs = get_city_slugs(csv_path)
        for city in city_slugs:
            city_dir = os.path.join(current_dir, city)
            
            if not os.path.exists(city_dir):
                print(f"\n[SALTATA] Cartella comune non trovata: {city}")
                continue

            print(f"\n--- Scansione cartella comune: {city} ---")
            for root, _, files in os.walk(city_dir):
                for file in files:
                    if file.endswith('.xml') and 'sitemap' in file.lower() and file != OUTPUT_FILENAME:
                        file_path = os.path.join(root, file)
                        add_sitemap_url(file_path)
    else:
        print(f"\n[AVVISO] File CSV non trovato ('citta_2.csv' o 'citta.csv'). Scansionata solo la root.")

    # Formattazione pulita ed indentata dell'XML
    xml_string = ET.tostring(sitemapindex, encoding='utf-8')
    parsed_xml = minidom.parseString(xml_string)
    pretty_xml = parsed_xml.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")

    # Salva il file sitemap-index.xml nella root del progetto
    output_path = os.path.join(current_dir, OUTPUT_FILENAME)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml)

    print("\n==========================================")
    print(f"SITEMAP INDEX GENERATA CON SUCCESSO!")
    print(f"File salvato: {OUTPUT_FILENAME}")
    print(f"Sitemap locali collegate: {found_sitemaps}")
    print("==========================================")

if __name__ == "__main__":
    generate_sitemap_index()