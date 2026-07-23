import os
from bs4 import BeautifulSoup
from datetime import datetime

REPORT_FILENAME = "report_missione_tutte_le_pagine_citta.txt"

# -----------------------------------------------------------------------------
# DATABASE CONTESTUALIZZATO PER OGNI CITTÀ
# -----------------------------------------------------------------------------
CITY_CONTEXTS = {
    "palermo": {
        "nome": "Palermo",
        "p1": "Operare a Palermo significa gestire un tessuto urbano estremamente vario: dai vincoli di tutela nel Centro Storico (Kalsa, Politeama) alle case di villeggiatura e residenze sul mare a Mondello e Addaura, fino ai complessi condominiali e commerciali di aree ad alta densità come Viale Regione o lo ZEN.",
        "p2": "La nostra missione è offrire un unico interlocutore tecnico qualificato per risolvere problemi idraulici, elettrici e di ristrutturazione, garantendo interventi tempestivi sia nei palazzi d'epoca che nei moderni residence cittadini."
    },
    "alcamo": {
        "nome": "Alcamo",
        "p1": "Operare ad Alcamo richiede una conoscenza capillare del territorio: dalla manutenzione delle abitazioni nel centro storico e attorno al Castello dei Conti di Modica, alle esigenze specifiche delle ville stagionali e strutture ricettive ad Alcamo Marina, esposte all'azione della salsedine.",
        "p2": "La nostra missione è preservare il valore degli immobili locali con interventi duraturi, sia nelle zone urbane interne che lungo la fascia costiera, garantendo rapidità e massima professionalità."
    },
    "carini": {
        "nome": "Carini",
        "p1": "Operare a Carini significa rispondere alle diverse esigenze di un territorio esteso: dalle ristrutturazioni nel borgo medievale all'ombra del Castello, agli interventi idraulici e di impiantistica nelle zone residenziali e industriali di Villagrazia di Carini e lungo la fascia costiera.",
        "p2": "La nostra missione è garantire standard elevati sia per la manutenzione ordinaria delle abitazioni private sia per l'adeguamento impianti delle attività commerciali della Piana di Carini."
    },
    "castellammare": {
        "nome": "Castellammare del Golfo",
        "p1": "Operare a Castellammare del Golfo significa conoscere a fondo le specificità del territorio: dai vincoli paesaggistici del centro storico e del porto, alle esigenze di manutenzione delle case vacanza a Scopello e Balata di Baida, fino alla resistenza necessaria contro la salsedine per le proprietà sul lungomare.",
        "p2": "La nostra missione è trasformare le criticità in soluzioni durature, offrendo ai residenti e agli amministratori di Castellammare del Golfo un unico referente affidabile, con tempi certi e la garanzia di un lavoro a regola d'arte."
    },
    "monreale": {
        "nome": "Monreale",
        "p1": "Operare a Monreale significa confrontarsi con un territorio collinare articolato: dai palazzi storici soggetti a vincoli architettonici nei pressi del Duomo, alle abitazioni e ville sparse nelle frazioni di San Martino delle Scale, Aquino, Pioppo e Grisì.",
        "p2": "La nostra missione è risolvere con precisione le criticità legate alle differenze altimetriche, all'umidità e alla conservazione degli immobili storici e collinari."
    },
    "partinico": {
        "nome": "Partinico",
        "p1": "Operare a Partinico richiede competenza sia nel centro urbano (attorno a Piazza Duomo e alla Real Cantina Borbonica) che nelle vaste aree periferiche e contrade agricole come San Giuseppe, Ciammarita, Valguarnera e la zona industriale.",
        "p2": "La nostra missione è garantire servizi idraulici, elettrici e di edilizia rapida ad elevata tenuta stagionale, al servizio sia delle famiglie che delle attività produttive locali."
    },
    "terrasini": {
        "nome": "Terrasini",
        "p1": "Operare a Terrasini significa intervenire in un contesto a forte vocazione turistica e marinara: dalle abitazioni storiche attorno al Duomo e al lungomare della Praiola, fino alle ville e case vacanza nelle zone di Calarossa, Perla del Golfo e Contrada Carrubbo.",
        "p2": "La nostra missione è proteggere le strutture dall'usura della salsedine e dal logorio estivo, assicurando interventi di ristrutturazione ed efficienza impianti prima e durante la stagione."
    },
    "cinisi": {
        "nome": "Cinisi",
        "p1": "Operare a Cinisi richiede interventi mirati sia nel centro cittadino che nelle aree costiere ed esposte come Magaggiari, oltre che nelle strutture ricettive nei pressi dello snodo aeroportuale di Punta Raisi.",
        "p2": "La nostra missione è offrire tempestività e continuità di servizio per abitazioni private e strutture B&B/Hotel, risolvendo guasti ed emergenze con materiali resistenti e certificati."
    },
    "isola-delle-femmine": {
        "nome": "Isola delle Femmine",
        "p1": "Operare ad Isola delle Femmine significa affrontare quotidianamente gli effetti dell'esposizione marina diretta su edifici residenziali, appartamenti ad uso estivo e locali commerciali della zona del porto e del lungomare.",
        "p2": "La nostra missione è applicare tecniche e materiali anticorrosivi di alta qualità per impianti e ristrutturazioni che resistano al vento salmastro e all'umidità costante."
    },
    "capaci": {
        "nome": "Capaci",
        "p1": "Operare a Capaci significa servire sia il nucleo abitativo storico che la vasta zona di espansione verso il mare ed il lungomare Kennedy, caratterizzata da un'alta concentrazione di condomini e residence estivi.",
        "p2": "La nostra missione è assicurare manutenzioni idrice, ripristini di facciate e rifacimenti interni rapidi per garantire il massimo comfort in ogni stagione."
    },
    "trappeto": {
        "nome": "Trappeto",
        "p1": "Operare a Trappeto richiede interventi specifici sul borgo marinaro, sulla zona della Ciammarita e sulle abitazioni collinari panoramiche, esposte ad agenti atmosferici stagionali intensi.",
        "p2": "La nostra missione è mantenere in perfetta efficienza sia le abitazioni dei residenti che i complessi turistici estivi con interventi trasparenti e duraturi."
    },
    "balestrate": {
        "nome": "Balestrate",
        "p1": "Operare a Balestrate comporta la gestione di un parco immobiliare estivo e residenziale distribuito tra il centro cittadino, la zona del Marina e le contrade rurali come Sicciarotta e Manico di Quarara.",
        "p2": "La nostra missione è fornire un punto di riferimento sicuro per lavori di ristrutturazione ed emergenze impianti, valorizzando il patrimonio immobiliare della costa."
    }
}

