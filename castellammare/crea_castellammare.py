#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
TEMPESTIVO SEO MASTER SUITE - V 9.2 (CORRECTED & INTEGRATED ENTERPRISE VERSION)
Adattato per Castellammare del Golfo
Script unico, completo e privo di omissioni con:
- Meta Tag Ottimizzati, Geo Tags, Twitter Cards & Open Graph Completo
- Schema.org Avanzato per AI Overviews
- Generazione pagine dinamiche da CSV/JSON esterni con Fix HTML & Contextual Logic
- Pagine Pilastro (Bonus Sicilia, Guida Bagno, Centro Storico, Vincoli, Index Castellammare)
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
    SERVIZI_CSV = "servizi_castellammare.csv"
    QUARTIERI_CSV = "quartieri_castellammare.csv"
    FRASI_JSON = "frasi_uniche_castellammare.json"
    
    # Dati aziendali (E-A-T)
    AZIENDA = "Tempestivo"
    TELEFONO = "+39 352 025 85 83"
    TELEFONO_RAW = "3520258583"
    EMAIL = "tempestivoweb@gmail.com"
    INDIRIZZO = "Contrada Incastrona, 90047 Partinico (PA)"
    P_IVA = "06772720824"
    URL_BASE = "https://tempestivo.it/castellammare-del-golfo"
    CSS_PATH = "/style.css"
    OG_IMAGE = f"{URL_BASE}/images/og-tempestivo.jpg"
    
    # Geo Tags Default (Castellammare del Golfo - TP)
    GEO_REGION = "IT-TP"
    GEO_PLACENAME = "Castellammare del Golfo"
    GEO_POSITION = "38.0285;12.8824"
    ICBM = "38.0285, 12.8824"
    
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
            {"testo": "Lavori a regola d'arte e prezzi onesti, esattamente come da preventivo. Tecnico arrivato in 40 minuti a Castellammare del Golfo. Consigliatissimi!", "autore": "Marco V.", "zona": "Castellammare del Golfo", "stelle": 5},
            {"testo": "Prezzi onesti e lavori a regola d'arte. Hanno gestito tutto tramite un unico Project Manager, zero stress. Ditta edile eccezionale!", "autore": "Giulia R.", "zona": "Centro Storico", "stelle": 5}
        ],
        "castellammare-centro": [
            {"testo": "Ho avuto un'emergenza idrica nel centro storico di Castellammare del Golfo. Tempestivo è arrivato in pochissimo tempo. Prezzi onesti e lavori a regola d'arte. Consigliatissimi!", "autore": "Cliente Verificato", "zona": "Centro Storico", "stelle": 5}
        ],
        "calatubo": [
            {"testo": "Gestisco una casa vacanza a Calatubo. Ho chiamato Tempestivo per una riparazione urgente del climatizzatore. Aria condizionata ripristinata in poche ore. Un partner indispensabile!", "autore": "Gestore Casa Vacanza", "zona": "Calatubo", "stelle": 5}
        ],
        "scopello": [
            {"testo": "Intervento di ristrutturazione a Scopello con servizio chiavi in mano. Hanno gestito tutto tramite un unico Project Manager. Zero stress, cantiere pulito e tempi rispettati. Lavori a regola d'arte!", "autore": "Proprietario di Casa", "zona": "Scopello", "stelle": 5}
        ],
        "guidaloca": [
            {"testo": "Tempestivo ha svolto un intervento impeccabile a Guidaloca nei tempi previsti. Professionali e puliti. Prezzi onesti e lavori a regola d'arte!", "autore": "Mario R.", "zona": "Guidaloca", "stelle": 5}
        ],
        "alcamo-marina": [
            {"testo": "Ho avuto un improvviso guasto elettrico vicino Castellammare. Il tecnico è arrivato in tempi record, ha individuato subito il problema e ha ripristinato tutto in totale sicurezza. Efficienti e competenti!", "autore": "Cliente Privato", "zona": "Zona Costiera", "stelle": 5}
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
        "castellammare-centro": {"intro": "Il centro storico di Castellammare del Golfo richiede particolare attenzione ai vicoli caratteristici, alle case tradizionali e alla logistica di cantiere.", "problematiche": ["Gestione accessi nei vicoli stretti del centro storico", "Conservazione delle facciate e degli elementi architettonici tipici", "Rifacimento impianti in edifici storici", "Coordinamento rapido per attività turistiche e case vacanza"]},
        "scopello": {"intro": "Le ville e i bagli storici di Scopello richiedono una gestione rigorosa dei vincoli paesaggistici e dei materiali resistenti alla salsedine.", "problematiche": ["Rispetto assoluto dei vincoli paesaggistici e ambientali", "Trattamento contro l'umidità e la salsedine della costa", "Finiture di pregio per ville e caseggiati rurali", "Logistica complessa per aree naturalistiche protette"]},
        "calatubo": {"intro": "Nella zona di Calatubo gestiamo interventi rapidi su complessi residenziali e case indipendenti con focus su efficienza e sicurezza.", "problematiche": ["Adeguamento impianti elettrici e idraulici obsoleti", "Interventi rapidi per case vacanza estive", "Soluzioni per isolamento termico e climatizzazione", "Trasparenza dei costi e rispetto dei tempi di consegna"]}
    }

# =============================================================================
# 1.5 IMAGE GENERATOR (PILLOW)
# =============================================================================
class ImageGenerator:
    @staticmethod
    def create_image(filename: str, title_text: str) -> Path:
        """
        Genera automaticamente un file immagine fisico tramite Pillow (PIL)
        salvandolo nella cartella di destinazione delle immagini.
        """
        Config.IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        img_path = Config.IMAGES_DIR / filename
        
        width, height = 1200, 630
        bg_color = (26, 37, 47)  # Blu scuro istituzionale
        accent_color = (40, 167, 69)  # Verde Tempestivo
        text_color = (255, 255, 255)
        
        if PILLOW_AVAILABLE:
            image = Image.new("RGB", (width, height), color=bg_color)
            draw = ImageDraw.Draw(image)
            
            # Decorazione grafica di base (barra superiore)
            draw.rectangle([0, 0, width, 25], fill=accent_color)
            
            # Tentativo di caricare un font di sistema, altrimenti fallback sul default
            try:
                font_title = ImageFont.truetype("arial.ttf", 48)
                font_brand = ImageFont.truetype("arial.ttf", 32)
            except IOError:
                font_title = ImageFont.load_default()
                font_brand = ImageFont.load_default()
                
            draw.text((80, 200), "TEMPESTIVO CASTELLAMMARE", fill=accent_color, font=font_brand)
            
            # Wrapping rudimentale del testo per evitare sbordi
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
            # Fallback se Pillow non è installato nel sistema: crea un file vuoto o segnaposto
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
        print(f"✅ Caricati {len(quartieri)} quartieri/zone da {filepath.name}")
        return quartieri

    @staticmethod
    def load_frasi_uniche(filepath: Path) -> Dict:
        if not filepath.exists(): 
            raise FileNotFoundError(f"File frasi uniche non trovato: {filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Caricate frasi uniche per {len(data)} zone da {filepath.name}")
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
            if header:
                blocks.append(str(header))
            if sub_nav:
                blocks.append(str(sub_nav))
            if page_offset:
                blocks.append(str(page_offset))
                
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
        intro = frasi.get('intro', f"I nostri interventi di {nome_servizio.lower()} a {nome_display} sono sviluppati per garantire massima qualità ed efficienza.")
        problematiche = frasi.get('problematiche', Config.FRASI_UNICHE.get(slug_quartiere, {}).get('problematiche', []))
        vincoli = frasi.get('vincoli_specifici', quartiere.get('vincoli', 'nessun vincolo bloccante'))
        missione = frasi.get('missione', '')
        
        keyword = servizio.get('keyword_principale', nome_servizio)
        prezzo_min = servizio.get('prezzo_min', '')
        prezzo_max = servizio.get('prezzo_max', '')
        
        # FIX REFUSO DOPPIO "Da"
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
        
        # FAQ Dinamiche adattate al servizio specifico
        faq_list = frasi.get('faq', [
            {"domanda": f"Quanto costa il servizio di {keyword.lower()} a {nome_display}?", "risposta": f"Il prezzo per {keyword.lower()} a {nome_display} parte da {prezzo_range}, con sopralluogo e preventivo dettagliato privo di costi nascosti."},
            {"domanda": f"Quali sono i tempi di esecuzione per {keyword.lower()} a {nome_display}?", "risposta": f"I tempi standard di consegna per {keyword.lower()} sono di circa {durata}, pienamente garantiti contrattualmente."},
            {"domanda": f"Fornite garanzia e certificazione per {keyword.lower()}?", "risposta": f"Sì, rilasciamo garanzia ufficiale e conformità sui lavori eseguiti a {nome_display} in base alle normative vigenti."}
        ])
        
        # Recensioni Dinamiche
        recensioni = frasi.get('recensioni', Config.RECENSIONI.get(slug_quartiere, Config.RECENSIONI.get('default', [])))

        prezzi_dettagliati_json = servizio.get('prezzi_dettagliati', '[]')
        try:
            prezzi_dettagliati = json.loads(prezzi_dettagliati_json)
        except json.JSONDecodeError:
            prezzi_dettagliati = []

        # CORREZIONE TITLE: Riconfigurato per includere "giorni" correttamente
        title = f"{keyword} a {nome_display}: Chiavi in Mano in {durata} | {Config.AZIENDA}"
        if len(title) > 65:
            title = f"{keyword} a {nome_display} in {durata} | {Config.AZIENDA}"

        # CORREZIONE META DESCRIPTION: Rimosso doppio "Da"
        meta_desc = (
            f"Servizio professionale di {keyword.lower()} a {nome_display} con formula chiavi in mano in {durata}. "
            f"Prezzi trasparenti a partire da {prezzo_range}. Sopralluogo e preventivo gratuito: "
            f"chiama il {Config.TELEFONO}."
        )

        schema = self._generate_schema(keyword, nome_display, zone_servite, faq_list)
        tabella_prezzi_html = self._generate_price_table(prezzi_dettagliati)
        link_correlati_html = self._generate_correlated_links(slug_servizio, slug_quartiere, nome_display)

        # Generazione automatica immagine fisica e recupero URL con fallback
        og_image = self.get_og_image(slug_servizio, slug_quartiere, title)

        # INTEGRATO PUNTO 1: CONDIZIONALE BUROCRAZIA / PERMESSI (inclusi nuovi servizi di manutenzione rapida)
        servizi_edilizia_libera = [
            'imbiancatura', 'tinteggiatura', 'pittura', 'riparazione',
            'sostituzione-sanitari', 'disostruzione', 'ricerca-perdite', 'manutenzione',
            'pronto-intervento', 'installazione-condizionatori', 'sostituzione-caldaie', 'apertura-porte'
        ]
        is_edilizia_libera = any(k in slug_servizio.lower() or k in keyword.lower() for k in servizi_edilizia_libera)

        if is_edilizia_libera:
            testo_burocrazia = f"<strong>Verifica Inquadramento ed Edilizia Libera:</strong> L'intervento di {keyword.lower()} rientra nelle attività di edilizia libera e manutenzione ordinaria/urgente. Non richiede la presentazione di pratiche burocratiche complesse (CILA/SCIA), garantendo un avvio immediato dei lavori a {nome_display} nel pieno rispetto dei regolamenti locali."
        else:
            testo_burocrazia = f"<strong>Gestione Burocratica e Permessi:</strong> Presentazione delle pratiche edilizie necessarie (CILA, SCIA o permessi della Soprintendenza ove richiesta) specifiche per la zona di {nome_display}."

        html = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    
    <!-- META TAG OTTIMIZZATI -->
    <meta name="description" content="{meta_desc}">
    <meta name="keywords" content="{keyword.lower()} {nome_display.lower()}, {keyword.lower()} chiavi in mano, Tempestivo">
    <meta name="robots" content="index, follow">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{meta_desc}">
    <meta property="og:type" content="website">
    <meta property="og:image" content="{og_image}">
    <meta property="og:locale" content="it_IT">
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{meta_desc}">
    <meta name="twitter:image" content="{og_image}">
    
    <!-- Geo Tags -->
    <meta name="geo.region" content="{Config.GEO_REGION}">
    <meta name="geo.placename" content="{nome_display}, {Config.GEO_PLACENAME}">
    <meta name="geo.position" content="{Config.GEO_POSITION}">
    <meta name="ICBM" content="{Config.ICBM}">
    
    <link rel="canonical" href="{Config.URL_BASE}/{slug_servizio}-{slug_quartiere}.html">
    <link rel="stylesheet" href="{Config.CSS_PATH}">
    
    <!-- SCHEMA.ORG AVANZATO PER AI OVERVIEWS -->
    <script type="application/ld+json">
{json.dumps(schema, indent=2, ensure_ascii=False)}
    </script>
