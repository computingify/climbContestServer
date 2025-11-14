let savedClimberBib = null;
let savedBlocTag = null;

function checkClimber() {
    // Ouvre la caméra et scanne le QRCode pour le grimpeur
    startQrScanAndSend('climberInput', '/api/v2/contest/climber/name', (success, message, value) => {
        if (success) {
            savedClimberBib = value;
        } else {
            savedClimberBib = null;
            document.getElementById('climberError').textContent = message || 'Erreur inconnue';
        }
    });
}

function checkBloc() {
    // Ouvre la caméra et scanne le QRCode pour le bloc
    startQrScanAndSend('blocInput', '/api/v2/contest/bloc/name', (success, message, value) => {
        if (success) {
            savedBlocTag = value;
        } else {
            savedBlocTag = null;
            document.getElementById('blocError').textContent = message || 'Erreur inconnue';
        }
    });
}

// Fonction qui ouvre la caméra, scanne le QRCode, puis envoie la donnée à l'API
function startQrScanAndSend(targetInputId, apiUrl, callback) {
    currentScanTarget = targetInputId;
    const qrRegion = document.getElementById('qr-region');
    qrRegion.style.display = 'block';

    if (!qrScanner) {
        qrScanner = new Html5Qrcode("qr-reader");
    }
    qrScanner.start(
        { facingMode: "environment" },
        {
            fps: 10,
            qrbox: 250
        },
        qrCodeMessage => {
            document.getElementById(targetInputId).value = qrCodeMessage;
            stopQrScan();
            // Envoie la donnée scannée à l'API correspondante
            fetch(apiUrl, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: qrCodeMessage})
            })
            .then(res => res.json().then(data => ({status: res.status, body: data})))
            .then(({status, body}) => {
                if (body.success) {
                    callback(true, null, qrCodeMessage);
                } else {
                    callback(false, body.message, null);
                }
            })
            .catch(() => {
                callback(false, 'Erreur réseau', null);
            });
        },
        errorMessage => {
            // ignore scan errors
        }
    ).catch(err => {
        document.getElementById('qr-error').textContent = "Erreur caméra : " + err;
    });
}

function sendSuccess() {
    document.getElementById('successError').textContent = '';
    if (!savedClimberBib || !savedBlocTag) {
        document.getElementById('successError').textContent = 'Veuillez vérifier le grimpeur et le bloc avant.';
        return;
    }
    fetch('/api/v2/contest/success', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({bib: savedClimberBib, bloc: savedBlocTag})
    })
    .then(res => res.json().then(data => ({status: res.status, body: data})))
    .then(({status, body}) => {
        if (body.success) {
            savedClimberBib = null;
            savedBlocTag = null;
            document.getElementById('climberInput').value = '';
            document.getElementById('blocInput').value = '';
        } else {
            document.getElementById('successError').textContent = body.message || 'Erreur inconnue';
        }
    })
    .catch(() => {
        document.getElementById('successError').textContent = 'Erreur réseau';
    });
}

function resetAll() {
    savedClimberBib = null;
    savedBlocTag = null;
    document.getElementById('climberInput').value = '';
    document.getElementById('blocInput').value = '';
    document.getElementById('climberError').textContent = '';
    document.getElementById('blocError').textContent = '';
    document.getElementById('successError').textContent = '';
}

// Ajout du scan QRCode avec html5-qrcode
let qrScanner = null;
let currentScanTarget = null;

function startQrScan(targetInputId) {
    currentScanTarget = targetInputId;
    const qrRegion = document.getElementById('qr-region');
    qrRegion.style.display = 'block';

    if (!qrScanner) {
        qrScanner = new Html5Qrcode("qr-reader");
    }
    qrScanner.start(
        { facingMode: "environment" },
        {
            fps: 10,
            qrbox: 250
        },
        qrCodeMessage => {
            document.getElementById(targetInputId).value = qrCodeMessage;
            stopQrScan();
        },
        errorMessage => {
            // ignore scan errors
        }
    ).catch(err => {
        document.getElementById('qr-error').textContent = "Erreur caméra : " + err;
    });
}

function stopQrScan() {
    if (qrScanner) {
        qrScanner.stop().then(() => {
            document.getElementById('qr-region').style.display = 'none';
            document.getElementById('qr-error').textContent = '';
        });
    }
}

// Ajoute les boutons de scan au chargement de la page
window.addEventListener('DOMContentLoaded', () => {
    // Ajoute le bouton scan grimpeur
    const climberScanBtn = document.createElement('button');
    climberScanBtn.textContent = 'Scanner QR Grimpeur';
    climberScanBtn.onclick = () => startQrScan('climberInput');
    document.getElementById('climberInput').parentNode.appendChild(climberScanBtn);

    // Ajoute le bouton scan bloc
    const blocScanBtn = document.createElement('button');
    blocScanBtn.textContent = 'Scanner QR Bloc';
    blocScanBtn.onclick = () => startQrScan('blocInput');
    document.getElementById('blocInput').parentNode.appendChild(blocScanBtn);

    // Ajoute la région d'affichage du scanner
    const qrRegion = document.createElement('div');
    qrRegion.id = 'qr-region';
    qrRegion.style.display = 'none';
    qrRegion.innerHTML = `
        <div id="qr-reader" style="width:300px"></div>
        <div id="qr-error" class="error"></div>
        <button onclick="stopQrScan()">Fermer le scan</button>
    `;
    document.body.appendChild(qrRegion);
});
