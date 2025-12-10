(() => {
  const qs = s => document.querySelector(s);
  const qsa = s => Array.from(document.querySelectorAll(s));

  /* Reveal on scroll (stagger) */
  function initReveal() {
    const io = new IntersectionObserver((entries, obs) => {
      entries.forEach(en => {
        if (en.isIntersecting) {
          const el = en.target;
          el.classList.add('show');
          obs.unobserve(el);
        }
      });
    }, { threshold: 0.12 });
    qsa('.reveal').forEach(el => io.observe(el));
  }

  /* Parallax blobs */
  function initParallax() {
    const blobs = qsa('.blob');
    if (!blobs.length) return;
    let mouse = { x: 0, y: 0 };
    let wh = window.innerHeight, ww = window.innerWidth;
    window.addEventListener('mousemove', e => { mouse.x = (e.clientX/ww)-0.5; mouse.y = (e.clientY/wh)-0.5; });
    window.addEventListener('resize', () => { wh = innerHeight; ww = innerWidth; });

    function tick() {
      blobs.forEach((b, i) => {
        const depth = (i+1)*8;
        b.style.transform = `translate3d(${mouse.x*depth}px, ${mouse.y*depth}px, 0)`;
      });
      requestAnimationFrame(tick);
    }
    tick();
  }

  /* Buttons: ripple + optional magnetic */
  function initButtons() {
    document.addEventListener('click', e => {
      const btn = e.target.closest('.btn');
      if (!btn) return;
      const rect = btn.getBoundingClientRect();
      const ripple = document.createElement('span');
      ripple.className = 'ripple';
      const size = Math.max(rect.width, rect.height)*1.2;
      ripple.style.width = ripple.style.height = size + 'px';
      ripple.style.left = (e.clientX - rect.left - size/2) + 'px';
      ripple.style.top = (e.clientY - rect.top - size/2) + 'px';
      btn.appendChild(ripple);
      setTimeout(()=> ripple.remove(), 650);
    });

    qsa('.btn-magnetic').forEach(btn => {
      btn.addEventListener('mousemove', e => {
        const r = btn.getBoundingClientRect();
        const dx = (e.clientX - r.left) - r.width/2;
        const dy = (e.clientY - r.top) - r.height/2;
        btn.style.transform = `translate3d(${dx*0.02}px, ${dy*0.02}px, 0) scale(1.02)`;
      });
      btn.addEventListener('mouseleave', () => btn.style.transform = '');
    });
  }

  /* File drop zones */
  function initFileDrop() {
    qsa('.file-drop').forEach(drop => {
      const input = drop.querySelector('input[type=file]');
      const label = drop.querySelector('.file-name') || drop;
      ['dragenter','dragover'].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.add('dragover'); }));
      ['dragleave','drop','mouseout'].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.remove('dragover'); }));
      drop.addEventListener('drop', e => {
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
          input.files = e.dataTransfer.files;
          label.textContent = e.dataTransfer.files[0].name;
        }
      });
      input && input.addEventListener('change', () => {
        const f = input.files[0];
        label.textContent = f ? f.name : 'No file selected';
      });
      drop.addEventListener('click', () => input && input.click());
    });
  }

  /* Fake progress for forms */
  function initFakeProgress() {
    qsa('form[data-fake-progress]').forEach(form => {
      form.addEventListener('submit', () => {
        form.querySelectorAll('button,input[type=submit]').forEach(b => b.disabled = true);
        if (!form._bar) {
          const wrap = document.createElement('div'); wrap.className = 'progress-wrap'; wrap.style.marginTop='12px';
          const bar = document.createElement('div'); bar.className='progress-bar'; bar.style.width='6%';
          wrap.appendChild(bar); form.appendChild(wrap); form._bar = bar;
          setTimeout(()=> bar.style.width='30%', 120); setTimeout(()=> bar.style.width='58%', 700); setTimeout(()=> bar.style.width='86%',1600);
        }
      });
    });
  }

  function init() {
    initReveal(); initParallax(); initButtons(); initFileDrop(); initFakeProgress();
    // small burst on primary hover
    qsa('.btn-primary').forEach(b => b.addEventListener('mouseenter', ()=> {
      b.animate([{ transform:'scale(.98)' }, { transform:'scale(1.02)' }, { transform:'scale(1)' }], { duration:400, easing:'cubic-bezier(.2,.9,.2,1)' });
    }));
  }

  if (document.readyState==='loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
