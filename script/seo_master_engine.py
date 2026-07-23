import os
import json
from bs4 import BeautifulSoup

# --- CARICAMENTO DATABASE ---
try:
    with open('zone.json', 'r', encoding='utf-8') as f:
        db_zone = json.load(f)
except FileNotFoundError:
    db_zone = {}

try:
    with open('faq_seo.json', 'r', encoding='utf-8') as f:
        db_faq = json.load(f)
except FileNotFoundError:
    db_faq = {}

# --- BLOCCHI HTML DA INIETTARE ---
footer_html = """
<footer class="footer" style="background-color: #444444; color: #FFFFFF; padding: 40px 20px; text-align: center; margin-top: 50px;">
    <div class="footer-inner" style="max-width: 1200px; margin: 0 auto; display: flex; flex-direction: column; align-items: center;">
        <div class="footer-logo" style="display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 20px;">
            <img alt="Logo Tempestivo - Pronto Intervento e Ristrutturazioni a Palermo e Trapani" src="img/logo.png" style="height: 40px; width: auto;">
            <div class="logo-text" style="text-align: left;">
                <span style="font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 18px; display: block;">TEMPESTIVO</span>
                <span style="font-size: 11px; text-transform: uppercase; opacity: 0.8; color: #FFC857;">RAPIDI & AFFIDABILI</span>
            </div>
        </div>
        <p class="footer-description" style="max-width: 700px; margin-bottom: 20px; font-size: 0.95rem; opacity: 0.9; line-height: 1.5;">
            Tempestivo è una divisione di <strong>Officina Creativa</strong> dedicata al General Contracting e alle manutenzioni rapide.
        </p>
        <div class="footer-links" style="display: flex; gap: 20px; justify-content: center; flex-wrap: wrap; margin-bottom: 20px;">
            <a href="soluzioni-business-palermo-trapani.html" style="color: #FFC857; font-weight: bold; text-decoration: none;">🏢 Soluzioni Business & Condomini</a>
            <a href="ristrutturazioni-palermo-trapani.html" style="color: #FFFFFF; text-decoration: none;">Ristrutturazioni</a>
            <a href="pronto-intervento-palermo-trapani.html" style="color: #FFFFFF; text-decoration: none;">🆘 Pronto Intervento H24</a>
            <a href="chi-siamo.html" style="color: #FFFFFF; text-decoration: none;">Chi Siamo</a>
        </div>
        <div style="margin-top:15px; margin-bottom:15px;">
            <a href="mappa-zone.html" style="color: #FFC857; text-decoration: underline;">Mappa delle Zone</a> ·
            <a href="servizi-partinico.html" style="color: #FFC857; text-decoration: underline;">Partinico</a> ·
            <a href="servizi-carini.html" style="color: #FFC857; text-decoration: underline;">Carini</a> ·
            <a href="servizi-alcamo.html" style="color: #FFC857; text-decoration: underline;">Alcamo</a>
        </div>
        <div class="footer-bottom" style="border-top: 1px solid rgba(255,255,255,0.1); padding-top: 20px; width: 100%; font-size: 0.8rem; opacity: 0.7;">
            <p>P.IVA: 06772720824 | Divisione di Officina Creativa</p>
            <p>&copy; 2026 Tempestivo. Tutti i diritti riservati. | <a href="privacy.html" style="color: #FFC857;">Privacy Policy</a></p>
        </div>
    </div>
</footer>
"""

btn_emergenza = """
<a href="tel:3520258583" class="btn-emergenza" style="
    position: fixed; top: 15px; right: 20px; background-color: #E32626; color: white;
    padding: 10px 20px; border-radius: 999px; font-weight: bold; z-index: 9999;
    text-decoration: none; box-shadow: 0 4px 6px rgba(0,0,0,0.2); font-family: sans-serif; font-size: 14px;
">🆘 Pronto Intervento</a>
"""

header_css_rule = """
<style>
header, .lp-header {
    position: sticky !important;
    top: 0;
    z-index: 1000;
}
</style>
"""

