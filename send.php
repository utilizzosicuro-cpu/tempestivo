<?php

// CONFIGURAZIONE
$destinatario = "salviamarcello@gmail.com"; 
$oggetto = "Nuova richiesta dal sito Tempestivo";

// PROTEZIONE ANTISPAM (honeypot)
if (!empty($_POST['website'])) {
    die("Spam rilevato.");
}

// RACCOLTA DATI
$nome = htmlspecialchars($_POST['nome']);
$azienda = htmlspecialchars($_POST['azienda']);
$telefono = htmlspecialchars($_POST['telefono']);
$email = htmlspecialchars($_POST['email']);
$area = htmlspecialchars($_POST['area']);
$messaggio = htmlspecialchars($_POST['messaggio']);

// CORPO EMAIL
$corpo = "
Hai ricevuto una nuova richiesta dal sito Tempestivo:

Nome: $nome
Azienda: $azienda
Telefono: $telefono
Email: $email
Area di intervento: $area

Messaggio:
$messaggio
";

// INTESTAZIONI EMAIL
$headers = "From: sito@tempestivo.it\r\n";
$headers .= "Reply-To: $email\r\n";

<input type="text" name="website" style="display:none">


// INVIO
mail($destinatario, $oggetto, $corpo, $headers);

// PAGINA DI CONFERMA
echo "
<!DOCTYPE html>
<html lang='it'>
<head>
<meta charset='UTF-8'>
<title>Richiesta Inviata</title>
<style>
body {
    font-family: Arial, sans-serif;
    background: #0B1B3B;
    color: white;
    text-align: center;
    padding: 80px 20px;
}
a {
    color: #FFC857;
    font-weight: bold;
}
</style>
</head>
<body>
    <h1>Richiesta inviata con successo!</h1>
    <p>Ti contatteremo entro poche ore.</p>
    <p><a href='index.html'>Torna al sito</a></p>
</body>
</html>
";
?>
