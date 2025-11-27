const { createApp } = Vue;

createApp({
    // Utilisation de [[ ]] pour ne pas entrer en conflit avec Flask Jinja2 si besoin
    compilerOptions: {
        delimiters: ['[[', ']]']
    },
    data() {
        return {
            // climber & bloc states: 'default', 'success', 'error'
            climberState: 'default', 
            blocState: 'default',
            validateState: 'default',
            
            savedClimberBib: null,
            savedBlocTag: null,
            
            globalError: "",
            
            // Scanner logic
            qrVisible: false,
            scanTarget: null, // 'climber' ou 'bloc'
            html5QrcodeScanner: null
        };
    },
    computed: {
        climberStatusClass() {
            return `status-${this.climberState}`;
        },
        blocStatusClass() {
            return `status-${this.blocState}`;
        },
        validateStatusClass() {
            return `status-${this.validateState}`;
        },
        climberLabel() {
            if (this.climberState === 'success') return "Grimpeur OK";
            if (this.climberState === 'error') return "Inconnu";
            return "Scanner Grimpeur";
        },
        blocLabel() {
            if (this.blocState === 'success') return "Bloc OK";
            if (this.blocState === 'error') return "Inconnu";
            return "Scanner Bloc";
        },
        canValidate() {
            // Le bouton valider n'est cliquable que si on a les deux infos valides
            return (this.climberState === 'success' && this.blocState === 'success' && this.validateState !== 'success');
        }
    },
    methods: {
        // --- API Helper ---
        async apiPost(url, body) {
            try {
                const res = await fetch(url, {
                    method: "POST",
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(body)
                });
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return await res.json();
            } catch (err) {
                console.error(err);
                return { success: false, message: "Erreur de connexion serveur" };
            }
        },

        // --- Logique Grimpeur ---
        async verifyClimber(bib) {
            // Reset état temporaire
            this.climberState = 'default';
            
            const res = await this.apiPost('/api/v2/contest/climber/name', { id: bib });
            
            if (res.success) {
                this.savedClimberBib = bib;
                this.climberState = 'success';
                this.globalError = "";
            } else {
                this.savedClimberBib = null;
                this.climberState = 'error';
                // On peut afficher l'erreur spécifique si besoin
                // this.globalError = res.message;
            }
        },

        // --- Logique Bloc ---
        async verifyBloc(tag) {
            this.blocState = 'default';
            
            const res = await this.apiPost('/api/v2/contest/bloc/name', { id: tag });
            
            if (res.success) {
                this.savedBlocTag = tag;
                this.blocState = 'success';
                this.globalError = "";
            } else {
                this.savedBlocTag = null;
                this.blocState = 'error';
            }
        },

        // --- Validation Finale ---
        async sendSuccess() {
            if (!this.canValidate) return;

            // Appel API
            const res = await this.apiPost('/api/v2/contest/success', {
                bib: this.savedClimberBib,
                bloc: this.savedBlocTag
            });

            if (res.success) {
                // 1. Bouton passe au vert
                this.validateState = 'success';
                
                // 2. Timer de 1.5 secondes
                setTimeout(() => {
                    // 3. Reset total
                    this.resetAll();
                }, 1500);
            } else {
                // Erreur serveur
                this.validateState = 'error';
                this.globalError = res.message || "Erreur lors de la validation";
                
                // On repasse en gris après un court délai pour permettre de réessayer
                setTimeout(() => {
                    this.validateState = 'default';
                }, 2000);
            }
        },

        // --- Reset ---
        resetAll() {
            this.climberState = 'default';
            this.blocState = 'default';
            this.validateState = 'default';
            this.savedClimberBib = null;
            this.savedBlocTag = null;
            this.globalError = "";
            this.scanTarget = null;
        },

        // --- Scanner Logic ---
        startScan(target) {
            this.scanTarget = target;
            this.qrVisible = true;
            
            // Attendre que le DOM se mette à jour pour que la div #qr-reader existe
            this.$nextTick(() => {
                const html5QrCode = new Html5Qrcode("qr-reader");
                this.html5QrcodeScanner = html5QrCode;

                const config = { fps: 10, qrbox: { width: 250, height: 250 } };
                
                // Préférer la caméra arrière (environment)
                html5QrCode.start({ facingMode: "environment" }, config, this.onScanSuccess)
                .catch(err => {
                    this.globalError = "Impossible d'accéder à la caméra.";
                    this.qrVisible = false;
                });
            });
        },

        onScanSuccess(decodedText, decodedResult) {
            // Arrêter le scan
            this.stopScan().then(() => {
                // Traiter le résultat
                if (this.scanTarget === 'climber') {
                    this.verifyClimber(decodedText);
                } else if (this.scanTarget === 'bloc') {
                    this.verifyBloc(decodedText);
                }
            });
        },

        async stopScan() {
            if (this.html5QrcodeScanner) {
                try {
                    await this.html5QrcodeScanner.stop();
                    this.html5QrcodeScanner.clear();
                } catch (e) {
                    console.log("Erreur stop scan", e);
                }
                this.html5QrcodeScanner = null;
            }
            this.qrVisible = false;
            this.scanTarget = null;
        }
    }
}).mount('#app');