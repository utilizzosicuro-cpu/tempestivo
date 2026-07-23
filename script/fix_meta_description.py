#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tempestivo Meta Description Optimizer
Normalizza tutte le meta description a ~120 caratteri (range 115-125)

USO:
    python fix_meta_description.py            # Applica modifiche
    python fix_meta_description.py --dry-run  # Anteprima senza salvare
    python fix_meta_description.py --target 120  # Target personalizzato
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

# Target e range per meta description
TARGET_LENGTH = 120
MIN_LENGTH = 120
MAX_LENGTH = 120

# CTA standard da aggiungere se la description è troppo corta
CTA_EXTENSIONS = [
    " Preventivo gratuito in 24h.",
    " Chiama 3520258583.",
    " Tempi certi contrattualizzati.",
    " Sopralluogo gratuito.",
    " Tecnici qualificati.",
]

# ============================================================================
# FUNZIONI DI OTTIMIZZAZIONE
# ============================================================================
def tronca_intelligente(testo, target=TARGET_LENGTH):
    """Tronca il testo al target mantenendo senso compiuto"""
    if len(testo) <= target:
        return testo
    
    # Prendo i primi 'target' caratteri
    troncato = testo[:target]
    
    # Cerco l'ultimo spazio prima del target
    ultimo_spazio = troncato.rfind(' ')
    
    if ultimo_spazio > target * 0.7:  # Almeno il 70% del target
        troncato = troncato[:ultimo_spazio]
    
    # Rimuovo punteggiatura finale sospesa
    troncato = troncato.rstrip(' ,;')
    
    # Se non finisce con punto, aggiungo "..."
    if not troncato.endswith('.') and not troncato.endswith('!') and not troncato.endswith('?'):
        troncato += "..."
    
    return troncato

def estendi_intelligente(testo, target=TARGET_LENGTH):
    """Estende il testo aggiungendo CTA fino al target"""
    if len(testo) >= target:
        return testo
    
    risultato = testo
    
    # Provo ad aggiungere CTA una alla volta
    for cta in CTA_EXTENSIONS:
        if len(risultato) + len(cta) <= target:
            risultato += cta
            if len(risultato) >= MIN_LENGTH:
                break
    
    # Se ancora troppo corto, aggiungo CTA completa
    if len(risultato) < MIN_LENGTH:
        risultato += " Preventivo gratuito in 24h. Chiama 3520258583."
    
    # Se ora troppo lungo, tronco
    if len(risultato) > MAX_LENGTH:
        risultato = tronca_intelligente(risultato, MAX_LENGTH)
    
    return risultato

def ottimizza_description(testo, target=TARGET_LENGTH):
    """Ottimizza la meta description al target"""
    if not testo:
        return "Ristrutturazioni e impianti a Tempestivo. Preventivo gratuito in 24h. Chiama 3520258583."
    
    # Rimuovo spazi multipli
    testo = re.sub(r'\s+', ' ', testo).strip()
    
    # Se è nel range accettabile, lascio invariato
    if MIN_LENGTH <= len(testo) <= MAX_LENGTH:
        return testo
    
    # Se troppo lunga, tronco
    if len(testo) > MAX_LENGTH:
        return tronca_intelligente(testo, target)
    
    # Se troppo corta, estendo
    if len(testo) < MIN_LENGTH:
        return estendi_intelligente(testo, target)
    
    return testo

