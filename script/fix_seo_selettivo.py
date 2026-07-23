#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tempestivo SEO Fix Selettivo
Corregge in modo intelligente:
1. Title Tag (se > 60 caratteri)
2. Meta Description (target ~120 caratteri, range 115-130)

USO:
python fix_seo_selettivo.py            # Applica le modifiche
python fix_seo_selettivo.py --dry-run  # Anteprima senza salvare
"""
import os
import re
import argparse
from pathlib import Path
from datetime import datetime

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ Errore: pip install beautifulsoup4")
    exit(1)

# ============================================================================
# CONFIGURAZIONE
# ============================================================================
BASE_DIR = Path(__file__).parent.resolve()
OUTPUT_DIR = BASE_DIR / 'output'

TITLE_MAX = 60
TARGET_DESC_LENGTH = 120
MIN_DESC_LENGTH = 115
MAX_DESC_LENGTH = 130  # Leggermente più di 120 per evitare tagli netti, ma ben sotto i 160 di Google

CTA_EXTENSIONS = [
    " Preventivo gratuito in 24h.",
    " Chiama 3520258583.",
    " Tempi certi contrattualizzati.",
    " Sopralluogo gratuito.",
    " Tecnici qualificati.",
    " Intervento rapido H24.",
]

# ============================================================================
# FUNZIONI DI OTTIMIZZAZIONE
# ============================================================================
def tronca_intelligente(testo, max_len):
    """Tronca il testo al max_len mantenendo il senso compiuto"""
    if len(testo) <= max_len:
        return testo, False
    
    troncato = testo[:max_len]
    ultimo_spazio = troncato.rfind(' ')
    
    # Se l'ultimo spazio è almeno al 70% del limite, taglia lì
    if ultimo_spazio > max_len * 0.7:
        troncato = troncato[:ultimo_spazio]
    
    # Rimuovi punteggiatura finale sospesa
    troncato = troncato.rstrip(' ,;')
    
    # Aggiungi puntini se non finisce con un segno di punteggiatura valido
    if not troncato.endswith('.') and not troncato.endswith('!') and not troncato.endswith('?'):
        troncato += "..."
        
    return troncato, True

def estendi_descrizione(testo, target=TARGET_DESC_LENGTH):
    """Estende la description aggiungendo CTA fino al target"""
    if len(testo) >= MIN_DESC_LENGTH:
        return testo, False
    
    risultato = testo
    for cta in CTA_EXTENSIONS:
        if len(risultato) + len(cta) <= MAX_DESC_LENGTH:
            risultato += cta
            if len(risultato) >= MIN_DESC_LENGTH:
                break
    
    # Se è ancora troppo corto, aggiungi una CTA completa
    if len(risultato) < MIN_DESC_LENGTH:
        risultato += " Preventivo gratuito in 24h. Chiama 3520258583."
    
    # Sicurezza: se superiamo il max, tronchiamo
    if len(risultato) > MAX_DESC_LENGTH:
        risultato, _ = tronca_intelligente(risultato, MAX_DESC_LENGTH)
        
    return risultato, True

# ============================================================================
# PROCESSING PAGINA
# ============================================================================
def processa_pagina(filepath, dry_run=False):
    """Processa una singola pagina HTML correggendo Title e Meta Description"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return None

    soup = BeautifulSoup(content, 'html.parser')
    modifiche = []

    # 1. CORREZIONE TITLE
    title_tag = soup.find('title')
    if title_tag:
        title_text = title_tag.get_text().strip()
        if len(title_text) > TITLE_MAX:
            nuovo_title, cambiato = tronca_intelligente(title_text, TITLE_MAX)
            if cambiato:
                modifiche.append({
                    'tipo': 'title',
                    'problema': f'Troppo lungo ({len(title_text)} char, max {TITLE_MAX})',
                    'prima': title_text,
                    'dopo': nuovo_title
                })
                if not dry_run:
                    title_tag.string = nuovo_title

    # 2. CORREZIONE META DESCRIPTION
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc:
        desc_text = meta_desc.get('content', '').strip()
        
        # Rimuovi spazi multipli
        desc_text = re.sub(r'\s+', ' ', desc_text)
        
        if len(desc_text) > MAX_DESC_LENGTH:
            nuova_desc, cambiato = tronca_intelligente(desc_text, MAX_DESC_LENGTH)
            if cambiato:
                modifiche.append({
                    'tipo': 'meta_description',
                    'problema': f'Troppo lunga ({len(desc_text)} char, max {MAX_DESC_LENGTH})',
                    'prima': desc_text[:70] + "...",
                    'dopo': nuova_desc[:70] + "..."
                })
                if not dry_run:
                    meta_desc['content'] = nuova_desc
                    
        elif len(desc_text) < MIN_DESC_LENGTH:
            nuova_desc, cambiato = estendi_descrizione(desc_text, TARGET_DESC_LENGTH)
            if cambiato:
                modifiche.append({
                    'tipo': 'meta_description',
                    'problema': f'Troppo corta ({len(desc_text)} char, min {MIN_DESC_LENGTH})',
                    'prima': desc_text,
                    'dopo': nuova_desc
                })
                if not dry_run:
                    meta_desc['content'] = nuova_desc

    # Se non ci sono modifiche, skip
    if not modifiche:
        return None

    # Salva il file se non è dry-run
    if not dry_run:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))

    return {
        'file': str(filepath.relative_to(OUTPUT_DIR)),
        'modifiche': modifiche
    }

# ============================================================================
# MAIN
# ============================================================================
def main():
    parser = argparse.ArgumentParser(description='Ottimizza Title e Meta Description per la SEO')
    parser.add_argument('--dry-run', action='store_true', help='Anteprima senza salvare le modifiche')
    args = parser.parse_args()

    print("🔧 TEMPESTIVO SEO FIX SELETTIVO")
    print("=" * 70)
    print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"🎯 Target: Title ≤ {TITLE_MAX} char | Description ~{TARGET_DESC_LENGTH} char (max {MAX_DESC_LENGTH})")
    print(f"🔧 Modalità: {'DRY RUN (anteprima)' if args.dry_run else 'APPLICAZIONE REALE'}")
    print("=" * 70)

    if not OUTPUT_DIR.exists():
        print(f"❌ Cartella output non trovata: {OUTPUT_DIR}")
        return

    html_files = list(OUTPUT_DIR.rglob('*.html'))
    print(f"\n📂 Trovate {len(html_files)} pagine HTML da analizzare\n")

    pagine_modificate = 0
    report_modifiche = []

    for html_file in html_files:
        risultato = processa_pagina(html_file, dry_run=args.dry_run)
        
        if risultato:
            pagine_modificate += 1
            report_modifiche.append(risultato)
            
            status = "📝" if args.dry_run else "✅"
            print(f"{status} {risultato['file']}")
            for mod in risultato['modifiche']:
                print(f"   • {mod['tipo']}: {mod['problema']}")
                print(f"     Prima: {mod['prima']}")
                print(f"     Dopo:  {mod['dopo']}")
            print()

    # Report finale
    print("\n" + "=" * 70)
    print("📊 REPORT FINALE")
    print("=" * 70)
    print(f"📄 Pagine analizzate: {len(html_files)}")
    print(f"✏️  Pagine ottimizzate: {pagine_modificate}")
    print(f"⏸️  Pagine già a posto: {len(html_files) - pagine_modificate}")

    if pagine_modificate > 0 and args.dry_run:
        print(f"\n💡 DRY RUN completato. Per applicare le modifiche, esegui:")
        print(f"   python fix_seo_selettivo.py")
    
    print("=" * 70)

if __name__ == "__main__":
    main()