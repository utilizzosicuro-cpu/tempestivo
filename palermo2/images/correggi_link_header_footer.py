from pathlib import Path
from bs4 import BeautifulSoup
import datetime

def correggi_link_header_footer(cartella_progetto: str = "."):
    root_dir = Path(cartella_progetto)
    # Trova tutti i file .html nella cartella e nelle sottocartelle
    file_html = list(root_dir.glob("**/*.html"))
    
    report_totale = []
    totale_file_modificati = 0
    totale_link_corretti = 0

    print(f"🔍 Avvio scansione di {len(file_html)} file HTML nella cartella: {root_dir.resolve()}\n")

    for file_path in file_html:
        # Salta eventuali file di sistema, venv o git
        if any(part in file_path.parts for part in ["venv", ".git", "node_modules"]):
            continue
            
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"⚠️ Impossibile leggere {file_path.name}: {e}")
            continue

        soup = BeautifulSoup(content, 'html.parser')
        modificato = f"📄 {file_path.name}\n"
        file_ha_modifiche = False
        link_corretti_file = 0

        # Funzione di supporto per correggere i link dentro un tag specifico (header/footer)
        def analizza_e_correggi_sezione(tag_sezione):
            nonlocal file_ha_modifiche, link_corretti_file, modificato
            if not tag_sezione:
                return

            # Cerca tutti i tag <a> con attributo href e <link> interni alla sezione
            for tag in tag_sezione.find_all(['a', 'link'], href=True):
                href = tag['href'].strip()
                
                # Ignora link vuoti, ancore interne, mailto, tel o link già assoluti/esterni
                if not href or href.startswith(('#', 'http://', 'https://', 'mailto:', 'tel:', '/')):
                    continue
                
                # Il link è relativo (es. "servizi.html" o "./pag.html")
                href_pulito = href.lstrip('./')
                nuovo_href = '/' + href_pulito
                
                modificato += f"  - [CORRETTO] Tag <{tag.name}>: '{href}' -> '{nuovo_href}'\n"
                tag['href'] = nuovo_href
                file_ha_modifiche = True
                link_corretti_file += 1

        # Analizza Header e Footer
        analizza_e_correggi_sezione(soup.find('header'))
        analizza_e_correggi_sezione(soup.find('footer'))

        # Se ci sono state modifiche, salva il file e aggiorna le statistiche
        if file_ha_modifiche:
            file_path.write_text(str(soup), encoding="utf-8")
            totale_file_modificati += 1
            totale_link_corretti += link_corretti_file
            report_totale.append(modificato)
            print(f"🛠️ File aggiornato: {file_path.name} ({link_corretti_file} link corretti)")

    # --- Generazione Report Finale ---
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report_testo = []
    report_testo.append("=" * 50)
    report_testo.append(f" REPORT ANALISI LINK HEADER & FOOTER - {timestamp}")
    report_testo.append("=" * 50)
    report_testo.append(f"📁 Directory scansionata: {root_dir.resolve()}")
    report_testo.append(f"📄 File HTML analizzati: {len(file_html)}")
    report_testo.append(f"📝 File modificati: {totale_file_modificati}")
    report_testo.append(f"🔗 Totale link corretti alla root: {totale_link_corretti}")
    report_testo.append("-" * 50)
    report_testo.append("DETTAGLIO MODIFICHE PER FILE:\n")
    
    if report_totale:
        report_testo.extend(report_totale)
    else:
        report_testo.append("Nessuna correzione necessaria. Tutti i link nell'header e nel footer puntavano già alla root o erano esterni.")

    testo_finale_report = "\n".join(report_testo)

    # Scrive il report su file di testo nella stessa cartella dello script
    report_path = root_dir / "report_link.txt"
    report_path.write_text(testo_finale_report, encoding="utf-8")

    # Stampa a video il report
    print("\n" + testo_finale_report)
    print(f"\n💾 Il report completo è stato salvato con successo in: {report_path.resolve()}")

if __name__ == "__main__":
    # Esegue lo script nella cartella corrente
    correggi_link_header_footer(".")