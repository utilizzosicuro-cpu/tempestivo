import os
import json
from bs4 import BeautifulSoup

# Carica il database
with open('faq_seo.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

folder_path = './'

for filename in os.listdir(folder_path):
    if not filename.endswith(".html"): continue
    
    contenuto_da_inserire = None
    
    # 1. Verifica se è una pagina specifica (generale)
    if filename in config["generale"]:
        contenuto_da_inserire = config["generale"][filename]
    
    # 2. Verifica se segue un modello (es. inizia con 'servizi-')
    else:
        for prefisso, modello in config["modelli_automatici"].items():
            if filename.startswith(prefisso):
                contenuto_da_inserire = modello.copy()
                # Sostituisce segnaposto {citta} con il nome del comune estratto dal nome file
                citta = filename.replace(prefisso, "").replace(".html", "").replace("-", " ").title()
                contenuto_da_inserire["testo"] = modello["testo"].format(citta=citta)
                break

    # 3. Iniezione (se trovato un modello)
    if contenuto_da_inserire:
        with open(filename, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        # Logica di iniezione identica a prima...
        # (Controllo duplicati e inserimento prima del footer)
        print(f"Applicato contenuto SEO a: {filename}")