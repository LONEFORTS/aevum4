/* Aevum — cinematic starfield for the auth experience */
(function () {
  const cv = document.getElementById('stars');
  if (!cv) return;
  const ctx = cv.getContext('2d');
  let W, H, stars = [], meteors = [];
  const DPR = Math.min(window.devicePixelRatio || 1, 2);

  function resize() {
    W = cv.width = innerWidth * DPR;
    H = cv.height = innerHeight * DPR;
    cv.style.width = innerWidth + 'px';
    cv.style.height = innerHeight + 'px';
  }
  resize();
  addEventListener('resize', resize);

  const COUNT = Math.min(220, Math.floor(innerWidth / 5));
  for (let i = 0; i < COUNT; i++) {
    stars.push({
      x: Math.random(), y: Math.random(),
      r: (Math.random() * 1.3 + 0.3) * DPR,
      tw: Math.random() * Math.PI * 2,
      sp: 0.004 + Math.random() * 0.012,
      hue: Math.random() < 0.12 ? 'rgba(142,205,248,' : 'rgba(231,233,234,'
    });
  }
  function spawnMeteor() {
    meteors.push({
      x: Math.random() * W * 0.8, y: Math.random() * H * 0.3,
      vx: (5 + Math.random() * 4) * DPR, vy: (2 + Math.random() * 1.6) * DPR,
      life: 1
    });
    setTimeout(spawnMeteor, 3500 + Math.random() * 5000);
  }
  setTimeout(spawnMeteor, 2000);

  function frame() {
    ctx.clearRect(0, 0, W, H);
    for (const s of stars) {
      s.tw += s.sp;
      const a = 0.25 + Math.abs(Math.sin(s.tw)) * 0.75;
      ctx.beginPath();
      ctx.arc(s.x * W, s.y * H, s.r, 0, Math.PI * 2);
      ctx.fillStyle = s.hue + a + ')';
      ctx.fill();
    }
    meteors = meteors.filter(m => m.life > 0);
    for (const m of meteors) {
      m.x += m.vx; m.y += m.vy; m.life -= 0.014;
      const grad = ctx.createLinearGradient(m.x, m.y, m.x - m.vx * 12, m.y - m.vy * 12);
      grad.addColorStop(0, 'rgba(142,205,248,' + (0.8 * m.life) + ')');
      grad.addColorStop(1, 'rgba(142,205,248,0)');
      ctx.strokeStyle = grad;
      ctx.lineWidth = 1.4 * DPR;
      ctx.beginPath();
      ctx.moveTo(m.x, m.y);
      ctx.lineTo(m.x - m.vx * 12, m.y - m.vy * 12);
      ctx.stroke();
    }
    requestAnimationFrame(frame);
  }
  frame();
})();
