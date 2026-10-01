(() => {
'use strict';
const EMAIL = 'gaia.robotica.uftm@gmail.com';
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const products = [
 {id:'chaveiro', name:'Chaveiro personalizado', category:'UM DETALHE SÓ SEU', description:'Seu nome, sua equipe ou sua ideia. Um pequeno detalhe para levar sua personalidade por onde for.', badge:'DO SEU JEITO', art:'key'},
 {id:'adesivo', name:'Adesivos GAIA', category:'COLE SUA PERSONALIDADE', description:'Dê uma nova cara ao notebook, à garrafa ou ao seu cantinho maker. Consulte artes e formatos.', badge:'CRIATIVIDADE QUE COLA', art:'adhesive'},
 {id:'kit', name:'Kit carrinho Arduino', category:'APRENDA CONSTRUINDO', description:'Tire a robótica do papel e comece um projeto na prática. Consulte componentes e disponibilidade.', badge:'SEU PRÓXIMO PROJETO', art:'kit'}
];
const keyArt = '<div class="keyring"></div><div class="hero-key"><img src="assets/gaia-g.svg" width="55" height="55" alt=""><strong>GAIA</strong><span>MAKE. BUILD. REPEAT.</span></div>';
const stickerArt = '<div class="sticker sticker-code">&lt;ideias&gt;<br><b>em movimento.</b><br>&lt;/ideias&gt;</div><div class="sticker sticker-round"><span>ROBÓTICA</span><img src="assets/gaia-g.svg" width="48" height="48" alt=""><span>FEITO NO GAIA</span></div><span class="mini-sticker">MAKE IT HAPPEN.</span>';
let cart = [];
try { const saved = JSON.parse(localStorage.getItem('gaia-shop-cart-v1')); if (Array.isArray(saved)) cart = products.flatMap(p => { const entry = saved.find(i => i.id === p.id); return entry && Number.isInteger(entry.quantity) && entry.quantity > 0 ? [{id:p.id, quantity:Math.min(99,entry.quantity)}] : []; }); } catch {}
function notify(message) { $('#toast').textContent = message; $('#toast').classList.add('visible'); clearTimeout(notify.timer); notify.timer = setTimeout(() => $('#toast').classList.remove('visible'), 3500); }
let activeFilter = 'todos';
let infiniteEnabled = true;
function productMarkup(items) {
 return items.map(p => `<div class="product-shell"><article class="product-card"><div class="product-visual ${p.art}" role="img" aria-label="${p.art === 'kit' ? 'Carrinhos do projeto GAIA, fotografia de referência' : 'Representação ilustrativa: '+p.name}"><span class="product-badge">${p.badge}</span>${p.art === 'key' ? keyArt : p.art === 'adhesive' ? stickerArt : '<img src="assets/carrinhos.webp" alt="" loading="lazy" width="1200" height="1600">'}</div><div class="product-body"><span class="product-category">${p.category}</span><h3>${p.name}</h3><p>${p.description}</p><div class="product-bottom"><span class="product-price">Sob consulta<small>Vamos montar seu orçamento</small></span><button class="add-button" data-add="${p.id}" aria-label="Adicionar ${p.name} à sacola">Adicionar <span aria-hidden="true">＋</span></button></div></div></article></div>`).join('');
}
// Keep layout measurements separate from the transformed cards to avoid feedback.
const productGrid = $('#product-grid');
const motionPreference = matchMedia('(prefers-reduced-motion: reduce)');
let collectionFrame = 0;
let previousScrollY = window.scrollY;
let appendRequested = false;
let scrollIdleTimer;
function filteredProducts() {
 return products.filter(p => activeFilter === 'todos' || p.id === activeFilter);
}
function renderProducts(filter = 'todos') {
 activeFilter = filter;
 appendRequested = false;
 productGrid.innerHTML = productMarkup(filteredProducts());
 scheduleCollection();
}
function scheduleCollection() {
 if (!collectionFrame) collectionFrame = requestAnimationFrame(updateCollection);
}
function updateCollection() {
 collectionFrame = 0;
 const gridRect = productGrid.getBoundingClientRect();
 const headerBottom = $('.header').getBoundingClientRect().bottom;
 $('#produtos').style.setProperty('--collection-top', `${$('.header').offsetHeight}px`);
 const centerY = headerBottom + (innerHeight - headerBottom) / 2;
 const halfHeight = Math.max(1, (innerHeight - headerBottom) / 2);
 if (appendRequested && infiniteEnabled && gridRect.top < centerY && gridRect.bottom < innerHeight + 220 && gridRect.bottom > headerBottom) {
  const items = filteredProducts();
  productGrid.insertAdjacentHTML('beforeend', productMarkup([...items, ...items]));
 }
 appendRequested = false;
 const shells = [...productGrid.children];
 const measurements = shells.map(shell => ({shell, top:gridRect.top + shell.offsetTop, left:gridRect.left + shell.offsetLeft, width:shell.offsetWidth, height:shell.offsetHeight}));
 measurements.forEach(({shell, top, left, width, height}) => {
  if (motionPreference.matches) return;
  if (top > innerHeight + height || top + height < -height) return;
  const y = Math.max(-1, Math.min(1, (top + height / 2 - centerY) / halfHeight));
  const x = Math.max(-1, Math.min(1, (left + width / 2 - innerWidth / 2) / (innerWidth / 2)));
  const scale = 1.04 - .16 * y * y - .07 * x * x;
  shell.style.setProperty('--lens-transform', `perspective(1100px) translateY(${-y * 18}px) rotateX(${-y * 18}deg) rotateY(${x * 16}deg) scale(${scale})`);
 });
}
window.addEventListener('scroll', () => {
 productGrid.classList.add('is-scrolling');
 clearTimeout(scrollIdleTimer);
 scrollIdleTimer = setTimeout(() => productGrid.classList.remove('is-scrolling'), 160);
 appendRequested = window.scrollY > previousScrollY;
 previousScrollY = window.scrollY;
 scheduleCollection();
}, {passive:true});
window.addEventListener('resize', scheduleCollection, {passive:true});
motionPreference.addEventListener('change', scheduleCollection);
new ResizeObserver(scheduleCollection).observe(productGrid);
$('#infinite-toggle').addEventListener('click', () => {
 infiniteEnabled = !infiniteEnabled;
 $('#infinite-toggle').setAttribute('aria-pressed', String(infiniteEnabled));
 $('#infinite-toggle').textContent = infiniteEnabled ? 'Pausar rolagem infinita' : 'Retomar rolagem infinita';
});
function renderCart() {
 $('#cart-count').textContent = cart.reduce((sum,item) => sum + item.quantity, 0);
 $('#checkout-btn').disabled = !cart.length;
 $('#cart-items').innerHTML = cart.length ? cart.map(item => { const p = products.find(p => p.id === item.id); return `<article class="cart-item"><div><h3>${p.name}</h3><small>Valor sob consulta</small><button class="remove" data-remove="${p.id}" aria-label="Remover ${p.name}">Remover</button></div><div class="quantity"><button data-qty="${p.id}" data-delta="-1" aria-label="Diminuir quantidade de ${p.name}">−</button><span aria-label="Quantidade">${item.quantity}</span><button data-qty="${p.id}" data-delta="1" aria-label="Aumentar quantidade de ${p.name}" ${item.quantity >= 99 ? 'disabled' : ''}>+</button></div></article>`; }).join('') : '<div class="empty-state"><h3>Sua próxima ideia começa aqui.</h3><p>Escolha um produto da coleção para montar seu pedido.</p><button class="button secondary" data-close>Explorar produtos ↗</button></div>';
}
function saveCart() { try {localStorage.setItem('gaia-shop-cart-v1',JSON.stringify(cart));} catch {notify('Não foi possível salvar a sacola neste navegador.');} $('#order-result').hidden = true; renderCart(); }
function openDialog(id) { $(id).showModal(); }
$('#product-grid').addEventListener('click', event => { const button = event.target.closest('[data-add]'); if (!button) return; const item = cart.find(i => i.id === button.dataset.add); if (item) { if(item.quantity >= 99) {notify('Limite de 99 unidades por produto.');return;} item.quantity++; } else cart.push({id:button.dataset.add,quantity:1}); saveCart(); openDialog('#cart-dialog'); });
$('#cart-items').addEventListener('click',event => { const button = event.target.closest('[data-qty], [data-remove]'); if(!button)return; const id = button.dataset.qty || button.dataset.remove; const item = cart.find(i => i.id === id); if(!item)return; if(button.hasAttribute('data-remove')) cart = cart.filter(i => i.id !== id); else {item.quantity = Math.min(99,item.quantity+Number(button.dataset.delta)); cart = cart.filter(i=>i.quantity > 0);} saveCart(); const next = $(`[data-qty="${id}"][data-delta="${button.dataset.delta}"]`) || $('[data-qty]') || $('#cart-dialog [data-close]'); next.focus(); });
$('#cart-toggle').addEventListener('click', () => openDialog('#cart-dialog'));
$('#custom-open').addEventListener('click', () => openDialog('#custom-dialog'));
$$('dialog').forEach(dialog => { dialog.addEventListener('click',event => {if(event.target.closest('[data-close]'))dialog.close(); if(event.target === dialog){const rect=dialog.getBoundingClientRect();if(event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom)dialog.close();}}); });
$$('[data-filter]').forEach(button=>button.addEventListener('click',()=>{ $$('[data-filter]').forEach(b=>{const active=b===button;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active));});renderProducts(button.dataset.filter); }));
function updateThemeButton() {const dark=document.documentElement.dataset.theme==='dark';$('#theme-toggle').textContent=dark?'☼':'☾';$('#theme-toggle').setAttribute('aria-label',dark?'Ativar tema claro':'Ativar tema escuro');document.querySelector('meta[name="theme-color"]').content=dark?'#06132e':'#f5f8ff';}
$('#theme-toggle').addEventListener('click',()=>{const theme=document.documentElement.dataset.theme==='dark'?'light':'dark';document.documentElement.dataset.theme=theme;try{localStorage.setItem('gaia-theme',theme);}catch{}updateThemeButton();});updateThemeButton();
const initialArt=$('#hero-art').innerHTML;
const slides=[{title:'Pequenas peças.<br>Grandes <em>ideias.</em>',description:'Leve um pouco do GAIA com você. Produtos que conectam criatividade, tecnologia e vontade de transformar o mundo.',cta:'Explore a coleção',href:'#produtos',art:initialArt},{title:'Seu primeiro robô.<br>O próximo <em>passo.</em>',description:'Aprender fica mais interessante quando a ideia ganha movimento. Conheça o kit de carrinho Arduino e converse com a equipe.',cta:'Conheça o kit',href:'#produtos',art:'<img class="hero-photo" src="assets/carrinhos.webp" alt="Carrinhos Arduino do projeto GAIA alinhados na pista"><div class="photo-label">DA BANCADA PARA A PISTA ↗<br><small>Projetos da equipe. Composição do kit sob consulta.</small></div>'},{title:'Tem uma ideia?<br>Deixe a sua <em>marca.</em>',description:'Chaveiros, adesivos ou algo que ainda não saiu do papel. Vamos descobrir juntos como transformar sua ideia em uma criação.',cta:'Vamos personalizar',href:'#personalize',art:'<div class="custom-hero"><div class="art-grid"></div><div class="idea-orbit">SUA<br><em>IDEIA</em><span>↗</span></div><span class="art-note">FEITO PARA SER DIFERENTE. FEITO COM VOCÊ.</span></div>'}];
let slide=0;function showSlide(index){slide=(index+slides.length)%slides.length;const s=slides[slide];$('#hero-title').innerHTML=s.title;$('.hero-description').textContent=s.description;$('#hero-cta').innerHTML=s.cta+' <span>↗</span>';$('#hero-cta').href=s.href;$('#hero-art').innerHTML=s.art;$('#slide-number').textContent=String(slide+1).padStart(2,'0');$$('[data-slide]').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.slide)===slide)));}
$('#prev-slide').addEventListener('click',()=>showSlide(slide-1));$('#next-slide').addEventListener('click',()=>showSlide(slide+1));$$('[data-slide]').forEach(b=>b.addEventListener('click',()=>showSlide(Number(b.dataset.slide))));
$('.hero').addEventListener('keydown',event=>{if(event.key==='ArrowRight'){event.preventDefault();showSlide(slide+1);}if(event.key==='ArrowLeft'){event.preventDefault();showSlide(slide-1);}});
let touchStart;$('#hero-art').addEventListener('touchstart',e=>{touchStart=e.changedTouches[0].clientX;},{passive:true});$('#hero-art').addEventListener('touchend',e=>{const distance=e.changedTouches[0].clientX-touchStart;if(Math.abs(distance)>60)showSlide(slide+(distance<0?1:-1));},{passive:true});
function prepareEmail(subject,body,resultId) {const result=$('#'+resultId);result.hidden=false;result.querySelector('textarea').value=body;const link=document.createElement('a');link.href=`mailto:${EMAIL}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;link.hidden=true;document.body.append(link);link.click();link.remove();result.scrollIntoView({block:'nearest'});}
$('#order-form').addEventListener('submit',event=>{event.preventDefault();if(!cart.length)return;const data=new FormData(event.currentTarget);const body=`Olá, equipe GAIA! Quero consultar este pedido:\n\n${cart.map(i=>`${i.quantity} × ${products.find(p=>p.id===i.id).name}`).join('\n')}\n\nNome: ${data.get('name').trim()}\nE-mail para retorno: ${data.get('email').trim()}\n\nPersonalização e observações:\n${data.get('details').trim() || 'Nenhuma observação.'}\n\nPodem confirmar valores, disponibilidade, componentes do kit (se houver), prazo, pagamento e entrega/retirada?\n\nEntendo que este pedido está sob consulta e depende de confirmação da equipe.`;prepareEmail('Pedido pela Loja GAIA',body,'order-result');});
$('#custom-form').addEventListener('submit',event=>{event.preventDefault();const data=new FormData(event.currentTarget);const body=`Olá, equipe GAIA! Gostaria de avaliar uma ideia personalizada.\n\nNome: ${data.get('name').trim()}\nE-mail para retorno: ${data.get('email').trim()}\nTipo: ${data.get('type')}\nQuantidade estimada: ${data.get('quantity')}\nPrazo desejado: ${data.get('date') || 'A combinar'}\n\nMinha ideia:\n${data.get('details').trim()}\n\nPodem avaliar a viabilidade, o orçamento e o prazo?`;prepareEmail('Consulta de personalização — Loja GAIA',body,'custom-result');});
const suggestionDialog = $('#suggestion-dialog');
$$('[data-suggestion-open]').forEach(button => button.addEventListener('click', event => {
 event.preventDefault();
 $('#suggestion-dialog-content').append($('#suggestion-form'), $('#suggestion-result'));
 suggestionDialog.showModal();
}));
suggestionDialog.addEventListener('close', () => {
 $('#sugestoes').append($('#suggestion-form'), $('#suggestion-result'));
});
$('#suggestion-form').addEventListener('submit', event => {
 event.preventDefault();
 const data = new FormData(event.currentTarget);
 const body = `Olá, equipe GAIA! Tenho uma sugestão de novo produto para a loja.\n\nNome: ${data.get('name').trim()}\nE-mail para retorno: ${data.get('email').trim()}\n\nMinha sugestão:\n${data.get('idea').trim()}`;
 prepareEmail('Sugestão de novo produto — Loja GAIA', body, 'suggestion-result');
});
document.addEventListener('click', event => {
 if (!event.target.closest('a[href="#personalize"], a[href="#como-funciona"]')) return;
 if (infiniteEnabled) $('#infinite-toggle').click();
});
$$('[data-copy]').forEach(button=>button.addEventListener('click',async()=>{const textarea=$('#'+button.dataset.copy+' textarea');try{await navigator.clipboard.writeText(textarea.value);notify('Mensagem copiada. Cole no seu e-mail para enviar.');}catch{textarea.focus();textarea.select();notify('Selecione e copie a mensagem para enviar por e-mail.');}}));
if (/\/loja\/(?:index\.html)?$/.test(location.pathname)) {$$('[data-blog]').forEach(a=>a.href='../index.html');$$('[data-sponsor]').forEach(a=>a.href='../paginas/patrocine.html');}
$('#year').textContent=new Date().getFullYear();renderProducts();renderCart();
})();
