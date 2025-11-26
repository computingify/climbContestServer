const { createApp } = Vue;

createApp({
    // C'est ici que l'on résout le conflit avec Jinja2 (Flask)
    // On utilise [[ ]] pour Vue, laissant {{ }} à Flask.
    compilerOptions: {
        delimiters: ['[[', ']]']
    },
    data() {
        return {
            ranking: {},
            previousRanking: {},
            loading: false
        };
    },
    methods: {
        async refreshRanking() {
            this.loading = true;
            try {
                const res = await fetch('/api/v2/contest/ranking_by_categories');
                const data = await res.json();

                // Gestion des animations de montée/descente
                for (const cat in data) {
                    const prev = this.previousRanking[cat] || [];
                    const bibToPrevRank = {};
                    prev.forEach((entry, idx) => { bibToPrevRank[entry.bib] = idx; });

                    data[cat].forEach((entry, idx) => {
                        entry._movement = '';
                        const prevRank = bibToPrevRank[entry.bib];
                        if (prevRank !== undefined) {
                            if (prevRank > idx) entry._movement = 'up'; // Monte au classement
                            else if (prevRank < idx) entry._movement = 'down'; // Descend
                        }
                    });
                }

                this.previousRanking = JSON.parse(JSON.stringify(data));
                this.ranking = data;

                // Nettoyer les statuts de mouvement après 2s
                setTimeout(() => {
                    for (const cat in this.ranking) {
                        this.ranking[cat].forEach(e => e._movement = '');
                    }
                }, 2000);

            } catch (err) {
                console.error('Erreur récupération ranking:', err);
            } finally {
                this.loading = false;
            }
        },
        getRowClass(category, idx) {
            const entry = this.ranking[category]?.[idx];
            let classes = [];
            
            // Animation mouvement
            if (entry?._movement) classes.push(entry._movement);
            
            // Podium styling
            if (idx === 0) classes.push('rank-1');
            if (idx === 1) classes.push('rank-2');
            if (idx === 2) classes.push('rank-3');
            
            return classes.join(' ');
        }
    },
    mounted() {
        this.refreshRanking();
        // Rafraichissement automatique toutes les 15 secondes
        setInterval(this.refreshRanking, 15000);
    }
}).mount('#app');