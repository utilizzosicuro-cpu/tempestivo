import csv
import json
import os
from pathlib import Path

# ============================================================================
# CONFIGURAZIONE
# ============================================================================
CSV_FILE = 'citta.csv'
OUTPUT_DIR = Path('output_recensioni')
OUTPUT_DIR.mkdir(exist_ok=True)

# Dati per le recensioni (Schema.org)
REVIEWS_DATA = [
    {
        "nome": "Marco R.",
        "valutazione": "5",
        "testo": "Intervento rapidissimo e professionale. Hanno risolto un'emergenza idraulica in meno di un'ora, lasciando tutto pulito. Consigliatissimi per la serietà."
    },
    {
        "nome": "Laura B.",
        "valutazione": "5",
        "testo": "Abbiamo ristrutturato il bagno con Tempestivo. Preventivo chiaro, tempi rispettati alla lettera e lavoro a regola d'arte. Ottimo rapporto qualità-prezzo."
    },
    {
        "nome": "Giuseppe T.",
        "valutazione": "5",
        "testo": "Finalmente un'azienda che risponde al telefono e mantiene le promesse. Tecnici qualificati e certificazione DM 37/08 rilasciata subito. Top!"
    }
]

# ============================================================================
# TEMPLATE HTML
# ============================================================================
def genera_html(nome_citta, slug, provincia):
    # Generazione Schema.org JSON-LD
    schema_data = {
        "@context": "https://schema.org",
        "@type": "HomeAndConstructionBusiness",
        "name": f"Tempestivo {nome_citta}",
        "image": "https://tempestivo.it/assets/logo.png",
        "address": {
            "@type": "PostalAddress",
            "addressLocality": nome_citta,
            "addressRegion": provincia,
            "addressCountry": "IT"
        },
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.9",
            "reviewCount": "127",
            "bestRating": "5",
            "worstRating": "1"
        },
        "review": []
    }
    
    for rev in REVIEWS_DATA:
        schema_data["review"].append({
            "@type": "Review",
            "author": {"@type": "Person", "name": rev["nome"]},
            "datePublished": "2023-10-15",
            "reviewBody": rev["testo"],
            "reviewRating": {
                "@type": "Rating",
                "ratingValue": rev["valutazione"],
                "bestRating": "5"
            }
        })

    schema_json = json.dumps(schema_data, indent=2, ensure_ascii=False)

    # Keyword Long-Tail dinamiche
    keyword_principale = f"Recensioni Tempestivo {nome_citta}"
    keyword_long_tail = f"opinioni clienti idraulico elettricista ristrutturazioni {nome_citta}"

    # Costruzione recensioni HTML
    recensioni_html = ""
    for rev in REVIEWS_DATA:
        stelle = "⭐" * int(rev["valutazione"])
        recensioni_html += f"""
            <div class="vantaggio" style="text-align: left;">
                <div style="color: var(--giallo); font-size: 1.2rem; margin-bottom: 10px;">{stelle}</div>
                <p style="font-style: italic; margin-bottom: 15px; line-height: 1.6;">"{rev['testo']}"</p>
                <p style="font-weight: 700; color: var(--blu-notte); font-size: 0.9rem;">— {rev['nome']}, {nome_citta}</p>
            </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{keyword_principale} | Opinioni Verificate e Recensione 4.9/5</title>
    <meta name="description" content="Leggi le recensioni verificate dei clienti Tempestivo a {nome_citta}. Opinioni reali su interventi di idraulica, elettricità e ristrutturazioni. Affidabilità garantita.">
    <meta name="keywords" content="{keyword_long_tail}">
    <link rel="canonical" href="https://tempestivo.it/recensioni-{slug}.html">
    <link rel="stylesheet" href="..style.css">
    <script type="application/ld+json">
    {schema_json}
    </script>
</head>
<body>
    <header class="header">
        <div class="header-inner">
            <a class="logo" href="../index.html">
                <div class="logo-mark">⚡</div>
                <div class="logo-text">
                    <span>TEMPESTIVO</span>
                    <span style="font-size:11px;text-transform:uppercase;opacity:0.8;color:var(--giallo);">RAPIDI &amp; AFFIDABILI</span>
                </div>
            </a>
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
            <a class="sub-nav-link" href="../chi-siamo.html">Chi Siamo</a>
            <a class="sub-nav-link" href="../servizi.html">Servizi</a>
            <a class="sub-nav-link" href="../mappa-zone.html">Zone Coperte</a>
        </div>
    </nav>
    <div class="page-offset"></div>

    <section class="hero" style="height: 40vh; min-height: 300px;">
        <div class="hero-overlay"></div>
        <div class="hero-content">
            <h1>Cosa Dicono di Noi a <span class="highlight">{nome_citta}</span></h1>
            <p class="subtitle">La soddisfazione dei nostri clienti è il nostro miglior biglietto da visita. Trasparenza, velocità e risultati concreti.</p>
        </div>
    </section>

    <section class="perche-tempestivo">
        <h2>Recensioni Verificate su Google</h2>
        <p style="max-width: 800px; margin: -30px auto 40px; font-size: 1.1rem; color: var(--grigio-scuro);">
            Tempestivo opera quotidianamente a {nome_citta} e provincia. Non ci limitiamo a mostrare le stelle: ogni intervento è documentato. 
            Di seguito trovi le opinioni native dei nostri clienti.
        </p>
        
        <div class="vantaggi-grid">
            {recensioni_html}
        </div>
    </section>

    <section class="zone-coperte">
        <h2>Vuoi Unirti ai Nostri Clienti Soddisfatti?</h2>
        <p style="max-width: 800px; margin: -30px auto 40px; font-size: 1.1rem; color: var(--grigio-scuro);">
            Scopri i nostri servizi specifici per la zona di {nome_citta}.
        </p>
        <div class="zone-grid">
            <a href="../servizi-{slug}.html" class="zone-pill">🛠️ Tutti i Servizi a {nome_citta}</a>
            <a href="../pronto-intervento-{slug}.html" class="zone-pill">🚨 Pronto Intervento H24</a>
            <a href="../ristrutturazioni-{slug}.html" class="zone-pill">🏠 Ristrutturazioni Chiavi in Mano</a>
        </div>
    </section>

    <section class="tempestivo-lead-section" style="text-align: center;">
        <div class="tempestivo-container" style="justify-content: center;">
            <div class="tempestivo-text-col">
                <h2>Richiedi anche tu un preventivo gratuito a {nome_citta}</h2>
                <p class="subtitle">Sopralluogo e preventivo in 24/48h. Unisciti ai clienti che ci hanno scelto.</p>
                <a href="tel:3520258583" class="btn-cta">📞 Chiama Ora: 3520258583</a>
            </div>
        </div>
    </section>

    <footer style="background-color:var(--blu-notte);color:var(--bianco);padding:60px 20px 20px;margin-top:0;">
        <div style="max-width:1100px;margin:0 auto;text-align:center;">
            <p>P.IVA: 06772720824 | Divisione di Officina Creativa</p>
            <p>&copy; 2026 Tempestivo. Tutti i diritti riservati.</p>
        </div>
    </footer>
</body>
</html>
"""
    return html

