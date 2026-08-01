import os
import glob
import re

# 1. Contenuto del file mobile-fix.css
CSS_CONTENT = """/* ==========================================
   MOBILE FIXES - Tempestivo.it
   Versione isolata per ottimizzazione mobile
   ========================================== */

@media (max-width: 768px) {
    /* Previene lo scorrimento orizzontale della pagina */
    html, body {
        overflow-x: hidden !important;
        max-width: 100vw !important;
    }

    /* Rende tutti i media fluidi e adatti allo schermo */
    img, video, iframe, svg {
        max-width: 100% !important;
        height: auto !important;
    }

    /* Aggiusta contenitori e sezioni rigide */
    .container, .main-container, section, article {
        max-width: 100% !important;
        box-sizing: border-box !important;
    }

    /* Forza la colonna singola per layout a griglia o colonne CSS */
    .reviews-grid, .vantaggi-grid, .grid, .row {
        display: flex !important;
        flex-direction: column !important;
        grid-template-columns: 1fr !important;
        width: 100% !important;
    }

    /* Corregge liste a colonne multipli (es. zone servite) */
    .zones-list ul {
        columns: 1 !important;
        -webkit-columns: 1 !important;
        -moz-columns: 1 !important;
    }

    /* Header e Nav bar mobile */
    .header-inner, .sub-nav-inner {
        flex-direction: column !important;
        align-items: center !important;
        text-align: center !important;
    }

    /* Tipografia adattiva per schermi piccoli */
    h1 { font-size: 1.8rem !important; }
    h2 { font-size: 1.5rem !important; }
    h3 { font-size: 1.2rem !important; }
}
"""

def create_css_file(root_dir="."):
    css_path = os.path.join(root_dir, "mobile-fix.css")
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(CSS_CONTENT)
    print(f"[OK] Creato file: {css_path}")

def inject_mobile_css_tag(root_dir="."):
    pattern = os.path.join(root_dir, "**", "*.html")
    files = glob.glob(pattern, recursive=True)
    
    tag_to_inject = '<link rel="stylesheet" href="/mobile-fix.css">'
    updated_count = 0

    print("--- Iniezione mobile-fix.css nei file HTML ---")
    for file_path in files:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Evita duplicati
        if "mobile-fix.css" in content:
            print(f"[SKIP] Già presente in: {file_path}")
            continue

        # Inserimento prima della chiusura del tag </head>
        if "</head>" in content:
            new_content = re.sub(r'(?i)(</head>)', f'  {tag_to_inject}\n\\1', content, count=1)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"[OK] Inserito in: {file_path}")
            updated_count += 1

    print(f"\nTotale pagine aggiornate con il fix mobile: {updated_count}")

if __name__ == "__main__":
    create_css_file()
    inject_mobile_css_tag()