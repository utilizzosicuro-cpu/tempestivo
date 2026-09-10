import os
import re

def rimuovi_citazioni():
    cartella = os.path.dirname(os.path.abspath(__file__))
    
    # Pattern mirato: cerca le parentesi quadre che contengono la parola 'cite' 
    # (es.[cite: 1],[cite: 1, 2], [cite]) e rimuove anche gli spazi precedenti.
    pattern = re.compile(r"\s*\[\s*cite[^\]]*\]", re.IGNORECASE)

    modificati = 0
    totale_rimosse = 0

    for root, dirs, files in os.walk(cartella):
        for file in files:
            if file.lower().endswith(('.html', '.htm')):
                file_path = os.path.join(root, file)
                
                if os.path.abspath(file_path) == os.path.abspath(__file__):
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        contenuto = f.read()
                    
                    nuovo_contenuto, conteggio = pattern.subn('', contenuto)

                    if conteggio > 0:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(nuovo_contenuto)
                        print(f"Pulito: {file_path} ({conteggio} occorrenze rimosse)")
                        modificati += 1
                        totale_rimosse += conteggio
                except Exception as e:
                    print(f"Errore nel file {file_path}: {e}")

    print(f"\nFatto. File modificati: {modificati}, citazioni rimosse in totale: {totale_rimosse}")

if __name__ == "__main__":
    rimuovi_citazioni()