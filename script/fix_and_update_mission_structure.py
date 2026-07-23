import os
from bs4 import BeautifulSoup
from datetime import datetime

REPORT_FILENAME = "report_ripristino_missione_struttura.txt"

# -----------------------------------------------------------------------------
# DATABASE TESTI CONTESTUALIZZATI PER CITTÀ
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
        "p2": "La nostra missione è applicare tecniche e materials anticorrosivi di alta qualità per impianti e ristrutturazioni che resistano al vento salmastro e all'umidità costante."
    },
    "capaci": {
        "nome": "Capaci",
        "p1": "Operare a Capaci significa servire sia il nucleo abitativo storico che la vasta zona di espansione verso il mare ed il lungomare Kennedy, caratterizzata da un'alta concentrazione di condomini e residence estivi.",
        "p2": "La nostra missione è assicurare manutenzioni idriche, ripristini di facciate e rifacimenti interni rapidi per garantire il massimo comfort in ogni stagione."
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
    "p2_template": "La nostra missione è trasformare le criticità in soluzioni durature, offrendo ai residenti di {nome} un unico referente affidabile con la garanzia di lavori eseguiti a regola d me."
}


def create_mission_section(soup, new_title, new_p1, new_p2):
    """
    Crea da zero un elemento <section class="perche-tempestivo"> 
    perfettamente conforme agli stili CSS del sito.
    """
    sec = soup.new_tag("section", attrs={"class": "perche-tempestivo"})
    
    h2 = soup.new_tag("h2")
    h2.string = new_title
    sec.append(h2)

    grid = soup.new_tag("div", attrs={"class": "vantaggi-grid", "style": "max-width: 900px; margin: 0 auto;"})
    
    # Box Paragrafo 1
    v1 = soup.new_tag("div", attrs={"class": "vantaggio", "style": "text-align: left;"})
    p1 = soup.new_tag("p")
    p1.string = new_p1
    v1.append(p1)
    
    # Box Paragrafo 2
    v2 = soup.new_tag("div", attrs={"class": "vantaggio", "style": "text-align: left;"})
    p2 = soup.new_tag("p")
    p2.string = new_p2
    v2.append(p2)

    grid.append(v1)
    grid.append(v2)
    sec.append(grid)
    
    return sec


def fix_and_rebuild_mission():
    root_dir = os.getcwd()
    total_files_scanned = 0
    modified_files_count = 0
    logs = []

    print("=== INIZIO SCANSIONE E RICOSTRUZIONE STRUTTURALE SEZIONE 'LA NOSTRA MISSIONE' ===")

    for current_root, _, files in os.walk(root_dir):
        if current_root == root_dir:
            continue

        folder_slug = os.path.basename(current_root).lower()

        for file in files:
            if not file.endswith('.html'):
                continue

            total_files_scanned += 1
            file_path = os.path.join(current_root, file)
            rel_file_path = os.path.relpath(file_path, root_dir).replace("\\", "/")

            # Recupera o genera i testi per la città
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

            # Cerca il punto in cui inserire o sostituire la sezione della missione
            existing_mission = None
            for element in soup.find_all(['section', 'div', 'h2', 'h3']):
                text_content = element.get_text().lower()
                if "nostra missione" in text_content or "missione a" in text_content:
                    # Risale alla section principale che contiene questo elemento
                    parent_sec = element if element.name == 'section' else element.find_parent('section')
                    existing_mission = parent_sec if parent_sec else element
                    break

            new_mission_sec = create_mission_section(soup, new_title, new_p1, new_p2)

            if existing_mission:
                # Sostituisce completamente la vecchia sezione danneggiata o vuota
                existing_mission.replace_with(new_mission_sec)
                file_modified = True
            else:
                # Se non c'è, la inserisce prima della CTA finale o prima del footer
                target_insertion = soup.find('section', class_='tempestivo-lead-section') or soup.find('footer')
                if target_insertion:
                    target_insertion.insert_before(new_mission_sec)
                    file_modified = True

            # Salva le modifiche
            if file_modified:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(str(soup))
                    modified_files_count += 1
                    logs.append(
                        f"[RICOSTRUITA & AGGIORNATA] {rel_file_path}\n"
                        f"   └─ Inserita struttura HTML completa per la missione di: '{city_name}'"
                    )
                except Exception as e:
                    logs.append(f"[ERRORE SCRITTURA] {rel_file_path}: {e}")

    # --- REPORT FINALE ---
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report_lines = [
        "=================================================================",
        "     REPORT RICOSTRUZIONE SEZIONE 'LA NOSTRA MISSIONE'",
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
        print(f"\n[COMPLETATO] Report salvato con successo: {REPORT_FILENAME}")
    except Exception as e:
        print(f"\n[ERRORE] Impossibile salvare il file di report: {e}")

    print(f"File analizzati: {total_files_scanned} | File aggiornati: {modified_files_count}")


if __name__ == "__main__":
    fix_and_rebuild_mission()