</head>
<body>
{self.template.header}
<main>
<article>
    <h1>{keyword} a {nome_display}: Chiavi in Mano in {durata}</h1>
    <p><strong>{keyword} a {nome_display}:</strong> {definizione}</p>
    
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
        <tr><td>Servizio</td><td>{keyword} chiavi in mano a {nome_display}</td></tr>
        <tr><td>Prezzo</td><td>A partire da {prezzo_range}</td></tr>
        <tr><td>Durata</td><td>{durata}</td></tr>
        <tr><td>Zona</td><td>{zone_servite}</td></tr>
        <tr><td>Vincoli</td><td>{vincoli}</td></tr>
        <tr><td>Materiali</td><td>{materiali_inclusi}</td></tr>
        <tr><td>Garanzia</td><td>{garanzia}</td></tr>
    </table>
    
    {tabella_prezzi_html}
    
    <!-- CORREZIONE HTML ANIDATO: h2 e p SEPARATI -->
    <h2>Le problematiche specifiche di {nome_display}</h2>
    <p>{intro}</p>
    <ul>
        {''.join([f'<li>✓ {p}</li>' for p in problematiche]) if problematiche else '<li>✓ Nessuna problematica specifica documentata</li>'}
    </ul>
    <p><em>Nota: Operiamo tenendo conto di {vincoli}.</em></p>

    <h2>Iter Operativo per {keyword} a {nome_display}</h2>
    <p>Per garantire un risultato impeccabile e senza intoppi nell'area di {nome_display}, adottiamo un processo collaudato che azzera gli imprevisti e ottimizza le tempistiche:</p>
    <ol>
        <li><strong>Sopralluogo tecnico sul posto:</strong> Un nostro responsabile si reca a {nome_display} per analizzare lo stato di fatto, rilievi metrici e verificare accessibilità e vincoli della zona.</li>
        <li><strong>Pianificazione e Preventivo Definitivo:</strong> Invio di una proposta chiara con specifica dettagliata delle lavorazioni, materiali scelti e costi trasparenti senza sorprese finali.</li>
        <li>{testo_burocrazia}</li>
        <li><strong>Esecuzione Lavori e Direzione Cantiere:</strong> Attuazione degli interventi con maestranze qualificate sotto la costante supervisione del nostro Project Manager dedicato.</li>
        <li><strong>Collaudo, Pulizia e Consegna:</strong> Verifica finale del perfetto funzionamento di impianti e finiture, pulizia profonda dell'immobile e rilascio di garanzia ufficiale.</li>
    </ol>

    <h2>Materiali e Tecnologie Adottate</h2>
    <p>La scelta delle materie prime è fondamentale per garantire la longevità dell'intervento, specialmente in un contesto costiero come {nome_display}. Impieghiamo esclusivamente materiali certificati, ecocompatibili e altamente resistenti all'usura e agli agenti atmosferici locali. I nostri impianti sono conformi alle normative europee di risparmio energetico e sicurezza, assicurando la massima efficienza termica e acustica per il tuo immobile.</p>

    <h2>La nostra soluzione per {keyword}</h2>
    <p>Il nostro approccio integrato per {keyword} unisce competenze di progettazione, impiantistica e finitura edile. Ascoltiamo le tue esigenze stilistiche e funzionali per realizzare una soluzione personalizzata a {nome_display}, coordinando ogni singola fase fino al completamento dell'opera nei tempi prestabiliti.</p>
    <p><strong>A partire da {prezzo_range}</strong> | ⏱️ Tempi stimati: {durata}</p>

    <h2>Trasparenza, Sicurezza e Normative</h2>
    <p>Ogni intervento svolto a {nome_display} viene eseguito nel rigoroso rispetto delle normative vigenti in materia di sicurezza sui luoghi di lavoro e smaltimento rifiuti edili. Rilasciamo tutte le certificazioni di conformità per gli impianti realizzati, consentendoti di accedere alle detrazioni fiscali e ai bonus ristrutturazione disponibili in Sicilia per l'anno in corso.</p>

    <h2>Perché sceglierci a {nome_display}</h2>
    <p>Con centinaia di cantieri portati a termine tra Castellammare del Golfo e la provincia di Trapani, Tempestivo rappresenta un punto di riferimento per chi cerca serietà, rispetto dei tempi e costi certi. Il nostro unico punto di contatto evita dispersioni di responsabilità, offrendo un servizio veramente completo e garantito.</p>
    
    {self._generate_reviews(recensioni, nome_display, keyword)}
    {self._generate_faq(faq_list)}
    
    {f'<h2>Servizi Correlati</h2><ul>{link_correlati_html}</ul>' if link_correlati_html else ''}
    
    <!-- CORREZIONE CTA TRONCATO -->
    <div style="text-align:center; margin: 30px 0;">
        <a href="tel:{Config.TELEFONO_RAW}" style="background:#28a745; color:white; padding:15px 30px; text-decoration:none; border-radius:5px; font-weight:bold; font-size:1.2em;">
            📞 CHIAMA ORA per {keyword} a {nome_display}: Chiavi in Mano {Config.TELEFONO}
        </a>
    </div>
</article>

<aside>
    <h3>La Nostra Missione a {nome_display}</h3>
    <p>{missione if missione else f'Operare a {nome_display} significa conoscere a fondo le specificità del territorio e garantire standard qualitativi elevati in ogni cantiere.'}</p>
</aside>
</main>

