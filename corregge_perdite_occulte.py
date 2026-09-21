#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script di correzione multipla link SEO per Tempestivo.it
Scansiona ricorsivamente tutte le cartelle e i file HTML per correggere
vari link errati terminanti con '/' trasformandoli nei rispettivi file .html.

Autore: Assistente SEO
Data: 2026-09-21
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

# ============================================================
# CONFIGURAZIONE
# ============================================================

# Directory base del sito (es. cartella corrente o percorso specifico)
BASE_DIR = Path(".") 

# Modalità test: True = mostra cosa farebbe senza modificare i file
# ⚠️ Metti False SOLO quando sei sicuro di voler applicare le modifiche reali
DRY_RUN = False  

# Crea backup prima di modificare?
MAKE_BACKUP = True

# Dizionario delle sostituzioni: { "stringa_errata": "stringa_corretta" }
LINK_REPLACEMENTS = {
    "servizi/perdite-occulte-diagnostica-palermo/": "servizi/perdite-occulte-diagnostica-palermo.html",
    "servizi/impianti-idraulici-civili-palermo/": "servizi/impianti-idraulici-civili-palermo.html",
    "servizi/collaudo-certificazione-impianti-palermo/": "servizi/collaudo-certificazione-impianti-palermo.html",
    "servizi/impianti-elettrici-industriali-commerciali-palermo/": "servizi/impianti-elettrici-industriali-commerciali-palermo.html",
    "servizi/impianti-idraulici-industriali-commerciali-palermo/": "servizi/impianti-idraulici-industriali-commerciali-palermo.html",
    "servizi/impianti-idraulici-condominiali-palermo/": "servizi/impianti-idraulici-condominiali-palermo.html",
    "servizi/riscaldamento-climatizzazione-palermo/": "servizi/riscaldamento-climatizzazione-palermo.html"
}

# Cartelle di sistema o ambienti da ignorare completamente durante la scansione
IGNORED_DIRS = {'.git', 'venv', 'env', '__pycache__', '.vscode', 'node_modules'}


# ============================================================
# FUNZIONI PRINCIPALI
# ============================================================

def crea_backup(file_path: Path) -> Path:
    """Crea una copia di backup del file con timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = file_path.with_suffix(f".html.backup_{timestamp}")
    shutil.copy2(file_path, backup_path)
    return backup_path


def processa_file(file_path: Path, dry_run: bool = True) -> dict:
    """
    Legge un singolo file HTML, verifica la presenza di uno o più link errati,
    li corregge senza creare duplicati e salva il file.
    """
    risultato = {
        "file": str(file_path),
        "stato": "ignorato",
        "sostituzioni_totali": 0,
        "dettagli": {},
        "messaggio": ""
    }
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            contenuto = f.read()
    except Exception as e:
        risultato["stato"] = "errore"
        risultato["messaggio"] = f"Errore di lettura: {e}"
        return risultato
    
    # Verifica quali stringhe errate sono presenti nel file
    modificato = False
    nuovo_contenuto = contenuto
    sostituzioni_file = 0
    
    for errata, corretta in LINK_REPLACEMENTS.items():
        if errata in nuovo_contenuto:
            count = nuovo_contenuto.count(errata)
            nuovo_contenuto = nuovo_contenuto.replace(errata, corretta)
            risultato["dettagli"][errata] = count
            sostituzioni_file += count
            modificato = True

    # Se non ci sono corrispondenze, esce
    if not modificato:
        risultato["stato"] = "nessuna_modifica"
        risultato["messaggio"] = "Nessun link errato trovato nel file."
        return risultato
    
    # Doppio controllo di sicurezza contro doppi suffissi
    nuovo_contenuto = nuovo_contenuto.replace(".html.html", ".html")
    
    risultato["sostituzioni_totali"] = sostituzioni_file
    
    if dry_run:
        risultato["stato"] = "dry_run"
        risultato["messaggio"] = f"[DRY RUN] Trovate {sostituzioni_file} occorrenze totali da correggere."
        return risultato
    
    # Crea backup prima di sovrascrivere
    if MAKE_BACKUP:
        try:
            crea_backup(file_path)
        except Exception as e:
            risultato["stato"] = "errore"
            risultato["messaggio"] = f"Errore creazione backup: {e}"
            return risultato
            
    # Salva il file corretto
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(nuovo_contenuto)
        risultato["stato"] = "successo"
        risultato["messaggio"] = f"Corrette con successo {sostituzioni_file} occorrenze."
    except Exception as e:
        risultato["stato"] = "errore"
        risultato["messaggio"] = f"Errore di scrittura: {e}"
        
    return risultato


def main():
    print("=" * 70)
    print("🔧 SCRIPT CORREZIONE MULTIPLA LINK SEO - TEMPESTIVO.IT")
    print("🎯 OBIETTIVO: Sostituzione di tutti i link errati con estensione .html")
    print("=" * 70)
    print(f"📁 Directory base di scansione: {BASE_DIR.absolute()}")
    print(f"🧪 Modalità DRY RUN: {'✅ ATTIVA (nessuna modifica)' if DRY_RUN else '❌ DISATTIVA (modifiche reali)'}")
    print(f"💾 Backup automatico: {'✅ ATTIVO' if MAKE_BACKUP else '❌ DISATTIVATO'}")
    print("=" * 70)
    print()

    if not BASE_DIR.exists():
        print(f"❌ ERRORE: La directory base non esiste: {BASE_DIR}")
        return

    risultati = []
    totale_file_modificati = 0
    totale_occorrenze_corrette = 0

    # Scansione ricorsiva di cartelle e sottocartelle
    for current_root, dirs, files in os.walk(BASE_DIR):
        # Esclude le cartelle di sistema/ambiente virtuale
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

        for filename in files:
            if filename.endswith(".html"):
                file_path = Path(current_root) / filename
                
                # Esegue il processo sul singolo file
                res = processa_file(file_path, dry_run=DRY_RUN)
                risultati.append(res)
                
                if res["stato"] in ["successo", "dry_run"]:
                    totale_file_modificati += 1
                    totale_occorrenze_corrette += res["sostituzioni_totali"]
                    rel_path = file_path.relative_to(BASE_DIR)
                    print(f"📄 File: {rel_path} ({res['sostituzioni_totali']} link corretti)")
                    for err, cnt in res["dettagli"].items():
                        print(f"   └─ {err} ➔ {cnt} volte")

    # Report finale
    print()
    print("=" * 70)
    print("📊 REPORT FINALE")
    print("=" * 70)
    print(f"📂 File HTML analizzati: {len(risultati)}")
    print(f"🛠️ File che {'verrebbero modificati' if DRY_RUN else 'sono stati modificati'}: {totale_file_modificati}")
    print(f"🔗 Totale link corretti su tutto il sito: {totale_occorrenze_corrette}")
    print("=" * 70)
    
    if DRY_RUN:
        print("💡 PROSSIMI PASSI:")
        print("  1. Verifica i dettagli stampati sopra.")
        print("  2. Se tutto è corretto, apri lo script e imposta: DRY_RUN = False")
        print("  3. Esegui nuovamente lo script per applicare le modifiche definitive.")
    else:
        print("💡 OPERAZIONE COMPLETATA CON SUCCESSO!")
        print("  • I backup di sicurezza (.html.backup_*) sono stati salvati nelle rispettive cartelle.")
        print("  • Puoi procedere con il controllo finale e il commit su Git.")
    print("=" * 70)


if __name__ == "__main__":
    main()