# ============================================================================
# PROCESSING PAGINA
# ============================================================================
def processa_pagina(filepath, dry_run=False):
    """Processa una singola pagina HTML"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return None
    
    soup = BeautifulSoup(content, 'html.parser')
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    
    if not meta_desc:
        return None
    
    vecchia_desc = meta_desc.get('content', '')
    nuova_desc = ottimizza_description(vecchia_desc)
    
    # Se non cambia, skip
    if vecchia_desc == nuova_desc:
        return None
    
    # Applica modifica
    if not dry_run:
        meta_desc['content'] = nuova_desc
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
    
    return {
        'file': str(filepath.relative_to(OUTPUT_DIR)),
        'vecchia_lunghezza': len(vecchia_desc),
        'nuova_lunghezza': len(nuova_desc),
        'vecchia': vecchia_desc[:80] + "..." if len(vecchia_desc) > 80 else vecchia_desc,
        'nuova': nuova_desc[:80] + "..." if len(nuova_desc) > 80 else nuova_desc,
        'delta': len(nuova_desc) - len(vecchia_desc)
    }

# ============================================================================
# MAIN
# ============================================================================
def main():
    parser = argparse.ArgumentParser(description='Ottimizza Meta Description a ~120 caratteri')
    parser.add_argument('--dry-run', action='store_true', help='Anteprima senza salvare')
    parser.add_argument('--target', type=int, default=TARGET_LENGTH, help=f'Target caratteri (default: {TARGET_LENGTH})')
    args = parser.parse_args()
    
    global TARGET_LENGTH, MIN_LENGTH, MAX_LENGTH
    TARGET_LENGTH = args.target
    MIN_LENGTH = TARGET_LENGTH - 5
    MAX_LENGTH = TARGET_LENGTH + 5
    
    print("🔧 TEMPESTIVO META DESCRIPTION OPTIMIZER")
    print("=" * 70)
    print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"🎯 Target: {TARGET_LENGTH} caratteri (range: {MIN_LENGTH}-{MAX_LENGTH})")
    print(f"🔧 Modalità: {'DRY RUN (anteprima)' if args.dry_run else 'APPLICAZIONE REALE'}")
    print("=" * 70)
    
    if not OUTPUT_DIR.exists():
        print(f"❌ Cartella output non trovata: {OUTPUT_DIR}")
        return
    
    # Trova tutte le pagine HTML
    html_files = list(OUTPUT_DIR.rglob('*.html'))
    print(f"\n📂 Trovate {len(html_files)} pagine HTML\n")
    
    modifiche = []
    pagine_invariate = 0
    pagine_errore = 0
    
    for html_file in html_files:
        risultato = processa_pagina(html_file, dry_run=args.dry_run)
        
        if risultato:
            modifiche.append(risultato)
            # Output in tempo reale
            status = "📝" if args.dry_run else "✅"
            print(f"{status} {risultato['file']}")
            print(f"   {risultato['vecchia_lunghezza']} → {risultato['nuova_lunghezza']} char (Δ{risultato['delta']:+d})")
            print(f"   Prima: {risultato['vecchia']}")
            print(f"   Dopo:  {risultato['nuova']}")
            print()
        else:
            pagine_invariate += 1
    
    # Report finale
    print("\n" + "=" * 70)
    print("📊 REPORT FINALE")
    print("=" * 70)
    print(f"📄 Pagine analizzate: {len(html_files)}")
    print(f"✏️  Pagine modificate: {len(modifiche)}")
    print(f"⏸️  Pagine invariate: {pagine_invariate}")
    
    if modifiche:
        # Statistiche
        vecchie_lunghezze = [m['vecchia_lunghezza'] for m in modifiche]
        nuove_lunghezze = [m['nuova_lunghezza'] for m in modifiche]
        
        print(f"\n📏 STATISTICHE LUNGHEZZE:")
        print(f"   Prima: media {sum(vecchie_lunghezze)/len(vecchie_lunghezze):.1f} char (min {min(vecchie_lunghezze)}, max {max(vecchie_lunghezze)})")
        print(f"   Dopo:  media {sum(nuove_lunghezze)/len(nuove_lunghezze):.1f} char (min {min(nuove_lunghezze)}, max {max(nuove_lunghezze)})")
        
        # Pagine ancora fuori range
        fuori_range = [m for m in modifiche if not (MIN_LENGTH <= m['nuova_lunghezza'] <= MAX_LENGTH)]
        if fuori_range:
            print(f"\n⚠️  Pagine ancora fuori range: {len(fuori_range)}")
            for m in fuori_range[:5]:
                print(f"   - {m['file']}: {m['nuova_lunghezza']} char")
    
    if args.dry_run and modifiche:
        print(f"\n💡 DRY RUN completato. Per applicare le modifiche:")
        print(f"   python fix_meta_description.py")
    
    print("=" * 70)

if __name__ == "__main__":
    main()