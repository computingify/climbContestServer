document.addEventListener('DOMContentLoaded', () => {
  const climberSelect = document.getElementById('climberSelect');
  const blocSelect = document.getElementById('blocSelect');
  const checkClimberBtn = document.getElementById('checkClimberBtn');
  const checkBlocBtn = document.getElementById('checkBlocBtn');
  const successBtn = document.getElementById('successBtn');
  const resultArea = document.getElementById('resultArea');

  // Charger options depuis /api/v2/contest/climber/all
  fetch('/api/v2/contest/climber/all')
    .then(r => r.json())
    .then(data => {
      // Nettoie les options existantes sauf la première
      while (climberSelect.options.length > 1) climberSelect.remove(1);
      while (blocSelect.options.length > 1) blocSelect.remove(1);

      data.climbers.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c.bib;
        opt.textContent = c.name;
        climberSelect.appendChild(opt);
      });

      // On ne remplit plus les blocs ici, on attend la sélection du grimpeur
      updateButtonsState();
    })
    .catch(err => {
      resultArea.textContent = 'Erreur lors du chargement des options: ' + err;
    });

  function updateButtonsState() {
    checkClimberBtn.disabled = climberSelect.value === '';
    checkBlocBtn.disabled = blocSelect.value === '';
    successBtn.disabled = (climberSelect.value === '' || blocSelect.value === '');
  }

  climberSelect.addEventListener('change', () => {
    updateButtonsState();
    // Remplit la liste des blocs associés au grimpeur sélectionné
    const bib = climberSelect.value;
    // Vide la liste des blocs sauf la première option
    while (blocSelect.options.length > 1) blocSelect.remove(1);

    if (bib) {
      fetch(`/api/v2/contest/climber/blocs?bib=${encodeURIComponent(bib)}`)
        .then(r => r.json())
        .then(data => {
          // data doit être une liste de blocs [{tag: ...}, ...]
          data.forEach(b => {
            const opt = document.createElement('option');
            opt.value = b.tag;
            opt.textContent = b.tag;
            blocSelect.appendChild(opt);
          });
          updateButtonsState();
        })
        .catch(err => {
          resultArea.textContent = 'Erreur lors du chargement des blocs du grimpeur: ' + err;
        });
    }
  });

  blocSelect.addEventListener('change', updateButtonsState);

  checkClimberBtn.addEventListener('click', () => {
    const payload = { id: climberSelect.value };
    fetch('/api/v2/contest/climber/name', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    .then(r => r.json().then(j => ({ok: r.ok, status: r.status, body: j})))
    .then(res => {
      resultArea.textContent = JSON.stringify(res, null, 2);
    })
    .catch(err => {
      resultArea.textContent = 'Erreur: ' + err;
    });
  });

  checkBlocBtn.addEventListener('click', () => {
    const payload = { id: blocSelect.value };
    fetch('/api/v2/contest/bloc/name', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    .then(r => r.json().then(j => ({ok: r.ok, status: r.status, body: j})))
    .then(res => {
      resultArea.textContent = JSON.stringify(res, null, 2);
    })
    .catch(err => {
      resultArea.textContent = 'Erreur: ' + err;
    });
  });

  successBtn.addEventListener('click', () => {
    const payload = { bib: climberSelect.value, bloc: blocSelect.value };
    fetch('/api/v2/contest/success', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    .then(r => r.json().then(j => ({ok: r.ok, status: r.status, body: j})))
    .then(res => {
      resultArea.textContent = JSON.stringify(res, null, 2);
    })
    .catch(err => {
      resultArea.textContent = 'Erreur: ' + err;
    });
  });
});