{self.template.footer}
</body>
</html>"""
        return html

    # INTEGRATO: ESTRAZIONE DINAMICA IMMAGINE OG CON GENERAZIONE FISICA E FALLBACK PRIORITARIO
    def get_og_image(self, slug_servizio: str = "", slug_quartiere: str = "", title_text: str = "") -> str:
        """
        Genera fisicamente il file immagine se non esiste e restituisce l'URL corretto
        seguendo una logica di fallback prioritaria.
        """
        filename = "og-tempestivo.jpg"
        if slug_servizio and slug_quartiere:
            filename = f"og-{slug_servizio}-{slug_quartiere}.jpg"
        elif slug_servizio:
            filename = f"og-{slug_servizio}.jpg"
            
        img_path = Config.IMAGES_DIR / filename
        if not img_path.exists():
            ImageGenerator.create_image(filename, title_text or "Tempestivo Castellammare del Golfo")
            
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
                    links.append(f'<li><a href="{filename}">→ {servizio.replace("-", " ").title()} a {nome_display}</a></li>')
        
        pilastro_pages = ['bonus-ristrutturazioni-sicilia.html', 'guida-ristrutturazione-bagno.html', 'servizi_castellammare.html']
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
                        {"@type": "ListItem", "position": 2, "name": "Castellammare del Golfo", "item": f"{Config.URL_BASE}/castellammare-del-golfo"},
                        {"@type": "ListItem", "position": 3, "name": nome_display, "item": f"{Config.URL_BASE}/{keyword.lower().replace(' ', '-')}-{nome_display.lower().replace(' ', '-')}"}
                    ]
                },
                {
                    "@type": "HowTo",
                    "name": f"Iter Operativo per {keyword} a {nome_display}",
                    "description": f"Processo operativo in 5 passaggi per la realizzazione di {keyword.lower()} a {nome_display} con la garanzia di Tempestivo.",
                    "step": [
                        {
                            "@type": "HowToStep",
                            "position": 1,
                            "name": "Sopralluogo tecnico sul posto",
                            "text": f"Un nostro responsabile si reca a {nome_display} per analizzare lo stato di fatto, rilievi metrici e verificare accessibilità e vincoli della zona."
                        },
                        {
                            "@type": "HowToStep",
                            "position": 2,
                            "name": "Pianificazione e Preventivo Definitivo",
                            "text": "Invio di una proposta chiara con specifica dettagliata delle lavorazioni, materiali scelti e costi trasparenti senza sorprese finali."
                        },
                        {
                            "@type": "HowToStep",
                            "position": 3,
                            "name": "Gestione Burocratica e Permessi",
                            "text": f"Verifica o presentazione delle pratiche edilizie (CILA, SCIA, Soprintendenza o Edilizia Libera) per la zona di {nome_display}."
                        },
                        {
                            "@type": "HowToStep",
                            "position": 4,
                            "name": "Esecuzione Lavori e Direzione Cantiere",
                            "text": "Attuazione degli interventi con maestranze qualificate sotto la costante supervisione del nostro Project Manager dedicato."
                        },
                        {
                            "@type": "HowToStep",
                            "position": 5,
                            "name": "Collaudo, Pulizia e Consegna",
                            "text": "Verifica finale del perfetto funzionamento di impianti e finiture, pulizia profonda dell'immobile e rilascio di garanzia ufficiale."
                        }
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

        html = f'<h2>Recensioni Clienti per {keyword} a {nome_display}</h2>\n'
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
        p = self._generate_bonus_sicilia()
        generated.append(p)
        p = self._generate_guida_bagno()
        generated.append(p)
        p = self._generate_centro_storico()
        generated.append(p)
        p = self._generate_vincolo_guida()
        generated.append(p)
        p = self._generate_index_castellammare()
        generated.append(p)
        return generated

    def _generate_bonus_sicilia(self) -> Path:
        filename = "bonus-ristrutturazioni-sicilia.html"
        filepath = Config.BASE_DIR / filename
        title = "Bonus Ristrutturazioni Sicilia 2026: Guida Completa | Tempestivo"
        meta_desc = "Bonus ristrutturazioni Sicilia 2026: cessione del credito, detrazioni 50% e 65%. Guida completa con Tempestivo. Preventivo gratuito."
        
        ImageGenerator.create_image("og-bonus-ristrutturazioni-sicilia.jpg", title)
        
        faq_list = [
            {"domanda": "Come funziona la cessione del credito in Sicilia nel 2026?", "risposta": "La cessione del credito permette di trasferire il credito d'imposta a banche o imprese in cambio di uno sconto immediato in fattura. Con Tempestivo gestiamo noi tutta la pratica: dalla verifica dei requisiti alla comunicazione all'Agenzia delle Entrate. Lo sconto in fattura può arrivare fino al 100% dell'importo dei lavori."},
            {"domanda": "Quali bonus sono ancora attivi nel 2026?", "risposta": "Nel 2026 sono attivi: Bonus Ristrutturazione 50% (manutenzione straordinaria), Ecobonus 65% (efficientamento energetico), Bonus Mobili (acquisto mobili ed elettrodomestici), e Superbonus per condomini. Ogni bonus ha requisiti specifici che il nostro team tecnico verifica gratuitamente."},
            {"domanda": "Quanto tempo serve per ottenere le detrazioni?", "risposta": "I tempi variano: 30-60 giorni per la pratica CILA/SCIA, 60-90 giorni per l'approvazione della cessione del credito. Tempestivo gestisce tutto in parallelo ai lavori, così non perdi tempo. Al termine dei lavori rilasciamo tutta la documentazione per il commercialista."},
            {"domanda": "Posso cumulare più bonus sullo stesso immobile?", "risposta": "Sì, in molti casi è possibile cumulare Bonus Ristrutturazione 50% con Ecobonus 65% e Bonus Mobili. Il nostro team tecnico analizza il tuo caso specifico per massimizzare le detrazioni disponibili."}
        ]
        html = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{meta_desc}">
    <meta name="keywords" content="bonus ristrutturazioni sicilia 2026, cessione del credito sicilia, detrazioni fiscali castellammare, tempestivo">
    <meta name="robots" content="index, follow">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{meta_desc}">
    <meta property="og:type" content="website">
    <meta property="og:image" content="{Config.URL_BASE}/images/og-bonus-ristrutturazioni-sicilia.jpg">
    <meta property="og:locale" content="it_IT">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{meta_desc}">
    <meta name="twitter:image" content="{Config.URL_BASE}/images/og-bonus-ristrutturazioni-sicilia.jpg">
    <meta name="geo.region" content="{Config.GEO_REGION}">
    <meta name="geo.placename" content="{Config.GEO_PLACENAME}">
    <meta name="geo.position" content="{Config.GEO_POSITION}">
    <meta name="ICBM" content="{Config.ICBM}">
    <link rel="canonical" href="{Config.URL_BASE}/{filename}">
    <link rel="stylesheet" href="{Config.CSS_PATH}">
    <script type="application/ld+json">
{json.dumps(self._generate_schema_bonus(faq_list), indent=2, ensure_ascii=False)}
    </script>
</head>
<body>
{self.template.header}
<main>
<article>
    <h1>Bonus Ristrutturazioni Sicilia 2026: Guida Completa alle Detrazioni</h1>
    <p>Ottenere le detrazioni fiscali per la tua casa in Sicilia può sembrare complicato, ma con <strong>Tempestivo</strong> gestiamo noi tutta la burocrazia. Ecco cosa devi sapere per il 2026.</p>
    <h2>🎯 Le Agevolazioni Principali</h2>
    <ul>
        <li><strong>Bonus Ristrutturazione 50%:</strong> Detrazione IRPEF per interventi di manutenzione straordinaria, restauro e risanamento conservativo.</li>
        <li><strong>Ecobonus 65%:</strong> Per interventi di efficientamento energetico (es. sostituzione infissi, caldaie a condensazione, cappotto termico).</li>
        <li><strong>Bonus Mobili:</strong> Detrazione per l'acquisto di mobili ed elettrodomestici di classe energetica elevata a seguito di ristrutturazione.</li>
        <li><strong>Superbonus Condomini:</strong> Detrazioni elevate per interventi trainanti su parti comuni dei condomini.</li>
    </ul>
    <h2>💰 Come Funziona la Cessione del Credito in Sicilia</h2>
    <p>La <strong>cessione del credito</strong> è il meccanismo che ti permette di ottenere uno <strong>sconto immediato in fattura</strong> fino al 100% dell'importo dei lavori, senza dover aspettare la dichiarazione dei redditi. Ecco come funziona:</p>
    <ol>
        <li><strong>Verifica dei requisiti:</strong> Il nostro team tecnico verifica che il tuo immobile e gli interventi previsti rispettino i requisiti di legge.</li>
        <li><strong>Pratica CILA/SCIA:</strong> Redigiamo e depositiamo in Comune la pratica edilizia necessaria.</li>
        <li><strong>Asseverazione tecnica:</strong> Un tecnico abilitato assevera la conformità degli interventi e calcola il credito d'imposta spettante.</li>
        <li><strong>Comunicazione all'Agenzia delle Entrate:</strong> Trasmettiamo telematicamente la richiesta di cessione del credito.</li>
        <li><strong>Sconto in fattura:</strong> L'impresa (Tempestivo) applica lo sconto direttamente in fattura, anticipando il credito.</li>
        <li><strong>Documentazione finale:</strong> Al termine dei lavori rilasciamo tutta la documentazione per il tuo commercialista.</li>
    </ol>
    <h2>📋 Come Ottenerli con Tempestivo</h2>
    <p>Non devi preoccuparti di commercialisti o pratiche ENEA. Il nostro team tecnico interno si occupa di:</p>
    <ul>
        <li>Redazione della pratica CILA o SCIA in Comune.</li>
        <li>Asseverazione tecnica e calcolo delle detrazioni.</li>
        <li>Invio telematico all'ENEA per l'Ecobonus.</li>
        <li>Gestione della cessione del credito con banche e istituti finanziari.</li>
        <li>Rilascio della documentazione finale per il tuo commercialista.</li>
    </ul>
    <h2>💶 Tabella Detrazioni 2026</h2>
    <table>
        <tr><th>Bonus</th><th>Percentuale</th><th>Massimale</th><th>Tipologia Intervento</th></tr>
        <tr><td>Bonus Ristrutturazione</td><td>50%</td><td>€96.000</td><td>Manutenzione straordinaria</td></tr>
        <tr><td>Ecobonus</td><td>65%</td><td>€100.000</td><td>Efficientamento energetico</td></tr>
        <tr><td>Bonus Mobili</td><td>50%</td><td>€10.000</td><td>Arredi ed elettrodomestici</td></tr>
        <tr><td>Superbonus Condomini</td><td>70%</td><td>€96.000</td><td>Interventi trainanti condominiali</td></tr>
    </table>
    <h2>❓ Domande Frequenti sui Bonus 2026</h2>
    {self._generate_faq_html(faq_list)}
    <h2>🔗 Approfondimenti e Guide Correlate</h2>
    <ul>
        <li><a href="guida-ristrutturazione-bagno.html">→ Ristrutturazione bagno: costi, tempi e permessi necessari</a></li>
        <li><a href="ristrutturazione-centro-storico.html">→ Ristrutturazione Centro Storico: vincoli e soluzioni</a></li>
        <li><a href="vincolo-paesaggistico-guida.html">→ Vincolo paesaggistico: la guida completa</a></li>
        <li><a href="servizi_castellammare.html">→ Tutti i servizi di Tempestivo a Castellammare del Golfo</a></li>
    </ul>
    <div style="text-align:center; margin: 30px 0;">
        <a href="tel:{Config.TELEFONO_RAW}" style="background:#28a745; color:white; padding:15px 30px; text-decoration:none; border-radius:5px; font-weight:bold; font-size:1.2em;">
            📞 CHIAMA ORA: {Config.TELEFONO}
        </a>
    </div>
</article>
<aside>
    <h3>La Nostra Missione</h3>
    <p>Tempestivo è l'unico General Contractor in Sicilia che gestisce direttamente i lavori e le pratiche per i bonus. Nessun intermediario, nessun rischio: lavori a regola d'arte e prezzi onesti garantiti.</p>
</aside>
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
        meta_desc = "Guida completa alla ristrutturazione bagno: costi, tempi, permessi CILA/SCIA. Prezzi trasparenti da €3.500. Tempestivo Castellammare."
        
        ImageGenerator.create_image("og-guida-ristrutturazione-bagno.jpg", title)
        
        faq_list = [
            {"domanda": "Quanto costa ristrutturare un bagno a Castellammare del Golfo?", "risposta": "La ristrutturazione bagno parte da €3.500 per interventi base, fino a €8.000 per bagni completi con finiture di pregio. Il prezzo include demolizioni, nuovi impianti, impermeabilizzazione, posa piastrelle e installazione sanitari."},
            {"domanda": "Servono permessi per ristrutturare il bagno?", "risposta": "Sì, per la ristrutturazione bagno è obbligatoria la CILA (Comunicazione Inizio Lavori Asseverata) se si modificano gli impianti. Tempestivo gestisce tutta la pratica in 48h, inclusa la dichiarazione di conformità impianti DM 37/08."},
            {"domanda": "Quanto tempo serve per ristrutturare un bagno?", "risposta": "Con Tempestivo garantiamo 7 giorni lavorativi per una ristrutturazione bagno completa chiavi in mano. I tempi sono contrattualizzati: se ritardiamo, paghiamo una penale."},
            {"domanda": "Posso usufruire dei bonus fiscali per il bagno?", "risposta": "Sì, la ristrutturazione bagno rientra nel Bonus Ristrutturazione 50% con detrazione fino a €96.000. Con Tempestivo gestiamo noi la pratica per la cessione del credito."}
        ]
        html = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{meta_desc}">
    <meta name="keywords" content="ristrutturazione bagno castellammare, costi bagno, permessi cila, tempestivo">
    <meta name="robots" content="index, follow">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{meta_desc}">
    <meta property="og:type" content="website">
    <meta property="og:image" content="{Config.URL_BASE}/images/og-guida-ristrutturazione-bagno.jpg">
    <meta property="og:locale" content="it_IT">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{meta_desc}">
    <meta name="twitter:image" content="{Config.URL_BASE}/images/og-guida-ristrutturazione-bagno.jpg">
    <meta name="geo.region" content="{Config.GEO_REGION}">
    <meta name="geo.placename" content="{Config.GEO_PLACENAME}">
    <meta name="geo.position" content="{Config.GEO_POSITION}">
    <meta name="ICBM" content="{Config.ICBM}">
    <link rel="canonical" href="{Config.URL_BASE}/{filename}">
    <link rel="stylesheet" href="{Config.CSS_PATH}">
    <script type="application/ld+json">
{json.dumps(self._generate_schema_pillar("Ristrutturazione Bagno Guida", faq_list), indent=2, ensure_ascii=False)}
    </script>
</head>
<body>
{self.template.header}
<main>
<article>
    <h1>Ristrutturazione Bagno: Costi, Tempi e Permessi Necessari</h1>
    <p>Rifare il bagno è uno degli interventi più richiesti. Ma quali permessi servono e quanto costa realmente a Castellammare del Golfo? Te lo spieghiamo in questa guida completa.</p>
    <h2>📋 Quali Permessi Servono?</h2>
    <ul>
        <li><strong>Edilizia Libera:</strong> Se mantieni invariati gli impianti e le tramezzature (es. semplice sostituzione sanitari).</li>
        <li><strong>CILA (Comunicazione Inizio Lavori Asseverata):</strong> Obbligatoria se rifai gli impianti idraulici o sposti i tramezzi. Tempestivo la gestisce in 48h.</li>
        <li><strong>SCIA:</strong> Necessaria solo per interventi straordinari pesanti o in edifici vincolati.</li>
    </ul>
    <h2>💶 Costi Medi in Sicilia (2026)</h2>
    <table>
        <tr><th>Intervento</th><th>Costo Stimato</th><th>Durata</th></tr>
        <tr><td>Rifacimento completo bagno</td><td>Da €3.500 a €8.000</td><td>7 giorni</td></tr>
        <tr><td>Solo sostituzione sanitari</td><td>Da €800</td><td>1-2 giorni</td></tr>
        <tr><td>Rifacimento impianto idraulico</td><td>€1.200 - €2.000</td><td>2-3 giorni</td></tr>
        <tr><td>Posa piastrelle (al mq)</td><td>€25 - €40</td><td>1-2 giorni</td></tr>
        <tr><td>Box doccia su misura</td><td>Da €600</td><td>1 giorno</td></tr>
    </table>
    <h2>⏱️ I Nostri Tempi Certi</h2>
    <p>Con la formula <strong>Chiavi in Mano</strong>, garantiamo la consegna in <strong>7 giorni lavorativi</strong>. Dalla demolizione alla pulizia finale, con un unico Project Manager.</p>
    <h2>🔧 Le Fasi della Ristrutturazione</h2>
    <ol>
        <li><strong>Demolizione:</strong> Rimozione vecchi elementi e smaltimento macerie.</li>
        <li><strong>Nuovi impianti:</strong> Rifacimento idraulico ed elettrico a norma DM 37/08.</li>
        <li><strong>Impermeabilizzazione:</strong> Fondamentale per evitare infiltrazioni.</li>
        <li><strong>Posa piastrelle:</strong> Rivestimenti e pavimento con materiali di qualità.</li>
        <li><strong>Installazione sanitari:</strong> WC, lavabo, box doccia, rubinetteria.</li>
        <li><strong>Collaudo finale:</strong> Verifica impianti e pulizia.</li>
    </ol>
    <h2>❓ Domande Frequenti</h2>
    {self._generate_faq_html(faq_list)}
    <h2>🔗 Approfondimenti Correlati</h2>
    <ul>
        <li><a href="bonus-ristrutturazioni-sicilia.html">→ Bonus Ristrutturazioni Sicilia 2026</a></li>
        <li><a href="ristrutturazione-bagno-castellammare-centro.html">→ Ristrutturazione Bagno a Castellammare Centro</a></li>
        <li><a href="ristrutturazione-bagno-scopello.html">→ Ristrutturazione Bagno a Scopello</a></li>
        <li><a href="servizi_castellammare.html">→ Tutti i servizi a Castellammare del Golfo</a></li>
    </ul>
    <div style="text-align:center; margin: 30px 0;">
        <a href="tel:{Config.TELEFONO_RAW}" style="background:#28a745; color:white; padding:15px 30px; text-decoration:none; border-radius:5px; font-weight:bold; font-size:1.2em;">
            📞 CHIAMA ORA per Preventivo Bagno: {Config.TELEFONO}
        </a>
    </div>
</article>
<aside>
    <h3>Perché Scegliere Tempestivo</h3>
    <p>Siamo l'unico General Contractor che garantisce tempi contrattualizzati per la ristrutturazione bagno a Castellammare del Golfo. Se ritardiamo, paghiamo noi. Prezzi onesti e lavori a regola d'arte.</p>
</aside>
</main>
{self.template.footer}
</body>
</html>"""
        filepath.write_text(html, encoding='utf-8')
        print(f"     ✅ Creato/Aggiornato: {filename}")
        return filepath

    def _generate_centro_storico(self) -> Path:
        filename = "ristrutturazione-centro-storico.html"
        filepath = Config.BASE_DIR / filename
        title = "Ristrutturazione Centro Storico Castellammare: Vincoli e Soluzioni | Tempestivo"
        meta_desc = "Ristrutturazione nel Centro Storico di Castellammare del Golfo: gestione vincoli Soprintendenza, edifici storici. Tempestivo esperti in restauri."
        
        ImageGenerator.create_image("og-ristrutturazione-centro-storico.jpg", title)
        
        faq_list = [
            {"domanda": "Quali vincoli ci sono per ristrutturare nel Centro Storico di Castellammare del Golfo?", "risposta": "Il centro storico e le zone di pregio sono soggetti a vincoli della Soprintendenza Beni Culturali e Ambientali. Ogni intervento deve rispettare l'architettura originale, i materiali tradizionali e le colorazioni tipiche."},
            {"domanda": "Quanto tempo serve per ottenere i permessi della Soprintendenza?", "risposta": "I tempi medi sono di 60-90 giorni. Noi presentiamo la documentazione con mesi di anticipo e seguiamo l'iter personalmente, riducendo i tempi di attesa rispetto alla media."},
            {"domanda": "Come gestite il trasporto materiali nei vicoli stretti?", "risposta": "Utilizziamo mezzi compatti e sistemi di sollevamento specifici per centri storici. Proteggiamo tutte le aree comuni e rispettiamo le disposizioni locali per zero disagi."}
        ]
        html = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{meta_desc}">
    <meta name="keywords" content="ristrutturazione centro storico castellammare del golfo, vincoli soprintendenza, tempestivo">
    <meta name="robots" content="index, follow">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{meta_desc}">
    <meta property="og:type" content="website">
    <meta property="og:image" content="{Config.URL_BASE}/images/og-ristrutturazione-centro-storico.jpg">
    <meta property="og:locale" content="it_IT">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{meta_desc}">
    <meta name="twitter:image" content="{Config.URL_BASE}/images/og-ristrutturazione-centro-storico.jpg">
    <meta name="geo.region" content="{Config.GEO_REGION}">
    <meta name="geo.placename" content="{Config.GEO_PLACENAME}">
    <meta name="geo.position" content="{Config.GEO_POSITION}">
    <meta name="ICBM" content="{Config.ICBM}">
    <link rel="canonical" href="{Config.URL_BASE}/{filename}">
    <link rel="stylesheet" href="{Config.CSS_PATH}">
    <script type="application/ld+json">
{json.dumps(self._generate_schema_pillar("Ristrutturazione Centro Storico", faq_list), indent=2, ensure_ascii=False)}
    </script>
