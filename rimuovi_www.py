import os
import re
from pathlib import Path

def modifica_file_html(directory):
    """
    Sostituisce:
    1. www.tempestivo.it → tempestivo.it
    2. www.tempestivoimpresa.it → tempestivo.it
    """
    
    # Definizioni delle sostituzioni
    sostituzioni = {
        r'www\.tempestivo\.it': 'tempestivo.it',
        r'www\.tempestivoimpresa\.it': 'tempestivo.it'
    }
    
    # Contatori
    file_modificati = 0
    totale_sostituzioni = 0
    dettagli = {}
    
    # Cerca tutti i file HTML nella directory
    for file_path in Path(directory).rglob('*.html'):
        try:
            # Leggi il contenuto del file
            with open(file_path, 'r', encoding='utf-8') as f:
                contenuto = f.read()
            
            contenuto_modificato = False
            sostituzioni_file = 0
            
            # Applica tutte le sostituzioni
            for pattern, replacement in sostituzioni.items():
                matches = re.findall(pattern, contenuto, re.IGNORECASE)
                num_occurrences = len(matches)
                
                if num_occurrences > 0:
                    contenuto = re.sub(pattern, replacement, contenuto, flags=re.IGNORECASE)
                    contenuto_modificato = True
                    sostituzioni_file += num_occurrences
                    
                    # Aggiorna i dettagli
                    key = f"{pattern} → {replacement}"
                    dettagli[key] = dettagli.get(key, 0) + num_occurrences
            
            if contenuto_modificato:
                # Salva il file modificato
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(contenuto)
                
                print(f"✅ {file_path.name}")
                print(f"   Modifiche: {sostituzioni_file}")
                
                file_modificati += 1
                totale_sostituzioni += sostituzioni_file
                
        except Exception as e:
            print(f"❌ Errore nel file {file_path}: {e}")
    
    # Report finale
    print(f"\n{'='*70}")
    print(f"📊 RIEPILOGO MODIFICHE")
    print(f"{'='*70}")
    
    for sostituzione, count in dettagli.items():
        print(f"  • {sostituzione}: {count} occorrenze")
    
    print(f"\n{'='*70}")
    print(f"✅ OPERAZIONE COMPLETATA")
    print(f"{'='*70}")
    print(f"📁 File modificati: {file_modificati}")
    print(f"🔄 Totale sostituzioni: {totale_sostituzioni}")
    print(f"{'='*70}")

# ==================== CONFIGURAZIONE ====================
if __name__ == "__main__":
    # Modifica questo percorso con la directory dei tuoi file HTML
    directory_html = "./"  # Usa "." per la directory corrente
    
    print("🔍 Ricerca file HTML da modificare...")
    print(f"📂 Directory: {os.path.abspath(directory_html)}")
    print(f"{'='*70}")
    print("📋 Sostituzioni previste:")
    print("   1. www.tempestivo.it → tempestivo.it")
    print("   2. www.tempestivoimpresa.it → tempestivo.it")
    print(f"{'='*70}")
    
    # Chiedi conferma
    risposta = input("\n⚠️  Vuoi procedere con la modifica? (sì/no): ").lower().strip()
    
    if risposta in ['sì', 'si', 's', 'yes', 'y']:
        print("\n🚀 Inizio modifiche...\n")
        modifica_file_html(directory_html)
    else:
        print("❌ Operazione annullata")