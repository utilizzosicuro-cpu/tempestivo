#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tempestivo SEO Fix - Corregge Title, H1, Meta Description di tutte le pagine
Versione robusta con BeautifulSoup e mappa hardcoded.

USO:
    python fix_seo.py              # Applica modifiche
    python fix_seo.py --dry-run    # Anteprima senza salvare
    python fix_seo.py --citta trappeto  # Solo una città
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
DESC_MAX = 160
DESC_MIN = 120
TELEFONO = "3520258583"

# Mappa hardcoded: non serve nessun file esterno
MAPPA_CITTA = {
    'palermo': 'Palermo',
    'castellammare': 'Castellammare del Golfo',
    'alcamo': 'Alcamo',
    'terrasini': 'Terrasini',
    'cinisi': 'Cinisi',
    'balestrate': 'Balestrate',
    'partinico': 'Partinico',
    'monreale': 'Monreale',
    'trappeto': 'Trappeto',
    'isola-delle-femmine': 'Isola delle Femmine',
    'carini': 'Carini',
}

MAPPA_PROFESSIONI = {
    'impianti-elettrici': {'prof': 'Elettricista', 'kw': 'Impianti Elettrici'},
    'impianti-idraulici': {'prof': 'Idraulico', 'kw': 'Impianti Idraulici'},
    'ristrutturazioni': {'prof': 'Impresa Edile', 'kw': 'Ristrutturazioni'},
    'pronto-intervento': {'prof': 'Pronto Intervento', 'kw': 'Emergenze H24'},
}

# Altri servizi (senza professione specifica, usa il nome del servizio)
ALTRI_SERVIZI = {
    'imbiancatura': {'prof': 'Imbianchino', 'kw': 'Imbiancatura'},
    'ristrutturazione-bagno': {'prof': 'Ristrutturazione', 'kw': 'Bagno'},
    'ristrutturazione-cucina': {'prof': 'Ristrutturazione', 'kw': 'Cucina'},
}

# Unisci le mappe
TUTTI_SERVIZI = {**MAPPA_PROFESSIONI, **ALTRI_SERVIZI}

# ============================================================================
# PARSING
# ============================================================================
def slug_to_readable(slug):
    """Converte slug in testo leggibile: 'centro-storico' → 'Centro Storico'"""
    if not slug:
        return ""
    # Eccezioni per nomi con apostrofi o formati speciali
    exceptions = {
        'isola-delle-femmine': 'Isola delle Femmine',
        'castellammare-del-golfo': 'Castellammare del Golfo',
    }
    if slug in exceptions:
        return exceptions[slug]
    return slug.replace('-', ' ').title()

def parse_filename(filename):
    """
    Estrae servizio, città e quartiere dal nome file.
    Es: 'impianti-elettrici-trappeto-centro-storico.html'
    Ritorna: ('impianti-elettrici', 'trappeto', 'centro-storico')
    """
    name = filename.replace('.html', '')
    
    # Prova ogni prefisso servizio (dal più lungo al più corto)
    prefissi_ordinati = sorted(TUTTI_SERVIZI.keys(), key=len, reverse=True)
    
    for prefisso in prefissi_ordinati:
        if name.startswith(prefisso + '-'):
            resto = name[len(prefisso) + 1:]
            
            # Trova la città nel resto
            for citta_slug in sorted(MAPPA_CITTA.keys(), key=len, reverse=True):
                if resto.startswith(citta_slug + '-'):
                    quartiere_slug = resto[len(citta_slug) + 1:]
                    return prefisso, citta_slug, quartiere_slug
                elif resto == citta_slug:
                    return prefisso, citta_slug, ''
            
            # Se non trova la città, usa la prima parte come città
            parts = resto.split('-', 1)
            citta_slug = parts[0]
            quartiere_slug = parts[1] if len(parts) > 1 else ''
            return prefisso, citta_slug, quartiere_slug
    
    return None, None, None

