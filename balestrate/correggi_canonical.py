import os
import json
from pathlib import Path
from bs4 import BeautifulSoup

def correggi_e_pulisci_balestrate(file_mappa="mappa_balestrate.json"):
    if not os.path.exists(file_mappa):
        print(f"Errore: Il file della mappa '{file_mappa}' non è stato trovato. Esegui prima lo script di mappatura.")
        return

    with open(file_mappa, 'r', encoding='utf-8') as f:
        dati_mappa = json.load(f)

    dominio_base = "https://tempestivo.it/balestrate"
    struttura = dati_mappa.get("struttura", {})
    
    file_eliminati = 0
    file_modificati = 0

    print("=== Avvio analisi e correzione pagine di Balestrate ==-\n")

    for percorso_relativo, info in struttura.items():
        # Consideriamo solo i file html
        if not percorso_relativo.endswith('.html'):
            continue
            
        # Escludiamo esplicitamente le cartelle di altre città (es. alcamo)
        if percorso_relativo.startswith("alcamo/"):
            continue

        percorso_assoluto = info.get("percorso_assoluto")
        if not percorso_assoluto or not os.path.exists(percorso_assoluto):
            continue

        # 1. Rilevamento e gestione duplicati / file anomali (es. indexx.html)
        if "indexx.html" in percorso_relativo:
            print(f"[ELIMINAZIONE DUPLICATO] Trovato file anomalo/duplicato: {percorso_relativo}")
            try:
                os.remove(percorso_assoluto)
                file_eliminati += 1
                print(f" -> File eliminato con successo.")
            except Exception as e:
                print(f" -> Errore durante l'eliminazione: {e}")
            continue

        # Calcolo dell'URL canonico corretto atteso per questa pagina
        # Se è index.html alla radice -> https://tempestivo.it/balestrate/
        # Se è in una sottocartella -> https://tempestivo.it/balestrate/sottocartella/
        dir_name = os.path.dirname(percorso_relativo)
        if percorso_relativo == "index.html":
            url_corretto = f"{dominio_base}/"
        else:
            url_corretto = f"{dominio_base}/{dir_name}/" if dir_name else f"{dominio_base}/"
            url_corretto = url_corretto.replace("\\", "/") # Normalizzazione path web

        # Leggiamo e analizziamo il contenuto HTML
        with open(percorso_assoluto, 'r', encoding='utf-8', errors='ignore') as f:
            contenuto_html = f.read()

        soup = BeautifulSoup(contenuto_html, 'html.parser')
        modificato = False

        # --- A. Controllo e Correzione Canonical ---
        link_canonical = soup.find('link', attrs={'rel': 'canonical'})
        if link_canonical:
            if link_canonical.get('href') != url_corretto:
                link_canonical['href'] = url_corretto
                modificato = True
        else:
            # Se manca, lo creiamo nell'head
            nuovo_canonical = soup.new_tag('link', rel='canonical', href=url_corretto)
            if soup.head:
                soup.head.append(nuovo_canonical)
                modificato = True

        # --- B. Controllo e Correzione og:url ---
        meta_og_url = soup.find('meta', property='og:url')
        if meta_og_url:
            if meta_og_url.get('content') != url_corretto:
                meta_og_url['content'] = url_corretto
                modificato = True
        else:
            # Se manca, lo creiamo nell'head
            nuovo_og = soup.new_tag('meta', property='og:url', content=url_corretto)
            if soup.head:
                soup.head.append(nuovo_og)
                modificato = True

        # --- C. Controllo e Correzione / Generazione ListItem (Breadcrumb JSON-LD) ---
        # Verifichiamo se esiste già un blocco JSON-LD con ListItem
        script_ld = None
        trovato_listitem = False
        
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data_json = json.loads(script.string or "{}")
                # Gestione array o singolo oggetto JSON-LD
                items = data_json if isinstance(data_json, list) else [data_json]
                for item in items:
                    if item.get('@type') == 'BreadcrumbList':
                        script_ld = script
                        trovato_listitem = True
                        break
            except:
                continue

        # Costruiamo il ListItem corretto basato sui segmenti del percorso
        parti_path = [p for p in dir_name.split('/') if p] if dir_name else []
        elementi_breadcrumb = [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://tempestivo.it/"},
            {"@type": "ListItem", "position": 2, "name": "Balestrate", "item": f"{dominio_base}/"}
        ]
        
        pos = 3
        url_accumulato = f"{dominio_base}/"
        for parte in parti_path:
            url_accumulato += f"{parte}/"
            nome_leggibile = parte.replace('-', ' ').capitalize()
            elementi_breadcrumb.append({
                "@type": "ListItem", 
                "position": pos, 
                "name": nome_leggibile, 
                "item": url_accumulato
            })
            pos += 1

        schema_breadcrumb = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": elementi_breadcrumb
        }

        if trovato_listitem and script_ld:
            # Aggiorna il blocco esistente se non è corretto
            try:
                corrente = json.loads(script_ld.string)
                if corrente != schema_breadcrumb:
                    script_ld.string = json.dumps(schema_breadcrumb, ensure_ascii=False, indent=4)
                    modificato = True
            except:
                script_ld.string = json.dumps(schema_breadcrumb, ensure_ascii=False, indent=4)
                modificato = True
        else:
            # Inserisce un nuovo script JSON-LD per il ListItem
            nuovo_script_ld = soup.new_tag('script', type='application/ld+json')
            nuovo_script_ld.string = json.dumps(schema_breadcrumb, ensure_ascii=False, indent=4)
            if soup.head:
                soup.head.append(nuovo_script_ld)
                modificato = True

        # Salvataggio del file se ci sono state modifiche
        if modificato:
            with open(percorso_assoluto, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            file_modificati += 1
            print(f"[CORRETTO] {percorso_relativo} -> Canonical/OG: {url_corretto}")

    print(f"\n=== Elaborazione completata ===")
    print(f"- File HTML corretti/aggiornati: {file_modificati}")
    print(f"- File duplicati/anomali eliminati: {file_eliminati}")

if __name__ == "__main__":
    correggi_e_pulisci_balestrate()