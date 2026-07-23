import os
import csv
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime

# 1. IL TUO DOMINIO FINALE SUL SERVER
BASE_URL = "https://tempestivo.it"

# File dell'indice principale per Search Console
INDEX_FILENAME = "sitemap-index.xml"

def get_city_slugs(csv_path):
    slugs = set()
    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'slug' in row and row['slug']:
                    slugs.add(row['slug'].strip())
    except Exception as e:
        print(f"Errore lettura CSV {csv_path}: {e}")
    return list(slugs)

def build_sitemap_file(html_files_info, output_path):
    """Crea un file sitemap.xml partendo da una lista di tuple (percorso_relativo, url_online)"""
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    today_date = datetime.now().strftime("%Y-%m-%d")

    for rel_path, full_url in html_files_info:
        url_elem = ET.SubElement(urlset, "url")
        ET.SubElement(url_elem, "loc").text = full_url
        ET.SubElement(url_elem, "lastmod").text = today_date
        ET.SubElement(url_elem, "changefreq").text = "monthly"
        
        # Assegna priorità 1.0 se è una pagina principale/index, altrimenti 0.8
        is_index = full_url.endswith('/') or rel_path in ['index.html', '']
        ET.SubElement(url_elem, "priority").text = "1.0" if is_index else "0.8"

    xml_string = ET.tostring(urlset, encoding='utf-8')
    pretty_xml = minidom.parseString(xml_string).toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml)

def main():
    current_dir = os.getcwd()
    csv_path = 'citta_2.csv' if os.path.exists('citta_2.csv') else 'citta.csv'
    
    if not os.path.exists(csv_path):
        print(f"Errore: CSV delle città non trovato ('citta_2.csv' o 'citta.csv')!")
        return

    city_slugs = get_city_slugs(csv_path)
    created_sitemaps_urls = []

    print("=== 1. ELABORAZIONE PAGINE DELLA ROOT ===")
    root_html_entries = []
    for item in os.listdir(current_dir):
        # Prende solo i file .html situati direttamente nella root
        if os.path.isfile(os.path.join(current_dir, item)) and item.endswith('.html'):
            if item == "index.html":
                url_online = f"{BASE_URL.rstrip('/')}/"
            else:
                url_online = f"{BASE_URL.rstrip('/')}/{item}"
            
            root_html_entries.append((item, url_online))
            print(f"  [ROOT] {item} -> {url_online}")

    if root_html_entries:
        root_sitemap_path = os.path.join(current_dir, "sitemap_root.xml")
        build_sitemap_file(root_html_entries, root_sitemap_path)
        created_sitemaps_urls.append(f"{BASE_URL.rstrip('/')}/sitemap_root.xml")
        print("  --> Generata: sitemap_root.xml")

    print("\n=== 2. ELABORAZIONE CARTELLE COMUNI DAL CSV ===")
    for city in city_slugs:
        city_dir = os.path.join(current_dir, city)
        if not os.path.exists(city_dir):
            print(f"  [SALTATA] Cartella comune non trovata: {city}")
            continue

        city_html_entries = []
        # Scansiona la cartella della città e eventuali sottocartelle
        for root, _, files in os.walk(city_dir):
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, current_dir).replace("\\", "/")

                    # GESTIONE PERCORSI CITTÀ:
                    # Se è il file index.html nella cartella città (es. palermo/index.html) -> https://tempestivo.it/palermo/
                    # Se è un'altra pagina (es. palermo/ristrutturazioni_palermo.html) -> https://tempestivo.it/palermo/ristrutturazioni_palermo.html
                    if rel_path.endswith("/index.html"):
                        url_path = rel_path[:-10]  # Mantiene solo 'palermo/'
                    else:
                        url_path = rel_path        # Mantiene 'palermo/ristrutturazioni_palermo.html'

                    url_online = f"{BASE_URL.rstrip('/')}/{url_path}"
                    city_html_entries.append((rel_path, url_online))
                    print(f"  [{city.upper()}] {rel_path} -> {url_online}")

        if city_html_entries:
            city_sitemap_path = os.path.join(city_dir, "sitemap.xml")
            build_sitemap_file(city_html_entries, city_sitemap_path)
            
            # URL della sitemap del comune per il server
            city_sitemap_url = f"{BASE_URL.rstrip('/')}/{city}/sitemap.xml"
            created_sitemaps_urls.append(city_sitemap_url)
            print(f"  --> Generata {city}/sitemap.xml ({len(city_html_entries)} URL)")

    print("\n=== 3. GENERAZIONE SITEMAP INDEX FINALE ===")
    sitemapindex = ET.Element("sitemapindex", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for sm_url in created_sitemaps_urls:
        sitemap_elem = ET.SubElement(sitemapindex, "sitemap")
        ET.SubElement(sitemap_elem, "loc").text = sm_url

    xml_string = ET.tostring(sitemapindex, encoding='utf-8')
    pretty_xml = minidom.parseString(xml_string).toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")

    index_path = os.path.join(current_dir, INDEX_FILENAME)
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml)

    print("\n==========================================")
    print(f"OPERAZIONE COMPLETATA SUCCESSEVOLMENTE!")
    print(f"File indice creato: {INDEX_FILENAME}")
    print(f"Sitemap collegate: {len(created_sitemaps_urls)}")
    print("==========================================")

if __name__ == '__main__':
    main()