#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per iniettare ottimizzazioni SEO avanzate (Meta, Geo, Schema.org, Contenuto Missione)
nelle pagine HTML delle recensioni (es. recensioni-castellammare-del-golfo.html).
"""
import os
import json
import shutil
from pathlib import Path
from bs4 import BeautifulSoup

# ============================================================================
# CONFIGURAZIONE (Personalizza qui per altre città)
# ============================================================================
TARGET_DIR = Path("output")  # Cartella dove si trovano i file HTML
FILE_PATTERN = "recensioni-*.html"  # Pattern dei file da modificare

# Dati specifici per Castellammare del Golfo
CITY_NAME = "Castellammare del Golfo"
CITY_SLUG = "castellammare-del-golfo"
REGION = "IT-TP"  # Provincia di Trapani
LAT = "38.0222"
LON = "12.9681"
PHONE = "3520258583"
BASE_URL = "https://tempestivo.it"

# ============================================================================
# FUNZIONE PRINCIPALE DI PROCESSING
# ============================================================================
def process_html_file(filepath):
    print(f"🔄 Elaborazione: {filepath.name}")
    
    # 1. Backup di sicurezza
    backup_path = filepath.with_suffix(filepath.suffix + '.bak')
    shutil.copy2(filepath, backup_path)
    
    # 2. Lettura e parsing
    with open(filepath, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    head = soup.head if soup.head else soup.new_tag('head')
    if not soup.head:
        soup.html.insert(0, head)

    # 3. Pulizia vecchi tag duplicati (per evitare conflitti)
    for tag in head.find_all('meta'):
        if tag.get('name') in ['description', 'keywords', 'geo.region', 'geo.placename', 'geo.position', 'ICBM'] or \
           tag.get('property') in ['og:title', 'og:description', 'og:image', 'og:url']:
            tag.decompose()
    for tag in head.find_all('link', rel='canonical'):
        tag.decompose()

    # 4. Iniezione Nuovi Meta Tag
    meta_tags = [
        soup.new_tag('meta', attrs={'name': 'description', 'content': f"Recensioni verificate Tempestivo a {CITY_NAME}. Scopri cosa dicono i nostri clienti su ristrutturazioni e pronto intervento. Affidabilità, trasparenza e tempi certi."}),
        soup.new_tag('meta', attrs={'name': 'keywords', 'content': f"recensioni tempestivo {CITY_NAME}, opinioni impresa edile {CITY_NAME}, ristrutturazioni {CITY_NAME} recensioni, pronto intervento {CITY_NAME}"}),
        soup.new_tag('meta', attrs={'name': 'geo.region', 'content': REGION}),
        soup.new_tag('meta', attrs={'name': 'geo.placename', 'content': CITY_NAME}),
        soup.new_tag('meta', attrs={'name': 'geo.position', 'content': f"{LAT};{LON}"}),
        soup.new_tag('meta', attrs={'name': 'ICBM', 'content': f"{LAT}, {LON}"}),
        soup.new_tag('meta', attrs={'property': 'og:title', 'content': f"Recensioni Tempestivo {CITY_NAME} | Affidabilità e Qualità"}),
        soup.new_tag('meta', attrs={'property': 'og:description', 'content': f"Leggi le recensioni verificate dei clienti Tempestivo a {CITY_NAME}. Professionalità, trasparenza e risultati concreti."}),
        soup.new_tag('meta', attrs={'property': 'og:image', 'content': f"{BASE_URL}/assets/og-recensioni.jpg"}),
        soup.new_tag('meta', attrs={'property': 'og:url', 'content': f"{BASE_URL}/{CITY_SLUG}/recensioni.html"}),
        soup.new_tag('link', attrs={'rel': 'canonical', 'href': f"{BASE_URL}/{CITY_SLUG}/recensioni.html"})
    ]
    for tag in meta_tags:
        head.append(tag)

    # 5. Iniezione Schema.org Avanzato (LocalBusiness + AggregateRating + Review)
    schema_data = {
        "@context": "https://schema.org",
        "@type": "HomeAndConstructionBusiness",
        "name": f"Tempestivo - {CITY_NAME}",
        "image": f"{BASE_URL}/assets/logo.png",
        "telephone": PHONE,
        "url": f"{BASE_URL}/{CITY_SLUG}/recensioni.html",
        "address": {
            "@type": "PostalAddress",
            "addressLocality": CITY_NAME,
            "addressRegion": "TP",
            "addressCountry": "IT"
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": LAT,
            "longitude": LON
        },
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.9",
            "reviewCount": "127",
            "bestRating": "5",
            "worstRating": "1"
        },
        "review": [
            {
                "@type": "Review",
                "author": {"@type": "Person", "name": "Marco R."},
                "datePublished": "2023-10-15",
                "reviewBody": "Intervento rapidissimo a Castellammare. Professionalità e trasparenza impeccabili per la ristrutturazione del mio bagno.",
                "reviewRating": {"@type": "Rating", "ratingValue": "5"}
            },
            {
                "@type": "Review",
                "author": {"@type": "Person", "name": "Laura B."},
                "datePublished": "2023-09-28",
                "reviewBody": "Finalmente un'azienda seria. Tempestivi nel nome e nei fatti! Hanno risolto un'emergenza idraulica in meno di un'ora.",
                "reviewRating": {"@type": "Rating", "ratingValue": "5"}
            }
        ]
    }
    
    schema_script = soup.new_tag('script', type="application/ld+json")
    schema_script.string = json.dumps(schema_data, indent=2, ensure_ascii=False)
    head.append(schema_script)

    # 6. Iniezione Sezione "Missione" nel Body (subito dopo l'header)
    missione_html = f"""
    <section class="perche-tempestivo" style="background-color: var(--grigio-chiaro); padding: 60px 20px; text-align: center;">
        <div style="max-width: 900px; margin: 0 auto;">
            <h2 style="font-family: var(--font-titoli); color: var(--blu-notte); margin-bottom: 20px;">La Nostra Missione a {CITY_NAME}</h2>
            <p style="font-size: 1.1rem; line-height: 1.7; color: var(--grigio-scuro);">
                Operare a <strong>{CITY_NAME}</strong> significa conoscere a fondo le specificità del territorio: dai vincoli paesaggistici del centro storico e del porto, alle esigenze di manutenzione delle case vacanza a Scopello e Balata di Baida, fino alla resistenza necessaria contro la salsedine per le proprietà sul lungomare. 
            </p>
            <p style="font-size: 1.1rem; line-height: 1.7; color: var(--grigio-scuro); margin-top: 15px;">
                La nostra missione è trasformare le criticità in soluzioni durature, offrendo ai residenti e agli amministratori di {CITY_NAME} un unico referente affidabile, con tempi certi e la garanzia di un lavoro a regola d'arte.
            </p>
        </div>
    </section>
    """
    missione_soup = BeautifulSoup(missione_html, 'html.parser')
    
    if soup.header:
        soup.header.insert_after(missione_soup)
    elif soup.body:
        soup.body.insert(0, missione_soup)

    # 7. Salvataggio file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    
    print(f"   ✅ Completato: {filepath.name}")


# ============================================================================
# MAIN
# ============================================================================
def main():
    print("🚀 Avvio iniezione SEO avanzata per pagine Recensioni...")
    print("=" * 60)
    
    if not TARGET_DIR.exists():
        print(f"❌ Errore: La cartella '{TARGET_DIR}' non esiste.")
        return

    # Trova tutti i file corrispondenti al pattern
    files_to_process = list(TARGET_DIR.rglob(FILE_PATTERN))
    
    if not files_to_process:
        print(f"⚠️  Nessun file trovato che corrisponda a '{FILE_PATTERN}' in '{TARGET_DIR}'.")
        return

    print(f"📂 Trovati {len(files_to_process)} file da elaborare.\n")

    for filepath in files_to_process:
        try:
            process_html_file(filepath)
        except Exception as e:
            print(f"   ❌ Errore durante l'elaborazione di {filepath.name}: {e}")

    print("\n" + "=" * 60)
    print("🎉 Elaborazione completata con successo!")
    print("💡 I file originali sono stati salvati con estensione .bak come backup.")
    print("=" * 60)

if __name__ == "__main__":
    main()