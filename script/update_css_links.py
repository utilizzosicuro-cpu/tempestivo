import os
import re
import csv

def fix_css_reference(file_path):
    """
    Legge il file HTML e sostituisce qualsiasi riferimento a style.css 
    (es. href="style.css", href="./style.css", href="../style.css") con href="/style.css".
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"[ERRORE LETTURA] {file_path}: {e}")
        return False

    # Regex che individua qualsiasi attributo href che termina con style.css
    # es: href="style.css", href="./style.css", href="../style.css"
    css_pattern = re.compile(r'href=["\'](?:[^"\']*/)?style\.css["\']', re.IGNORECASE)

    # Verifica se il file contiene un riferimento che DEVE essere aggiornato (diverso da /style.css)
    matches = css_pattern.findall(content)
    needs_update = any(match != 'href="/style.css"' for match in matches)

    if not needs_update:
        print(f"  [INVARIATO/GIÀ GIUSTO] {file_path}")
        return False

    # Sostituisce i riferimenti con href="/style.css"
    new_content = css_pattern.sub('href="/style.css"', content)

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  [MODIFICATO] {file_path}")
        return True
    except Exception as e:
        print(f"[ERRORE SCRITTURA] {file_path}: {e}")
        return False

def get_city_slugs(csv_path):
    """Legge il file CSV e restituisce l'elenco dei comuni/slug."""
    slugs = set()
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'slug' in row and row['slug']:
                slugs.add(row['slug'].strip())
    return list(slugs)

def main():
    # Cerca 'citta_2.csv' oppure 'citta.csv'
    csv_path = 'citta_2.csv' if os.path.exists('citta_2.csv') else 'citta.csv'
    
    if not os.path.exists(csv_path):
        print(f"Errore: Impossibile trovare il file CSV ('citta_2.csv' o 'citta.csv').")
        return

    print(f"Utilizzo file CSV: {csv_path}")
    city_folders = get_city_slugs(csv_path)

    total_files = 0
    modified_files = 0

    print("=== INIZIO AGGIORNAMENTO RIFERIMENTI CSS ===")

    for city in city_folders:
        folder_path = os.path.join(os.getcwd(), city)

        if not os.path.exists(folder_path):
            print(f"\n[SALTATA] Cartella non trovata: {city}")
            continue

        print(f"\n--- Scansione cartella comune: {city} ---")

        # Scansiona tutti i file .html nella cartella e nelle sottocartelle del comune
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(root, file)
                    total_files += 1
                    if fix_css_reference(file_path):
                        modified_files += 1

    print("\n==========================================")
    print(f"Scansione completata!")
    print(f"File HTML analizzati: {total_files}")
    print(f"File HTML aggiornati: {modified_files}")
    print("==========================================")

if __name__ == '__main__':
    main()