import os
import json
from bs4 import BeautifulSoup

# 1. Carica il database delle zone
with open('zone.json', 'r', encoding='utf-8') as f:
    db_zone = json.load(f)

folder_path = './'

for filename, data in db_zone.items():
    filepath = os.path.join(folder_path, filename)
    
    # Verifica che il file HTML esista prima di elaborarlo
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        # Estrae tutto il testo visibile della pagina per il controllo
        page_text = soup.get_text()
        
        modificato = False
        
        # 2. Controlla ogni quartiere associato alla pagina
        for quartiere in data["quartieri"]:
            # Se il quartiere NON è presente nel testo della pagina
            if quartiere.lower() not in page_text.lower():
                # Costruisce il paragrafo standard ottimizzato
                testo_paragrafo = f"Operiamo con rapidità anche nella zona di {quartiere}, garantendo assistenza tecnica in tempi brevissimi."
                
                # Crea il tag <p> con BeautifulSoup
                nuovo_p = soup.new_tag("p")
                nuovo_p.string = testo_paragrafo
                nuovo_p['style'] = "margin: 15px 0; font-size: 1rem; color: #444444;"
                
                # 3. Inietta il paragrafo strategicamente prima dell'ultimo tag di sezione o prima del footer
                footer_tag = soup.find('footer')
                if footer_tag:
                    footer_tag.insert_before(nuovo_p)
                    modificato = True
                else:
                    # Fallback: se non c'è il footer, lo accoda al body
                    if soup.body:
                        soup.body.append(nuovo_p)
                        modificato = True
                
                print(f"[Aggiunto] Quartiere '{quartiere}' inserito in {filename}")

        # Salva il file solo se sono state fatte modifiche
        if modificato:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            print(f"[Salvato] File aggiornato: {filename}\n")
    else:
        print(f"[Attenzione] File non trovato nella cartella: {filename}")