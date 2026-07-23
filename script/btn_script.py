import os
import re

# Il blocco del pulsante di emergenza da iniettare se assente
btn_emergenza_html = """
<a href="tel:3520258583" class="btn-emergenza">
    <span class="icon">⚠️</span>
    <span>3520258583</span>
</a>
"""

# Regola CSS per garantire che l'header sia posizionato in modo fisso/sticky
header_css_rule = """
header {
    position: fixed !important;
    top: 0;
    left: 0;
    width: 100%;
    z-index: 1000;
}
"""

def update_header_and_sticky_button(folder_path):
    if not os.path.exists(folder_path):
        print(f"Errore: La cartella {folder_path} non esiste.")
        return

    for filename in os.listdir(folder_path):
        if filename.endswith(".html"):
            filepath = os.path.join(folder_path, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            modified = False

            # 1. Verifica se il blocco btn-emergenza esiste già nel codice
            if 'class="btn-emergenza"' not in content:
                # Cerca l'elemento .header-inner o il tag <header> per iniettare il bottone nel posto giusto
                if '<div class="header-inner">' in content:
                    # Inserisce il bottone alla fine di .header-inner
                    content = content.replace(
                        '<div class="header-inner">',
                        '<div class="header-inner">\n' + btn_emergenza_html
                    )
                    modified = True
                elif '<header>' in content:
                    # Fallback: inserisce subito dopo l'apertura del tag header
                    content = content.replace('<header>', '<header>\n' + btn_emergenza_html)
                    modified = True

            # 2. Verifica se l'header ha il corretto posizionamento fixed/sticky nel CSS
            # Controlliamo se all'interno dei tag <style> esiste già una regola per l'header con position fixed o sticky
            if 'position: fixed' not in content and 'position: sticky' not in content:
                # Se non c'è, iniettiamo la regola CSS prima della chiusura del tag </style> o dentro l'head
                if '</style>' in content:
                    content = content.replace('</style>', header_css_rule + '\n</style>')
                    modified = True
                elif '</head>' in content:
                    content = content.replace('</head>', '<style>\n' + header_css_rule + '\n</style>\n</head>')
                    modified = True

            # Salva il file solo se sono state effettuate modifiche
            if modified:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"[Aggiornato] Header e pulsante verificati in: {filename}")
            else:
                print(f"[Saltato] Nessuna modifica necessaria per: {filename}")

if __name__ == "__main__":
    # Esegue lo script nella cartella corrente (assicurati di aver fatto il backup prima)
    update_header_and_sticky_button('.')
    print("Processo di aggiornamento header completato.")