</head>
<body>
{self.template.header}
<main>
<article>
    <h1>Ristrutturazione Centro Storico Castellammare del Golfo: Vincoli e Soluzioni</h1>
    <p>Ristrutturare nel <strong>Centro Storico di Castellammare del Golfo</strong> significa lavorare in un contesto di grande pregio architettonico e paesaggistico. Edifici tradizionali e vicoli caratteristici richiedono competenze specifiche che noi possediamo.</p>
    <h2>🏛️ I Vincoli della Soprintendenza</h2>
    <p>Le aree storiche sono soggette a <strong>vincoli della Soprintendenza</strong>. Ogni intervento deve:</p>
    <ul>
        <li>Rispettare l'architettura originaria e le tipologie costruttive locali.</li>
        <li>Conservare elementi di pregio architettonico e facciate storiche.</li>
        <li>Utilizzare materiali compatibili con le murature esistenti.</li>
        <li>Attenersi alle normative paesaggistiche della provincia di Trapani.</li>
    </ul>
    <h2>⚠️ Le Sfide Specifiche</h2>
    <ul>
        <li><strong>Vicoli stretti:</strong> Comicano la logistica e il trasporto dei materiali edili.</li>
        <li><strong>Impianti obsoleti:</strong> Da adeguare alle normative vigenti (DM 37/08) preservando l'estetica.</li>
        <li><strong>Coordinamento turistico:</strong> Gestione delle tempistiche in base alla stagione turistica e alle ordinanze comunali.</li>
    </ul>
    <h2>💶 Costi Medi per Ristrutturazioni nel Centro Storico</h2>
    <table>
        <tr><th>Intervento</th><th>Costo Stimato</th><th>Note</th></tr>
        <tr><td>Ristrutturazione bagno completa</td><td>Da €4.500 a €10.000</td><td>Inclusi permessi Soprintendenza</td></tr>
        <tr><td>Ristrutturazione cucina</td><td>Da €6.500 a €16.000</td><td>Conservazione elementi storici</td></tr>
        <tr><td>Ristrutturazione completa appartamento</td><td>Da €22.000 a €65.000</td><td>Restauro conservativo incluso</td></tr>
    </table>
    <h2>❓ Domande Frequenti</h2>
    {self._generate_faq_html(faq_list)}
    <h2>🔗 Approfondimenti Correlati</h2>
    <ul>
        <li><a href="bonus-ristrutturazioni-sicilia.html">→ Bonus Ristrutturazioni Sicilia 2026</a></li>
        <li><a href="vincolo-paesaggistico-guida.html">→ Vincolo paesaggistico: la guida completa</a></li>
        <li><a href="servizi_castellammare.html">→ Tutti i servizi a Castellammare del Golfo</a></li>
    </ul>
    <div style="text-align:center; margin: 30px 0;">
        <a href="tel:{Config.TELEFONO_RAW}" style="background:#28a745; color:white; padding:15px 30px; text-decoration:none; border-radius:5px; font-weight:bold; font-size:1.2em;">
            📞 CHIAMA ORA per Consulenza Centro Storico: {Config.TELEFONO}
        </a>
    </div>