schema_recensioni_template = """
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Tempestivo - Servizi e Ristrutturazioni",
  "image": "https://tempestivo.it/img/logo.png",
  "telephone": "+393520258583",
  "priceRange": "€€",
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "reviewCount": "52",
    "bestRating": "5",
    "worstRating": "1"
  }
}
</script>
"""

def genera_widget_recensioni(citta_formattata, link_destinazione, testo_bottone, titolo_box):
    return f"""
    <div class="review-cta-box" style="background-color: #0B1B3B; color: #FFFFFF; padding: 30px 20px; border-radius: 12px; margin: 40px auto; max-width: 900px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
        <div style="font-size: 1.5rem; color: #FFC857; margin-bottom: 8px;">⭐⭐⭐⭐⭐</div>
        <h3 style="font-family: Montserrat, sans-serif; font-size: 1.4rem; margin-bottom: 10px; color: #FFFFFF;">{titolo_box}</h3>
        <p style="font-size: 0.95rem; opacity: 0.9; margin-bottom: 20px; color: #F5F5F5;">La trasparenza e la qualità certificate dai nostri clienti sul territorio.</p>
        <a href="{link_destinazione}" style="background-color: #FFC857; color: #0B1B3B; padding: 12px 25px; border-radius: 999px; font-weight: bold; text-decoration: none; display: inline-block; font-size: 0.9rem;">{text_bottone} →</a>
    </div>
    """