# ============================================================================
# GENERAZIONE CONTENUTO SEO
# ============================================================================
def tronca_intelligente(testo, max_len):
    """Tronca testo a max_len caratteri in modo intelligente"""
    if len(testo) <= max_len:
        return testo
    # Tronca all'ultimo spazio prima del limite
    troncato = testo[:max_len]
    ultimo_spazio = troncato.rfind(' ')
    if ultimo_spazio > max_len * 0.7:
        troncato = troncato[:ultimo_spazio]
    return troncato.rstrip(' ,;') + '...'

def genera_title(prof, kw, quartiere_nome, citta_nome):
    """Genera title ottimizzato (max 60 caratteri)"""
    # Prova diverse varianti dalla più lunga alla più corta
    varianti = [
        f"{prof} e {kw} a {quartiere_nome} | {citta_nome}",
        f"{prof} {kw} a {quartiere_nome} | {citta_nome}",
        f"{prof} a {quartiere_nome} | Tempestivo {citta_nome}",
        f"{prof} a {quartiere_nome} | {citta_nome}",
    ]
    
    for variante in varianti:
        if len(variante) <= TITLE_MAX:
            return variante
    
    # Se tutte superano, tronca l'ultima
    return tronca_intelligente(varianti[-1], TITLE_MAX)

def genera_description(prof, kw, quartiere_nome, citta_nome):
    """Genera meta description ottimizzata (120-160 caratteri)"""
    # Template base
    template = f"{prof} e {kw} a {quartiere_nome}, {citta_nome}. Preventivo gratuito in 24h, tempi certi. Chiama {TELEFONO}."
    
    if len(template) <= DESC_MAX:
        # Se è troppo corta, aggiungi dettagli
        if len(template) < DESC_MIN:
            template = f"{prof} e {kw} a {quartiere_nome}, {citta_nome}. Preventivo gratuito in 24h, tempi certi contrattualizzati. Chiama {TELEFONO}."
        return template[:DESC_MAX]
    
    # Se troppo lunga, prova versione compatta
    template_compatto = f"{prof} a {quartiere_nome}, {citta_nome}. Preventivo gratuito in 24h. Chiama {TELEFONO}."
    
    if len(template_compatto) <= DESC_MAX:
        return template_compatto
    
    return tronca_intelligente(template, DESC_MAX)