</article>
<aside>
    <h3>La Nostra Esperienza nel Centro Storico</h3>
    <p>Abbiamo ristrutturato numerosi immobili vincolati a Castellammare del Golfo e Scopello. Conosciamo le procedure per ottenere l'approvazione al primo colpo. Prezzi onesti e lavori a regola d'arte.</p>
</aside>
</main>
{self.template.footer}
</body>
</html>"""
        filepath.write_text(html, encoding='utf-8')
        print(f"     ✅ Creato/Aggiornato: {filename}")
        return filepath

    def _generate_vincolo_guida(self) -> Path:
        filename = "vincolo-paesaggistico-guida.html"
        filepath = Config.BASE_DIR / filename
        title = "Vincolo Paesaggistico: Guida Completa alle Ristrutturazioni | Tempestivo"
        meta_desc = "Guida completa al vincolo paesaggistico a Castellammare e Scopello: autorizzazioni, tempi, costi. Tempestivo esperti in vincoli paesaggistici."
        
        ImageGenerator.create_image("og-vincolo-paesaggistico-guida.jpg", title)
        
        faq_list = [
            {"domanda": "Cos'è l'autorizzazione paesaggistica?", "risposta": "L'autorizzazione paesaggistica è un atto obbligatorio rilasciato dalla Soprintendenza o dagli enti competenti. Serve per qualsiasi intervento che modifichi l'aspetto esteriore dell'immobile in aree tutelate (coste, Scopello, riserve naturali)."},
            {"domanda": "Quanto tempo serve per ottenere l'autorizzazione?", "risposta": "I tempi medi sono di 30-90 giorni. Noi presentiamo la pratica con anticipo e seguiamo l'iter personalmente per minimizzare i tempi d'attesa."},
            {"domanda": "Cuáles materiali sono compatibili con il vincolo?", "risposta": "Materiali tradizionali e locali: infissi in legno o alluminio effetto legno certificato, intonaci tradizionali a calce, coperture in coppi siciliani."}
        ]
        html = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{meta_desc}">
    <meta name="keywords" content="vincolo paesaggistico castellammare, scopello, autorizzazione soprintendenza, tempestivo">
    <meta name="robots" content="index, follow">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{meta_desc}">
    <meta property="og:type" content="website">
    <meta property="og:image" content="{Config.URL_BASE}/images/og-vincolo-paesaggistico-guida.jpg">
    <meta property="og:locale" content="it_IT">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{meta_desc}">
    <meta name="twitter:image" content="{Config.URL_BASE}/images/og-vincolo-paesaggistico-guida.jpg">
    <meta name="geo.region" content="{Config.GEO_REGION}">
    <meta name="geo.placename" content="{Config.GEO_PLACENAME}">
    <meta name="geo.position" content="{Config.GEO_POSITION}">
    <meta name="ICBM" content="{Config.ICBM}">
    <link rel="canonical" href="{Config.URL_BASE}/{filename}">
    <link rel="stylesheet" href="{Config.CSS_PATH}">
    <script type="application/ld+json">
{json.dumps(self._generate_schema_pillar("Vincolo Paesaggistico Guida", faq_list), indent=2, ensure_ascii=False)}
    </script>
</head>
<body>
{self.template.header}
<main>
<article>
    <h1>Ristrutturazione in Vincolo Paesaggistico: La Guida Completa</h1>
    <p>Operare in zone vincolate e di straordinario pregio naturalistico come <strong>Scopello, Guidaloca e la costa di Castellammare del Golfo</strong> richiede il rispetto di severe normative. Ecco come muoversi senza blocchi del cantiere.</p>
    <h2>📋 Cos'è l'Autorizzazione Paesaggistica?</h2>
    <p>È un atto obbligatorio rilasciato per qualsiasi intervento che modifichi l'aspetto esteriore di fabbricati ricadenti in aree sottoposte a tutela paesaggistica.</p>
    <h2>⚠️ Le Criticità che Gestiamo Noi</h2>
    <ul>
        <li><strong>Tempi della Soprintendenza:</strong> Possono variare da 30 a 90 giorni. Tempestivo gestisce l'iter tecnico preventivo.</li>
        <li><strong>Materiali Compatibili:</strong> Utilizzo di finiture e infissi conformi alle prescrizioni paesaggistiche locali.</li>
        <li><strong>Tutela Ambientale:</strong> Attenzione massima agli scarichi, alla gestione dei rifiuti e al rispetto della flora locale.</li>
    </ul>
    <h2>✅ La Nostra Esperienza nei Vincoli</h2>
    <p>Conosciamo a fondo le peculiarità normative del territorio di Castellammare del Golfo e Trapani, garantendo un servizio chiavi in mano sicuro e a norma di legge.</p>
    <h2>❓ Domande Frequenti</h2>
    {self._generate_faq_html(faq_list)}
    <h2>🔗 Approfondimenti Correlati</h2>
    <ul>
        <li><a href="bonus-ristrutturazioni-sicilia.html">→ Bonus Ristrutturazioni Sicilia 2026</a></li>
        <li><a href="ristrutturazione-centro-storico.html">→ Ristrutturazione Centro Storico</a></li>
        <li><a href="servizi_castellammare.html">→ Tutti i servizi a Castellammare del Golfo</a></li>
    </ul>
    <div style="text-align:center; margin: 30px 0;">
        <a href="tel:{Config.TELEFONO_RAW}" style="background:#28a745; color:white; padding:15px 30px; text-decoration:none; border-radius:5px; font-weight:bold; font-size:1.2em;">
            📞 CHIAMA ORA per Consulenza Vincoli: {Config.TELEFONO}
        </a>
    </div>
</article>
<aside>
    <h3>Perché Scegliere Tempestivo per i Vincoli</h3>
    <p>Siamo il General Contractor con un ufficio tecnico interno specializzato in pratiche paesaggistiche e urbanistiche. Nessuna sorpresa, nessun blocco del cantiere. Prezzi onesti e lavori a regola d'arte.</p>
</aside>
</main>
{self.template.footer}
</body>
</html>"""
        filepath.write_text(html, encoding='utf-8')
        print(f"     ✅ Creato/Aggiornato: {filename}")
        return filepath

    def _generate_index_castellammare(self) -> Path:
        filename = "servizi_castellammare.html"
        filepath = Config.BASE_DIR / filename
        title = "Servizi di Ristrutturazione a Castellammare del Golfo | Tempestivo"
        meta_desc = "Tempestivo: ristrutturazioni chiavi in mano a Castellammare del Golfo. Bagno, cucina, completa, impianti, imbiancatura. Preventivo gratuito."
        
        ImageGenerator.create_image("og-servizi_castellammare.jpg", title)
        
        quartieri_html = ""
        for q in self.quartieri:
            slug = q['slug']
            nome = q.get('nome_display', q.get('nome', slug.title()))
            quartieri_html += f'<li><a href="ristrutturazione-bagno-{slug}.html">→ Ristrutturazione Bagno a {nome}</a></li>\n'
        servizi_html = ""
        for s in self.servizi:
            slug = s['slug']
            nome = s['nome']
            servizi_html += f'<li><a href="{slug}-castellammare-centro.html">→ {nome} a Castellammare del Golfo</a></li>\n'
        html = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{meta_desc}">
    <meta name="keywords" content="ristrutturazioni castellammare del golfo, tempestivo, bagno, cucina, completa, imbiancatura">
    <meta name="robots" content="index, follow">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{meta_desc}">
    <meta property="og:type" content="website">
    <meta property="og:image" content="{Config.URL_BASE}/images/og-servizi_castellammare.jpg">
    <meta property="og:locale" content="it_IT">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{meta_desc}">
    <meta name="twitter:image" content="{Config.URL_BASE}/images/og-servizi_castellammare.jpg">
    <meta name="geo.region" content="{Config.GEO_REGION}">
    <meta name="geo.placename" content="{Config.GEO_PLACENAME}">
    <meta name="geo.position" content="{Config.GEO_POSITION}">
    <meta name="ICBM" content="{Config.ICBM}">
    <link rel="canonical" href="{Config.URL_BASE}/{filename}">
    <link rel="stylesheet" href="{Config.CSS_PATH}">
    <script type="application/ld+json">
{json.dumps(self._generate_schema_pillar("Servizi Castellammare del Golfo", []), indent=2, ensure_ascii=False)}
    </script>
</head>
<body>
{self.template.header}
<main>
<article>
    <h1>Servizi di Ristrutturazione e Manutenzione a Castellammare del Golfo</h1>
    <p><strong>Tempestivo</strong> è il General Contractor di riferimento per le ristrutturazioni e i servizi di pronto intervento a Castellammare del Golfo e zone limitrofe come Scopello e Calatubo. Unico referente, tempi certi, prezzi onesti.</p>
    <h2>🛠️ I Nostri Servizi</h2>
    <ul>
        {servizi_html}
    </ul>
    <h2>📍 Zone Coperti a Castellammare del Golfo</h2>
    <ul>
        {quartieri_html}
    </ul>
    <h2>💶 Prezzi Trasparenti</h2>
    <table>
        <tr><th>Servizio</th><th>Prezzo</th><th>Durata</th></tr>
        <tr><td>Ristrutturazione Bagno</td><td>Da €3.500 a €8.000</td><td>7 giorni</td></tr>
        <tr><td>Ristrutturazione Cucina</td><td>Da €5.000 a €12.000</td><td>15 giorni</td></tr>
        <tr><td>Ristrutturazione Completa</td><td>Da €15.000 a €50.000</td><td>45-90 giorni</td></tr>
        <tr><td>Imbiancatura</td><td>Da €8 a €15/mq</td><td>2 giorni</td></tr>
    </table>
    <h2>🔗 Guide e Approfondimenti</h2>
    <ul>
        <li><a href="bonus-ristrutturazioni-sicilia.html">→ Bonus Ristrutturazioni Sicilia 2026</a></li>
        <li><a href="guida-ristrutturazione-bagno.html">→ Guida Ristrutturazione Bagno</a></li>
        <li><a href="ristrutturazione-centro-storico.html">→ Ristrutturazione Centro Storico</a></li>
        <li><a href="vincolo-paesaggistico-guida.html">→ Vincolo Paesaggistico: la guida</a></li>
    </ul>
    <div style="text-align:center; margin: 30px 0;">
        <a href="tel:{Config.TELEFONO_RAW}" style="background:#28a745; color:white; padding:15px 30px; text-decoration:none; border-radius:5px; font-weight:bold; font-size:1.2em;">
            📞 CHIAMA ORA per Preventivo Castellammare: {Config.TELEFONO}
        </a>
    </div>
