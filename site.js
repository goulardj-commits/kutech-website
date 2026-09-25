
/* ============================================================
   CONTACT FORM EMAIL SETUP
   Paste your free Web3Forms access key below (see the setup
   note that came with this website). Messages sent through the
   form are then emailed to the address you registered it with.
   ============================================================ */
const WEB3FORMS_ACCESS_KEY = "YOUR_WEB3FORMS_ACCESS_KEY";


(function () {
  const navLinks = document.getElementById('nav-links');
  const toggle = document.querySelector('.menu-toggle');
  toggle.addEventListener('click', () => {
    const open = navLinks.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  });
  const y = document.getElementById('year'); if (y) y.textContent = new Date().getFullYear();
})();
(function () {
  if (!document.getElementById('trace')) return;
  /* ---------- Hero: signal trace + watch list ---------- */
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const hero = document.getElementById('hero');
  const canvas = document.getElementById('trace');
  const ctx = canvas.getContext('2d');
  let started = false, t = 0, spike = 0, raf = 0;

  function size() {
    const r = canvas.getBoundingClientRect(), d = window.devicePixelRatio || 1;
    canvas.width = Math.max(1, r.width * d); canvas.height = Math.max(1, r.height * d);
    ctx.setTransform(d, 0, 0, d, 0, 0);
  }
  function y(x, w, h) {
    const base = h * 0.58;
    let v = Math.sin((x + t) * 0.045) * 5 + Math.sin((x + t * 1.7) * 0.11) * 3;
    const beat = ((x + t * 2) % 180);
    if (beat > 150 && beat < 170) v -= Math.sin((beat - 150) / 20 * Math.PI) * 22;
    if (spike > 0) { const c = w * 0.72, dist = Math.abs(x - c); if (dist < 40) v -= spike * (1 - dist / 40) * 26; }
    return base + v;
  }
  function draw() {
    const w = canvas.clientWidth, h = canvas.clientHeight;
    ctx.clearRect(0, 0, w, h);
    ctx.strokeStyle = 'rgba(169,184,206,.12)'; ctx.lineWidth = 1;
    for (let gy = 14; gy < h; gy += 20) { ctx.beginPath(); ctx.moveTo(0, gy); ctx.lineTo(w, gy); ctx.stroke(); }
    const grad = ctx.createLinearGradient(0, 0, w, 0);
    grad.addColorStop(0, 'rgba(63,193,240,0)'); grad.addColorStop(.25, 'rgba(63,193,240,.9)'); grad.addColorStop(1, spike > .05 ? '#F2A93B' : '#3FC1F0');
    ctx.beginPath();
    for (let x = 0; x <= w; x += 2) { const yy = y(x, w, h); x ? ctx.lineTo(x, yy) : ctx.moveTo(x, yy); }
    ctx.strokeStyle = grad; ctx.lineWidth = 2.2; ctx.lineJoin = 'round'; ctx.stroke();
    ctx.lineTo(w, h); ctx.lineTo(0, h); ctx.closePath();
    const fill = ctx.createLinearGradient(0, 0, 0, h); fill.addColorStop(0, 'rgba(63,193,240,.18)'); fill.addColorStop(1, 'rgba(63,193,240,0)');
    ctx.fillStyle = fill; ctx.fill();
    const ex = w - 3, ey = y(ex, w, h);
    ctx.beginPath(); ctx.arc(ex, ey, 3.5, 0, Math.PI * 2); ctx.fillStyle = '#fff'; ctx.fill();
  }
  function loop() {
    t += 1.2; spike = Math.max(0, spike - 0.012); draw();
    raf = requestAnimationFrame(loop);
  }

  const items = [...document.querySelectorAll('#watch-list .status')];
  const foot = document.getElementById('watch-foot');
  const script = [
    { i: 0, warn: 'Disk nearly full', fixed: 'Space freed', msg: 'AI cleared old log files on the file server. No action needed.' },
    { i: 1, warn: 'Update failed', fixed: 'Update applied', msg: 'A security patch failed on one laptop. It was retried and installed automatically.' },
    { i: 4, warn: 'Slow connection', fixed: 'Restored', msg: 'An office access point was restarted overnight, before anyone logged on.' },
    { i: 2, warn: 'Backup delayed', fixed: 'Re-run and verified', msg: 'A backup job was re-run and checked. Your data is safe.' }
  ];
  let step = 0;
  function cycle() {
    const s = script[step % script.length]; step++;
    const el = items[s.i], orig = el.textContent;
    el.className = 'status warn'; el.textContent = s.warn; spike = 1;
    foot.textContent = 'Something looks off. The AI is investigating...';
    setTimeout(() => { el.className = 'status fixed'; el.textContent = s.fixed; foot.textContent = s.msg; }, 1800);
    setTimeout(() => { el.className = 'status ok'; el.textContent = orig; }, 5200);
  }
  function startHero() {
    if (started) return; started = true;
    size(); draw();
    if (!reduce) { hero.classList.add('play'); loop(); setTimeout(cycle, 2600); setInterval(cycle, 7000); }
  }
  window.addEventListener('resize', () => { size(); draw(); });
  startHero();
  document.addEventListener('visibilitychange', () => {
    if (reduce || !started) return;
    if (document.hidden) cancelAnimationFrame(raf); else raf = requestAnimationFrame(loop);
  });

})();
(function () {
  /* ---------- Contact form ---------- */
  const form = document.getElementById('contact-form');
  if (!form) return;
  try { const r = new URLSearchParams(location.search).get('reason'); const sel = document.getElementById('f-reason'); if (r && sel && [...sel.options].some(o => o.value === r)) sel.value = r; } catch (_) {}
  const statusEl = document.getElementById('form-status');
  const success = document.getElementById('form-success');
  const submit = document.getElementById('f-submit');
  const reasonLabels = {};
  [...document.getElementById('f-reason').options].forEach(o => reasonLabels[o.value] = o.textContent);

  const rules = {
    name: v => v.trim().length >= 2 || 'Enter your full name.',
    email: v => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim()) || 'Enter an email address like name@company.com.',
    phone: v => !v.trim() || /^[+()\-.\s\d]{7,}$/.test(v.trim()) || 'Enter a phone number using digits, spaces or dashes.',
    reason: v => !!v || 'Choose why you are reaching out.',
    message: v => v.trim().length >= 10 || 'Add a few words so we know how to help.'
  };
  function check(name) {
    const input = form.elements[name]; const res = rules[name](input.value);
    const field = input.closest('.field'); const err = document.getElementById('e-' + name);
    const ok = res === true;
    field.classList.toggle('invalid', !ok); input.setAttribute('aria-invalid', String(!ok));
    if (err) { err.textContent = ok ? '' : res; input.setAttribute('aria-describedby', 'e-' + name); }
    return ok;
  }
  Object.keys(rules).forEach(n => form.elements[n].addEventListener('blur', () => { if (form.elements[n].value) check(n); }));
  Object.keys(rules).forEach(n => form.elements[n].addEventListener('input', () => { if (form.elements[n].closest('.field').classList.contains('invalid')) check(n); }));

  function setStatus(kind, text) { statusEl.hidden = false; statusEl.className = 'form-status ' + kind; statusEl.textContent = text; }

  form.addEventListener('submit', async e => {
    e.preventDefault();
    const bad = Object.keys(rules).filter(n => !check(n));
    if (bad.length) { form.elements[bad[0]].focus(); setStatus('bad', 'Please fix the highlighted fields and try again.'); return; }
    if (form.elements.botcheck.checked) return;
    statusEl.hidden = true;

    const d = new FormData(form);
    const reason = reasonLabels[d.get('reason')] || d.get('reason');
    const payload = {
      access_key: WEB3FORMS_ACCESS_KEY,
      subject: 'New website inquiry: ' + reason,
      from_name: 'Ku Tech website',
      name: d.get('name'), email: d.get('email'), phone: d.get('phone') || 'Not provided',
      company: d.get('company') || 'Not provided', preferred_contact: d.get('contact_preference'),
      reason: reason, message: d.get('message'), botcheck: ''
    };

    if (!WEB3FORMS_ACCESS_KEY || WEB3FORMS_ACCESS_KEY.startsWith('YOUR_')) {
      setStatus('info', 'Preview only: this form checks your entries correctly, but it is not connected to an inbox yet, so nothing was sent. Add the Web3Forms access key to start receiving these messages by email.');
      return;
    }

    submit.disabled = true; const label = submit.textContent; submit.textContent = 'Sending...';
    try {
      const r = await fetch('https://api.web3forms.com/submit', { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(payload) });
      const j = await r.json().catch(() => ({}));
      if (!r.ok || j.success === false) throw new Error(j.message || 'Request failed');
      form.reset(); form.hidden = true; success.hidden = false; success.focus();
    } catch (err) {
      setStatus('bad', 'Your message could not be sent. Check your internet connection and try again in a moment.');
    } finally { submit.disabled = false; submit.textContent = label; }
  });
  document.getElementById('f-again').addEventListener('click', () => { success.hidden = true; form.hidden = false; statusEl.hidden = true; form.elements.name.focus(); });

})();