# ============================================================================
# MODIFICA FILE HTML
# ============================================================================
def modifica_file_html(filepath, new_title, new_description, new_h1, dry_run=False):
    """Modifica title, meta description, h1, og tags di un file HTML"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    modifiche = []
    
    # 1. Title
    title_tag = soup.find('title')
    if title_tag:
        old_title = title_tag.string
        if old_title != new_title:
            title_tag.string = new_title
            modifiche.append(f"Title: '{old_title}' → '{new_title}'")
    
    # 2. Meta Description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc:
        old_desc = meta_desc.get('content', '')
        if old_desc != new_description:
            meta_desc['content'] = new_description
            modifiche.append(f"Desc: '{old_desc[:50]}...' → '{new_description[:50]}...'")
    
    # 3. H1
    h1_tag = soup.find('h1')
    if h1_tag and new_h1:
        old_h1 = h1_tag.get_text().strip()
        if old_h1 != new_h1:
            # Mantieni lo span highlight se presente
            span = h1_tag.find('span', class_='highlight')
            if span:
                # Ricostruisci h1 mantenendo lo span
                span_text = span.get_text()
                before_span = new_h1.split(' a ')[0] + ' a ' if ' a ' in new_h1 else new_h1
                h1_tag.clear()
                h1_tag.append(before_span)
                new_span = soup.new_tag('span', **{'class': 'highlight'})
                new_span.string = span_text
                h1_tag.append(new_span)
            else:
                h1_tag.string = new_h1
            modifiche.append(f"H1: '{old_h1}' → '{new_h1}'")
    
    # 4. OG Title
    og_title = soup.find('meta', property='og:title')
    if og_title:
        og_title['content'] = new_title
    
    # 5. OG Description
    og_desc = soup.find('meta', property='og:description')
    if og_desc:
        og_desc['content'] = new_description[:DESC_MAX]
    
    # Salva se ci sono modifiche
    if modifiche and not dry_run:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
    
    return modifiche

# ============================================================================
# MAIN
# ============================================================================
def main():
    parser = argparse.ArgumentParser(description='Fix SEO Title e Description')
    parser.add_argument('--dry-run', action='store_true', help='Anteprima senza salvare')
    parser.add_argument('--citta', type=str, help='Solo una città (slug)')
    args = parser.parse_args()
    
    print("🔧 TEMPESTIVO SEO FIX")
    print("=" * 70)
    print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"🔧 Modalità: {'DRY RUN (anteprima)' if args.dry_run else 'APPLICAZIONE REALE'}")
    print(f"📏 Limiti: Title ≤ {TITLE_MAX} char | Description ≤ {DESC_MAX} char")
    print("=" * 70)
    
    if not OUTPUT_DIR.exists():
        print(f"❌ Cartella output non trovata: {OUTPUT_DIR}")
        return
    
    # Trova città
    if args.citta:
        citta_dirs = [OUTPUT_DIR / args.citta]
    else:
        citta_dirs = sorted([d for d in OUTPUT_DIR.iterdir() if d.is_dir()])
    
    total_modified = 0
    total_skipped = 0
    total_errors = 0
    
    for citta_dir in citta_dirs:
        if not citta_dir.exists():
            continue
        
        print(f"\n🏙️  {citta_dir.name.upper()}")
        print("-" * 70)
        
        html_files = sorted(citta_dir.glob('*.html'))
        citta_modified = 0
        
        for html_file in html_files:
            filename = html_file.name
            
            # Skip file hub e index
            if filename == 'index.html' or filename.startswith('servizi-') or filename.startswith('hub-'):
                continue
            
            # Parsa il nome file
            servizio_tipo, citta_slug, quartiere_slug = parse_filename(filename)
            
            if not servizio_tipo:
                print(f"   ⏭️  {filename} (servizio non riconosciuto)")
                total_skipped += 1
                continue
            
            if servizio_tipo not in TUTTI_SERVIZI:
                print(f"   ⏭️  {filename} (servizio '{servizio_tipo}' non in mappa)")
                total_skipped += 1
                continue
            
            # Recupera info
            info = TUTTI_SERVIZI[servizio_tipo]
            prof = info['prof']
            kw = info['kw']
            citta_nome = MAPPA_CITTA.get(citta_slug, slug_to_readable(citta_slug))
            quartiere_nome = slug_to_readable(quartiere_slug) if quartiere_slug else citta_nome
            
            # Genera contenuti
            new_title = genera_title(prof, kw, quartiere_nome, citta_nome)
            new_desc = genera_description(prof, kw, quartiere_nome, citta_nome)
            new_h1 = f"{prof} e {kw} a {quartiere_nome}"
            
            # Applica modifiche
            try:
                modifiche = modifica_file_html(html_file, new_title, new_desc, new_h1, dry_run=args.dry_run)
                
                if modifiche:
                    citta_modified += 1
                    total_modified += 1
                    status = "🔄" if not args.dry_run else "📝"
                    print(f"   {status} {filename}")
                    for mod in modifiche:
                        print(f"      {mod}")
                    print(f"      📏 Title: {len(new_title)} char | Desc: {len(new_desc)} char")
                else:
                    print(f"   ✅ {filename} (già OK)")
            except Exception as e:
                print(f"   ❌ {filename}: {e}")
                total_errors += 1
        
        print(f"   → {citta_dir.name}: {citta_modified} pagine modificate")
    
    # Report finale
    print("\n" + "=" * 70)
    print("📊 REPORT FINALE")
    print("=" * 70)
    print(f"🔄 Pagine modificate: {total_modified}")
    print(f"⏭️  Pagine saltate: {total_skipped}")
    print(f"❌ Errori: {total_errors}")
    
    if args.dry_run and total_modified > 0:
        print(f"\n💡 Per applicare le modifiche:")
        print(f"   python fix_seo.py")
    
    print("=" * 70)

if __name__ == "__main__":
    main()