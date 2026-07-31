import os
import glob
from bs4 import BeautifulSoup

def process_html_files(root_dir):
    # Cerca ricorsivamente tutti i file .html nelle cartelle e sottocartelle
    html_files = glob.glob(os.path.join(root_dir, '**', '*.html'), recursive=True)
    
    modified_count = 0
    
    for html_path in html_files:
        # Salva la cartella che contiene la pagina HTML corrente
        html_dir = os.path.dirname(html_path)
        page_name = os.path.basename(html_path)
        base_name, _ = os.path.splitext(page_name)
        
        # Nome dell'immagine attesa (es. og-idraulico-centro-storico.jpg)
        img_filename = f"og-{base_name}.jpg"
        
        # Percorso fisico dell'immagine nella cartella localeimages/ della pagina
        img_physical_path = os.path.join(html_dir, "images", img_filename)
        
        # Verifica se l'immagine fisica esiste veramente nella cartella images
        if os.path.exists(img_physical_path):
            with open(html_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')
                
            # Verifica se l'immagine è già presente nel corpo per evitare duplicati
            existing_img = soup.find('img', src=f"images/{img_filename}") or soup.find('img', src=f"./images/{img_filename}")
            
            if not existing_img:
                # Trova il primo tag H1 nella pagina
                h1_tag = soup.find('h1')
                
                if h1_tag:
                    # Crea il tag immagine con lo stile richiesto
                    alt_text = h1_tag.get_text(strip=True)
                    img_tag = soup.new_tag('img', 
                                           src=f"images/{img_filename}", 
                                           alt=alt_text,
                                           style="width:100%; height:auto; border-radius:8px; margin-bottom:20px;")
                    
                    # Inserisce l'immagine subito dopo il tag H1
                    h1_tag.insert_after(img_tag)
                    
                    # Salva il file HTML modificato
                    with open(html_path, 'w', encoding='utf-8') as file:
                        file.write(str(soup))
                        
                    print(f"[OK] Aggiunta immagine a: {html_path}")
                    modified_count += 1
                else:
                    print(f"[SKIP] Nessun H1 trovato in: {html_path}")
            else:
                print(f"[SKIP] Immagine già presente in: {html_path}")
        else:
            # L'immagine non esiste nella cartella images di quel comune
            pass

    print(f"\nOperazione completata! Modificate con successo {modified_count} pagine.")

if __name__ == "__main__":
    # Esegue lo script partendo dalla cartella corrente in cui si trova lo script
    current_directory = os.getcwd()
    process_html_files(current_directory)