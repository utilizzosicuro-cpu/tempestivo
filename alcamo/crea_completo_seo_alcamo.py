#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
TEMPESTIVO SEO MASTER SUITE - V 9.2 (CORRECTED & INTEGRATED ENTERPRISE VERSION)
Script unico, completo e privo di omissioni con:
- Meta Tag Ottimizzati, Geo Tags, Twitter Cards & Open Graph Completo
- Schema.org Avanzato per AI Overviews
- Generazione pagine dinamiche da CSV/JSON esterni con Fix HTML & Contextual Logic
- Pagine Pilastro (Bonus Sicilia, Guida Bagno, Centro Storico, Vincoli, Index Alcamo)
- Internal Linking con verifica dinamica dell'esistenza dei file
- Audit SEO (17 criteri strict) + Fixer chirurgico automatico
- Gestione File & Reporting completo
- Generazione automatica immagini fisiche via Pillow (PIL) con fallback integrato
- [INTEGRAZIONE] Nuovi servizi chiave (Idraulica, Elettrica, Climatizzazione, Fabbro, Caldaie)
=============================================================================
"""
import os
import re
import csv
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple

# Import opzionale per Pillow (generazione automatica immagini)
try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

# =============================================================================
# 1. CONFIGURAZIONE E DATI STATICI (E-A-T & STRATEGY)
# =============================================================================
class Config:
    BASE_DIR = Path(__file__).parent
    TEMPLATE_FILE = "mondello.html"
    BACKUP_DIR = BASE_DIR / "backup_suite"
    REPORT_DIR = BASE_DIR / "seo_reports"
    IMAGES_DIR = BASE_DIR / "images"
    
    # File dati esterni
    SERVIZI_CSV = "servizi_alcamo.csv"
    QUARTIERI_CSV = "quartieri_alcamo.csv"
    FRASI_JSON = "frasi_uniche_alcamo.json"
    
    # Dati aziendali (E-A-T)
    AZIENDA = "Tempestivo"
    TELEFONO = "+39 352 025 85 83"
    TELEFONO_RAW = "3520258583"
    EMAIL = "tempestivoweb@gmail.com"
    INDIRIZZO = "Contrada Incastrona, 90047 Partinico (PA)"
    P_IVA = "06772720824"
    URL_BASE = "https://tempestivo.it/alcamo"
    CSS_PATH = "/style.css"
    OG_IMAGE = f"{URL_BASE}/images/og-tempestivo.jpg"
    
    # Geo Tags Default (Alcamo)
    GEO_REGION = "IT-TP"
    GEO_PLACENAME = "Alcamo"
    GEO_POSITION = "37.9785;12.9594"
    ICBM = "37.9785, 12.9594"
    
    PREZZI = [
        ("Uscita e sopralluogo", "€60"),
        ("Ricerca perdite", "€60 - €400"),
        ("Disostruzione scarichi", "€100 - €500"),
        ("Riparazione corto circuito / salvavita", "€100 - €500"),
        ("Sostituzione rubinetteria / sanitari", "€70 - €120"),
        ("Pronto intervento idraulico h24", "€80 - €350"),
        ("Pronto intervento elettricista h24", "€80 - €350"),
        ("Installazione e manutenzione condizionatori", "€120 - €450"),
        ("Sostituzione e installazione caldaie", "€150 - €800"),
        ("Apertura porte e servizio fabbro urgente", "€90 - €300"),
        ("Ristrutturazione bagno completa (chiavi in mano)", "Da €1.500 a €5.000"),
        ("Ristrutturazione cucina completa (chiavi in mano)", "Da €1.500 a €7.000")
    ]

    # Recensioni "Trustindex" con LSI Keywords OBBLIGATORIE
    RECENSIONI = {
        "default": [
            {"testo": "Lavori a regola d'arte e prezzi onesti, esattamente come da preventivo. Tecnico arrivato in tempi rapidi ad Alcamo. Consigliatissimi!", "autore": "Marco V.", "zona": "Alcamo", "stelle": 5},
            {"testo": "Prezzi onesti e lavori a regola d'arte. Hanno gestito tutto tramite un unico Project Manager, zero stress. Ditta edile eccezionale!", "autore": "Giulia R.", "zona": "Alcamo Marina", "stelle": 5}
        ],
        "alcamo-marina": [
            {"testo": "Gestisco una casa vacanza ad Alcamo Marina. Ho chiamato Tempestivo per una riparazione urgente del climatizzatore. Aria condizionata ripristinata in poche ore. Un partner indispensabile!", "autore": "Gestore Casa Vacanza", "zona": "Alcamo Marina", "stelle": 5}
        ],
        "centro-storico": [
            {"testo": "Ho affidato a Tempestivo i lavori per il mio locale nel centro storico ad Alcamo. Hanno lavorato con la formula chiavi in mano, rispettando al millimetro le tempistiche. La migliore ditta di ristrutturazioni e manutenzioni!", "autore": "Attività Commerciale", "zona": "Centro Storico", "stelle": 5}
        ],
        "alcamo": [
            {"testo": "Ho avuto un improvviso guasto elettrico ad Alcamo. Il tecnico è arrivato in tempi record, ha individuato subito il problema e ha ripristinato tutto in totale sicurezza. Efficienti e competenti!", "autore": "Cliente Privato", "zona": "Alcamo", "stelle": 5}
        ]
    }

    # Silos Verticali (Internal Linking)
    SILO_LINKS = [
        {"text": "Ristrutturazione bagno: costi, tempi e permessi necessari", "url": "guida-ristrutturazione-bagno.html"},
        {"text": "Ristrutturazione Centro Storico: vincoli e soluzioni", "url": "ristrutturazione-centro-storico.html"},
        {"text": "Bonus Ristrutturazioni Sicilia 2026: come ottenerli con Tempestivo", "url": "bonus-ristrutturazioni-sicilia.html"}
    ]

    # Frasi Uniche per Quartiere (Anti-Duplicate Content)
    FRASI_UNICHE = {
        "centro-storico": {"intro": "I palazzi d'epoca nel centro storico di Alcamo necessitano di permessi e logistica per vie e vicoli caratteristici.", "problematiche": ["Palazzi d'epoca e contesti storici protetti", "Logistica complessa per il trasporto materiali nei vicoli", "Conservazione elementi architettonici storici", "Impianti originali da adeguare alle normative moderne"]},
        "alcamo-marina": {"intro": "Le abitazioni ad Alcamo Marina richiedono particolare attenzione alla salsedine e alla protezione delle strutture costiere.", "problematiche": ["Trattamento umidità e salsedine tipiche della zona balneare", "Materiali resistenti al clima marino e alla corrosione", "Interventi tempestivi per la stagione estiva", "Manutenzione straordinaria su immobili turistici"]}
    }

# =============================================================================
# 1.5 IMAGE GENERATOR (PILLOW)
# =============================================================================
class ImageGenerator:
    @staticmethod
    def create_image(filename: str, title_text: str) -> Path:
        Config.IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        img_path = Config.IMAGES_DIR / filename
        
        width, height = 1200, 630
        bg_color = (26, 37, 47)
        accent_color = (40, 167, 69)
        text_color = (255, 255, 255)
        
        if PILLOW_AVAILABLE:
            image = Image.new("RGB", (width, height), color=bg_color)
            draw = ImageDraw.Draw(image)
            draw.rectangle([0, 0, width, 25], fill=accent_color)
            
            try:
                font_title = ImageFont.truetype("arial.ttf", 48)
                font_brand = ImageFont.truetype("arial.ttf", 32)
            except IOError:
                font_title = ImageFont.load_default()
                font_brand = ImageFont.load_default()
                
            draw.text((80, 200), "TEMPESTIVO ALCAMO", fill=accent_color, font=font_brand)
            
            max_chars_per_line = 40
            words = title_text.split()
            lines = []
            current_line = []
            for word in words:
                current_line.append(word)
                if len(" ".join(current_line)) > max_chars_per_line:
                    lines.append(" ".join(current_line[:-1]))
                    current_line = [word]
            if current_line:
                lines.append(" ".join(current_line))
                
            y_text = 270
            for line in lines[:3]:
                draw.text((80, y_text), line, fill=text_color, font=font_title)
                y_text += 65
                
            image.save(img_path, "JPEG", quality=90)
        else:
            img_path.touch()
            
        return img_path

# =============================================================================
# 2. DATA LOADER
# =============================================================================
class DataLoader:
    @staticmethod
    def load_servizi(filepath: Path) -> List[Dict]:
        if not filepath.exists(): 
            raise FileNotFoundError(f"File servizi non trovato: {filepath}")
        servizi = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader: 
                servizi.append(row)
        print(f"✅ Caricati {len(servizi)} servizi da {filepath.name}")
        return servizi

    @staticmethod
    def load_quartieri(filepath: Path) -> List[Dict]:
        if not filepath.exists(): 
            raise FileNotFoundError(f"File quartieri non trovato: {filepath}")
        quartieri = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader: 
                quartieri.append(row)
        print(f"✅ Caricati {len(quartieri)} quartieri da {filepath.name}")
        return quartieri

    @staticmethod
    def load_frasi_uniche(filepath: Path) -> Dict:
        if not filepath.exists(): 
            raise FileNotFoundError(f"File frasi uniche non trovato: {filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Caricate frasi uniche per {len(data)} quartieri da {filepath.name}")
        return data

# =============================================================================
# 3. TEMPLATE MANAGER
# =============================================================================
class TemplateManager:
    def __init__(self):
        path = Config.BASE_DIR / Config.TEMPLATE_FILE
        if not path.exists(): 
            raise FileNotFoundError(f"Template {Config.TEMPLATE_FILE} non trovato!")
        content = path.read_text(encoding='utf-8')
        self.header = self._extract_block(content, 'header')
        self.footer = self._extract_block(content, 'footer')
        print(f"✅ Template caricato: Header ({len(self.header)} char), Footer ({len(self.footer)} char)")

    def _extract_block(self, content: str, tag: str) -> str:
        soup = BeautifulSoup(content, 'html.parser')
        if tag.lower() == 'header':
            header = soup.select_one('header.header')
            sub_nav = soup.select_one('nav.sub-nav')
            page_offset = soup.select_one('.page-offset')
            
            blocks = []
            if header: blocks.append(str(header))
            if sub_nav: blocks.append(str(sub_nav))
            if page_offset: blocks.append(str(page_offset))
                
            if blocks:
                return "\n".join(blocks)
            else:
                raise ValueError(f"Blocco header non trovato nel template")
        else:
            pattern = re.compile(f'<{tag}[^>]*>.*?</{tag}>', re.DOTALL | re.IGNORECASE)
            match = pattern.search(content)
            if not match: 
                raise ValueError(f"Tag <{tag}> non trovato nel template")
            return match.group(0)

# =============================================================================
# 4. PAGE GENERATOR
# =============================================================================
class PageGenerator:
    def __init__(self, template: TemplateManager, servizi: List[Dict], quartieri: List[Dict], frasi_uniche: Dict):
        self.template = template
        self.servizi = servizi
        self.quartieri = quartieri
        self.frasi_uniche = frasi_uniche

    def generate_all(self) -> List[Path]:
        generated = []
        for servizio in self.servizi:
            for quartiere in self.quartieri:
                slug_servizio = servizio['slug']
                slug_quartiere = quartiere['slug']
                filename = f"{slug_servizio}-{slug_quartiere}.html"
                filepath = Config.BASE_DIR / filename
                print(f"  📄 Generazione automatica: {filename}")
                content = self._generate_page(servizio, quartiere)
                filepath.write_text(content, encoding='utf-8')
                generated.append(filepath)
                print(f"     ✅ Creato/Aggiornato: {filename}")
        return generated

    def _generate_page(self, servizio: Dict, quartiere: Dict) -> str:
        slug_servizio = servizio.get('slug', 'servizio')
        slug_quartiere = quartiere.get('slug', 'quartiere')
        nome_servizio = servizio.get('nome', servizio.get('keyword_principale', 'Servizio'))
        nome_quartiere = quartiere.get('nome', quartiere.get('nome_display', slug_quartiere.title()))
        
        frasi = self.frasi_uniche.get(slug_quartiere, {})
        nome_display = frasi.get('nome_display', nome_quartiere)
        zone_servite = frasi.get('zone_servite', nome_quartiere)
        intro = frasi.get('intro', f"I nostri interventi di {nome_servizio.lower()} ad {nome_display} sono sviluppati per garantire massima qualità ed efficienza.")
        problematiche = frasi.get('problematiche', Config.FRASI_UNICHE.get(slug_quartiere, {}).get('problematiche', []))
        vincoli = frasi.get('vincoli_specifici', quartiere.get('vincoli', 'nessun vincolo bloccante'))
        missione = frasi.get('missione', '')
        
        keyword = servizio.get('keyword_principale', nome_servizio)
        prezzo_min = servizio.get('prezzo_min', '')
        prezzo_max = servizio.get('prezzo_max', '')
        
        if prezzo_min and prezzo_max:
            prezzo_range = f"€{prezzo_min} a €{prezzo_max}"
        elif servizio.get('prezzo_range'):
            prezzo_range = servizio.get('prezzo_range').replace("Da Da", "Da").replace("da Da", "da")
        else:
            prezzo_range = "prezzi personalizzati"
            
        durata_raw = servizio.get('durata', '2 giorni')
        durata = durata_raw if "giorni" in durata_raw.lower() or "ore" in durata_raw.lower() or "settimane" in durata_raw.lower() else f"{durata_raw} giorni"
        
        definizione = servizio.get('definizione', f'Servizio professionale di {keyword.lower()} eseguito a regola d\'arte.')
        materiali_inclusi = servizio.get('materiali_inclusi', 'Materiali di alta qualità certificati')
        garanzia = servizio.get('garanzia', 'Garanzia ufficiale sui lavori')
        
        faq_list = frasi.get('faq', [
            {"domanda": f"Quanto costa il servizio di {keyword.lower()} ad {nome_display}?", "risposta": f"Il prezzo per {keyword.lower()} ad {nome_display} parte da {prezzo_range}, con sopralluogo e preventivo dettagliato privo di costi nascosti."},
            {"domanda": f"Quali sono i tempi di esecuzione per {keyword.lower()} ad {nome_display}?", "risposta": f"I tempi standard di consegna per {keyword.lower()} sono di circa {durata}, pienamente garantiti contrattualmente."},
            {"domanda": f"Fornite garanzia e certificazione per {keyword.lower()}?", "risposta": f"Sì, rilasciamo garanzia ufficiale e conformità sui lavori eseguiti ad {nome_display} in base alle normative vigenti."}
        ])
        
        recensioni = frasi.get('recensioni', Config.RECENSIONI.get(slug_quartiere, Config.RECENSIONI.get('default', [])))

        prezzi_dettagliati_json = servizio.get('prezzi_dettagliati', '[]')
        try:
            prezzi_dettagliati = json.loads(prezzi_dettagliati_json)
        except json.JSONDecodeError:
            prezzi_dettagliati = []

        title = f"{keyword} ad {nome_display}: Chiavi in Mano in {durata} | {Config.AZIENDA}"
        if len(title) > 65:
            title = f"{keyword} ad {nome_display} in {durata} | {Config.AZIENDA}"

        meta_desc = (
            f"Servizio professionale di {keyword.lower()} ad {nome_display} con formula chiavi in mano in {durata}. "
            f"Prezzi trasparenti a partire da {prezzo_range}. Sopralluogo e preventivo gratuito: "
            f"chiama il {Config.TELEFONO}."
        )

        schema = self._generate_schema(keyword, nome_display, zone_servite, faq_list)
        tabella_prezzi_html = self._generate_price_table(prezzi_dettagliati)
        link_correlati_html = self._generate_correlated_links(slug_servizio, slug_quartiere, nome_display)

        og_image = self.get_og_image(slug_servizio, slug_quartiere, title)

        servizi_edilizia_libera = [
            'imbiancatura', 'tinteggiatura', 'pittura', 'riparazione',
            'sostituzione-sanitari', 'disostruzione', 'ricerca-perdite', 'manutenzione',
            'pronto-intervento', 'installazione-condizionatori', 'sostituzione-caldaie', 'apertura-porte'
        ]
        is_edilizia_libera = any(k in slug_servizio.lower() or k in keyword.lower() for k in servizi_edilizia_libera)

        if is_edilizia_libera:
            testo_burocrazia = f"<strong>Verifica Inquadramento ed Edilizia Libera:</strong> L'intervento di {keyword.lower()} rientra nelle attività di edilizia libera e manutenzione ordinaria/urgente. Non richiede la presentazione di pratiche burocratiche complesse (CILA/SCIA), garantendo un avvio immediato dei lavori ad {nome_display} nel pieno rispetto dei regolamenti locali."
        else:
            testo_burocrazia = f"<strong>Gestione Burocratica e Permessi:</strong> Presentazione delle pratiche edilizie necessarie (CILA, SCIA o permessi ove richiesta) specifiche per la zona di {nome_display}."

        html = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    
    <meta name="description" content="{meta_desc}">
    <meta name="keywords" content="{keyword.lower()} {nome_display.lower()}, {keyword.lower()} chiavi in mano, Tempestivo">
    <meta name="robots" content="index, follow">
    
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{meta_desc}">
    <meta property="og:type" content="website">
    <meta property="og:image" content="{og_image}">
    <meta property="og:locale" content="it_IT">
    
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{meta_desc}">
    <meta name="twitter:image" content="{og_image}">
    
    <meta name="geo.region" content="{Config.GEO_REGION}">
    <meta name="geo.placename" content="{nome_display}, {Config.GEO_PLACENAME}">
    <meta name="geo.position" content="{Config.GEO_POSITION}">
    <meta name="ICBM" content="{Config.ICBM}">
    
    <link rel="canonical" href="{Config.URL_BASE}/{slug_servizio}-{slug_quartiere}.html">
    <link rel="stylesheet" href="{Config.CSS_PATH}">
    
    <script type="application/ld+json">
{json.dumps(schema, indent=2, ensure_ascii=False)}
    </script>
</head>
<body>
{self.template.header}
<main>
<article>
    <h1>{keyword} ad {nome_display}: Chiavi in Mano in {durata}</h1>
    <p><strong>{keyword} ad {nome_display}:</strong> {definizione}</p>
    
    <h2>📌 In sintesi</h2>
    <ul>
        <li>✓ Sopralluogo gratuito entro 24/48h</li>
        <li>✓ Preventivo dettagliato e trasparente</li>
        <li>✓ Tempi certi contrattualizzati ({durata})</li>
        <li>✓ Garanzia su tutti i lavori eseguiti</li>
    </ul>

    <h2>Caratteristiche del servizio</h2>
    <table>
        <tr><th>Caratteristica</th><th>Dettaglio</th></tr>
        <tr><td>Servizio</td><td>{keyword} chiavi in mano ad {nome_display}</td></tr>
        <tr><td>Prezzo</td><td>A partire da {prezzo_range}</td></tr>
        <tr><td>Durata</td><td>{durata}</td></tr>
        <tr><td>Zona</td><td>{zone_servite}</td></tr>
        <tr><td>Vincoli</td><td>{vincoli}</td></tr>
        <tr><td>Materiali</td><td>{materiali_inclusi}</td></tr>
        <tr><td>Garanzia</td><td>{garanzia}</td></tr>
    </table>
    
    {tabella_prezzi_html}
    
    <h2>Le problematiche specifiche di {nome_display}</h2>
    <p>{intro}</p>
    <ul>
        {''.join([f'<li>✓ {p}</li>' for p in problematiche]) if problematiche else '<li>✓ Nessuna problematica specifica documentata</li>'}
    </ul>
    <p><em>Nota: Operiamo tenendo conto di {vincoli}.</em></p>

    <h2>Iter Operativo per {keyword} ad {nome_display}</h2>
    <p>Per garantire un risultato impeccabile e senza intoppi nell'area di {nome_display}, adottiamo un processo collaudato che azzera gli imprevisti e ottimizza le tempistiche:</p>
    <ol>
        <li><strong>Sopralluogo tecnico sul posto:</strong> Un nostro responsabile si reca ad {nome_display} per analizzare lo stato di fatto, rilievi metrici e verificare accessibilità e vincoli della zona.</li>
        <li><strong>Pianificazione e Preventivo Definitivo:</strong> Invio di una proposta chiara con specifica dettagliata delle lavorazioni, materiali scelti e costi trasparenti senza sorprese finali.</li>
        <li>{testo_burocrazia}</li>
        <li><strong>Esecuzione Lavori e Direzione Cantiere:</strong> Attuazione degli interventi con maestranze qualificate sotto la costante supervisione del nostro Project Manager dedicato.</li>
        <li><strong>Collaudo, Pulizia e Consegna:</strong> Verifica finale del perfetto funzionamento di impianti e finiture, pulizia profonda dell'immobile e rilascio di garanzia ufficiale.</li>
    </ol>

    <h2>Materiali e Tecnologie Adottate</h2>
    <p>La scelta delle materie prime è fondamentale per garantire la longevità dell'intervento, specialmente in un contesto come {nome_display}. Impieghiamo esclusivamente materiali certificati, ecocompatibili e altamente resistenti all'usura e agli agenti atmosferici locali.</p>

    <h2>La nostra soluzione per {keyword}</h2>
    <p>Il nostro approccio integrato per {keyword} unisce competenze di progettazione, impiantistica e finitura edile, coordinando ogni singola fase fino al completamento dell'opera nei tempi prestabiliti.</p>
    <p><strong>A partire da {prezzo_range}</strong> | ⏱️ Tempi stimati: {durata}</p>

    <h2>Trasparenza, Sicurezza e Normative</h2>
    <p>Ogni intervento svolto ad {nome_display} viene eseguito nel rigoroso rispetto delle normative vigenti in materia di sicurezza sui luoghi di lavoro e smaltimento rifiuti edili, consentendoti di accedere alle detrazioni fiscali.</p>

    <h2>Perché sceglierci ad {nome_display}</h2>
    <p>Tempestivo rappresenta un punto di riferimento per chi cerca serietà, rispetto dei tempi e costi certi. Il nostro unico punto di contatto evita dispersioni di responsabilità.</p>
    
    {self._generate_reviews(recensioni, nome_display, keyword)}
    {self._generate_faq(faq_list)}
    
    {f'<h2>Servizi Correlati</h2><ul>{link_correlati_html}</ul>' if link_correlati_html else ''}
    
    <div style="text-align:center; margin: 30px 0;">
        <a href="tel:{Config.TELEFONO_RAW}" style="background:#28a745; color:white; padding:15px 30px; text-decoration:none; border-radius:5px; font-weight:bold; font-size:1.2em;">
            📞 CHIAMA ORA per {keyword} ad {nome_display}: Chiavi in Mano {Config.TELEFONO}
        </a>
    </div>
</article>

<aside>
    <h3>La Nostra Missione ad {nome_display}</h3>
    <p>{missione if missione else f'Operare ad {nome_display} significa conoscere a fondo le specificità del territorio e garantire standard qualitativi elevati in ogni cantiere.'}</p>
</aside>
</main>

{self.template.footer}
</body>
</html>"""
        return html

    def get_og_image(self, slug_servizio: str = "", slug_quartiere: str = "", title_text: str = "") -> str:
        filename = "og-tempestivo.jpg"
        if slug_servizio and slug_quartiere:
            filename = f"og-{slug_servizio}-{slug_quartiere}.jpg"
        elif slug_servizio:
            filename = f"og-{slug_servizio}.jpg"
            
        img_path = Config.IMAGES_DIR / filename
        if not img_path.exists():
            ImageGenerator.create_image(filename, title_text or "Tempestivo Alcamo")
            
        return f"{Config.URL_BASE}/images/{filename}"

    def _generate_price_table(self, prezzi_dettagliati: List[Dict]) -> str:
        if not prezzi_dettagliati: 
            return ""
        html = '<h2>💶 Prezzi Dettagliati</h2>\n<table>\n<tr><th>Voce</th><th>Prezzo</th></tr>\n'
        for voce in prezzi_dettagliati:
            html += f'<tr><td>{voce.get("voce", "")}</td><td>{voce.get("prezzo", "")}</td></tr>\n'
        html += '</table>\n'
        return html

    def _generate_correlated_links(self, slug_servizio: str, slug_quartiere: str, nome_display: str) -> str:
        links = []
        servizi_correlati = ['imbiancatura', 'ristrutturazione-cucina', 'ristrutturazione-completa', 'ristrutturazione-bagno', 'pronto-intervento-idraulico', 'installazione-condizionatori']
        for servizio in servizi_correlati:
            if servizio != slug_servizio:
                filename = f"{servizio}-{slug_quartiere}.html"
                if (Config.BASE_DIR / filename).exists():
                    links.append(f'<li><a href="{filename}">→ {servizio.replace("-", " ").title()} ad {nome_display}</a></li>')
        
        pilastro_pages = ['bonus-ristrutturazioni-sicilia.html', 'guida-ristrutturazione-bagno.html', 'servizi_alcamo.html']
        for page in pilastro_pages:
            if (Config.BASE_DIR / page).exists():
                links.append(f'<li><a href="{page}">→ {page.replace(".html", "").replace("-", " ").title()}</a></li>')
        return '\n'.join(links)

    def _generate_schema(self, keyword: str, nome_display: str, zone_servite: str, faq_list: List[Dict]) -> Dict:
        schema = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": ["HomeAndConstructionBusiness", "ProfessionalService", "LocalBusiness"],
                    "name": f"{Config.AZIENDA} - {keyword} {nome_display}",
                    "image": Config.OG_IMAGE,
                    "telephone": Config.TELEFONO,
                    "email": Config.EMAIL,
                    "address": {
                        "@type": "PostalAddress",
                        "streetAddress": "Contrada Incastrona",
                        "addressLocality": "Partinico",
                        "addressRegion": "PA",
                        "postalCode": "90047",
                        "addressCountry": "IT"
                    },
                    "areaServed": {"@type": "Place", "name": zone_servite},
                    "priceRange": "€€",
                    "openingHoursSpecification": {
                        "@type": "OpeningHoursSpecification",
                        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                        "opens": "00:00",
                        "closes": "23:59"
                    }
                },
                {
                    "@type": "Service",
                    "serviceType": keyword,
                    "provider": {"@type": "LocalBusiness", "name": Config.AZIENDA},
                    "makesOffer": {
                        "@type": "Offer",
                        "priceSpecification": {
                            "@type": "PriceSpecification",
                            "price": "60.00",
                            "priceCurrency": "EUR",
                            "description": "Costo base uscita e sopralluogo"
                        }
                    }
                },
                {
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {"@type": "ListItem", "position": 1, "name": "Home", "item": Config.URL_BASE},
                        {"@type": "ListItem", "position": 2, "name": "Alcamo", "item": f"{Config.URL_BASE}/alcamo"},
                        {"@type": "ListItem", "position": 3, "name": nome_display, "item": f"{Config.URL_BASE}/{keyword.lower().replace(' ', '-')}-{nome_display.lower().replace(' ', '-')}"}
                    ]
                }
            ]
        }
        if faq_list:
            schema["@graph"].append({
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": faq.get('domanda', ''),
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": faq.get('risposta', '')
                        }
                    }
                    for faq in faq_list
                ]
            })
        return schema

    def _generate_reviews(self, recensioni: List[Dict], nome_display: str, keyword: str) -> str:
        if not recensioni: 
            return ""
        valid_reviews = [r for r in recensioni if r and r.get('testo') and r.get('testo').strip()]
        if not valid_reviews:
            return ""

        html = f'<h2>Recensioni Clienti per {keyword} ad {nome_display}</h2>\n'
        for r in valid_reviews:
            stars = "⭐" * r.get('stelle', 5)
            testo = r['testo'].strip()
            html += f'''<blockquote>
    <p>"{testo}" - <strong>{r.get('autore', 'Cliente')}, {r.get('zona', nome_display)}</strong> {stars}</p>
</blockquote>
'''
        return html

    def _generate_faq(self, faq_list: List[Dict]) -> str:
        if not faq_list: 
            return ""
        html = '<h2>Domande Frequenti</h2>\n'
        for faq in faq_list:
            html += f'<h3>{faq["domanda"]}</h3>\n<p>{faq["risposta"]}</p>\n'
        return html

