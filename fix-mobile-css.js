const fs = require('fs');
const path = require('path');

// ⚙️ CONFIGURAZIONE: Verifichi che questo percorso sia corretto
const TARGET_DIR = '.'; 
const BACKUP_DIR = './_backup_mobile_css_fix';
const REPORT_FILE = 'report-fix-mobile-css.json';

const results = {
    totalFilesScanned: 0,
    filesModified: 0,
    details: []
};

// Crea cartella di backup se non esiste
if (!fs.existsSync(BACKUP_DIR)) {
    fs.mkdirSync(BACKUP_DIR, { recursive: true });
}

// Regex intelligente: trova <link ... href="...mobile-fix.css" ... >
// Funziona indipendentemente dall'ordine degli attributi (rel, href, ecc.)
const cssRegex = /<link\b[^>]*?href=["'][^"']*mobile-fix\.css["'][^>]*\/?>/gi;

// Stringa di sostituzione esatta richiesta
const replacementString = `<link rel="preload" href="/mobile-fix.css" as="style" onload="this.onload=null;this.rel='stylesheet'">\n<noscript><link rel="stylesheet" href="/mobile-fix.css"></noscript>`;

// Funzione ricorsiva per scansionare le cartelle
function walkDir(dir) {
    const files = fs.readdirSync(dir);
    files.forEach(file => {
        const filePath = path.join(dir, file);
        const stat = fs.statSync(filePath);
        
        if (stat.isDirectory()) {
            walkDir(filePath);
        } else if (file.endsWith('.html') || file.endsWith('.htm')) {
            results.totalFilesScanned++;
            processFile(filePath);
        }
    });
}

function processFile(filePath) {
    const relativePath = path.relative(TARGET_DIR, filePath).replace(/\\/g, '/');
    let htmlContent = '';
    
    try {
        htmlContent = fs.readFileSync(filePath, 'utf8');
    } catch (err) {
        console.error(`❌ Errore lettura: ${relativePath}`);
        return;
    }

    // Verifica se il file contiene il target
    if (cssRegex.test(htmlContent)) {
        // 1. Backup del file originale
        const backupPath = path.join(BACKUP_DIR, relativePath);
        const backupDirPath = path.dirname(backupPath);
        if (!fs.existsSync(backupDirPath)) {
            fs.mkdirSync(backupDirPath, { recursive: true });
        }
        fs.writeFileSync(backupPath, htmlContent, 'utf8');

        // 2. Sostituzione (ripristina l'indice della regex per riutilizzarla)
        cssRegex.lastIndex = 0; 
        const newHtmlContent = htmlContent.replace(cssRegex, replacementString);

        // 3. Salvataggio del file modificato
        fs.writeFileSync(filePath, newHtmlContent, 'utf8');
        
        results.filesModified++;
        results.details.push(relativePath);
        console.log(`✅ MODIFICATO: ${relativePath}`);
    }
}

// ==========================================
// ESECUZIONE
// ==========================================
console.log(`\n🔧 AVVIO FIX CSS MOBILE (Preload Asincrono)`);
console.log(`📂 Cartella target: ${path.resolve(TARGET_DIR)}`);
console.log('⏳ Scansione in corso...\n');

if (!fs.existsSync(TARGET_DIR)) {
    console.error(`❌ ERRORE FATALE: La cartella "${TARGET_DIR}" non esiste.`);
    console.error(`   Modifichi la variabile TARGET_DIR nello script (riga 6).`);
    process.exit(1);
}

walkDir(TARGET_DIR);

// Generazione Report
fs.writeFileSync(REPORT_FILE, JSON.stringify(results, null, 2), 'utf8');

console.log('\n' + '='.repeat(60));
console.log('🏁 FIX COMPLETATO');
console.log('='.repeat(60));
console.log(`📁 File totali scansionati: ${results.totalFilesScanned}`);
console.log(`✅ File modificati con successo: ${results.filesModified}`);
console.log(`💾 Backup originali salvati in: ${path.resolve(BACKUP_DIR)}`);
console.log(`📄 Report dettagliato: ${path.resolve(REPORT_FILE)}`);
console.log('='.repeat(60) + '\n');

if (results.filesModified > 0) {
    console.log('💡 PROSSIMO PASSO: Carichi questi file sul server live, svuoti la cache e testi su PageSpeed Insights.');
} else {
    console.log('🎉 NESSUNA MODIFICA NECESSARIA: Nessun tag mobile-fix.css trovato da modificare.');
}