/* Progressive enhancements: content and links remain usable without JavaScript. */
(() => {
  const button = document.querySelector('.site-menu-toggle');
  const menu = document.querySelector('.site-links');
  const setOpen = (open) => {
    if (!button || !menu) return;
    button.setAttribute('aria-expanded', String(open));
    button.setAttribute('aria-label', open ? 'Fechar menu' : 'Abrir menu');
    button.textContent = open ? '×' : '☰';
    menu.classList.toggle('is-open', open);
  };
  if (button && menu) {
    button.addEventListener('click', () => setOpen(button.getAttribute('aria-expanded') !== 'true'));
    menu.addEventListener('click', (event) => { if (event.target.closest('a')) setOpen(false); });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && button.getAttribute('aria-expanded') === 'true') {
        setOpen(false);
        button.focus();
      }
    });
    document.addEventListener('click', (event) => { if (!event.target.closest('.site-header')) setOpen(false); });
    matchMedia('(min-width: 801px)').addEventListener('change', () => setOpen(false));
  }

  const progress = document.querySelector('.rp-fill');
  if (progress) {
    const update = () => {
      const height = document.documentElement.scrollHeight - innerHeight;
      progress.style.width = `${height > 0 ? Math.min(100, Math.max(0, scrollY / height * 100)) : 0}%`;
    };
    addEventListener('scroll', update, { passive: true });
    addEventListener('resize', update);
    update();
  }
  const toc = [...document.querySelectorAll('.toc-list a[href^="#"]')];
  if (toc.length && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        toc.forEach((link) => {
          if (link.hash === `#${entry.target.id}`) link.setAttribute('aria-current', 'location');
          else link.removeAttribute('aria-current');
        });
      });
    }, { rootMargin: '-100px 0px -55% 0px' });
    toc.forEach((link) => { const section = document.getElementById(link.hash.slice(1)); if (section) observer.observe(section); });
  }
  document.querySelectorAll('.code-wrap').forEach((wrapper) => {
    const pre = wrapper.querySelector('pre');
    const header = wrapper.querySelector('.code-header');
    if (!pre || !header || !navigator.clipboard) return;
    const copy = document.createElement('button');
    copy.className = 'copy-code';
    copy.type = 'button';
    copy.textContent = 'Copiar código';
    copy.setAttribute('aria-live', 'polite');
    copy.addEventListener('click', async () => {
      try { await navigator.clipboard.writeText(pre.textContent); copy.textContent = 'Copiado!'; }
      catch { copy.textContent = 'Selecione e copie o código'; }
      setTimeout(() => { copy.textContent = 'Copiar código'; }, 2500);
    });
    header.append(copy);
  });

  document.querySelectorAll('.carousel-track').forEach((track) => {
    const slides = [...track.children];
    if (!slides.length) return;
    const container = track.closest('.carousel-container, .carousel, .gallery-carousel') || track.parentElement.parentElement;
    const next = container.querySelector('.carousel-btn.next');
    const previous = container.querySelector('.carousel-btn.prev');
    const current = document.getElementById('currentSlide');
    const total = document.getElementById('totalSlides');
    const dots = document.getElementById('carouselDots');
    let index = 0;
    container.setAttribute('role', 'region');
    container.setAttribute('aria-label', 'Galeria de fotos');
    container.tabIndex = 0;
    if (total) total.textContent = String(slides.length).padStart(2, '0');
    if (current) current.setAttribute('aria-live', 'polite');
    const update = () => {
      track.style.transform = `translateX(-${index * 100}%)`;
      if (current) current.textContent = String(index + 1).padStart(2, '0');
      slides.forEach((slide, i) => { slide.setAttribute('aria-hidden', String(i !== index)); slide.inert = i !== index; });
      if (dots) [...dots.children].forEach((dot, i) => {
        dot.classList.toggle('active', i === index);
        dot.setAttribute('aria-pressed', String(i === index));
      });
    };
    if (dots) slides.forEach((_, i) => {
      const dot = document.createElement('button');
      dot.type = 'button';
      dot.className = 'carousel-dot';
      dot.setAttribute('aria-label', `Ir para foto ${i + 1}`);
      dot.addEventListener('click', () => { index = i; update(); });
      dots.append(dot);
    });
    const advance = (direction) => { index = (index + direction + slides.length) % slides.length; update(); };
    if (next) { next.setAttribute('aria-label', 'Próxima foto'); next.addEventListener('click', () => advance(1)); }
    if (previous) { previous.setAttribute('aria-label', 'Foto anterior'); previous.addEventListener('click', () => advance(-1)); }
    container.addEventListener('keydown', (event) => {
      if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') { event.preventDefault(); advance(event.key === 'ArrowRight' ? 1 : -1); }
    });
    update();
  });
})();