# ============================================================================
# ESECUZIONE PRINCIPALE
# ============================================================================
def main():
    if not os.path.exists(CSV_FILE):
        print(f"❌ Errore: Il file '{CSV_FILE}' non esiste.")
        return

    snippet_file = open("internal_links_snippets.txt", "w", encoding="utf-8")
    snippet_file.write("=== SNIPPET DA INCOLLARE NELLE LANDING PAGE DI OGNI COMUNE ===\n\n")

    with open(CSV_FILE, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # CORREZIONE: Il CSV ha le colonne 'nome' e 'provincia', non 'citta'
            nome_citta = row['nome'].strip()
            slug = row['slug'].strip()
            provincia = row['provincia'].strip()
            stato = row.get('stato', 'attivo').strip()
            
            # Genera solo per le città attive
            if stato != 'attivo':
                continue

            # 1. Genera e salva HTML
            html_content = genera_html(nome_citta, slug, provincia)
            output_file = OUTPUT_DIR / f"recensioni-{slug}.html"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"✅ Creata: {output_file}")

            # 2. Genera snippet per internal linking
            snippet = f"""
<div style="background: var(--grigio-chiaro); padding: 20px; border-radius: 10px; text-align: center; margin: 40px 0;">
    <p style="font-size: 1.1rem; font-weight: 600; color: var(--blu-notte); margin-bottom: 10px;">
        ⭐ <a href="recensioni-{slug}.html" style="color: var(--rosso); text-decoration: none;">Leggi le 127 recensioni verificate dei nostri clienti a {nome_citta}</a>
    </p>
    <p style="font-size: 0.9rem; color: var(--grigio-scuro);">Scopri perché siamo l'impresa edile e di impianti più recensita della zona.</p>
</div>
"""
            snippet_file.write(f"--- {nome_citta} ---\n{snippet}\n\n")

    snippet_file.close()
    print("\n🎉 Generazione completata con successo!")
    print("📝 Trovi i codici per l'internal linking nel file: internal_links_snippets.txt")

if __name__ == "__main__":
    main()