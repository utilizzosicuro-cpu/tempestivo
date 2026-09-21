#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script di generazione automatica Sitemap.xml e Robots.txt
Scansiona la cartella corrente e le sottocartelle alla ricerca di file HTML.

Autore: Assistente SEO
Data: 2026-09-20
"""

import os
from pathlib import Path
from datetime import datetime

# ============================================================
# CONFIGURAZIONE
# ============================================================
# Inserisci l'URL di base del tuo sito web (senza slash finale)
BASE_URL = "https://www.tempestivo.it"

# Directory di lavoro (cartella corrente in cui viene eseguito lo script)
BASE_DIR = Path(".")

# Estensioni o pattern da ignorare (es. file di backup)
IGNORA_PATTERN = ["backup", ".DS_Store", "template"]

# ============================================================
# FUNZIONE PRINCIPALE
# ============================================================
def genera_sitemap_e_robots():
    print("=" * 60)
    print("🚀 GENERATORE AUTOMATICO SITEMAP.XML & ROBOTS.TXT")
    print("=" * 60)
    print(f"🌐 URL Base: {BASE_URL}")
    print(f"📁 Directory di scansione: {BASE_DIR.absolute()}")
    print("-" * 60)

    html_files = []
    
    # Scansione ricorsiva di cartelle e sottocartelle
    for file_path in BASE_DIR.rglob("*.html"):
        # Salta i file che contengono parole chiave da ignorare (es. i backup)
        nome_file_str = str(file_path).lower()
        if any(pattern in nome_file_str for pattern in IGNORA_PATTERN):
            continue
        html_files.append(file_path)

    if not html_files:
        print("⚠️ Nessun file HTML trovato nella directory e nelle sottocartelle.")
        return

    # 1. Generazione di sitemap.xml
    sitemap_path = BASE_DIR / "sitemap.xml"
    data_odierna = datetime.now().strftime("%Y-%m-%d")
    
    xml_content = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    count = 0
    for file_path in sorted(html_files):
        # Converte il percorso in URL pulito
        rel_path = file_path.relative_to(BASE_DIR)
        url_path = str(rel_path).replace("\\", "/")
        
        # Se il file è index.html, puliamo l'URL rimuovendo "index.html" alla fine
        if url_path.endswith("index.html"):
            url_path = url_path[:-len("index.html")]
            
        # Costruisce l'URL completo
        full_url = f"{BASE_URL}/{url_path}".rstrip("/") + ("/" if not url_path.endswith("/") and "." not in url_path.split("/")[-1] else "")
        # Nota: se l'URL non ha estensione finale (es. cartella pulita), aggiungiamo lo slash
        if not url_path.endswith("/") and not url_path.endswith(".html"):
             full_url += "/"

        xml_content.append("  <url>")
        xml_content.append(f"    <loc>{full_url}</loc>")
        xml_content.append(f"    <lastmod>{data_odierna}</lastmod>")
        xml_content.append(f"    <changefreq>weekly</changefreq>")
        xml_content.append(f"    <priority>0.8</priority>")
        xml_content.append("  </url>")
        count += 1

    xml_content.append('</urlset>')
    
    try:
        with open(sitemap_path, "w", encoding="utf-8") as f:
            f.write("\n".join(xml_content))
        print(f"✅ File sitemap.xml creato con successo ({count} URL indicizzati).")
    except Exception as e:
        print(f"❌ Errore nella scrittura di sitemap.xml: {e}")

    # 2. Generazione di robots.txt
    robots_path = BASE_DIR / "robots.txt"
    robots_content = f"""User-agent: *
Allow: /

# Mappa del sito
Sitemap: {BASE_URL}/sitemap.xml
"""
    try:
        with open(robots_path, "w", encoding="utf-8") as f:
            f.write(robots_content)
        print(f"✅ File robots.txt creato con successo.")
    except Exception as e:
        print(f"❌ Errore nella scrittura di robots.txt: {e}")

    print("=" * 60)
    print("💡 Operazione completata! Carica sitemap.xml e robots.txt sul server.")
    print("=" * 60)

if __name__ == "__main__":
    genera_sitemap_e_robots()