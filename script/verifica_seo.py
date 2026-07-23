#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tempestivo SEO Verifier - Script di verifica completa
Analizza tutte le pagine HTML generate e produce report dettagliato
Controlla: title, meta, link, schema.org, OG tags, geo tags, H1, canonical, etc.
"""
import os
import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ Errore: BeautifulSoup non installato")
    print("Esegui: pip install beautifulsoup4")
    exit(1)

# ============================================================================
# CONFIGURAZIONE
# ============================================================================
BASE_DIR = Path(__file__).parent.resolve()
OUTPUT_DIR = BASE_DIR / 'output'
REPORT_DIR = BASE_DIR / 'reports'

# Elementi SEO da verificare
SEO_CHECKS = {
    'title': {
        'required': True,
        'min_length': 30,
        'max_length': 60,
        'description': 'Title tag'
    },
    'meta_description': {
        'required': True,
        'min_length': 120,
        'max_length': 160,
        'description': 'Meta description'
    },
    'meta_keywords': {
        'required': False,
        'description': 'Meta keywords'
    },
    'h1': {
        'required': True,
        'count': 1,
        'description': 'H1 tag (deve essercene esattamente 1)'
    },
    'canonical': {
        'required': True,
        'description': 'Canonical URL'
    },
    'og_title': {
        'required': True,
        'description': 'Open Graph title'
    },
    'og_description': {
        'required': True,
        'description': 'Open Graph description'
    },
    'og_image': {
        'required': True,
        'description': 'Open Graph image'
    },
    'geo_region': {
        'required': True,
        'description': 'Geo region tag'
    },
    'geo_placename': {
        'required': True,
        'description': 'Geo placename tag'
    },
    'geo_position': {
        'required': True,
        'description': 'Geo position tag'
    },
    'schema_org': {
        'required': True,
        'description': 'Schema.org JSON-LD'
    },
    'internal_links': {
        'required': True,
        'description': 'Link interni validi'
    }
}

# ============================================================================
# FUNZIONI DI VERIFICA
# ============================================================================
def verifica_title(soup, filepath):
    """Verifica title tag"""
    title = soup.find('title')
    if not title:
        return False, "Title tag mancante", 0
    
    title_text = title.get_text().strip()
    length = len(title_text)
    
    issues = []
    score = 100
    
    if length < SEO_CHECKS['title']['min_length']:
        issues.append(f"Title troppo corto ({length} caratteri, minimo {SEO_CHECKS['title']['min_length']})")
        score -= 30
    elif length > SEO_CHECKS['title']['max_length']:
        issues.append(f"Title troppo lungo ({length} caratteri, massimo {SEO_CHECKS['title']['max_length']})")
        score -= 20
    
    if not title_text:
        return False, "Title vuoto", 0
    
    return True, issues if issues else "OK", score

def verifica_meta_description(soup):
    """Verifica meta description"""
    meta = soup.find('meta', attrs={'name': 'description'})
    if not meta:
        return False, "Meta description mancante", 0
    
    content = meta.get('content', '').strip()
    length = len(content)
    
    issues = []
    score = 100
    
    if length < SEO_CHECKS['meta_description']['min_length']:
        issues.append(f"Meta description troppo corta ({length} caratteri, minimo {SEO_CHECKS['meta_description']['min_length']})")
        score -= 30
    elif length > SEO_CHECKS['meta_description']['max_length']:
        issues.append(f"Meta description troppo lunga ({length} caratteri, massimo {SEO_CHECKS['meta_description']['max_length']})")
        score -= 20
    
    if not content:
        return False, "Meta description vuota", 0
    
    return True, issues if issues else "OK", score

def verifica_h1(soup):
    """Verifica H1 tag"""
    h1_tags = soup.find_all('h1')
    count = len(h1_tags)
    
    if count == 0:
        return False, "H1 tag mancante", 0
    elif count > 1:
        return False, f"Troppi H1 tag trovati ({count})", 50
    
    h1_text = h1_tags[0].get_text().strip()
    if not h1_text:
        return False, "H1 vuoto", 0
    
    return True, "OK", 100

def verifica_canonical(soup):
    """Verifica canonical URL"""
    canonical = soup.find('link', rel='canonical')
    if not canonical:
        return False, "Canonical URL mancante", 0
    
    href = canonical.get('href', '').strip()
    if not href:
        return False, "Canonical URL vuota", 0
    
    if not href.startswith('https://'):
        return False, "Canonical URL non HTTPS", 70
    
    return True, "OK", 100

def verifica_og_tags(soup):
    """Verifica Open Graph tags"""
    checks = {
        'og:title': soup.find('meta', property='og:title'),
        'og:description': soup.find('meta', property='og:description'),
        'og:image': soup.find('meta', property='og:image')
    }
    
    missing = []
    for tag_name, tag in checks.items():
        if not tag or not tag.get('content'):
            missing.append(tag_name)
    
    if missing:
        return False, f"OG tags mancanti: {', '.join(missing)}", 100 - (len(missing) * 20)
    
    return True, "OK", 100

def verifica_geo_tags(soup):
    """Verifica geo tags"""
    checks = {
        'geo.region': soup.find('meta', attrs={'name': 'geo.region'}),
        'geo.placename': soup.find('meta', attrs={'name': 'geo.placename'}),
        'geo.position': soup.find('meta', attrs={'name': 'geo.position'})
    }
    
    missing = []
    for tag_name, tag in checks.items():
        if not tag or not tag.get('content'):
            missing.append(tag_name)
    
    if missing:
        return False, f"Geo tags mancanti: {', '.join(missing)}", 100 - (len(missing) * 20)
    
    return True, "OK", 100

def verifica_schema_org(soup):
    """Verifica Schema.org JSON-LD"""
    scripts = soup.find_all('script', type='application/ld+json')
    
    if not scripts:
        return False, "Schema.org JSON-LD mancante", 0
    
    valid_schemas = 0
    for script in scripts:
        try:
            data = json.loads(script.string)
            if '@context' in data and '@type' in data:
                valid_schemas += 1
        except:
            pass
    
    if valid_schemas == 0:
        return False, "Nessuno Schema.org valido trovato", 0
    
    return True, f"{valid_schemas} Schema.org validi", 100

def verifica_link_interni(soup, filepath, output_dir):
    """Verifica link interni"""
    links = soup.find_all('a', href=True)
    broken_links = []
    valid_links = 0
    
    for link in links:
        href = link['href']
        
        # Skip link esterni, anchor, tel, mailto
        if href.startswith(('http://', 'https://', '#', 'tel:', 'mailto:', 'javascript:')):
            continue
        
        # Link interno relativo
        if href.endswith('.html'):
            # Rimuovi anchor se presente
            link_path = href.split('#')[0]
            full_path = filepath.parent / link_path
            
            if not full_path.exists():
                broken_links.append(href)
            else:
                valid_links += 1
    
    if broken_links:
        return False, f"{len(broken_links)} link rotti: {', '.join(broken_links[:3])}", max(0, 100 - len(broken_links) * 10)
    
    return True, f"{valid_links} link interni validi", 100

def calcola_punteggio_seo(results):
    """Calcola punteggio SEO complessivo"""
    if not results:
        return 0
    
    total_score = sum(r['score'] for r in results.values())
    max_score = len(results) * 100
    
    return round((total_score / max_score) * 100, 1)

# ============================================================================
# ANALISI PAGINA
# ============================================================================
def analizza_pagina(filepath, output_dir):
    """Analizza una singola pagina HTML"""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    results = {}
    
    # Verifica tutti gli elementi SEO
    checks = [
        ('title', verifica_title, (soup, filepath)),
        ('meta_description', verifica_meta_description, (soup,)),
        ('h1', verifica_h1, (soup,)),
        ('canonical', verifica_canonical, (soup,)),
        ('og_tags', verifica_og_tags, (soup,)),
        ('geo_tags', verifica_geo_tags, (soup,)),
        ('schema_org', verifica_schema_org, (soup,)),
        ('internal_links', verifica_link_interni, (soup, filepath, output_dir))
    ]
    
    for check_name, check_func, args in checks:
        try:
            valid, message, score = check_func(*args)
            results[check_name] = {
                'valid': valid,
                'message': message,
                'score': score
            }
        except Exception as e:
            results[check_name] = {
                'valid': False,
                'message': f"Errore durante verifica: {str(e)}",
                'score': 0
            }
    
    # Calcola punteggio complessivo
    overall_score = calcola_punteggio_seo(results)
    
    return {
        'file': str(filepath.relative_to(output_dir)),
        'results': results,
        'overall_score': overall_score,
        'status': 'ok' if overall_score >= 80 else 'warning' if overall_score >= 60 else 'error'
    }

# ============================================================================
# GENERAZIONE REPORT
# ============================================================================
def genera_report(analisi_list, output_dir):
    """Genera report completo"""
    REPORT_DIR.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Report testuale
    report_txt = REPORT_DIR / f'seo_report_{timestamp}.txt'
    with open(report_txt, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("TEMPESTIVO SEO VERIFICATION REPORT\n")
        f.write(f"Generato: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        # Statistiche generali
        total_pages = len(analisi_list)
        ok_pages = sum(1 for a in analisi_list if a['status'] == 'ok')
        warning_pages = sum(1 for a in analisi_list if a['status'] == 'warning')
        error_pages = sum(1 for a in analisi_list if a['status'] == 'error')
        
        avg_score = sum(a['overall_score'] for a in analisi_list) / total_pages if total_pages > 0 else 0
        
        f.write("📊 STATISTICHE GENERALI\n")
        f.write("-" * 80 + "\n")
        f.write(f"Totale pagine analizzate: {total_pages}\n")
        f.write(f"✅ Pagine OK (score >= 80): {ok_pages}\n")
        f.write(f"⚠️  Pagine Warning (score 60-79): {warning_pages}\n")
        f.write(f"❌ Pagine Error (score < 60): {error_pages}\n")
        f.write(f"📈 Punteggio medio: {avg_score:.1f}/100\n")
        f.write("\n")
        
        # Pagine con errori
        if error_pages > 0:
            f.write("❌ PAGINE CON ERRORI CRITICI\n")
            f.write("-" * 80 + "\n")
            for analisi in analisi_list:
                if analisi['status'] == 'error':
                    f.write(f"\n📄 {analisi['file']}\n")
                    f.write(f"   Punteggio: {analisi['overall_score']}/100\n")
                    for check_name, result in analisi['results'].items():
                        if not result['valid']:
                            f.write(f"   ❌ {check_name}: {result['message']}\n")
            f.write("\n")
        
        # Pagine con warning
        if warning_pages > 0:
            f.write("⚠️  PAGINE CON WARNING\n")
            f.write("-" * 80 + "\n")
            for analisi in analisi_list:
                if analisi['status'] == 'warning':
                    f.write(f"\n📄 {analisi['file']}\n")
                    f.write(f"   Punteggio: {analisi['overall_score']}/100\n")
                    for check_name, result in analisi['results'].items():
                        if not result['valid'] or result['score'] < 100:
                            f.write(f"   ⚠️  {check_name}: {result['message']}\n")
            f.write("\n")
        
        # Dettaglio completo
        f.write("📋 DETTAGLIO COMPLETO\n")
        f.write("-" * 80 + "\n")
        for analisi in sorted(analisi_list, key=lambda x: x['overall_score']):
            f.write(f"\n📄 {analisi['file']}\n")
            f.write(f"   Punteggio: {analisi['overall_score']}/100 [{analisi['status'].upper()}]\n")
            for check_name, result in analisi['results'].items():
                status_icon = "✅" if result['valid'] else "❌"
                f.write(f"   {status_icon} {check_name}: {result['message']} ({result['score']}/100)\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("FINE REPORT\n")
        f.write("=" * 80 + "\n")
    
    # Report JSON
    report_json = REPORT_DIR / f'seo_report_{timestamp}.json'
    with open(report_json, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_pages': total_pages,
            'statistics': {
                'ok': ok_pages,
                'warning': warning_pages,
                'error': error_pages,
                'average_score': avg_score
            },
            'pages': analisi_list
        }, f, indent=2, ensure_ascii=False)
    
    return report_txt, report_json

# ============================================================================
# MAIN
# ============================================================================
def main():
    print("🔍 TEMPESTIVO SEO VERIFIER")
    print("=" * 80)
    
    if not OUTPUT_DIR.exists():
        print(f"❌ Cartella output non trovata: {OUTPUT_DIR}")
        print("   Esegui prima generator.py per generare le pagine")
        return
    
    # Trova tutte le città
    citta_dirs = [d for d in OUTPUT_DIR.iterdir() if d.is_dir()]
    
    if not citta_dirs:
        print("❌ Nessuna città trovata in output/")
        return
    
    print(f"📂 Trovate {len(citta_dirs)} città\n")
    
    analisi_list = []
    
    for citta_dir in citta_dirs:
        print(f"🏙️  Analizzando {citta_dir.name}...")
        
        # Trova tutti i file HTML
        html_files = list(citta_dir.glob('**/*.html'))
        
        for html_file in html_files:
            try:
                analisi = analizza_pagina(html_file, OUTPUT_DIR)
                analisi_list.append(analisi)
                
                # Output in tempo reale
                status_icon = "✅" if analisi['status'] == 'ok' else "⚠️" if analisi['status'] == 'warning' else "❌"
                print(f"   {status_icon} {html_file.name}: {analisi['overall_score']}/100")
            except Exception as e:
                print(f"   ❌ Errore durante analisi {html_file.name}: {e}")
    
    print(f"\n📊 Generazione report...")
    report_txt, report_json = genera_report(analisi_list, OUTPUT_DIR)
    
    print(f"\n✅ Report generati:")
    print(f"   📄 {report_txt}")
    print(f"   📄 {report_json}")
    
    # Statistiche finali
    total_pages = len(analisi_list)
    ok_pages = sum(1 for a in analisi_list if a['status'] == 'ok')
    avg_score = sum(a['overall_score'] for a in analisi_list) / total_pages if total_pages > 0 else 0
    
    print(f"\n📈 STATISTICHE FINALI")
    print(f"   Totale pagine: {total_pages}")
    print(f"   Pagine OK: {ok_pages} ({ok_pages/total_pages*100:.1f}%)")
    print(f"   Punteggio medio: {avg_score:.1f}/100")
    print("=" * 80)

if __name__ == "__main__":
    main()