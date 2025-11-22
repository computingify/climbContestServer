document.addEventListener('DOMContentLoaded', () => {
  let rankingDiv = document.getElementById('rankingDiv');
  if (!rankingDiv) {
    rankingDiv = document.createElement('div');
    rankingDiv.id = 'rankingDiv';
    const h1 = document.querySelector('h1');
    h1.parentNode.insertBefore(rankingDiv, h1.nextSibling);
  }

  let previousranking = {};

  // Ajoute le bouton de rafraîchissement manuel
  const refreshBtn = document.createElement('button');
  refreshBtn.textContent = 'Forcer le rafraîchissement';
  refreshBtn.style.marginBottom = '18px';
  refreshBtn.style.fontSize = '1.1em';
  refreshBtn.style.padding = '8px 18px';
  refreshBtn.onclick = () => refreshranking();
  rankingDiv.parentNode.insertBefore(refreshBtn, rankingDiv);

  function refreshranking() {
    fetch('/api/v2/contest/ranking_by_categories')
      .then(r => r.json())
      .then(data => {
        let html = '';
        for (const [cat, entries] of Object.entries(data)) {
          html += `<h3>Catégorie : ${cat}</h3>`;
          html += `<table class="ranking-table"><thead><tr>
            <th>Place</th>
            <th>Dossard</th>
            <th>Nom</th>
            <th>Club</th>
            <th>Score</th>
          </tr></thead><tbody>`;

          let prev = previousranking[cat] || [];
          let bibToPrevRank = {};
          prev.forEach((entry, idx) => { bibToPrevRank[entry.bib] = idx; });

          entries.forEach((entry, idx) => {
            let prevRank = bibToPrevRank[entry.bib];
            let animClass = '';
            if (prevRank !== undefined) {
              if (prevRank > idx) animClass = 'row-up';
              else if (prevRank < idx) animClass = 'row-down';
            }
            html += `<tr class="${animClass}">
              <td>${idx + 1}</td>
              <td>${entry.bib}</td>
              <td>${entry.name}</td>
              <td>${entry.club}</td>
              <td>${entry.score}</td>
            </tr>`;
          });
          html += `</tbody></table>`;
          previousranking[cat] = entries;
        }
        rankingDiv.innerHTML = html;

        // Animation
        document.querySelectorAll('.row-up, .row-down').forEach(row => {
          row.classList.remove('row-up');
          row.classList.remove('row-down');
          void row.offsetWidth;
        });
        setTimeout(() => {
          document.querySelectorAll('.ranking-table tr').forEach(row => {
            if (row.classList.contains('row-up') || row.classList.contains('row-down')) {
              row.classList.remove('row-up');
              row.classList.remove('row-down');
            }
          });
        }, 3500);
      })
      .catch(err => {
        rankingDiv.textContent = 'Erreur lors de la récupération du ranking: ' + err;
      });
  }

  // Rafraîchit le ranking toutes les 20 secondes
  setInterval(refreshranking, 20000);
  refreshranking();
});