DEFAULT_CONTEXT = {
    "p1_template": "Operare a {nome} significa conoscere a fondo le specificità del territorio: dalle esigenze del centro urbano e delle zone residenziali, alla manutenzione di immobili privati e strutture locali esposte agli agenti atmosferici.",
    "p2_template": "La nostra missione è trasformare le criticità in soluzioni durature, offrendo ai residenti di {nome} un unico referente affidabile con la garanzia di lavori eseguiti a regola d'arte."
}


def process_all_pages_mission():
    root_dir = os.getcwd()
    total_files_scanned = 0
    modified_files_count = 0
    logs = []

    print("=== INIZIO AGGIORNAMENTO MISSIONE SU TUTTE LE PAGINE DELLE CITTÀ ===")

    for current_root, _, files in os.walk(root_dir):
        # Esclude la root principale, lavora SOLO nelle cartelle delle città
        if current_root == root_dir:
            continue

        folder_slug = os.path.basename(current_root).lower()

        for file in files:
            # ORA SCANSIONA TUTTI I FILE .HTML (index.html, servizi, recensioni, ecc.)
            if not file.endswith('.html'):
                continue

            total_files_scanned += 1
            file_path = os.path.join(current_root, file)
            rel_file_path = os.path.relpath(file_path, root_dir).replace("\\", "/")

            # Determina il testo dinamico per il comune
            if folder_slug in CITY_CONTEXTS:
                city_info = CITY_CONTEXTS[folder_slug]
                city_name = city_info["nome"]
                new_title = f"La Nostra Missione a {city_name}"
                new_p1 = city_info["p1"]
                new_p2 = city_info["p2"]
            else:
                city_name = folder_slug.replace('-', ' ').title()
                new_title = f"La Nostra Missione a {city_name}"
                new_p1 = DEFAULT_CONTEXT["p1_template"].format(nome=city_name)
                new_p2 = DEFAULT_CONTEXT["p2_template"].format(nome=city_name)

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                logs.append(f"[ERRORE LETTURA] {rel_file_path}: {e}")
                continue

            soup = BeautifulSoup(content, 'html.parser')
            file_modified = False

            # Cerca il tag del titolo della Sezione Missione
            mission_title_tag = None
            for tag in soup.find_all(['h2', 'h3', 'h4', 'div']):
                if "la nostra missione" in tag.get_text().lower():
                    mission_title_tag = tag
                    break

            if mission_title_tag:
                # 1. Aggiorna il Titolo
                if mission_title_tag.get_text().strip() != new_title:
                    mission_title_tag.string = new_title
                    file_modified = True

                # 2. Cerca e aggiorna i due paragrafi
                parent = mission_title_tag.parent
                if parent:
                    paragraphs = parent.find_all('p')
                    if len(paragraphs) >= 2:
                        paragraphs[0].string = new_p1
                        paragraphs[1].string = new_p2
                        file_modified = True
                    else:
                        next_p1 = mission_title_tag.find_next_sibling('p')
                        if next_p1:
                            next_p1.string = new_p1
                            next_p2 = next_p1.find_next_sibling('p')
                            if next_p2:
                                next_p2.string = new_p2
                            file_modified = True

            # Salva le modifiche nel file HTML
            if file_modified:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(str(soup))
                    modified_files_count += 1
                    logs.append(
                        f"[AGGIORNATO] {rel_file_path}\n"
                        f"   └─ Sezione Missione personalizzata per: '{city_name}'"
                    )
                except Exception as e:
                    logs.append(f"[ERRORE SCRITTURA] {rel_file_path}: {e}")

    # --- GENERAZIONE FILE DI REPORT ---
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report_lines = [
        "=================================================================",
        "   REPORT AGGIORNAMENTO MISSIONE (TUTTE LE PAGINE DELLE CITTÀ)",
        "=================================================================",
        f"Data Esecuzione          : {now_str}",
        f"Cartella Principale      : {root_dir}",
        f"Pagine HTML Scansionate  : {total_files_scanned}",
        f"Pagine HTML Modificate   : {modified_files_count}",
        "=================================================================\n",
        "DETTAGLIO DEGLI INTERVENTI:\n"
    ]

    if logs:
        report_lines.extend(logs)

    report_content = "\n\n".join(report_lines)

    report_path = os.path.join(root_dir, REPORT_FILENAME)
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"\n[COMPLETATO] Report salvato con successo in: {REPORT_FILENAME}")
    except Exception as e:
        print(f"\n[ERRORE] Impossibile salvare il file di report: {e}")

    print(f"Pagine HTML analizzate nelle cartelle città: {total_files_scanned} | Pagine aggiornate: {modified_files_count}")


if __name__ == "__main__":
    process_all_pages_mission()