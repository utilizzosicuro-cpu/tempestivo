import os
import csv
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime

BASE_URL = "https://tempestivo.it"
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

def build_single_sitemap(directory_path, output_filename):
    """ Genera un file sitemap.xml scansionando le pagine .html di una specifica cartella """
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    today_date = datetime.now().strftime("%Y-%m-%d")
    total_urls = 0

    current_dir = os.getcwd()

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, current_dir).replace("\\", "/")

                if rel_path == "index.html":
                    page_path = ""
                elif rel_path.endswith("/index.html"):
                    page_path = rel_path[:-10]
                else:
                    page_path = rel_path

                url = f"{BASE_URL.rstrip('/')}/{page_path.lstrip('/')}" if page_path else f"{BASE_URL.rstrip('/')}/"

                url_elem = ET.SubElement(urlset, "url")
                ET.SubElement(url_elem, "loc").text = url
                ET.SubElement(url_elem, "lastmod").text = today_date
                ET.SubElement(url_elem, "changefreq").text = "monthly"
                ET.SubElement(url_elem, "priority").text = "1.0" if not page_path or "/" not in page_path else "0.8"
                total_urls += 1

    if total_urls > 0:
        xml_string = ET.tostring(urlset, encoding='utf-8')
        pretty_xml = minidom.parseString(xml_string).toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")
        
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(pretty_xml)
        return True
    return False

def generate_all():
    current_dir = os.getcwd()
    csv_path = 'citta_2.csv' if os.path.exists('citta_2.csv') else 'citta.csv'
    
    if not os.path.exists(csv_path):
        print(f"Errore: CSV non trovato!")
        return

    city_slugs = get_city_slugs(csv_path)
    created_sitemaps = []

    print("=== 1. GENERAZIONE SITEMAP LOCALI PER OGNI CITTÀ ===")
    for city in city_slugs:
        city_dir = os.path.join(current_dir, city)
        if os.path.exists(city_dir):
            sitemap_path = os.path.join(city_dir, "sitemap.xml")
            if build_single_sitemap(city_dir, sitemap_path):
                rel_sitemap = os.path.relpath(sitemap_path, current_dir).replace("\\", "/")
                created_sitemaps.append(rel_sitemap)
                print(f"  [CREATA] {rel_sitemap}")

    print("\n=== 2. CREAZIONE SITEMAP PRINCIPALE PER LA ROOT ===")
    root_sitemap_path = os.path.join(current_dir, "sitemap_root.xml")
    # Scansiona solo la root senza entrare nelle sottocartelle delle città
    root_html_files = [f for f in os.listdir(current_dir) if f.endswith('.html')]
    if root_html_files:
        if build_single_sitemap(current_dir, root_sitemap_path):
            created_sitemaps.append("sitemap_root.xml")
            print("  [CREATA] sitemap_root.xml")

    print("\n=== 3. GENERAZIONE SITEMAP INDEX FINALE ===")
    sitemapindex = ET.Element("sitemapindex", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for sm_rel in created_sitemaps:
        sitemap_url = f"{BASE_URL.rstrip('/')}/{sm_rel}"
        sitemap_elem = ET.SubElement(sitemapindex, "sitemap")
        ET.SubElement(sitemap_elem, "loc").text = sitemap_url

    xml_string = ET.tostring(sitemapindex, encoding='utf-8')
    pretty_xml = minidom.parseString(xml_string).toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")

    index_path = os.path.join(current_dir, INDEX_FILENAME)
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml)

    print(f"\nCOMPLETATO! {INDEX_FILENAME} generato correttamente con {len(created_sitemaps)} sitemap collegate.")

if __name__ == '__main__':
    generate_all()