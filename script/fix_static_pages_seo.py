#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per aggiungere Geo Tags e Schema.org valido 
SOLO alle pagine statiche specifiche: 
chi-siamo.html, landing-ristrutturazioni.html, mappa-zone.html, servizi.html
"""
import os
from pathlib import Path

# ============================================================================
# CONFIGURAZIONE
# ============================================================================
TARGET_FILES = [
    "chi-siamo.html",
    "landing-ristrutturazioni.html",
    "mappa-zone.html",
    "pronto-intervento-palermo-trapani.html", 
    "soluzioni-business-palermo-trapani.html",
    "servizi.html"
]

# Blocco di Geo Tags da inserire
GEO_TAGS = """    <!-- Geo Tags -->
    <meta name="geo.region" content="IT-PA">
    <meta name="geo.placename" content="Palermo, Trapani, Sicilia">
    <meta name="geo.position" content="38.1157;13.3615">
    <meta name="ICBM" content="38.1157, 13.3615">
"""

# Blocco di Schema.org valido (Organization + WebSite) da inserire
SCHEMA_ORG = """    <!-- Schema.org Organization -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "Organization",
      "name": "Tempestivo",
      "alternateName": "Tempestivo Ristrutturazioni e Pronto Intervento",
      "url": "https://tempestivo.it",
      "logo": "https://tempestivo.it/assets/logo.png",
      "description": "Divisione di Officina Creativa dedicata al General Contracting, ristrutturazioni chiavi in mano e pronto intervento H24 in Sicilia Occidentale.",
      "address": {
        "@type": "PostalAddress",
        "addressLocality": "Palermo",
        "addressRegion": "PA",
        "addressCountry": "IT"
      },
      "contactPoint": {
        "@type": "ContactPoint",
        "telephone": "+393520258583",
        "contactType": "customer service",
        "areaServed": "IT",
        "availableLanguage": ["Italian"]
      }
    }
    </script>
"""

# ============================================================================
# FUNZIONI
# ============================================================================
def fix_file(filepath):
    """Legge il file, aggiunge i tag mancanti e salva."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  ❌ Errore nella lettura di {filepath}: {e}")
        return False

    modified = False

    # 1. Controllo e aggiunta Geo Tags
    if 'name="geo.region"' not in content:
        content = content.replace('</head>', GEO_TAGS + '    </head>')
        modified = True
        print(f"  [+] Aggiunti Geo Tags")

    # 2. Controllo e aggiunta Schema.org
    # Controlliamo se esiste già uno script ld+json valido per evitare duplicati inutili
    has_valid_schema = any(x in content for x in ['"@type": "Organization"', '"@type": "LocalBusiness"', '"@type": "WebSite"'])
    
    if not has_valid_schema:
        content = content.replace('</head>', SCHEMA_ORG + '    </head>')
        modified = True
        print(f"  [+] Aggiunto Schema.org Organization valido")
    elif '<script type="application/ld+json">' not in content:
        # Fallback: se non c'è proprio il tag script, lo aggiungiamo
        content = content.replace('</head>', SCHEMA_ORG + '    </head>')
        modified = True
        print(f"  [+] Aggiunto Schema.org (fallback)")

    # Salvataggio se modificato
    if modified:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"  ❌ Errore nel salvataggio di {filepath}: {e}")
            return False
            
    return False

# ============================================================================
# MAIN
# ============================================================================
def main():
    print("🔧 Avvio fix SEO per pagine statiche specifiche...")
    print("=" * 60)
    
    # Directory da scansionare (priorità a 'output', poi la cartella corrente)
    search_dirs = [Path('output'), Path('.')]
    files_found = 0
    files_modified = 0

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
            
        print(f"🔍 Ricerca in: {search_dir.absolute()}")
        
        # Cerca ricorsivamente tutti gli HTML
        for filepath in search_dir.rglob('*.html'):
            if filepath.name in TARGET_FILES:
                files_found += 1
                print(f"\n📄 Trovato: {filepath.relative_to(search_dir) if search_dir.name != '.' else filepath.name}")
                
                if fix_file(filepath):
                    print(f"    ✅ File modificato con successo.")
                    files_modified += 1
                else:
                    print(f"    ℹ️  Nessuna modifica necessaria (tag già presenti).")

    print("\n" + "=" * 60)
    print("📊 REPORT FINALE")
    print("=" * 60)
    print(f"File target trovati: {files_found}")
    print(f"File modificati:     {files_modified}")
    print("=" * 60)
    
    if files_modified == 0 and files_found > 0:
        print("💡 Nessun file è stato modificato perché conteneva già i tag corretti.")
    elif files_found == 0:
        print("⚠️  Nessun file target trovato. Verifica di essere nella cartella giusta del progetto.")

if __name__ == "__main__":
    main()