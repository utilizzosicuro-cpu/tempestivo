import os
import json
from bs4 import BeautifulSoup

# --- HTML UNIFICATO DELLA NAVBAR E SUB-NAV (Estratto dalla tua index) ---
unified_navbar_html = """
<header>
<div class="header-inner">
<a class="logo" href="index.html">
<img alt="Logo Tempestivo - Pronto Intervento e Ristrutturazioni a Palermo e Trapani" class="logo-img" src="img/logo.png" style="height:34px; width:auto;"/>
<div class="logo-text">
<span>TEMPESTIVO</span>
<span style="font-size: 11px; text-transform: uppercase; opacity: 0.8; color: var(--giallo);">RAPIDI &amp; AFFIDABILI</span>
</div>
</a>
<nav class="main-nav">
<a class="business-nav-link" href="soluzioni-business-palermo-trapani.html">Area Business</a>
</nav>
<div class="header-cta">
<a class="btn-emergenza" href="tel:3520258583">
<span class="icon">⚠️</span>
<span>3520258583</span>
</a>
</div>
</div>
</header>
<nav class="sub-nav">
<div class="sub-nav-inner">
<a class="sub-nav-link" href="chi-siamo.html">Chi Siamo</a>
<a class="sub-nav-link" href="servizi.html">Servizi</a>
<a class="sub-nav-link" href="mappa-zone.html">Zone Coperte</a>
<a class="sub-nav-link" href="landing-ristrutturazioni.html">Ristrutturazioni complete e veloci</a>
</div>
</nav>
<div class="page-offset"></div>
"""

# CSS di sicurezza per garantire che l'header sia posizionato correttamente in alto
header_css_rule = """
<style>
header {
    position: fixed !important;
    top: 0;
    left: 0;
    width: 100%;
    z-index: 1000;
}
</style>
"""

def update_navbars_across_site():
    report = {
        "file_analizzati": 0,
        "dettagli": []
    }

    folder_path = '.'
    for filename in os.listdir(folder_path):
        if not filename.endswith(".html"):
            continue

        report["file_analizzati"] += 1
        filepath = os.path.join(folder_path, filename)

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        soup = BeautifulSoup(content, 'html.parser')
        modificato = False

        # 1. Rimuove eventuali header, sub-nav o page-offset esistenti per evitare duplicazioni o conflitti
        for old_header in soup.find_all('header'):
            old_header.decompose()
            modificato = True

        for old_sub_nav in soup.find_all('nav', class_='sub-nav'):
            old_sub_nav.decompose()
            modificato = True

        for old_offset in soup.find_all('div', class_='page-offset'):
            old_offset.decompose()
            modificato = True

        # 2. Inietta la nuova navbar unificata subito dopo l'apertura del body
        if soup.body:
            new_nav_soup = BeautifulSoup(unified_navbar_html, 'html.parser')
            # Inserisce gli elementi all'inizio del body
            first_child = soup.body.find(True)
            if first_child:
                first_child.insert_before(new_nav_soup)
            else:
                soup.body.append(new_nav_soup)
            modificato = True

        # 3. Assicura che il CSS per l'header fixed/sticky sia presente nell'head
        if 'position: fixed' not in str(soup) and 'position: sticky' not in str(soup):
            if soup.head:
                soup.head.append(BeautifulSoup(header_css_rule, 'html.parser'))

        # Salva il file HTML aggiornato
        if modificato:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            status = "Aggiornato con successo"
        else:
            status = "Nessuna modifica necessaria"

        report["dettagli"].append({"file": filename, "stato": status})

    # --- REPORT FINALE ---
    print("\n" + "="*50)
    print("📊 REPORT FINALE - AGGIORNAMENTO NAVBAR UNIFICATA")
    print("="*50)
    print(f"📁 Totale file HTML esaminati: {report['file_analizzati']}\n")

    for item in report["dettagli"]:
        print(f"📄 {item['file']} ──> {item['stato']}")
    print("-" * 50)
    print("[SUCCESS] Tutte le navbar sono state sincronizzate!")

if __name__ == "__main__":
    update_navbars_across_site()