document.addEventListener('DOMContentLoaded', () => {
  const climberSelect = document.getElementById('climberSelect');
  const blocSelect = document.getElementById('blocSelect');
  const checkClimberBtn = document.getElementById('checkClimberBtn');
  const checkBlocBtn = document.getElementById('checkBlocBtn');
  const successBtn = document.getElementById('successBtn');
  const resultArea = document.getElementById('resultArea');

  // Charger options depuis /api/v2/contest/options
  fetch('/api/v2/contest/options')
    .then(r => r.json())
    .then(data => {
      data.climbers.forEach(c => {
        const opt = document.createElement('option');
        // visible: name, value: bib (pour l'API /climber/name attend 'id' = bib)
        opt.value = c.bib;
        opt.textContent = c.name;
        climberSelect.appendChild(opt);
      });
      data.blocs.forEach(b => {
        const opt = document.createElement('option');
        opt.value = b.tag;
        opt.textContent = b.tag;
        blocSelect.appendChild(opt);
      });
    })
    .catch(err => {
      resultArea.textContent = 'Erreur lors du chargement des options: ' + err;
    });

  function updateButtonsState() {
    checkClimberBtn.disabled = climberSelect.value === '';
    checkBlocBtn.disabled = blocSelect.value === '';
    successBtn.disabled = (climberSelect.value === '' || blocSelect.value === '');
  }

  climberSelect.addEventListener('change', updateButtonsState);
  blocSelect.addEventListener('change', updateButtonsState);

  checkClimberBtn.addEventListener('click', () => {
    const payload = { id: climberSelect.value }; // id = bib attendu par l'API
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