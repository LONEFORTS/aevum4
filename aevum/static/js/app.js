/* Aevum — app interactions */
(function () {
  // mark active bottom tab
  const path = location.pathname;
  document.querySelectorAll('.bottom-tabs a').forEach(a => {
    const href = a.getAttribute('href');
    if (href && href !== '/' && path.startsWith(href)) a.classList.add('active');
    if (href === '/dashboard/' && path === '/dashboard/') a.classList.add('active');
  });

  // focus presets
  const fd = document.getElementById('focusDisplay');
  if (fd) {
    const set = m => {
      fd.textContent = String(m).padStart(2, '0') + ':00';
      const inp = document.querySelector('#focusForm [name=duration_min]');
      if (inp) inp.value = m;
    };
    [['custom25', 25], ['custom45', 45], ['custom60', 60]].forEach(([id, m]) => {
      const b = document.getElementById(id);
      if (b) b.addEventListener('click', e => { e.preventDefault(); set(m); });
    });
    const inp = document.querySelector('#focusForm [name=duration_min]');
    if (inp) inp.addEventListener('input', () => set(parseInt(inp.value || 25, 10)));
  }

  // copy link buttons
  document.querySelectorAll('[data-copy]').forEach(btn => {
    btn.addEventListener('click', () => {
      navigator.clipboard && navigator.clipboard.writeText(btn.dataset.copy);
      const old = btn.textContent;
      btn.textContent = 'Copied';
      setTimeout(() => { btn.textContent = old; }, 1400);
    });
  });
})();