</article>
<aside>
    <h3>La Nostra Missione a Castellammare del Golfo</h3>
    <p>Operare a Castellammare del Golfo significa gestire un territorio unico, che spazia dal borgo storico marinaro e le caratteristiche vie del centro fino alle splendide ville e case vacanza immerse nella natura di Scopello e Calatubo. La nostra missione è offrire un interlocutore unico e qualificato per interventi edili, impiantistici e di pronto intervento, garantendo massima affidabilità e velocità.</p>
</aside>
</main>
{self.template.footer}
</body>
</html>"""
        filepath.write_text(html, encoding='utf-8')
        print(f"     ✅ Creato/Aggiornato: {filename}")
        return filepath

    def _generate_faq_html(self, faq_list: List[Dict]) -> str:
        html = ""
        for faq in faq_list:
            html += f'<h3>{faq["domanda"]}</h3>\n<p>{faq["risposta"]}</p>\n'
        return html

    def _generate_schema_bonus(self, faq_list: List[Dict]) -> Dict:
        return {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": ["HomeAndConstructionBusiness", "ProfessionalService", "LocalBusiness"],
                    "name": f"{Config.AZIENDA} - Bonus Ristrutturazioni Sicilia",
                    "telephone": Config.TELEFONO,
                    "address": {"@type": "PostalAddress", "streetAddress": "Contrada Incastrona", "addressLocality": "Partinico", "addressRegion": "PA", "postalCode": "90047", "addressCountry": "IT"},
                    "areaServed": {"@type": "Place", "name": "Sicilia"}
                },
                {
                    "@type": "FAQPage",
                    "mainEntity": [
                        {"@type": "Question", "name": faq.get('domanda', ''), "acceptedAnswer": {"@type": "Answer", "text": faq.get('risposta', '')}}
                        for faq in faq_list
                    ]
                }
            ]
        }

    def _generate_schema_pillar(self, title: str, faq_list: List[Dict]) -> Dict:
        schema = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": ["HomeAndConstructionBusiness", "ProfessionalService", "LocalBusiness"],
                    "name": f"{Config.AZIENDA} - {title}",
                    "telephone": Config.TELEFONO,
                    "address": {"@type": "PostalAddress", "streetAddress": "Contrada Incastrona", "addressLocality": "Partinico", "addressRegion": "PA", "postalCode": "90047", "addressCountry": "IT"},
                    "areaServed": {"@type": "Place", "name": "Castellammare del Golfo"}
                },
                {
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {"@type": "ListItem", "position": 1, "name": "Home", "item": Config.URL_BASE},
                        {"@type": "ListItem", "position": 2, "name": title, "item": f"{Config.URL_BASE}/{title.lower().replace(' ', '-')}"}
                    ]
                }
            ]
        }
        if faq_list:
            schema["@graph"].append({
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": faq.get('domanda', ''), "acceptedAnswer": {"@type": "Answer", "text": faq.get('risposta', '')}}
                    for faq in faq_list
                ]
            })
        return schema

# =============================================================================
# 6. SEO AUDITOR
# =============================================================================
class SEOAuditor:
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.content = filepath.read_text(encoding='utf-8')
        self.soup = BeautifulSoup(self.content, 'html.parser')
        self.issues = []
        self.successes = []
        self.score = 100

    def audit(self) -> Dict:
        self._check_meta_tags()
        self._check_open_graph()
        self._check_schema_org()
        self._check_heading_structure()
        self._check_price_table()
        self._check_reviews()
        self._check_faq()
        self._check_internal_links()
        self._check_cta()
        self._check_keyword_density()
        self._check_local_seo()
        self._check_content_uniqueness()
        self._check_ai_overviews()
        self._check_eat()
        self._check_silos()
        self._check_link_validation()
        self._check_quarter_specificity()
        return {
            'file': self.filepath.name,
            'score': max(0, self.score),
            'issues': self.issues,
            'successes': self.successes,
            'timestamp': datetime.now().isoformat()
        }

    def _deduct(self, pts: int, msg: str):
        self.score -= pts
        self.issues.append(f"[-{pts}] {msg}")

    def _success(self, msg: str):
        self.successes.append(f"[✓] {msg}")

    def _check_meta_tags(self):
        title_tag = self.soup.find('title')
        if not title_tag:
            self._deduct(30, "Title tag ASSENTE")
        else:
            title_text = title_tag.get_text(strip=True)
            if len(title_text) > 75: self._deduct(10, f"Title troppo lungo ({len(title_text)} char)")
            if 'tempestivo' not in title_text.lower(): self._deduct(10, "Brand 'Tempestivo' mancante nel Title")
            else: self._success("Brand presente nel Title")
        meta_desc = self.soup.find('meta', attrs={'name': 'description'})
        if not meta_desc: self._deduct(25, "Meta description ASSENTE")
        else:
            desc = meta_desc.get('content', '')
            if len(desc) > 175: self._deduct(10, f"Meta description troppo lunga ({len(desc)} char)")
            elif len(desc) < 100: self._deduct(5, f"Meta description troppo corta ({len(desc)} char)")
            else: self._success(f"Meta description ottimale ({len(desc)} char)")
            
        robots_tags = self.soup.find_all('meta', attrs={'name': 'robots'})
        if len(robots_tags) > 1:
            self._deduct(10, f"Tag meta robots DUPLICATO ({len(robots_tags)} trovati)")
        elif not robots_tags:
            self._deduct(5, "Meta robots ASSENTE")
            
        if not self.soup.find('link', attrs={'rel': 'canonical'}): self._deduct(15, "Canonical tag ASSENTE")
        else: self._success("Canonical tag presente")

    def _check_open_graph(self):
        og_tags = ['og:title', 'og:description', 'og:type', 'og:image']
        missing = [tag for tag in og_tags if not self.soup.find('meta', attrs={'property': tag})]
        if len(missing) > 2: self._deduct(15, f"Open Graph mancanti: {', '.join(missing)}")
        elif missing: self._deduct(10, f"Open Graph parziali: {', '.join(missing)}")
        else: self._success("Tutti gli Open Graph presenti")

    def _check_schema_org(self):
        scripts = self.soup.find_all('script', attrs={'type': 'application/ld+json'})
        if not scripts: self._deduct(30, "Schema.org JSON-LD ASSENTE"); return
        types = set()
        for s in scripts:
            try:
                data = json.loads(s.string)
                schemas = data.get('@graph', [data]) if isinstance(data, dict) else [data]
                for item in schemas:
                    t = item.get('@type', [])
                    types.update(t if isinstance(t, list) else [t])
            except: pass
        required = ['LocalBusiness', 'Service', 'FAQPage', 'BreadcrumbList']
        missing = [r for r in required if r not in types]
        if missing: self._deduct(20, f"Schema mancanti: {', '.join(missing)}")
        else: self._success("Schema.org completo")

    def _check_heading_structure(self):
        h1 = self.soup.find_all('h1')
        if not h1: self._deduct(30, "H1 ASSENTE")
        elif len(h1) > 1: self._deduct(10, f"Multipli H1 ({len(h1)})")
        else: self._success(f"H1 presente: '{h1[0].get_text(strip=True)[:50]}'")
        
        bad_h2 = [h for h in self.soup.find_all('h2') if h.find('p')]
        if bad_h2:
            self._deduct(20, "Struttura HTML non valida: Tag <p> annidato dentro <h2>")
        
        if not self.soup.find_all('h2'): self._deduct(10, "Nessun H2 trovato")

    def _check_price_table(self):
        tables = self.soup.find_all('table')
        price_tables = [t for t in tables if '€' in t.get_text()]
        if not price_tables: self._deduct(40, "Nessuna tabella prezzi trovata")
        else:
            rows = sum(1 for t in price_tables for r in t.find_all('tr') if '€' in r.get_text())
            if rows < 2: self._deduct(15, f"Tabella prezzi povera ({rows} voci)")
            else: self._success(f"Tabella prezzi dettagliata ({rows} voci)")

    def _check_reviews(self):
        reviews = self.soup.find_all('blockquote')
        valid_reviews = [r for r in reviews if r.get_text(strip=True)]
        if not valid_reviews: self._deduct(30, "Sezione recensioni ASSENTE o VUOTA")
        elif len(valid_reviews) < 2: self._deduct(10, f"Poche recensioni ({len(valid_reviews)})")
        else: self._success(f"Recensioni presenti ({len(valid_reviews)})")

    def _check_faq(self):
        faq_h2 = self.soup.find_all('h2', string=re.compile('domande frequenti', re.IGNORECASE))
        faq_items = self.soup.find_all('h3')
        if not faq_h2: self._deduct(15, "Sezione FAQ non trovata")
        elif len(faq_items) < 3: self._deduct(10, f"Poche FAQ ({len(faq_items)})")
        else: self._success(f"FAQ presenti ({len(faq_items)} domande)")

    def _check_internal_links(self):
        empty_lists = [ul for ul in self.soup.find_all('ul') if not ul.find_all('li') and ul.find_previous('h2', string=re.compile('servizi correlati', re.IGNORECASE))]
        if empty_lists:
            self._deduct(15, "Trovata intestazione 'Servizi Correlati' con lista <ul> vuota")

        internal = [a for a in self.soup.find_all('a', href=True) if '.html' in a['href']]
        if len(internal) < 3: self._deduct(10, f"Pochi link interni ({len(internal)})")
        else: self._success(f"Link interni presenti ({len(internal)})")

    def _check_cta(self):
        phone_links = self.soup.find_all('a', href=re.compile(r'tel:', re.IGNORECASE))
        if not phone_links: self._deduct(25, "Nessun link telefonico")
        else: 
            for a in phone_links:
                if 'chiav:' in a.get_text().lower():
                    self._deduct(15, "Testo CTA finale troncato ('Chiav:')")
            self._success(f"CTA presenti ({len(phone_links)})")

    def _check_keyword_density(self):
        main = self.soup.find('main') or self.soup.find('article')
        if main:
            first_p = main.find('p')
            if first_p and len(first_p.get_text(strip=True)) < 30: self._deduct(5, "Primo paragrafo troppo corto")

    def _check_local_seo(self):
        text = self.soup.get_text().lower()
        if 'castellammare' not in text and 'sicilia' not in text: self._deduct(15, "Riferimento locale non trovato")
        else: self._success("Riferimento geografico locale presente")

    def _check_content_uniqueness(self):
        main = self.soup.find('main') or self.soup.find('article')
        if main:
            words = len(main.get_text().split())
            if words < 300: self._deduct(20, f"Contenuto breve ({words} parole)")
            else: self._success(f"Contenuto ben strutturato ({words} parole)")

    def _check_ai_overviews(self):
        lists = self.soup.find_all(['ul', 'ol'])
        tables = self.soup.find_all('table')
        if not lists and not tables: self._deduct(20, "Mancano liste/tabelle per AI Overviews")
        else: self._success("Struttura ottimizzata per AI Overviews")

    def _check_eat(self):
        text = self.soup.get_text().lower()
        if 'tempestivo' not in text: self._deduct(10, "Brand non menzionato nel contenuto")

    def _check_silos(self):
        links = self.soup.find_all('a', href=True)
        related = [l for l in links if 'ristrutturazione' in l['href'] or 'servizi' in l['href'] or 'imbiancatura' in l['href']]
        if len(related) < 2: self._deduct(15, "Struttura silos debole")
        else: self._success("Struttura silos presente")

    def _check_link_validation(self):
        broken = 0
        for a in self.soup.find_all('a', href=True):
            href = a['href']
            if href.endswith('.html') and not href.startswith('http'):
                target = self.filepath.parent / href
                if not target.exists(): broken += 1
        if broken > 0: self._deduct(5 * broken, f"{broken} link interni rotti")
        else: self._success("Tutti i link interni validi")

    def _check_quarter_specificity(self):
        text = self.soup.get_text().lower()
        quarter_keywords = ['castellammare', 'scopello', 'calatubo', 'guidaloca', 'salsedine', 'vincolo', 'soprintendenza']
        found = sum(1 for kw in quarter_keywords if kw in text)
        if found < 1: self._deduct(20, "Contenuto poco specifico per zona")
        else: self._success("Contenuto specifico per zona")

# =============================================================================
# 7. SEO FIXER (SURGEON AUTOMATIC REPAIR)
# =============================================================================
class SEOFixer:
    def __init__(self, template: TemplateManager):
        self.template = template

    def fix(self, filepath: Path):
        content = filepath.read_text(encoding='utf-8')
        
        content = re.sub(
            r'<h2>\s*(.*?)\s*<p>(.*?)</p>\s*(.*?)</h2>',
            r'<h2>\1 \3</h2>\n<p>\2</p>',
            content,
            flags=re.DOTALL | re.IGNORECASE
        )

        soup = BeautifulSoup(content, 'html.parser')

        for bq in soup.find_all('blockquote'):
            if not bq.get_text(strip=True):
                bq.decompose()

        for h2 in soup.find_all('h2'):
            for p in h2.find_all('p'):
                p.unwrap()

        robots_tags = soup.find_all('meta', attrs={'name': 'robots'})
        if len(robots_tags) > 1:
            for tag in robots_tags[1:]:
                tag.decompose()
                
        content = str(soup)

        content = content.replace("Da Da ", "Da ")
        content = content.replace("da Da ", "da ")
        content = content.replace("a partire da Da ", "a partire da ")
        content = content.replace("Chiav: +39", "Chiavi in Mano: +39")
        content = content.replace("Chiav:", "Chiavi in Mano")

        content = re.sub(r'<h2>Servizi Correlati</h2>\s*<ul>\s*</ul>', '', content, flags=re.IGNORECASE)

        soup = BeautifulSoup(content, 'html.parser')
        content = self._sync_header_footer(content)
        content = self._fix_meta_tags(content, soup, filepath)
        content = self._inject_schema(content, soup, filepath)
        content = self._inject_cta_and_silos(content, soup, filepath)
        
        filepath.write_text(content, encoding='utf-8')

    def _sync_header_footer(self, content: str) -> str:
        content = re.sub(r'<header[^>]*>.*?</header>(\s*<nav[^>]*class=["\']sub-nav["\'][^>]*>.*?</nav>)?(\s*<div[^>]*class=["\']page-offset["\'][^>]*></div>)?', self.template.header, content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<footer[^>]*>.*?</footer>', self.template.footer, content, flags=re.DOTALL | re.IGNORECASE)
        return content

    def _fix_meta_tags(self, content: str, soup: BeautifulSoup, filepath: Path) -> str:
        title_tag = soup.find('title')
        title_text = title_tag.get_text(strip=True) if title_tag else filepath.stem
        if title_tag:
            t_text = title_text
            if "2 |" in t_text:
                t_text = t_text.replace("2 |", "2 giorni |")
            title_tag.string = t_text
            
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            meta_desc['content'] = meta_desc['content'].replace("Da Da ", "Da ").replace("a partire da Da ", "a partire da ")
            
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            og_desc['content'] = og_desc['content'].replace("Da Da ", "Da ").replace("a partire da Da ", "a partire da ")
            
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        if not canonical:
            canonical = soup.new_tag('link', attrs={'rel': 'canonical'})
            if soup.head: soup.head.append(canonical)
        canonical['href'] = f'{Config.URL_BASE}/{filepath.name}'

        parts = filepath.stem.split('-')
        slug_servizio = "-".join(parts[:-1]) if len(parts) > 1 else ""
        slug_quartiere = parts[-1] if len(parts) > 1 else ""

        og_img_url = PageGenerator.get_og_image(self, slug_servizio, slug_quartiere, title_text)

        og_img_tag = soup.find('meta', attrs={'property': 'og:image'})
        if og_img_tag:
            og_img_tag['content'] = og_img_url
        else:
            if soup.head:
                new_og = soup.new_tag('meta', attrs={'property': 'og:image', 'content': og_img_url})
                soup.head.append(new_og)

        tw_img_tag = soup.find('meta', attrs={'name': 'twitter:image'})
        if tw_img_tag:
            tw_img_tag['content'] = og_img_url
        else:
            if soup.head:
                new_tw = soup.new_tag('meta', attrs={'name': 'twitter:image', 'content': og_img_url})
                soup.head.append(new_tw)

        return str(soup)

    def _inject_schema(self, content: str, soup: BeautifulSoup, filepath: Path) -> str:
        content = re.sub(r'<script type="application/ld\+json">.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        h1_tag = soup.find('h1')
        h1 = h1_tag.get_text(strip=True) if h1_tag else filepath.stem
        quartiere = filepath.stem.split('-')[-1] if '-' in filepath.stem else 'castellammare'
        faqs = []
        for h3 in soup.find_all('h3'):
            p = h3.find_next_sibling('p')
            if p: faqs.append({"@type": "Question", "name": h3.get_text(strip=True), "acceptedAnswer": {"@type": "Answer", "text": p.get_text(strip=True)}})
        
        parts = filepath.stem.split('-')
        slug_servizio = "-".join(parts[:-1]) if len(parts) > 1 else ""
        slug_quartiere = parts[-1] if len(parts) > 1 else ""
        og_img = PageGenerator.get_og_image(self, slug_servizio, slug_quartiere, h1)

        schema = {
            "@context": "https://schema.org",
            "@graph": [
                {"@type": ["HomeAndConstructionBusiness", "ProfessionalService", "LocalBusiness"], "name": f"{Config.AZIENDA} - {h1}", "image": og_img, "telephone": Config.TELEFONO, "address": {"@type": "PostalAddress", "streetAddress": "Contrada Incastrona", "addressLocality": "Partinico", "addressRegion": "PA", "postalCode": "90047", "addressCountry": "IT"}, "areaServed": {"@type": "City", "name": quartiere.title()}},
                {"@type": "Service", "serviceType": h1, "makesOffer": {"@type": "Offer", "priceSpecification": {"@type": "PriceSpecification", "price": "60.00", "priceCurrency": "EUR", "description": "Costo base uscita e sopralluogo"}}},
                {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": Config.URL_BASE}, {"@type": "ListItem", "position": 2, "name": quartiere.title(), "item": f"{Config.URL_BASE}/{quartiere}"}, {"@type": "ListItem", "position": 3, "name": h1, "item": f"{Config.URL_BASE}/{filepath.name}"}]}
            ]
        }
        if faqs: schema["@graph"].append({"@type": "FAQPage", "mainEntity": faqs})
        schema_json = json.dumps(schema, indent=2, ensure_ascii=False)
        return content.replace('</head>', f'<script type="application/ld+json">\n{schema_json}\n</script>\n</head>')

    def _inject_cta_and_silos(self, content: str, soup: BeautifulSoup, filepath: Path) -> str:
        silo_html = '<h2>Approfondimenti e Guide Correlate</h2><ul>'
        for link in Config.SILO_LINKS: 
            silo_html += f'<li><a href="{link["url"]}">→ {link["text"]}</a></li>'
        silo_html += '</ul>'
        if '</article>' in content and 'Approfondimenti e Guide Correlate' not in content:
            content = content.replace('</article>', f'{silo_html}\n</article>', 1)
        return content

# =============================================================================
# 8. FILE MANAGER
# =============================================================================
class FileManager:
    @staticmethod
    def rename_indexes():
        print("\n🔄 Rinomina index.html -> servizi_[comune].html")
        for folder in Config.BASE_DIR.iterdir():
            if folder.is_dir() and folder.name not in ['backup_suite', 'seo_reports', 'images', '__pycache__']:
                index_file = folder / "index.html"
                if index_file.exists():
                    new_name = folder / f"servizi_{folder.name}.html"
                    index_file.rename(new_name)
                    print(f"   ✅ Rinominato: {index_file.name} -> {new_name.name}")

    @staticmethod
    def verify_quartieri():
        print("\n Verifica coerenza Zone vs File HTML")
        csv_file = Config.BASE_DIR / Config.QUARTIERI_CSV
        if not csv_file.exists():
            print("   ⚠️ quartieri_castellammare.csv non trovato.")
            return
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            expected_slugs = [row['slug'] for row in reader]
        html_files = [f.stem for f in Config.BASE_DIR.glob("*.html")]
        for slug in expected_slugs:
            matches = [h for h in html_files if slug in h]
            if not matches: print(f"   ❌ Zona '{slug}' presente nel CSV ma nessun file HTML corrispondente!")
            else: print(f"   ✅ Zona '{slug}': {len(matches)} file trovati.")

# =============================================================================
# 9. REPORT GENERATOR
# =============================================================================
class ReportGenerator:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(self, results: List[Dict], phase: str) -> Path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.output_dir / f"seo_report_{phase}_{timestamp}.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"TEMPESTIVO SEO REPORT - {phase.upper()}\n")
            f.write(f"Generato il: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write("=" * 80 + "\n\n")
            avg_score = sum(r['score'] for r in results) / len(results) if results else 0
            f.write(f" STATISTICHE GENERALI\n")
            f.write(f"Totale pagine: {len(results)}\n")
            f.write(f"Punteggio medio: {avg_score:.1f}/100\n")
            f.write(f"Pagine ottime (≥90): {sum(1 for r in results if r['score'] >= 90)}\n")
            f.write(f"Pagine da migliorare (70-89): {sum(1 for r in results if 70 <= r['score'] < 90)}\n")
            f.write(f"Pagine critiche (<70): {sum(1 for r in results if r['score'] < 70)}\n\n")
            for result in results:
                f.write("\n" + "=" * 80 + "\n")
                f.write(f"📄 {result['file']} - Punteggio: {result['score']}/100\n")
                f.write("=" * 80 + "\n\n")
                if result['successes']:
                    f.write("✅ PUNTI DI FORZA:\n")
                    for s in result['successes']: f.write(f"   {s}\n")
                if result['issues']:
                    f.write("\n❌ PROBLEMI DA CORREGGERE:\n")
                    for i in result['issues']: f.write(f"   {i}\n")
                f.write("\n💡 GIUDIZIO:\n")
                if result['score'] >= 95: f.write("   🏆 ECCELLENTE - Pagina perfettamente ottimizzata\n")
                elif result['score'] >= 85: f.write("   ✅ OTTIMO - Pochi miglioramenti necessari\n")
                elif result['score'] >= 70: f.write("   ⚠️ SUFFICIENTE - Necessari interventi SEO importanti\n")
                else: f.write("   ❌ CRITICO - Revisione completa necessaria\n")
        return report_path

# =============================================================================
# 10. DYNAMIC INTERNAL LINKER
# =============================================================================
class DynamicInternalLinker:
    def __init__(self, quartieri: List[Dict], servizi: List[Dict]):
        self.quartieri = quartieri
        self.servizi = servizi

    def add_links_to_all_pages(self):
        html_files = list(Config.BASE_DIR.glob("*.html"))
        updated = 0
        for filepath in html_files:
            if filepath.name in ['mondello.html', 'bonus-ristrutturazioni-sicilia.html', 'guida-ristrutturazione-bagno.html', 'ristrutturazione-centro-storico.html', 'vincolo-paesaggistico-guida.html', 'servizi_castellammare.html']:
                continue
            content = filepath.read_text(encoding='utf-8')
            links_html = self._generate_cross_links(filepath.stem)
            
            if links_html:
                if 'Servizi Correlati' in content:
                    content = re.sub(r'<h2>Servizi Correlati</h2>\s*<ul>.*?</ul>', f'<h2>Servizi Correlati</h2>\n<ul>\n{links_html}\n</ul>', content, flags=re.DOTALL)
                else:
                    content = content.replace('</article>', f'<h2>Servizi Correlati</h2>\n<ul>\n{links_html}\n</ul>\n</article>')
                filepath.write_text(content, encoding='utf-8')
                updated += 1
            else:
                content = re.sub(r'<h2>Servizi Correlati</h2>\s*<ul>\s*</ul>', '', content, flags=re.IGNORECASE)
                filepath.write_text(content, encoding='utf-8')
                
        print(f"✅ Aggiornati {updated} file con link incrociati dinamici")

    def _generate_cross_links(self, current_slug: str) -> str:
        links = []
        parts = current_slug.split('-')
        if len(parts) < 2:
            return ""
            
        quartiere = parts[-1]
        servizio = "-".join(parts[:-1])
        
        for s in self.servizi:
            s_slug = s['slug']
            if s_slug != servizio:
                filename = f"{s_slug}-{quartiere}.html"
                filepath = Config.BASE_DIR / filename
                if filepath.exists():
                    links.append(f'<li><a href="{filename}">→ {s["nome"]} a {quartiere.title()}</a></li>')
        count = 0
        for q in self.quartieri:
            q_slug = q['slug']
            if q_slug != quartiere and count < 3:
                filename = f"{servizio}-{q_slug}.html"
                filepath = Config.BASE_DIR / filename
                if filepath.exists():
                    links.append(f'<li><a href="{filename}">→ {servizio.replace("-", " ").title()} a {q["nome"]}</a></li>')
                    count += 1
        pilastro_pages = ['bonus-ristrutturazioni-sicilia.html', 'guida-ristrutturazione-bagno.html', 'servizi_castellammare.html']
        for page in pilastro_pages:
            filepath = Config.BASE_DIR / page
            if filepath.exists():
                links.append(f'<li><a href="{page}">→ {page.replace(".html", "").replace("-", " ").title()}</a></li>')
        return '\n'.join(links)

# =============================================================================
# 11. MAIN CONTROLLER
# =============================================================================
def main():
    parser = argparse.ArgumentParser(description="Tempestivo SEO Master Suite - V 9.2 Enterprise Corrected")
    parser.add_argument('--fase', choices=['generate', 'pillars', 'link', 'audit', 'fix', 'manage', 'all'], default='all', help='Fase da eseguire')
    parser.add_argument('--pagina', help='Esegue su una singola pagina')
    args = parser.parse_args()
    
    print("\n" + "=" * 80)
    print(" TEMPESTIVO SEO MASTER SUITE - V 9.2 (CASTELLAMMARE DEL GOLFO)")
    print("=" * 80)
    print(f"📁 Directory: {Config.BASE_DIR}")
    
    try:
        template = TemplateManager()
    except Exception as e:
        print(f"❌ Errore template: {e}")
        return
    
    fixer = SEOFixer(template)
    report_gen = ReportGenerator(Config.REPORT_DIR)
    
    servizi = []
    quartieri = []
    frasi_uniche = {}
    
    if args.fase in ['generate', 'pillars', 'link', 'all']:
        try:
            servizi_path = Config.BASE_DIR / Config.SERVIZI_CSV
            quartieri_path = Config.BASE_DIR / Config.QUARTIERI_CSV
            frasi_path = Config.BASE_DIR / Config.FRASI_JSON
            if servizi_path.exists():
                servizi = DataLoader.load_servizi(servizi_path)
            if quartieri_path.exists():
                quartieri = DataLoader.load_quartieri(quartieri_path)
            if frasi_path.exists():
                frasi_uniche = DataLoader.load_frasi_uniche(frasi_path)
        except Exception as e:
            print(f"⚠️ Errore caricamento dati: {e}")
    
    if args.pagina:
        html_files = [Config.BASE_DIR / args.pagina]
    else:
        html_files = list(Config.BASE_DIR.glob("*.html"))
    
    if not html_files and args.fase not in ['generate', 'all']:
        print("❌ Nessun file HTML trovato.")
        return
    
    print(f"\n Trovati {len(html_files)} file HTML")
    
    if args.fase in ['generate', 'all']:
        print("\n" + "=" * 80)
        print("🚀 FASE 0: GENERAZIONE PAGINE DA CSV/JSON")
        print("=" * 80)
        if servizi and quartieri and frasi_uniche:
            generator = PageGenerator(template, servizi, quartieri, frasi_uniche)
            print(f"\n📊 Generazione: {len(servizi)} servizi × {len(quartieri)} zone = {len(servizi) * len(quartieri)} pagine")
            generated = generator.generate_all()
            print(f"\n✅ Generate {len(generated)} nuove pagine")
            html_files = list(Config.BASE_DIR.glob("*.html"))
        else:
            print("⚠️ File dati non trovati, salto generazione")
    
    if args.fase in ['pillars', 'all']:
        print("\n" + "=" * 80)
        print("🏛️ FASE 0.5: GENERAZIONE PAGINE PILASTRO")
        print("=" * 80)
        pillar_gen = PillarPageGenerator(template, quartieri, servizi)
        generated = pillar_gen.generate_all()
        print(f"\n✅ Generate {len(generated)} pagine pilastro")
        html_files = list(Config.BASE_DIR.glob("*.html"))
    
    if args.fase in ['link', 'all']:
        print("\n" + "=" * 80)
        print("🔗 FASE 0.7: INTERNAL LINKING DINAMICO")
        print("=" * 80)
        if servizi and quartieri:
            linker = DynamicInternalLinker(quartieri, servizi)
            linker.add_links_to_all_pages()
        else:
            print("⚠️ Dati non caricati, salto internal linking")
    
    if args.fase in ['audit', 'all']:
        print("\n" + "=" * 80)
        print("🔍 FASE 1: AUDIT STRICT (17 Criteri SEO)")
        print("=" * 80)
        audit_results = []
        for f in html_files:
            print(f"   ⏳ Analisi: {f.name}...", end=" ")
            auditor = SEOAuditor(f)
            res = auditor.audit()
            audit_results.append(res)
            status = "✅" if res['score'] >= 90 else "⚠️" if res['score'] >= 70 else "❌"
            print(f"{status} {res['score']}/100")
        report_path = report_gen.generate_report(audit_results, "audit")
        print(f"\n📄 Report audit salvato: {report_path}")
    
    if args.fase in ['fix', 'all']:
        print("\n" + "=" * 80)
        print("🔧 FASE 2: FIX SURGEON (Correzione Automatica)")
        print("=" * 80)
        Config.BACKUP_DIR.mkdir(exist_ok=True)
        for f in html_files:
            backup_path = Config.BACKUP_DIR / f"{f.stem}_backup_{f.suffix}"
            shutil.copy2(f, backup_path)
            print(f"   🔧 Fix: {f.name}...", end=" ")
            try:
                fixer.fix(f)
                print("✅ Corretto")
            except Exception as e:
                print(f"❌ Errore: {e}")
        print(f"\n💾 Backup salvati in: {Config.BACKUP_DIR}")
    
    if args.fase in ['manage', 'all']:
        print("\n" + "=" * 80)
        print("📂 FASE 3: FILE MANAGEMENT")
        print("=" * 80)
        FileManager.rename_indexes()
        FileManager.verify_quartieri()
    
    if args.fase == 'all':
        print("\n" + "=" * 80)
        print("🔍 FASE 4: POST-FIX AUDIT (Verifica Finale)")
        print("=" * 80)
        html_files = list(Config.BASE_DIR.glob("*.html"))
        post_results = []
        for f in html_files:
            print(f"   🔎 Verifica: {f.name}...", end=" ")
            auditor = SEOAuditor(f)
            res = auditor.audit()
            post_results.append(res)
            status = "✅" if res['score'] >= 90 else "⚠️" if res['score'] >= 70 else "❌"
            print(f"{status} {res['score']}/100")
        report_path = report_gen.generate_report(post_results, "post_fix")
        print(f"\n📄 Report post-fix salvato: {report_path}")
    
    print("\n" + "=" * 80)
    print("🏁 Operazione completata!")
    print("=" * 80)

if __name__ == "__main__":
    main()