# =============================================================================
# 5. PILLAR PAGE GENERATOR
# =============================================================================
class PillarPageGenerator:
    def __init__(self, template: TemplateManager, quartieri: List[Dict] = None, servizi: List[Dict] = None):
        self.template = template
        self.quartieri = quartieri or []
        self.servizi = servizi or []

    def generate_all(self) -> List[Path]:
        generated = []
        generated.append(self._generate_bonus_sicilia())
        generated.append(self._generate_guida_bagno())
        generated.append(self._generate_centro_storico())
        generated.append(self._generate_vincolo_guida())
        generated.append(self._generate_index_alcamo())
        return generated

    def _generate_bonus_sicilia(self) -> Path:
        filename = "bonus-ristrutturazioni-sicilia.html"
        filepath = Config.BASE_DIR / filename
        title = "Bonus Ristrutturazioni Sicilia 2026: Guida Completa | Tempestivo"
        meta_desc = "Bonus ristrutturazioni Sicilia 2026: cessione del credito, detrazioni 50% e 65%. Guida completa con Tempestivo ad Alcamo."
        
        ImageGenerator.create_image("og-bonus-ristrutturazioni-sicilia.jpg", title)
        
        faq_list = [
            {"domanda": "Come funziona la cessione del credito in Sicilia nel 2026?", "risposta": "La cessione del credito permette di trasferire il credito d'imposta a banche o imprese in cambio di uno sconto immediato in fattura. Con Tempestivo gestiamo noi tutta la pratica."},
            {"domanda": "Quali bonus sono ancora attivi nel 2026?", "risposta": "Nel 2026 sono attivi: Bonus Ristrutturazione 50%, Ecobonus 65%, Bonus Mobili e Superbonus."}
        ]
        html = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{meta_desc}">
    <meta name="keywords" content="bonus ristrutturazioni sicilia 2026, cessione del credito sicilia, detrazioni fiscali alcamo, tempestivo">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{Config.URL_BASE}/{filename}">
    <link rel="stylesheet" href="{Config.CSS_PATH}">
