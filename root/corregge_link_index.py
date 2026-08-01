import os
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup
import re

def correggi_link_citta_cartella_corrente():
    cartella_corrente = os.getcwd()
    print(f"Scansione e correzione nella cartella (solo livello corrente): {cartella_corrente}\n")
    
    # Trova SOLO i file HTML direttamente nella cartella corrente (senza ricorsione)
    try:
        elementi = os.listdir(cartella_corrente)
    except Exception as e:
        print(f"Errore nella lettura della cartella: {e}")
        return

    file_html = {elemento: os.path.join(cartella_corrente, elemento) 
                 for elemento in elementi 
                 if elemento.lower().endswith(('.html', '.htm')) and os.path.isfile(os.path.join(cartella_corrente, elemento))}

    if not file_html:
        print("Nessun file HTML trovato nella cartella corrente.")
        return

    print(f"Trovati {len(file_html)} file HTML. Analisi e aggiornamento link città in corso...\n")

    modifiche_effettuate = 0

    # Analizza ogni file HTML della cartella
    for rel_path, abs_path in file_html.items():
        try:
            with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            soup = BeautifulSoup(content, 'html.parser')
        except Exception as e:
            print(f"[ERRORE LETTURA] {rel_path}: {e}")
            continue

        tag_a = soup.find_all('a', href=True)
        file_modificato = False

        for tag in tag_a:
            href = tag['href'].strip()
            
            # Salta anchor, mailto, tel e link esterni
            if not href or href.startswith(('#', 'mailto:', 'tel:', 'javascript:')):
                continue
            
            parsed_url = urlparse(href)
            if parsed_url.scheme in ('http', 'https', 'ftp'):
                continue

            percorso_pulito = unquote(parsed_url.path)
            if not percorso_pulito:
                continue

            # Verifica se il link corrisponde a una index di una città (es. /palermo/index.html o palermo/index.html)
            if 'index.html' in percorso_pulito.lower():
                parti_path = [p for p in percorso_pulito.split('/') if p]
                if len(parti_path) >= 2 and parti_path[-1].lower() == 'index.html':
                    citta = parti_path[-2].lower()
                    
                    # Genera il nuovo percorso corretto richiesto: /nomedelcomune/servizi_comune.html[cite: 9]
                    # Mantiene lo slash iniziale se era presente nell'href originale
                    prefisso_slash = '/' if percorso_pulito.startswith('/') else ''
                    nuovo_percorso_pulito = f"{prefisso_slash}{citta}/servizi_{citta}.html"
                    
                    if percorso_pulito != nuovo_percorso_pulito:
                        nuovo_href = href.replace(percorso_pulito, nuovo_percorso_pulito)
                        tag['href'] = nuovo_href
                        file_modificato = True
                        modifiche_effettuate += 1
                        print(f"[AGGIORNATO] In '{rel_path}':")
                        print(f"  Da: {href}")
                        print(f"  A:  {nuovo_href}\n")

        # Salva il file HTML modificato solo se sono state fatte variazioni
        if file_modificato:
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))

    print("=" * 40)
    print(f"ELABORAZIONE COMPLETATA. Sostituzioni applicate: {modifiche_effettuate}")
    print("=" * 40)

if __name__ == '__main__':
    correggi_link_citta_cartella_corrente()