import os
import json
from bs4 import BeautifulSoup, Comment

def gestisci_css_e_duplicati(file_mappa="mappa_balestrate_2.json"):
    if not os.path.exists(file_mappa):
        print(f"Errore: Il file della mappa '{file_mappa}' non è stato trovato.")
        return

    with open(file_mappa, 'r', encoding='utf-8') as f:
        dati_mappa = json.load(f)  #[cite: 2]

    struttura = dati_mappa.get("struttura", {})  #[cite: 2]
    file_modificati = 0
    file_eliminati = 0

    print("=== Avvio ottimizzazione CSS Tempestivo e pulizia duplicati ==-\n")

    for percorso_relativo, info in struttura.items():
        if not percorso_relativo.endswith('.html'):
            continue
            
        if percorso_relativo.startswith("alcamo/"):  #[cite: 2]
            continue

        percorso_assoluto = info.get("percorso_assoluto")  #[cite: 2]
        if not percorso_assoluto or not os.path.exists(percorso_assoluto):
            continue

        if "indexx.html" in percorso_relativo:  #[cite: 2]
            print(f"[ELIMINAZIONE DUPLICATO] Trovato file anomalo: {percorso_relativo}")  #[cite: 2]
            try:
                os.remove(percorso_assoluto)
                file_eliminati += 1
                print(" -> File eliminato con successo.")
            except Exception as e:
                print(f" -> Errore durante l'eliminazione: {e}")
            continue

        with open(percorso_assoluto, 'r', encoding='utf-8', errors='ignore') as f:
            contenuto_html = f.read()

        soup = BeautifulSoup(contenuto_html, 'html.parser')
        modificato = False

        # 1. Individuiamo i vecchi commenti "CSS Tempestivo"
        commenti_da_rimuovere = [c for c in soup.find_all(string=lambda text: isinstance(text, Comment) and 'CSS Tempestivo' in text)]
        if commenti_da_rimuovere:
            for c in commenti_da_rimuovere:
                c.extract()
            modificato = True

        # 2. Raccogliamo TUTTI i vecchi link CSS da rimuovere (evitando il bug dell'iterazione in-place)
        link_da_rimuovere = []
        for link in soup.find_all('link'):
            href = link.get('href', '').lower()
            rel = link.get('rel', [])
            rel_str = " ".join(rel).lower() if isinstance(rel, list) else str(rel).lower()
            
            if 'stylesheet' in rel_str or 'style.css' in href or 'mobile' in href:
                link_da_rimuovere.append(link)

        if link_da_rimuovere:
            for link in link_da_rimuovere:
                link.decompose()
            modificato = True

        # 3. Iniettiamo il blocco pulito con commento e link mirati alla root
        if soup.head:
            nuovo_commento = Comment(" CSS Tempestivo ")
            link_style = soup.new_tag('link', href='/style.css', rel='stylesheet')
            link_mobile = soup.new_tag('link', href='/mobile-fix.css', rel='stylesheet')
            
            soup.head.append(nuovo_commento)
            soup.head.append(link_style)
            soup.head.append(link_mobile)
            modificato = True

        # Salvataggio delle modifiche nel file HTML
        if modificato:
            with open(percorso_assoluto, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            file_modificati += 1
            print(f"[AGGIORNATO] CSS Tempestivo configurato correttamente in: {percorso_relativo}")  #[cite: 2]

    print(f"\n=== Elaborazione completata ===")
    print(f"- File HTML aggiornati: {file_modificati}")
    print(f"- File duplicati/anomali rimossi: {file_eliminati}")

if __name__ == "__main__":
    gestisci_css_e_duplicati()