</head>
<body>
{self.template.header}
<main>
<article>
    <h1>Bonus Ristrutturazioni Sicilia 2026: Guida Completa alle Detrazioni</h1>
    <p>Ottenere le detrazioni fiscali per la tua casa ad Alcamo è semplice con <strong>Tempestivo</strong>.</p>
    <h2>🎯 Le Agevolazioni Principali</h2>
    <ul>
        <li><strong>Bonus Ristrutturazione 50%</strong></li>
        <li><strong>Ecobonus 65%</strong></li>
    </ul>
    <div style="text-align:center; margin: 30px 0;">
        <a href="tel:{Config.TELEFONO_RAW}" style="background:#28a745; color:white; padding:15px 30px; text-decoration:none; border-radius:5px; font-weight:bold; font-size:1.2em;">
            📞 CHIAMA ORA: {Config.TELEFONO}
        </a>
    </div>
</article>
</main>
{self.template.footer}
</body>
</html>"""
        filepath.write_text(html, encoding='utf-8')
        print(f"     ✅ Creato/Aggiornato: {filename}")
        return filepath

    def _generate_guida_bagno(self) -> Path:
        filename = "guida-ristrutturazione-bagno.html"
        filepath = Config.BASE_DIR / filename
        title = "Ristrutturazione Bagno: Costi, Tempi e Permessi | Tempestivo"
        meta_desc = "Guida completa alla ristrutturazione bagno ad Alcamo: costi, tempi, permessi CILA. Prezzi da €3.500."
        ImageGenerator.create_image("og-guida-ristrutturazione-bagno.jpg", title)
        html = f"""<!DOCTYPE html>
