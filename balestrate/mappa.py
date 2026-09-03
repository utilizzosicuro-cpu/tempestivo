import os
import json
from pathlib import Path
from bs4 import BeautifulSoup

def scansiona_cartella(percorso_base):
    root_path = Path(percorso_base)
    
    if not root_path.exists() or not root_path.is_dir():
        raise ValueError(f"La cartella '{percorso_base}' non esiste o non è una directory valida.")
    
    mappa_sito = {
        "cartella_radice": str(root_path.resolve()),
        "file_totali": 0,
        "struttura": {}
    }
    
    # Estensioni dei file che vogliamo analizzare nel dettaglio (es. HTML, PHP)
    estensioni_analizzabili = {'.html', '.htm', '.php'}
    
    for percorso_file in root_path.rglob('*'):
        if percorso_file.is_file():
            mappa_sito["file_totali"] += 1
            rel_path = percorso_file.relative_to(root_path)
            percorso_str = str(rel_path).replace("\\", "/") # Normalizza i separatori per i percorsi web
            
            dati_file = {
                "nome_file": percorso_file.name,
                "estensione": percorso_file.suffix.lower(),
                "percorso_assoluto": str(percorso_file.resolve()),
                "percorso_relativo": percorso_str,
                "dimensione_bytes": percorso_file.stat().st_size,
                "canonical_attuale": None,
                "og_url_attuale": None,
                "titolo": None
            }
            
            # Se è un file HTML/PHP, estraiamo alcune info utili per la futura correzione
            if percorso_file.suffix.lower() in estensioni_analizzabili:
                try:
                    with open(percorso_file, 'r', encoding='utf-8', errors='ignore') as f:
                        soup = BeautifulSoup(f.read(), 'html.parser')
                        
                        # Estrae il titolo
                        tag_title = soup.find('title')
                        if tag_title:
                            dati_file["titolo"] = tag_title.get_text(strip=True)
                            
                        # Estrae il tag canonical esistente
                        link_canonical = soup.find('link', attrs={'rel': 'canonical'})
                        if link_canonical and link_canonical.get('href'):
                            dati_file["canonical_attuale"] = link_canonical['href']
                            
                        # Estrae l'og:url esistente
                        meta_og_url = soup.find('meta', property='og:url')
                        if meta_og_url and meta_og_url.get('content'):
                            dati_file["og_url_attuale"] = meta_og_url['content']
                            
                except Exception as e:
                    dati_file["errore_parsing"] = str(e)
            
            mappa_sito["struttura"][percorso_str] = dati_file

    return mappa_sito

def salva_mappa(mappa, nome_file_output="mappa_balestrate.json"):
    with open(nome_file_output, 'w', encoding='utf-8') as f:
        json.dump(mappa, f, ensure_ascii=False, indent=4)
    print(f"Mappa generata con successo e salvata in: {nome_file_output}")

if __name__ == "__main__":
    # Sostituisci 'balestrate' con il percorso corretto se la cartella non è nella stessa directory dello script
    cartella_target = "."
    
    print(f"Scansione della cartella '{cartella_target}' in corso...")
    try:
        mappa = scansiona_cartella(cartella_target)
        salva_mappa(mappa)
        print(f"Totale file indicizzati: {mappa['file_totali']}")
    except Exception as e:
        print(f"Errore durante l'esecuzione: {e}")