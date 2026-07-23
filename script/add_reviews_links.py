import os
import csv
import re
from bs4 import BeautifulSoup

def get_city_slugs(csv_path):
    """Legge l'elenco delle città e dei relativi nomi dal file CSV"""
    cities = []
    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'slug' in row and row['slug']:
                    # Recupera il nome formattato se esiste, altrimenti usa lo slug in maiuscolo
                    nome_citta = row.get('nome', row['slug'].capitalize())
                    cities.append({
                        'slug': row['slug'].strip(),
                        'nome': nome_citta.strip()
                    })
    except Exception as e:
        print(f"Errore nella lettura del CSV {csv_path}: {e}")
    return cities

def process_city_index(file_path, city_slug, city_name):
    """
    Legge il file index.html di una città e aggiunge il link alle recensioni
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  [ERRORE LETTURA] {file_path}: {e}")
        return False

    # Percorso del link desiderato: /palermo/recensioni-palermo.html
    review_url = f"/{city_slug}/recensioni-{city_slug}.html"
    
    # Evita di aggiungere il link due volte se è già presente
    if review_url in content:
        print(f"  [GIÀ PRESENTE] Link recensioni già esistente in {file_path}")
        return False

    soup = BeautifulSoup(content, 'html.parser')

    # Creazione del blocco HTML da iniettare
    # Inserisce un div formattato con il link contestuale per le recensioni della città
    review_box = soup.new_tag("div", **{"class": "seo-reviews-link", "style": "margin: 20px 0; text-align: center;"})
    a_tag = soup.new_tag("a", href=review_url, **{"class": "btn-reviews", "style": "font-weight: bold; text-decoration: underline;"})
    a_tag.string = f"⭐ Leggi tutte le recensioni dei clienti di {city_name}"
    review_box.append(a_tag)

    # 1. Prova ad inserire il blocco nel footer
    footer = soup.find('footer')
    if footer:
        footer.append(review_box)
    else:
        # 2. Se manca il footer, inserisci prima della chiusura del body
        body = soup.find('body')
        if body:
            body.append(review_box)
        else:
            print(f"  [ATTENZIONE] Nessun <footer> o <body> trovato in {file_path}")
            return False

    # Salva il file HTML aggiornato
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        print(f"  [AGGIORNATO] Aggiunto link '{review_url}' in {file_path}")
        return True
    except Exception as e:
        print(f"  [ERRORE SCRITTURA] {file_path}: {e}")
        return False

def main():
    current_dir = os.getcwd()
    csv_path = 'citta_2.csv' if os.path.exists('citta_2.csv') else 'citta.csv'

    if not os.path.exists(csv_path):
        print(f"Errore: File CSV delle città non trovato ('citta_2.csv' o 'citta.csv').")
        return

    cities = get_city_slugs(csv_path)
    updated_files = 0

    print("=== INIZIO AGGIORNAMENTO LINK RECENSIONI NEI FILE INDEX ===")

    for city in cities:
        slug = city['slug']
        nome = city['nome']
        
        city_dir = os.path.join(current_dir, slug)
        
        if not os.path.exists(city_dir):
            print(f"\n[SALTATA] Cartella comune non trovata: {slug}")
            continue

        index_path = os.path.join(city_dir, "index.html")
        
        if os.path.exists(index_path):
            print(f"\n--- Elaborazione: {slug.upper()} ({nome}) ---")
            if process_city_index(index_path, slug, nome):
                updated_files += 1
        else:
            print(f"\n[NON TROVATO] File index.html assente in {slug}")

    print("\n==========================================")
    print(f"OPERAZIONE COMPLETATA!")
    print(f"File index.html aggiornati con successo: {updated_files}")
    print("==========================================")

if __name__ == '__main__':
    main()