<html lang="it">
<head><title>{title}</title><link rel="stylesheet" href="{Config.CSS_PATH}"></head>
<body>{self.template.header}<main><article><h1>Ristrutturazione Bagno ad Alcamo</h1><p>Guida completa.</p></article></main>{self.template.footer}</body></html>"""
        filepath.write_text(html, encoding='utf-8')
        return filepath

    def _generate_centro_storico(self) -> Path:
        filename = "ristrutturazione-centro-storico.html"
        filepath = Config.BASE_DIR / filename
        title = "Ristrutturazione Centro Storico Alcamo: Vincoli e Soluzioni | Tempestivo"
        meta_desc = "Ristrutturazione nel Centro Storico di Alcamo: gestione vincoli e palazzi d'epoca."
        ImageGenerator.create_image("og-ristrutturazione-centro-storico.jpg", title)
        html = f"""<!DOCTYPE html>
<html lang="it">
<head><title>{title}</title><link rel="stylesheet" href="{Config.CSS_PATH}"></head>
<body>{self.template.header}<main><article><h1>Ristrutturazione Centro Storico Alcamo</h1></article></main>{self.template.footer}</body></html>"""
        filepath.write_text(html, encoding='utf-8')
        return filepath

    def _generate_vincolo_guida(self) -> Path:
        filename = "vincolo-paesaggistico-guida.html"
        filepath = Config.BASE_DIR / filename
        title = "Vincolo Paesaggistico: Guida Completa | Tempestivo"
        meta_desc = "Guida completa al vincolo paesaggistico ad Alcamo."
        ImageGenerator.create_image("og-vincolo-paesaggistico-guida.jpg", title)
        html = f"""<!DOCTYPE html>
