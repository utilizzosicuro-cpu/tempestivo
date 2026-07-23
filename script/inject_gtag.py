import os
import re

# Lo snippet Google Tag da iniettare
GTAG_SNIPPET = """<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-CVM98Z28DB"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-CVM98Z28DB');
</script>"""

# ID univoco per evitare duplicati
GTAG_ID = "G-CVM98Z28DB"

def inject_gtag_into_file(file_path):
    """
    Inietta lo snippet GTAG subito dopo l'apertura del tag <head>
    se non è già presente.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"[ERRORE LETTURA] {file_path}: {e}")
        return False

    # 1. Verifica se lo snippet è già presente nel file
    if GTAG_ID in content:
        print(f"[GIÀ PRESENTE] {file_path}")
        return False

    # 2. Cerca il tag <head> (gestisce anche attributi o maiuscole/minuscole es. <head class="...">)
    head_pattern = re.compile(r'(<head[^>]*>)', re.IGNORECASE)
    match = head_pattern.search(content)

    if not match:
        print(f"[TAG <head> NON TROVATO] {file_path}")
        return False

    # 3. Inserisce lo snippet subito dopo <head>
    replacement = f"{match.group(1)}\n{GTAG_SNIPPET}"
    new_content = head_pattern.sub(replacement, content, count=1)

    # 4. Salva il file modificato
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"[INNIETTATO] {file_path}")
        return True
    except Exception as e:
        print(f"[ERRORE SCRITTURA] {file_path}: {e}")
        return False

def main():
    root_dir = os.getcwd()  # Cartella corrente del progetto
    total_files = 0
    injected_files = 0

    print("=== INIZIO INIEZIONE GTAG.JS IN TUTTI I FILE HTML ===")

    # Scansiona tutte le cartelle e sottocartelle
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                total_files += 1
                if inject_gtag_into_file(file_path):
                    injected_files += 1

    print("\n==========================================")
    print(f"Scansione completata!")
    print(f"File HTML trovati:   {total_files}")
    print(f"File HTML aggiornati: {injected_files}")
    print("==========================================")

if __name__ == '__main__':
    main()