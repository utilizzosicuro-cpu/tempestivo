from bs4 import BeautifulSoup
import os

# Il footer ottimizzato che abbiamo definito
new_footer_html = """
<footer class="footer" style="background-color: #444444; color: #FFFFFF; padding: 40px 20px; text-align: center; margin-top: 50px;">
    <div class="footer-inner" style="max-width: 1200px; margin: 0 auto; display: flex; flex-direction: column; align-items: center;">
        <div class="footer-logo" style="display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 20px;">
            <img src="img/logo.png" alt="Logo Tempestivo - Pronto Intervento e Ristrutturazioni a Palermo e Trapani" style="height: 40px; width: auto;">
            <div class="logo-text" style="text-align: left;">
                <span style="font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 18px; display: block;">TEMPESTIVO</span>
                <span style="font-size: 11px; text-transform: uppercase; opacity: 0.8; color: #FFC857;">RAPIDI & AFFIDABILI</span>
            </div>
        </div>
        <p class="footer-description" style="max-width: 700px; margin-bottom: 20px; font-size: 0.95rem; opacity: 0.9; line-height: 1.5;">
            Tempestivo è una divisione di <strong>Officina Creativa</strong> dedicata al General Contracting e alle manutenzioni rapide.
            Il team Tempestivo è composto da professionisti selezionati e aziende certificate tra Palermo e Trapani.
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

# Cartella dove si trovano i tuoi file HTML
folder_path = './' 

for filename in os.listdir(folder_path):
    if filename.endswith(".html"):
        filepath = os.path.join(folder_path, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        # Cerca il footer esistente e rimuovilo
        old_footer = soup.find('footer')
        if old_footer:
            old_footer.decompose()
        
        # Aggiunge il nuovo footer alla fine del body
        new_footer = BeautifulSoup(new_footer_html, 'html.parser')
        soup.body.append(new_footer)
        
        # Salva il file aggiornato
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        print(f"Aggiornato: {filename}")