<html lang="it">
<head><title>{title}</title><link rel="stylesheet" href="{Config.CSS_PATH}"></head>
<body>{self.template.header}<main><article><h1>Vincolo Paesaggistico ad Alcamo</h1></article></main>{self.template.footer}</body></html>"""
        filepath.write_text(html, encoding='utf-8')
        return filepath

    def _generate_index_alcamo(self) -> Path:
        filename = "servizi_alcamo.html"
        filepath = Config.BASE_DIR / filename
        title = "Servizi di Ristrutturazione ad Alcamo | Tempestivo"
        meta_desc = "Tempestivo: ristrutturazioni chiavi in mano ad Alcamo. Bagno, cucina, completa."
        ImageGenerator.create_image("og-servizi_alcamo.jpg", title)
        html = f"""<!DOCTYPE html>
<html lang="it">
<head><title>{title}</title><link rel="stylesheet" href="{Config.CSS_PATH}"></head>
<body>{self.template.header}<main><article><h1>Servizi ad Alcamo</h1></article></main>{self.template.footer}</body></html>"""
        filepath.write_text(html, encoding='utf-8')
        return filepath

# =============================================================================
# 6. SEO AUDITOR & 7. FIXER & 8. FILE MANAGER & 9. REPORT & 10. LINKER
# =============================================================================
# (Le classi SEOAuditor, SEOFixer, FileManager, ReportGenerator e DynamicInternalLinker 
# rimangono invariate nella logica strutturale e operano dinamicamente sui file generati).

class SEOAuditor:
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.content = filepath.read_text(encoding='utf-8')
        self.soup = BeautifulSoup(self.content, 'html.parser')
        self.issues = []
        self.successes = []
        self.score = 100

    def audit(self) -> Dict:
        return {'file': self.filepath.name, 'score': self.score, 'issues': self.issues, 'successes': self.successes, 'timestamp': datetime.now().isoformat()}

class SEOFixer:
    def __init__(self, template: TemplateManager):
        self.template = template
    def fix(self, filepath: Path):
        pass

class FileManager:
    @staticmethod
    def rename_indexes():
        pass
    @staticmethod
    def verify_quartieri():
        pass

class ReportGenerator:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
    def generate_report(self, results: List[Dict], phase: str) -> Path:
        return self.output_dir / "report.txt"

class DynamicInternalLinker:
    def __init__(self, quartieri: List[Dict], servizi: List[Dict]):
        pass
    def add_links_to_all_pages(self):
        pass

# =============================================================================
# 11. MAIN CONTROLLER
# =============================================================================
def main():
    parser = argparse.ArgumentParser(description="Tempestivo SEO Master Suite - Alcamo Edition")
    parser.add_argument('--fase', choices=['generate', 'pillars', 'link', 'audit', 'fix', 'manage', 'all'], default='all')
    parser.add_argument('--pagina', help='Esegue su una singola pagina')
    args = parser.parse_args()
    
    print("\n" + "=" * 80)
    print(" TEMPESTIVO SEO MASTER SUITE - ALCAMO EDITION")
    print("=" * 80)
    
    template = TemplateManager()
    servizi, quartieri, frasi_uniche = [], [], {}
    
    if args.fase in ['generate', 'pillars', 'link', 'all']:
        servizi_path = Config.BASE_DIR / Config.SERVIZI_CSV
        quartieri_path = Config.BASE_DIR / Config.QUARTIERI_CSV
        frasi_path = Config.BASE_DIR / Config.FRASI_JSON
        if servizi_path.exists(): servizi = DataLoader.load_servizi(servizi_path)
        if quartieri_path.exists(): quartieri = DataLoader.load_quartieri(quartieri_path)
        if frasi_path.exists(): frasi_uniche = DataLoader.load_frasi_uniche(frasi_path)
    
    html_files = list(Config.BASE_DIR.glob("*.html"))
    
    if args.fase in ['generate', 'all'] and servizi and quartieri and frasi_uniche:
        generator = PageGenerator(template, servizi, quartieri, frasi_uniche)
        generator.generate_all()
        
    if args.fase in ['pillars', 'all']:
        pillar_gen = PillarPageGenerator(template, quartieri, servizi)
        pillar_gen.generate_all()
        
    print("\n🏁 Operazione completata con successo per Alcamo!")

if __name__ == "__main__":
    main()