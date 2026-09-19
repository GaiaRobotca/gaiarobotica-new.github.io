

(() => {
  const search = document.getElementById('article-search');
  const cards = [...document.querySelectorAll('.learn-card')];
  const filters = [...document.querySelectorAll('[data-filter]')];
  const count = document.getElementById('results-count');
  const empty = document.getElementById('empty-results');
  let category = 'todos';
  const normalize = text => text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
  function update() {
    const query = normalize(search.value);
    let visible = 0;
    cards.forEach(card => {
      const matches = (category === 'todos' || card.dataset.categories.split(' ').includes(category)) && normalize(card.textContent).includes(query);
      card.hidden = !matches;
      if (matches) visible++;
    });
    filters.forEach(button => {
      const selected = button.dataset.filter === category;
      button.classList.toggle('active', selected);
      button.setAttribute('aria-pressed', String(selected));
    });
    count.textContent = visible + (visible === 1 ? ' guia encontrado' : ' guias encontrados');
    empty.hidden = visible > 0;
  }
  filters.forEach(button => button.addEventListener('click', () => { category = button.dataset.filter; update(); }));
  search.addEventListener('input', update);
  document.getElementById('reset-search').addEventListener('click', () => { search.value = ''; category = 'todos'; update(); search.focus(); });
})();