def master_engine():
    report = {
        "file_analizzati": 0,
        "dettagli_file": []
    }

    folder_path = '.'
    for filename in os.listdir(folder_path):
        if not filename.endswith(".html"): 
            continue
        
        report["file_analizzati"] += 1
        filepath = os.path.join(folder_path, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        modifiche_file = {
            "nome_file": filename,
            "btn_aggiunto": False,
            "css_sticky_aggiunto": False,
            "alt_aggiornati": 0,
            "footer_sostituito": False,
            "quartieri_aggiunti": [],
            "faq_aggiunta": False,
            "cross_link_aggiunto": False,
            "schema_aggiunto": False
        }

        # 1. Sticky Header & Pulsante Emergenza
        if not soup.find(class_="btn-emergenza"):
            if soup.body:
                soup.body.insert(0, BeautifulSoup(btn_emergenza, 'html.parser'))
                modifiche_file["btn_aggiunto"] = True

        if 'position: sticky' not in str(soup) and 'position: fixed' not in str(soup):
            if soup.head:
                soup.head.append(BeautifulSoup(header_css_rule, 'html.parser'))
                modifiche_file["css_sticky_aggiunto"] = True

        # 2. Tag ALT Automatici (Georeferenziati)
        citta = filename.replace("servizi-", "").replace("recensioni-", "").replace(".html", "").replace("-", " ")
        for img in soup.find_all('img'):
            if not img.get('alt'):
                img['alt'] = f"Tempestivo - Servizi tecnici e ristrutturazioni a {citta.title()}"
                modifiche_file["alt_aggiornati"] += 1

        # 3. Footer Unificato
        old_footer = soup.find('footer')
        if old_footer:
            old_footer.decompose()
        soup.append(BeautifulSoup(footer_html, 'html.parser'))
        modifiche_file["footer_sostituito"] = True

        # 4. Pertinenza Territoriale (Quartieri per pagine servizi)
        if filename.startswith("servizi-") and filename in db_zone:
            page_text = soup.get_text()
            for quartiere in db_zone[filename]["quartieri"]:
                if quartiere.lower() not in page_text.lower():
                    new_p = soup.new_tag("p")
                    new_p.string = f"Operiamo con rapidità anche nella zona di {quartiere}, garantendo assistenza tecnica in tempi brevissimi."
                    new_p['style'] = "margin: 15px 0; font-size: 1rem; color: #444444;"
                    
                    footer_tag = soup.find('footer')
                    if footer_tag:
                        footer_tag.insert_before(new_p)
                    elif soup.body:
                        soup.body.append(new_p)
                        
                    modifiche_file["quartieri_aggiunti"].append(quartiere)

        # 5. Iniezione Contenuti SEO (FAQ)
        if filename in db_faq:
            if db_faq[filename]["titolo"] not in soup.get_text():
                box_html = f"""
                <div class='seo-info-box' style='background-color: #F5F5F5; border-left: 5px solid #FFC857; padding: 25px; margin: 40px auto; max-width: 900px; border-radius: 8px;'>
                    <h3 style='font-family: Montserrat, Arial, sans-serif; color: #0B1B3B; font-size: 1.3rem; margin-bottom: 12px;'>{db_faq[filename]['titolo']}</h3>
                    <p style='font-family: Roboto, Arial, sans-serif; color: #444444; font-size: 1rem; line-height: 1.6; margin: 0;'>{db_faq[filename]['testo']}</p>
                </div>
                """
                primo_h2 = soup.find('h2')
                if primo_h2:
                    primo_h2.insert_after(BeautifulSoup(box_html, 'html.parser'))
                elif soup.body:
                    footer_tag = soup.find('footer')
                    if footer_tag:
                        footer_tag.insert_before(BeautifulSoup(box_html, 'html.parser'))
                    else:
                        soup.body.append(BeautifulSoup(box_html, 'html.parser'))
                modifiche_file["faq_aggiunta"] = True

        # 6. Cross-Linking & Widget tra Servizi e Recensioni
        if "review-cta-box" not in str(soup):
            citta_clean = citta.title()
            widget_html = None
            
            # Se siamo in una pagina servizi e la pagina recensioni corrispondente esiste
            if filename.startswith("servizi-"):
                file_recensione = filename.replace("servizi-", "recensioni-")
                if os.path.exists(file_recensione):
                    titolo = f"Cosa dicono i clienti a {citta_clean}?"
                    testo_btn = f"Leggi le Recensioni verificate a {citta_clean}"
                    widget_html = genera_widget_recensioni(citta_clean, file_recensione, testo_btn, titolo)
                    modifiche_file["cross_link_aggiunto"] = True

            # Se siamo in una pagina recensioni e la pagina servizi corrispondente esiste
            elif filename.startswith("recensioni-"):
                file_servizio = filename.replace("recensioni-", "servizi-")
                if os.path.exists(file_servizio):
                    titolo = f"Vuoi scoprire i servizi attivi a {citta_clean}?"
                    testo_btn = f"Vai ai Servizi di {citta_clean}"
                    widget_html = genera_widget_recensioni(citta_clean, file_servizio, testo_btn, titolo)
                    modifiche_file["cross_link_aggiunto"] = True
                    
                    # Aggiunge Schema Markup AggregateRating se manca nelle pagine recensioni
                    if "AggregateRating" not in str(soup):
                        if soup.head:
                            soup.head.append(BeautifulSoup(schema_recensioni_template, 'html.parser'))
                            modifiche_file["schema_aggiunto"] = True

            # Inserimento effettivo del widget prima del footer
            if widget_html:
                widget_soup = BeautifulSoup(widget_html, 'html.parser')
                footer_tag = soup.find('footer')
                if footer_tag:
                    footer_tag.insert_before(widget_soup)
                elif soup.body:
                    soup.body.append(widget_soup)

        # Salva il file HTML aggiornato
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
            
        report["dettagli_file"].append(modifiche_file)

    # --- STAMPA DEL REPORT FINALE ---
    print("\n" + "="*50)
    print("📊 REPORT FINALE - MASTER ENGINE SEO (RECENSIONI & CROSS-LINKING)")
    print("="*50)
    print(f"📁 Totale file HTML elaborati: {report['file_analizzati']}\n")

    for item in report["dettagli_file"]:
        print(f"📄 Pagina: {item['nome_file']}")
        print(f"   ├── 🆘 Pulsante emergenza: {'Aggiunto' if item['btn_aggiunto'] else 'Già presente'}")
        print(f"   ├── 🔻 Footer unificato: Sì")
        print(f"   ├── 🔗 Cross-Link / Widget Recensioni: {'Inserito' if item['cross_link_aggiunto'] else 'Non applicabile / Già presente'}")
        print(f"   └── ⭐ Schema Rich Snippets (Stelle): {'Aggiunto' if item['schema_aggiunto'] else 'Non richiesto / Già presente'}")
        print("-" * 50)

    print("\n[SUCCESS] Ottimizzazione recensioni e cross-linking completata!")

if __name__ == "__main__":
    master_engine()