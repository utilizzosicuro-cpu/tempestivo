const fs = require('fs');
const path = require('path');

// ⚙️ CONFIGURAZIONE
const TARGET_DIR = '.'; // Modifichi se necessario
const BACKUP_DIR = './_backup_css_fonts_fix';
const REPORT_FILE = 'report-css-fix.json';

const results = {
    totalFilesScanned: 0,
    filesModified: 0,
    details: []
};

// Crea cartella backup
if (!fs.existsSync(BACKUP_DIR)) {
    fs.mkdirSync(BACKUP_DIR, { recursive: true });
}

function walkDir(dir) {
    const files = fs.readdirSync(dir);
    files.forEach(file => {
        const filePath = path.join(dir, file);
        const stat = fs.statSync(filePath);
        if (stat.isDirectory()) walkDir(filePath);
        else if (file.endsWith('.html') || file.endsWith('.htm')) {
            results.totalFilesScanned++;
            processFile(filePath);
        }
    });
}

function backupFile(filePath) {
    const relativePath = path.relative(TARGET_DIR, filePath).replace(/\\/g, '/');
    const backupPath = path.join(BACKUP_DIR, relativePath);
    const backupDirPath = path.dirname(backupPath);
    if (!fs.existsSync(backupDirPath)) fs.mkdirSync(backupDirPath, { recursive: true });
    fs.writeFileSync(backupPath, fs.readFileSync(filePath, 'utf8'), 'utf8');
}

function processFile(filePath) {
    const relativePath = path.relative(TARGET_DIR, filePath).replace(/\\/g, '/');
    let html = fs.readFileSync(filePath, 'utf8');
    let modified = false;
    let changes = [];

    // ==========================================
    // 1. FIX STYLE.CSS (Render-blocking -> Async Preload)
    // ==========================================
    // Regex robusta: trova <link ... href="...style.css" ...>
    const styleRegex = /<link\b[^>]*?href=["'][^"']*style\.css["'][^>]*\/?>/gi;
    if (styleRegex.test(html)) {
        if (!modified) { backupFile(filePath); modified = true; }
        html = html.replace(styleRegex, `<link rel="preload" href="/style.css" as="style" onload="this.onload=null;this.rel='stylesheet'">\n<noscript><link rel="stylesheet" href="/style.css"></noscript>`);
        changes.push('style.css -> async preload');
    }

    // ==========================================
    // 2. FIX MOBILE-FIX.CSS (Standardizzazione)
    // ==========================================
    const mobileRegex = /<link\b[^>]*?href=["'][^"']*mobile-fix\.css["'][^>]*\/?>/gi;
    if (mobileRegex.test(html)) {
        if (!modified) { backupFile(filePath); modified = true; }
        html = html.replace(mobileRegex, `<link rel="stylesheet" href="/mobile-fix.css">`);
        changes.push('mobile-fix.css -> standard link');
    }

    // ==========================================
    // 3. FIX GOOGLE FONTS (Aggiunta display=swap)
    // ==========================================
    // Trova i link ai font di Google e aggiunge display=swap se manca
    const fontRegex = /<link\b[^>]*?href=["'](https:\/\/fonts\.googleapis\.com\/css[^"']*)["'][^>]*\/?>/gi;
    
    html = html.replace(fontRegex, (match, url) => {
        if (!url.includes('display=swap')) {
            if (!modified) { backupFile(filePath); modified = true; }
            changes.push('Google Fonts -> added display=swap');
            
            // Determina se usare ? o & per aggiungere il parametro
            const separator = url.includes('?') ? '&' : '?';
            const newUrl = `${url}${separator}display=swap`;
            return match.replace(url, newUrl);
        }
        return match; // Se ha già display=swap, non tocca nulla
    });

    // Salva se modificato
    if (modified) {
        fs.writeFileSync(filePath, html, 'utf8');
        results.filesModified++;
        results.details.push({
            file: relativePath,
            changes: changes
        });
        console.log(`✅ MODIFICATO: ${relativePath}`);
        changes.forEach(c => console.log(`   → ${c}`));
    }
}

// ==========================================
// ESECUZIONE
// ==========================================
console.log(`\n🔧 AVVIO FIX CSS E FONT (Ottimizzazione LCP)`);
console.log(`📂 Cartella: ${path.resolve(TARGET_DIR)}\n`);

if (!fs.existsSync(TARGET_DIR)) {
    console.error(`❌ ERRORE: La cartella "${TARGET_DIR}" non esiste.`);
    process.exit(1);
}

walkDir(TARGET_DIR);

fs.writeFileSync(REPORT_FILE, JSON.stringify(results, null, 2), 'utf8');

console.log('\n' + '='.repeat(60));
console.log('🏁 FIX COMPLETATO');
console.log('='.repeat(60));
console.log(`📁 File totali scansionati: ${results.totalFilesScanned}`);
console.log(`✅ File modificati: ${results.filesModified}`);
console.log(`💾 Backup in: ${path.resolve(BACKUP_DIR)}`);
console.log(`📄 Report: ${path.resolve(REPORT_FILE)}`);
console.log('='.repeat(60));

if (results.filesModified > 0) {
    console.log('\n💡 PROSSIMO PASSO: Carichi i file modificati sul server live, svuoti la cache e testi su PageSpeed Insights.');
} else {
    console.log('\n NESSUNA MODIFICA NECESSARIA: I tag CSS e Font sono già ottimizzati.');
}