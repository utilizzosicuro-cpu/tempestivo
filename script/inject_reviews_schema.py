import os
import csv
import json
import re

# 1. PARAMETRI GENERALI E RATING
BASE_URL = "https://tempestivo.it"
LOGO_URL = "https://tempestivo.it/logo.png"
RATING_VALUE = "4.8"
REVIEW_COUNT = "65"

def load_config():
    """Carica i dati aziendali dal file config.json"""
    config_file = "config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Errore nella lettura di {config_file}: {e}")
    
    # Fallback con i dati forniti
    return {
        "azienda": "Tempestivo",
        "telefono": "+39 352 025 85 83",
        "email": "tempestivoweb@gmail.com",
        "indirizzo": "Contrada Incastrone 90047 Partinico PA"
    }

def get_city_data(csv_path):
    """Legge lo slug e il nome di ogni città dal file CSV"""
    cities = []
    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'slug' in row and row['slug']:
                    nome_citta = row.get('nome', row['slug'].capitalize())
                    cities.append({
                        'slug': row['slug'].strip(),
                        'nome': nome_citta.strip()
                    })
    except Exception as e:
        print(f"Errore nella lettura del CSV {csv_path}: {e}")
    return cities

def generate_json_ld(city_slug, city_name, config):
    """Genera lo schema JSON-LD LocalBusiness + AggregateRating"""
    page_url = f"{BASE_URL.rstrip('/')}/{city_slug}/recensioni-{city_slug}.html"
    
    azienda = config.get("azienda", "Tempestivo")
    telefono = config.get("telefono", "+39 352 025 85 83")
    email = config.get("email", "tempestivoweb@gmail.com")
    indirizzo = config.get("indirizzo", "Contrada Incastrone 90047 Partinico PA")

    schema_data = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": f"{azienda} - {city_name}",
        "url": page_url,
        "image": LOGO_URL,
        "logo": LOGO_URL,
        "telephone": telefono,
        "email": email,
        "priceRange": "€€",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": indirizzo,
            "addressLocality": city_name,
            "addressCountry": "IT"
        },
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": RATING_VALUE,
            "reviewCount": REVIEW_COUNT,
            "bestRating": "5",
            "worstRating": "1"
        },
        "review": [
            {
                "@type": "Review",
                "author": {
                    "@type": "Person",
                    "name": "Marco V."
                },
                "datePublished": "2026-02-15",
                "reviewBody": f"Servizio impeccabile e pronto intervento rapidissimo a {city_name}. Professionisti veloci e affidabili!",
                "reviewRating": {
                    "@type": "Rating",
                    "ratingValue": "5",
                    "bestRating": "5"
                }
            },
            {
                "@type": "Review",
                "author": {
                    "@type": "Person",
                    "name": "Laura G."
                },
                "datePublished": "2026-03-01",
                "reviewBody": f"Lavoro svolto a regola d'arte a {city_name}. Estremamente soddisfatta della tempestività.",
                "reviewRating": {
                    "@type": "Rating",
                    "ratingValue": "5",
                    "bestRating": "5"
                }
            }
        ]
    }
    return schema_data

def inject_schema_to_html(file_path, city_slug, city_name, config):
    """Legge il file HTML ed inietta il blocco JSON-LD prima del tag </head>"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  [ERRORE LETTURA] {file_path}: {e}")
        return False

    # Evita duplicati se lo schema è già presente
    if "AggregateRating" in content and "application/ld+json" in content:
        print(f"  [GIÀ PRESENTE] Schema JSON-LD già esistente in {file_path}")
        return False

    head_closing_pattern = re.compile(r'(</head>)', re.IGNORECASE)
    if not head_closing_pattern.search(content):
        print(f"  [ATTENZIONE] Tag </head> non trovato in {file_path}")
        return False

    json_data = generate_json_ld(city_slug, city_name, config)
    json_str = json.dumps(json_data, ensure_ascii=False, indent=2)
    script_tag = f"\n<!-- Schema.org JSON-LD Recensioni -->\n<script type=\"application/ld+json\">\n{json_str}\n</script>\n"

    # Inietta lo script prima della chiusura del tag </head>
    new_content = head_closing_pattern.sub(f"{script_tag}\\1", content, count=1)

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  [INIETTATO SUCCESSO] {file_path}")
        return True
    except Exception as e:
        print(f"  [ERRORE SCRITTURA] {file_path}: {e}")
        return False

def main():
    current_dir = os.getcwd()
    config = load_config()

    # Cerca citta_2.csv o citta.csv
    csv_path = 'citta_2.csv' if os.path.exists('citta_2.csv') else 'citta.csv'
    if not os.path.exists(csv_path):
        print(f"Errore: File CSV non trovato ('citta_2.csv' o 'citta.csv').")
        return

    cities = get_city_data(csv_path)
    updated_count = 0

    print("=== INIZIO SCANSIONE ED INIEZIONE JSON-LD RECENSIONI ===")

    for city in cities:
        slug = city['slug']
        nome = city['nome']
        
        city_dir = os.path.join(current_dir, slug)
        
        if not os.path.exists(city_dir):
            print(f"\n[SALTATA] Cartella comune non trovata: {slug}")
            continue

        # Cerca precisamente il file recensioni-{slug}.html
        review_filename = f"recensioni-{slug}.html"
        review_file_path = os.path.join(city_dir, review_filename)

        # Fallback nel caso in cui il file si chiami recensioni.html
        if not os.path.exists(review_file_path):
            alt_path = os.path.join(city_dir, "recensioni.html")
            if os.path.exists(alt_path):
                review_file_path = alt_path

        if os.path.exists(review_file_path):
            print(f"\n--- Elaborazione cartella: {slug}/ ({nome}) ---")
            if inject_schema_to_html(review_file_path, slug, nome, config):
                updated_count += 1
        else:
            print(f"\n[NON TROVATO] File {review_filename} assente nella cartella {slug}/")

    print("\n==========================================")
    print(f"OPERAZIONE COMPLETATA!")
    print(f"Pagine recensioni aggiornate: {updated_count}")
    print("==========================================")

if __name__ == '__main__':
    main()