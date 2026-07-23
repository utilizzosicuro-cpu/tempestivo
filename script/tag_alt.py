from bs4 import BeautifulSoup
import os

# Dizionario per personalizzare i tag ALT in base al nome del file (es. logo.png)
alt_map = {
    "logo.png": "Logo Tempestivo - Pronto Intervento e Ristrutturazioni a Palermo e Trapani",
    "tecnico-impianti-elettrici-cantiere.png": "Tempestivo - Ristrutturazioni e Impianti nelle province di Palermo e Trapani",
    "ristrutturazione-bagno-moderno-tempestivo.png": "Tempestivo Ristrutturazione bagno, progettazione ambienti moderni",
    # Aggiungi qui altre immagini man mano che le aggiungi al sito
}

folder_path = './'

for filename in os.listdir(folder_path):
    if filename.endswith(".html"):
        filepath = os.path.join(folder_path, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        # Trova tutte le immagini
        images = soup.find_all('img')
        for img in images:
            # Se il tag alt è mancante o vuoto
            if not img.get('alt'):
                img_src = os.path.basename(img.get('src', ''))
                # Cerca nella mappa, altrimenti usa un default generico ottimizzato
                alt_text = alt_map.get(img_src, "Servizi tecnici Tempestivo a Palermo e Trapani")
                img['alt'] = alt_text
                
        # Salva il file aggiornato
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        print(f"ALT aggiornati in: {filename}")