#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tempestivo SEO Generator - Multi-Città Automatizzato
=====================================================
Unico script che:
1. Legge l'elenco città da dati/citta.csv
2. Per ogni città ATTIVA:
   - Verifica presenza CSV e template
   - Aggiunge automaticamente la colonna 'keyword_principale' ai CSV
   - Genera tutte le pagine (hub + landing)
3. Mostra report finale con statistiche

USO: python generator_multi.py
"""
import os
import csv
import json
import random
import hashlib
import textwrap
from datetime import datetime
from pathlib import Path

try:
    from jinja2 import Environment, FileSystemLoader
    from PIL import Image, ImageDraw, ImageFont
except ImportError as e:
    print(f"❌ Errore import: {e}")
    print("Esegui: pip install Jinja2 Pillow")
    exit(1)

# ============================================================================
# CONFIGURAZIONE
# ============================================================================
BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR / 'dati'
TEMPLATES_DIR = BASE_DIR / 'templates'
OUTPUT_DIR = BASE_DIR / 'output'
ASSETS_DIR = BASE_DIR / 'assets'

OG_WIDTH = 1200
OG_HEIGHT = 630

# Mappatura prefisso servizio → Template keyword principale
# {prep_nome} verrà sostituito con "a/ad + nome città"
SERVIZIO_KEYWORD_MAP = {
    'impianti-elettrici': 'Elettricista e Impianti Elettrici {prep_nome}',
    'impianti-idraulici': 'Idraulico e Impianti Idraulici {prep_nome}',
    'ristrutturazioni': 'Impresa Edile e Ristrutturazioni {prep_nome}',
    'pronto-intervento': 'Pronto Intervento H24 {prep_nome}',
}

# ============================================================================
# FUNZIONI HELPER
# ============================================================================
def load_csv(filepath):
    """Carica un file CSV e ritorna lista di dizionari"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def save_csv(filepath, fieldnames, rows):
    """Salva una lista di dizionari in un file CSV"""
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def load_json(filepath):
    """Carica un file JSON con pulizia automatica degli spazi nelle chiavi"""
    with open(filepath, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    cleaned_data = {}
    for k, v in raw_data.items():
        clean_key = k.strip()
        if isinstance(v, dict):
            cleaned_data[clean_key] = {sub_k.strip(): sub_v for sub_k, sub_v in v.items()}
        else:
            cleaned_data[clean_key] = v
    return cleaned_data

def slugify(text):
    """Converte testo in slug URL-friendly"""
    return text.lower().strip().replace(' ', '-').replace("'", "")

def load_font(size):
    """Carica un font con fallback automatico"""
    font_paths = [
        ASSETS_DIR / 'fonts' / 'Roboto-Bold.ttf',
        ASSETS_DIR / 'fonts' / 'Arial-Bold.ttf',
        Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
    ]
    for fp in font_paths:
        if fp.exists():
            try:
                return ImageFont.truetype(str(fp), size)
            except Exception:
                continue
    return ImageFont.load_default()

# ============================================================================
# AGGIUNTA AUTOMATICA KEYWORD PRINCIPALE AI CSV
# ============================================================================
def estrai_citta_e_servizio(slug_servizio, citta_slug):
    """
    Estrae il tipo di servizio dallo slug, verificando che appartenga alla città corretta.
    Es: 'impianti-elettrici-trappeto' con citta_slug='trappeto' → 'impianti-elettrici'
    """
    prefissi_ordinati = sorted(SERVIZIO_KEYWORD_MAP.keys(), key=len, reverse=True)
    
    for prefisso in prefissi_ordinati:
        expected_slug = f"{prefisso}-{citta_slug}"
        if slug_servizio == expected_slug:
            return prefisso
    
    return None

def genera_keyword_principale(slug_servizio, citta_info):
    """Genera la keyword principale per un dato slug di servizio"""
    tipo_servizio = estrai_citta_e_servizio(slug_servizio, citta_info['slug'])
    
    if not tipo_servizio:
        return None
    
    template = SERVIZIO_KEYWORD_MAP[tipo_servizio]
    
    # Preposizione corretta (es. "ad Alcamo" invece di "a Alcamo")
    nome = citta_info['nome']
    if nome[0].upper() in 'AEIOU':
        prep = 'ad'
    else:
        prep = 'a'
    
    prep_nome = f"{prep} {nome}"
    return template.format(prep_nome=prep_nome)

def aggiungi_keyword_csv(filepath, citta_info):
    """
    Aggiunge la colonna 'keyword_principale' a un CSV servizi se manca.
    Ritorna: (aggiornato: bool, num_righe: int)
    """
    rows = load_csv(filepath)
    fieldnames = list(rows[0].keys()) if rows else []
    
    # Se la colonna esiste già, skip
    if 'keyword_principale' in fieldnames:
        return False, len(rows)
    
    # Aggiungi la nuova colonna
    nuovi_fieldnames = fieldnames + ['keyword_principale']
    aggiornamenti = 0
    
    for row in rows:
        slug = row.get('slug', '')
        keyword = genera_keyword_principale(slug, citta_info)
        if keyword:
            row['keyword_principale'] = keyword
            aggiornamenti += 1
        else:
            # Fallback: usa il nome del servizio
            row['keyword_principale'] = row.get('nome', '')
    
    # Salva il CSV aggiornato
    save_csv(filepath, nuovi_fieldnames, rows)
    return True, aggiornamenti

# ============================================================================
# A/B TESTING
# ============================================================================
AB_VARIANTS = {
    'cta': [
        {'id': 'cta_call', 'text': 'Chiama ora per un preventivo gratuito', 'button_text': '📞 Chiama Ora', 'color': '#E32626'},
        {'id': 'cta_form', 'text': 'Richiedi progetto AI e preventivo gratis', 'button_text': '📝 Richiedi Progetto', 'color': '#0B1B3B'},
        {'id': 'cta_whatsapp', 'text': 'Contattaci su WhatsApp per una risposta immediata', 'button_text': '💬 WhatsApp', 'color': '#25D366'}
    ],
    'trust_badge': [
        {'id': 'badge_reviews', 'text': '4.9/5 su oltre 500 interventi eseguiti', 'icon': '⭐', 'color': '#FFC857'},
        {'id': 'badge_speed', 'text': 'Sopralluogo e preventivo in 24/48h', 'icon': '⚡', 'color': '#E32626'},
        {'id': 'badge_guarantee', 'text': 'Tempi certi contrattualizzati', 'icon': '✅', 'color': '#28a745'}
    ],
    'price_display': [
        {'id': 'price_from', 'format': 'from', 'label': 'A partire da'},
        {'id': 'price_range', 'format': 'range', 'label': 'Prezzo'},
        {'id': 'price_avg', 'format': 'avg', 'label': 'Prezzo medio'}
    ]
}

def select_ab_variant(page_slug):
    """Seleziona varianti A/B deterministiche basate sull'hash dello slug"""
    seed = int(hashlib.md5(page_slug.encode('utf-8')).hexdigest(), 16)
    rng = random.Random(seed)
    return {category: rng.choice(options) for category, options in AB_VARIANTS.items()}

def generate_ab_tracking_code(ab_variants, quartiere_nome, servizio_nome):
    """Genera codice JavaScript per tracciare le conversioni A/B"""
    variants_json = json.dumps(ab_variants, ensure_ascii=False)
    return f"""<script>
    (function() {{
        const abVariants = {variants_json};
        function trackABEvent(action, label) {{
            if (typeof gtag !== 'undefined') {{
                gtag('event', action, {{
                    'event_category': 'AB_Testing',
                    'event_label': label,
                    'cta_variant': abVariants.cta.id,
                    'trust_variant': abVariants.trust_badge.id,
                    'price_variant': abVariants.price_display.id,
                    'quartiere': '{quartiere_nome}',
                    'servizio': '{servizio_nome}'
                }});
            }}
        }}
        document.addEventListener('DOMContentLoaded', function() {{
            document.querySelectorAll('.btn-cta, .btn-emergenza').forEach(btn => {{
                btn.addEventListener('click', function() {{ trackABEvent('cta_click', abVariants.cta.id); }});
            }});
        }});
    }})();
    </script>"""

# ============================================================================
# OG IMAGE GENERATOR
# ============================================================================
def generate_og_image(titolo, sottotitolo, output_path, accent_color='#E32626'):
    """Genera un'immagine OG personalizzata per ogni landing page"""
    img = Image.new('RGB', (OG_WIDTH, OG_HEIGHT), color=(11, 27, 59))
    draw = ImageDraw.Draw(img)
    for i in range(OG_HEIGHT):
        ratio = i / OG_HEIGHT
        r = int(11 + ratio * 20)
        g = int(27 - ratio * 10)
        b = int(59 + ratio * 30)
        draw.line([(0, i), (OG_WIDTH, i)], fill=(r, g, b))
    draw.rectangle([(0, 0), (OG_WIDTH, 10)], fill=accent_color)
    font_titolo = load_font(58)
    font_sottotitolo = load_font(36)
    font_brand = load_font(28)
    font_badge = load_font(22)
    draw.text((50, 40), "TEMPESTIVO", fill='white', font=font_brand)
    draw.text((50, 72), "RAPIDI & AFFIDABILI", fill=(255, 200, 87), font=font_badge)
    y_position = 250
    for line in textwrap.fill(titolo, width=22).split('\n'):
        bbox = draw.textbbox((0, 0), line, font=font_titolo)
        x_pos = (OG_WIDTH - (bbox[2] - bbox[0])) // 2
        draw.text((x_pos + 2, y_position + 2), line, fill='black', font=font_titolo)
        draw.text((x_pos, y_position), line, fill='white', font=font_titolo)
        y_position += 75
    bbox = draw.textbbox((0, 0), sottotitolo, font=font_sottotitolo)
    draw.text(((OG_WIDTH - (bbox[2] - bbox[0])) // 2, y_position + 30), sottotitolo, fill=(255, 200, 87), font=font_sottotitolo)
    draw.rectangle([(0, OG_HEIGHT - 70), (OG_WIDTH, OG_HEIGHT)], fill=(0, 0, 0, 180))
    draw.text((50, OG_HEIGHT - 55), "✓ Preventivo Gratuito  ✓ Tempi Certi  ✓ Tecnici Certificati", fill='white', font=font_badge)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path), 'PNG', optimize=True)

def generate_hub_og_image(titolo, sottotitolo, output_path, is_hub=False):
    """Genera immagine OG per hub pages"""
    img = Image.new('RGB', (OG_WIDTH, OG_HEIGHT), color=(11, 27, 59))
    draw = ImageDraw.Draw(img)
    for i in range(OG_HEIGHT):
        ratio = i / OG_HEIGHT
        draw.line([(0, i), (OG_WIDTH, i)], fill=(int(11 + ratio * 15), int(27 - ratio * 10), int(59 + ratio * 30)))
    draw.rectangle([(0, 0), (OG_WIDTH, 10)], fill='#FFC857')
    font_titolo = load_font(54)
    font_sottotitolo = load_font(32)
    font_brand = load_font(26)
    font_badge = load_font(22)
    draw.text((50, 40), "TEMPESTIVO", fill='white', font=font_brand)
    draw.text((50, 72), "RAPIDI & AFFIDABILI", fill=(255, 200, 87), font=font_badge)
    draw.text((OG_WIDTH - 150, 40), "🏘️" if is_hub else "📍", fill='white', font=font_brand)
    y_position = 220
    for line in textwrap.fill(titolo, width=24).split('\n'):
        bbox = draw.textbbox((0, 0), line, font=font_titolo)
        x_pos = (OG_WIDTH - (bbox[2] - bbox[0])) // 2
        draw.text((x_pos + 2, y_position + 2), line, fill='black', font=font_titolo)
        draw.text((x_pos, y_position), line, fill='white', font=font_titolo)
        y_position += 70
    bbox = draw.textbbox((0, 0), sottotitolo, font=font_sottotitolo)
    draw.text(((OG_WIDTH - (bbox[2] - bbox[0])) // 2, y_position + 20), sottotitolo, fill=(255, 200, 87), font=font_sottotitolo)
    draw.rectangle([(0, OG_HEIGHT - 80), (OG_WIDTH, OG_HEIGHT)], fill='#E32626')
    badge_text = "✓ Tutte le Zone  ✓ Intervento Rapido  ✓ H24"
    bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
    draw.text(((OG_WIDTH - (bbox[2] - bbox[0])) // 2, OG_HEIGHT - 55), badge_text, fill='white', font=font_badge)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path), 'PNG', optimize=True)

# ============================================================================
# INTERNAL LINKING (LINK RELATIVI)
# ============================================================================
def genera_link_correlati(quartiere_corrente, servizio_corrente, quartieri, servizi, CITTA):
    """Genera link interni strategici per SEO"""
    link_correlati = []
    
    # 1. Altri servizi nello stesso quartiere (max 4)
    altri_servizi = [s for s in servizi if s['slug'] != servizio_corrente['slug']]
    servizi_random = random.sample(altri_servizi, min(4, len(altri_servizi)))
    
    anchor_templates_servizi = [
        "{servizio} a {quartiere}",
        "Servizio di {servizio} nel quartiere {quartiere}",
        "Richiedi {servizio} a {quartiere}",
        "{servizio} professionale a {quartiere}"
    ]
    
    for i, servizio in enumerate(servizi_random):
        slug = f"{servizio['slug']}-{quartiere_corrente['slug']}"
        anchor = anchor_templates_servizi[i % len(anchor_templates_servizi)].format(
            servizio=servizio['nome'],
            quartiere=quartiere_corrente['nome']
        )
        link_correlati.append({
            'url': f"{slug}.html",
            'anchor': anchor,
            'tipo': 'servizio_correlato'
        })
    
    # 2. Lo stesso servizio in quartieri vicini (max 3)
    # Mappa generica basata sui quartieri disponibili (funziona per tutte le città)
    vicini = [q['slug'] for q in quartieri if q['slug'] != quartiere_corrente['slug']][:3]
    quartieri_target = [q for q in quartieri if q['slug'] in vicini]
    quartieri_random = random.sample(quartieri_target, min(3, len(quartieri_target)))
    
    anchor_templates_quartieri = [
        "{servizio} anche a {quartiere}",
        "Operiamo con {servizio} nel quartiere {quartiere}",
        "Servizio di {servizio} disponibile a {quartiere}"
    ]
    
    for i, quartiere in enumerate(quartieri_random):
        slug = f"{servizio_corrente['slug']}-{quartiere['slug']}"
        anchor = anchor_templates_quartieri[i % len(anchor_templates_quartieri)].format(
            servizio=servizio_corrente['nome'],
            quartiere=quartiere['nome']
        )
        link_correlati.append({
            'url': f"{slug}.html",
            'anchor': anchor,
            'tipo': 'quartiere_correlato'
        })
    
    # 3. Link a pagine hub
    link_correlati.append({
        'url': "index.html",
        'anchor': f"Tutti i servizi di ristrutturazione a {CITTA['nome']}",
        'tipo': 'hub'
    })
    link_correlati.append({
        'url': f"servizi-{quartiere_corrente['slug']}.html",
        'anchor': f"Tutti i servizi disponibili a {quartiere_corrente['nome']}",
        'tipo': 'hub_quartiere'
    })
    
    return link_correlati

# ============================================================================
# NAVBAR & FOOTER
# ============================================================================
def get_navbar_html(config):
    """Genera HTML della navbar con classi Tempestivo"""
    telefono = config.get('telefono', '3520258583')
    return (
        '<header>'
        '<div class="header-inner">'
        '<a class="logo" href="index.html">'
        '<div class="logo-mark">⚡</div>'
        '<div class="logo-text">'
        '<span>TEMPESTIVO</span>'
        '<span style="font-size:11px;text-transform:uppercase;opacity:0.8;color:var(--giallo);">RAPIDI &amp; AFFIDABILI</span>'
        '</div>'
        '</a>'
        '<nav class="main-nav">'
        '<a class="business-nav-link" href="soluzioni-business-palermo-trapani.html">Area Business</a>'
        '</nav>'
        '<div class="header-cta">'
        '<a class="btn-emergenza" href="tel:' + telefono + '">'
        '<span class="icon">⚠️</span>'
        '<span>' + telefono + '</span>'
        '</a>'
        '</div>'
        '</div>'
        '</header>'
        '<nav class="sub-nav">'
        '<div class="sub-nav-inner">'
        '<a class="sub-nav-link" href="chi-siamo.html">Chi Siamo</a>'
        '<a class="sub-nav-link" href="servizi.html">Servizi</a>'
        '<a class="sub-nav-link" href="mappa-zone.html">Zone Coperte</a>'
        '<a class="sub-nav-link" href="landing-ristrutturazioni.html">Ristrutturazioni complete e veloci</a>'
        '</div>'
        '</nav>'
        '<div class="page-offset"></div>'
    )

def get_footer_html(config, quartieri, CITTA):
    """Genera HTML del footer Tempestivo"""
    telefono = config.get('telefono', '3520258583')
    email = config.get('email', 'tempestivoweb@gmail.com')
    zone_links = ''.join([
        f'<li style="margin-bottom:10px;"><a href="servizi-{q["slug"]}.html" style="color:var(--bianco);text-decoration:none;">{q["nome"]}</a></li>'
        for q in quartieri[:6]
    ])
    return (
        '<footer style="background-color:var(--blu-notte);color:var(--bianco);padding:60px 20px 20px;margin-top:60px;">'
        '<div style="max-width:1100px;margin:0 auto;display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:40px;">'
        '<div>'
        '<div class="logo" style="margin-bottom:20px;"><div class="logo-mark">⚡</div><div class="logo-text"><span>TEMPESTIVO</span><span style="font-size:11px;text-transform:uppercase;opacity:0.8;color:var(--giallo);">RAPIDI &amp; AFFIDABILI</span></div></div>'
        '<p>Tempestivo è una divisione di Officina Creativa dedicata al General Contracting e alle manutenzioni rapide.</p>'
        '<p><strong>📞 ' + telefono + '</strong></p>'
        '<p><strong>✉️ ' + email + '</strong></p>'
        '</div>'
        '<div>'
        '<h4 style="font-family:var(--font-titoli);color:var(--giallo);margin-bottom:20px;">Servizi Principali</h4>'
        '<ul style="list-style:none;padding:0;">'
        '<li style="margin-bottom:10px;"><a href="ristrutturazioni-palermo-trapani.html" style="color:var(--bianco);text-decoration:none;">Ristrutturazioni</a></li>'
        '<li style="margin-bottom:10px;"><a href="pronto-intervento-palermo-trapani.html" style="color:var(--bianco);text-decoration:none;">🆘 Pronto Intervento H24</a></li>'
        '<li style="margin-bottom:10px;"><a href="index.html" style="color:var(--bianco);text-decoration:none;">Ristrutturazioni ' + CITTA['nome'] + '</a></li>'
        '</ul>'
        '</div>'
        '<div>'
        '<h4 style="font-family:var(--font-titoli);color:var(--giallo);margin-bottom:20px;">Zone Operative</h4>'
        '<ul style="list-style:none;padding:0;">' + zone_links + '<li style="margin-bottom:10px;"><a href="mappa-zone.html" style="color:var(--bianco);text-decoration:none;">Vedi tutte le zone →</a></li></ul>'
        '</div>'
        '<div>'
        '<h4 style="font-family:var(--font-titoli);color:var(--giallo);margin-bottom:20px;">Informazioni</h4>'
        '<ul style="list-style:none;padding:0;">'
        '<li style="margin-bottom:10px;"><a href="chi-siamo.html" style="color:var(--bianco);text-decoration:none;">Chi Siamo</a></li>'
        '<li style="margin-bottom:10px;"><a href="mappa-zone.html" style="color:var(--bianco);text-decoration:none;">Mappa delle Zone</a></li>'
        '<li style="margin-bottom:10px;"><a href="privacy.html" style="color:var(--bianco);text-decoration:none;">Privacy Policy</a></li>'
        '</ul>'
        '</div>'
        '</div>'
        '<div style="max-width:1100px;margin:40px auto 0;padding-top:20px;border-top:1px solid rgba(255,255,255,0.1);text-align:center;font-size:0.9rem;opacity:0.8;">'
        '<p>P.IVA: 06772720824 | Divisione di Officina Creativa</p>'
        '<p>&copy; ' + str(datetime.now().year) + ' Tempestivo. Tutti i diritti riservati.</p>'
        '</div>'
        '</footer>'
    )

def get_btn_script():
    """Script smooth scroll"""
    return """<script>
    document.addEventListener('DOMContentLoaded', function() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const target = document.querySelector(this.getAttribute('href'));
                if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
            });
        });
    });
    </script>"""

def get_tag_alt(quartiere_nome, servizio_nome, slug, CITTA):
    """Genera tag alternativi per SEO"""
    return (
        '<link rel="alternate" hreflang="it" href="https://tempestivo.it/' + CITTA['slug'] + '/' + slug + '.html" />'
        '<link rel="alternate" hreflang="x-default" href="https://tempestivo.it/' + CITTA['slug'] + '/' + slug + '.html" />'
        '<meta name="geo.region" content="' + CITTA['regione'] + '" />'
        '<meta name="geo.placename" content="' + quartiere_nome + ', ' + CITTA['nome'] + '" />'
        '<meta name="geo.position" content="' + CITTA['lat'] + ';' + CITTA['lon'] + '" />'
        '<meta name="ICBM" content="' + CITTA['lat'] + ', ' + CITTA['lon'] + '" />'
        '<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" />'
    )

# ============================================================================
# AI OVERVIEWS OPTIMIZATION
# ============================================================================
def genera_definizione(servizio, quartiere):
    """Genera definizione concisa per snippet AI"""
    definizione = servizio.get('definizione', f"{servizio['nome']} professionale a {quartiere['nome']}.")
    return (
        '<div class="definizione-servizio" style="background:var(--grigio-chiaro);padding:20px;border-radius:8px;margin-bottom:30px;">'
        '<p style="font-size:1.05rem;line-height:1.6;margin:0;">'
        '<strong style="color:var(--blu-notte);">' + servizio['nome'] + ' a ' + quartiere['nome'] + ':</strong> ' + definizione +
        '</p></div>'
    )

def genera_box_sintesi(punti_sintesi):
    """Genera box 'In sintesi' per AI Overviews"""
    items_html = ''.join([f'<li style="margin-bottom:8px;">{p}</li>' for p in punti_sintesi])
    return (
        '<div class="box-sintesi" style="background:#e7f3ff;border-left:5px solid var(--blu-notte);padding:25px;border-radius:8px;margin:30px 0;">'
        '<h3 style="color:var(--blu-notte);font-family:var(--font-titoli);margin-bottom:15px;font-size:1.3rem;">📌 In sintesi</h3>'
        '<ul style="list-style:none;padding:0;margin:0;">' + items_html + '</ul>'
        '</div>'
    )

def genera_tabella_comparativa(servizio, quartiere, CITTA):
    """Genera tabella HTML comparativa per AI Overviews"""
    garanzia = servizio.get('garanzia', '10 anni su impianti, 2 anni su finiture')
    materiali = servizio.get('materiali_inclusi', 'Materiali di prima qualità inclusi')
    return (
        '<table class="tabella-comparativa" style="width:100%;border-collapse:collapse;margin:30px 0;font-size:0.95rem;">'
        '<thead><tr style="background:var(--blu-notte);color:white;">'
        '<th style="padding:12px;text-align:left;border:1px solid #ddd;">Caratteristica</th>'
        '<th style="padding:12px;text-align:left;border:1px solid #ddd;">Dettaglio</th>'
        '</tr></thead><tbody>'
        '<tr><td style="padding:12px;border:1px solid #ddd;font-weight:600;">Servizio</td><td style="padding:12px;border:1px solid #ddd;">' + servizio['nome'] + ' a ' + quartiere['nome'] + '</td></tr>'
        '<tr style="background:#f8f9fa;"><td style="padding:12px;border:1px solid #ddd;font-weight:600;">Prezzo</td><td style="padding:12px;border:1px solid #ddd;">Da €' + str(servizio['prezzo_min']) + ' a €' + str(servizio['prezzo_max']) + '</td></tr>'
        '<tr><td style="padding:12px;border:1px solid #ddd;font-weight:600;">Durata</td><td style="padding:12px;border:1px solid #ddd;">' + servizio['durata'] + '</td></tr>'
        '<tr style="background:#f8f9fa;"><td style="padding:12px;border:1px solid #ddd;font-weight:600;">Zona</td><td style="padding:12px;border:1px solid #ddd;">' + quartiere['nome'] + ', ' + CITTA['nome'] + '</td></tr>'
        '<tr><td style="padding:12px;border:1px solid #ddd;font-weight:600;">Vincoli</td><td style="padding:12px;border:1px solid #ddd;">' + quartiere.get('vincoli', 'Nessuno') + '</td></tr>'
        '<tr style="background:#f8f9fa;"><td style="padding:12px;border:1px solid #ddd;font-weight:600;">Materiali</td><td style="padding:12px;border:1px solid #ddd;">' + materiali + '</td></tr>'
        '<tr><td style="padding:12px;border:1px solid #ddd;font-weight:600;">Garanzia</td><td style="padding:12px;border:1px solid #ddd;">' + garanzia + '</td></tr>'
        '</tbody></table>'
    )

def genera_schema_howto(servizio, CITTA):
    """Genera Schema.org HowTo per il processo step-by-step"""
    steps = []
    step_keys = ['step1', 'step2', 'step3', 'step4']
    for i, key in enumerate(step_keys, 1):
        if servizio.get(key):
            steps.append({
                "@type": "HowToStep",
                "position": i,
                "name": f"Fase {i}",
                "text": servizio[key]
            })
    durata = servizio.get('durata', '30 giorni')
    if '7' in durata:
        total_time = "P7D"
    elif '10' in durata:
        total_time = "P10D"
    elif '2' in durata:
        total_time = "P2D"
    else:
        total_time = "P30D"
    return {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": f"Come si esegue {servizio['nome']} a {CITTA['nome']}",
        "description": servizio.get('definizione', ''),
        "totalTime": total_time,
        "step": steps,
        "tool": ["Attrezzi professionali", "Materiali di prima qualità"],
        "supply": servizio.get('materiali_inclusi', 'Materiali inclusi nel preventivo')
    }

# ============================================================================
# GENERAZIONE PER UNA SINGOLA CITTÀ
# ============================================================================
def genera_citta(CITTA, config, env):
    """
    Genera tutte le pagine per una singola città.
    Ritorna un dict con le statistiche della generazione.
    """
    stats = {
        'nome': CITTA['nome'],
        'slug': CITTA['slug'],
        'stato': 'successo',
        'errori': [],
        'quartieri': 0,
        'servizi': 0,
        'landing': 0,
        'og_images': 0,
        'csv_aggiornato': False,
    }
    
    print(f"\n{'='*60}")
    print(f"🏙️  GENERAZIONE: {CITTA['nome']}")
    print(f"{'='*60}")
    
    # Verifica file necessari
    file_quartieri = DATA_DIR / CITTA['file_quartieri']
    file_servizi = DATA_DIR / CITTA['file_servizi']
    file_frasi = DATA_DIR / CITTA['file_frasi']
    
    for f in [file_quartieri, file_servizi, file_frasi]:
        if not f.exists():
            msg = f"File mancante: {f.name}"
            print(f"   ❌ {msg}")
            stats['errori'].append(msg)
            stats['stato'] = 'errore'
            return stats
    
    # Verifica template necessari
    for tpl_name in [CITTA['template_hub'], CITTA['template_hub_quartiere'], CITTA['template_landing']]:
        if not (TEMPLATES_DIR / tpl_name).exists():
            msg = f"Template mancante: {tpl_name}"
            print(f"   ❌ {msg}")
            stats['errori'].append(msg)
            stats['stato'] = 'errore'
            return stats
    
    # Carica dati
    quartieri = load_csv(file_quartieri)
    servizi = load_csv(file_servizi)
    frasi_uniche = load_json(file_frasi)
    
    stats['quartieri'] = len(quartieri)
    stats['servizi'] = len(servizi)
    
    print(f"   ✓ {len(quartieri)} quartieri caricati")
    print(f"   ✓ {len(servizi)} servizi caricati")
    
    # 🔄 AGGIUNTA AUTOMATICA KEYWORD PRINCIPALE AI CSV
    csv_aggiornato, num_aggiornamenti = aggiungi_keyword_csv(file_servizi, CITTA)
    stats['csv_aggiornato'] = csv_aggiornato
    if csv_aggiornato:
        print(f"   ✅ CSV aggiornato: {num_aggiornamenti} keyword principali aggiunte")
        # Ricarica i servizi con la nuova colonna
        servizi = load_csv(file_servizi)
    else:
        print(f"   ℹ️  CSV già aggiornato (keyword_principale presente)")
    
    # Setup template
    template_landing = env.get_template(CITTA['template_landing'])
    template_hub = env.get_template(CITTA['template_hub'])
    template_hub_quartiere = env.get_template(CITTA['template_hub_quartiere'])
    
    # Componenti condivisi
    navbar_html = get_navbar_html(config)
    footer_html = get_footer_html(config, quartieri, CITTA)
    btn_script = get_btn_script()
    
    pages_generated = []
    og_images_count = 0
    
    # Output directory
    citta_output = OUTPUT_DIR / CITTA['slug']
    citta_output.mkdir(parents=True, exist_ok=True)
    
    # 1. HUB PRINCIPALE
    print(f"\n   🏠 Generazione hub principale...")
    hub_context = {
        'quartieri': quartieri,
        'servizi': servizi,
        'config': config,
        'CITTA': CITTA,
        'navbar': navbar_html,
        'footer': footer_html,
        'btn_script': btn_script
    }
    
    with open(citta_output / 'index.html', 'w', encoding='utf-8') as f:
        f.write(template_hub.render(**hub_context))
    
    generate_hub_og_image(
        f"Ristrutturazioni {CITTA['nome']}",
        "Tutti i servizi in tutte le zone",
        citta_output / 'og-image.png',
        is_hub=True
    )
    og_images_count += 1
    pages_generated.append(f"https://tempestivo.it/{CITTA['slug']}/")
    
    # 2. HUB QUARTIERI
    print(f"   🏘️  Generazione hub quartieri...")
    for quartiere in quartieri:
        output_file = citta_output / f"servizi-{quartiere['slug']}.html"
        
        hub_quartiere_context = {
            'quartiere': quartiere,
            'servizi': servizi,
            'config': config,
            'CITTA': CITTA,
            'navbar': navbar_html,
            'footer': footer_html,
            'btn_script': btn_script
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(template_hub_quartiere.render(**hub_quartiere_context))
        
        og_hub_path = citta_output / f"servizi-{quartiere['slug']}-og.png"
        sottotitolo = (quartiere['descrizione_unica'][:60] + "...") if len(quartiere['descrizione_unica']) > 60 else quartiere['descrizione_unica']
        generate_hub_og_image(f"Servizi a {quartiere['nome']}", sottotitolo, og_hub_path, is_hub=False)
        
        canonical_url = f"https://tempestivo.it/{CITTA['slug']}/servizi-{quartiere['slug']}.html"
        pages_generated.append(canonical_url)
        og_images_count += 1
    
    print(f"      ✓ {len(quartieri)} hub quartieri generati")
    
    # 3. LANDING PAGES
    print(f"   🤖 Generazione landing pages...")
    landing_count = 0
    
    for quartiere in quartieri:
        for servizio in servizi:
            slug = f"{servizio['slug']}-{quartiere['slug']}"
            output_file = citta_output / f"{slug}.html"
            
            # Selezione frasi uniche
            intro = random.choice(frasi_uniche['introduzioni'].get(quartiere['slug'], frasi_uniche['introduzioni']['default']))
            problema = random.choice(frasi_uniche['problemi'].get(quartiere['slug'], frasi_uniche['problemi']['default']))
            soluzione = random.choice(frasi_uniche['soluzioni'].get(servizio['slug'], frasi_uniche['soluzioni']['default']))
            trust = random.choice(frasi_uniche['trust_signals'].get(quartiere['slug'], frasi_uniche['trust_signals']['default']))
            punti_sintesi = frasi_uniche['sintesi'].get(servizio['slug'], frasi_uniche['sintesi']['default'])
            
            # Componenti AI Overviews
            definizione = genera_definizione(servizio, quartiere)
            box_sintesi = genera_box_sintesi(punti_sintesi)
            tabella_comparativa = genera_tabella_comparativa(servizio, quartiere, CITTA)
            schema_howto = genera_schema_howto(servizio, CITTA)
            link_correlati = genera_link_correlati(quartiere, servizio, quartieri, servizi, CITTA)
            faq_servizio = frasi_uniche['faq'].get(servizio['slug'], frasi_uniche['faq']['default'])
            
            # A/B Testing
            ab_variants = select_ab_variant(slug)
            ab_tracking = generate_ab_tracking_code(ab_variants, quartiere['nome'], servizio['nome'])
            tag_alt = get_tag_alt(quartiere['nome'], servizio['nome'], slug, CITTA)
            
            avg_price = (int(servizio['prezzo_min']) + int(servizio['prezzo_max'])) // 2
            canonical_url = f"https://tempestivo.it/{CITTA['slug']}/{slug}.html"
            
            context = {
                'quartiere': quartiere,
                'servizio': servizio,
                'config': config,
                'CITTA': CITTA,
                'intro': intro,
                'problema': problema,
                'soluzione': soluzione,
                'trust': trust,
                'definizione': definizione,
                'box_sintesi': box_sintesi,
                'tabella_comparativa': tabella_comparativa,
                'schema_howto': schema_howto,
                'link_correlati': link_correlati,
                'faq': faq_servizio,
                'ab_variants': ab_variants,
                'ab_tracking': ab_tracking,
                'tag_alt': tag_alt,
                'navbar': navbar_html,
                'footer': footer_html,
                'btn_script': btn_script,
                'avg_price': avg_price,
                'slug': slug,
                'canonical_url': canonical_url
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(template_landing.render(**context))
            
            generate_og_image(
                f"{servizio['nome']} a {quartiere['nome']}",
                "Preventivo gratuito in 24h | Tempestivo",
                citta_output / f"{slug}-og.png"
            )
            
            pages_generated.append(canonical_url)
            landing_count += 1
            og_images_count += 1
    
    stats['landing'] = landing_count
    stats['og_images'] = og_images_count
    print(f"      ✓ {landing_count} landing pages generate")
    
    # 4. SITEMAP.XML
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += f'  <url><loc>https://tempestivo.it/{CITTA["slug"]}/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>\n'
    for q in quartieri:
        sitemap += f'  <url><loc>https://tempestivo.it/{CITTA["slug"]}/servizi-{q["slug"]}.html</loc><changefreq>weekly</changefreq><priority>0.9</priority></url>\n'
    for url in pages_generated[1 + len(quartieri):]:
        sitemap += f'  <url><loc>{url}</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>\n'
    sitemap += '</urlset>'
    
    with open(citta_output / 'sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(sitemap)
    
    print(f"\n   ✅ {CITTA['nome']} completato: {landing_count} landing + {len(quartieri)} hub + sitemap")
    return stats

# ============================================================================
# MAIN - ORCHESTRATORE
# ============================================================================
def main():
    print("🚀 TEMPESTIVO SEO GENERATOR - MULTI-CITTÀ")
    print("=" * 60)
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"📂 Directory base: {BASE_DIR}")
    print("=" * 60)
    
    # Verifica file citta.csv
    citta_file = DATA_DIR / 'citta.csv'
    if not citta_file.exists():
        print(f"❌ File mancante: {citta_file}")
        print("   Crea il file dati/citta.csv con l'elenco delle città")
        return
    
    # Carica elenco città
    tutte_citta = load_csv(citta_file)
    citta_attive = [c for c in tutte_citta if c.get('stato', '').strip().lower() == 'attivo']
    
    print(f"\n📊 Città totali: {len(tutte_citta)}")
    print(f"✅ Città attive: {len(citta_attive)}")
    print(f"⏸️  Città disattive: {len(tutte_citta) - len(citta_attive)}")
    
    if not citta_attive:
        print("\n⚠️  Nessuna città attiva. Modifica dati/citta.csv impostando stato='attivo'")
        return
    
    # Carica config.json
    config_file = DATA_DIR / 'config.json'
    if not config_file.exists():
        print(f"❌ File mancante: {config_file}")
        return
    config = load_json(config_file)
    
    # Setup Jinja2
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    
    # Genera per ogni città attiva
    stats_totali = []
    for citta in citta_attive:
        stats = genera_citta(citta, config, env)
        stats_totali.append(stats)
    
    # REPORT FINALE
    print("\n" + "=" * 60)
    print("📊 REPORT FINALE GENERAZIONE")
    print("=" * 60)
    
    totale_landing = 0
    totale_hub = 0
    totale_og = 0
    successi = 0
    errori = 0
    
    for stats in stats_totali:
        if stats['stato'] == 'successo':
            successi += 1
            totale_landing += stats['landing']
            totale_hub += stats['quartieri'] + 1  # +1 per hub principale
            totale_og += stats['og_images']
            csv_status = "🔄 AGGIORNATO" if stats['csv_aggiornato'] else "✓ OK"
            print(f"✅ {stats['nome']:30} | {stats['landing']:3} landing | {stats['quartieri']:2} hub | CSV: {csv_status}")
        else:
            errori += 1
            print(f"❌ {stats['nome']:30} | ERRORI: {', '.join(stats['errori'])}")
    
    print("=" * 60)
    print(f"🎉 GENERAZIONE COMPLETATA!")
    print(f"   ✅ Città processate con successo: {successi}")
    print(f"   ❌ Città con errori: {errori}")
    print(f"   📄 Landing pages totali: {totale_landing}")
    print(f"   🏘️  Hub pages totali: {totale_hub}")
    print(f"   🖼️  Immagini OG totali: {totale_og}")
    print(f"   📁 Output: {OUTPUT_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()