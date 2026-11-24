const toggle = document.querySelector('[data-menu-toggle]');
const nav = document.querySelector('[data-navigation]');
toggle?.addEventListener('click', () => {
  const open = toggle.getAttribute('aria-expanded') !== 'true';
  toggle.setAttribute('aria-expanded', String(open));
  nav.classList.toggle('is-open', open);
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && toggle?.getAttribute('aria-expanded') === 'true') {
    toggle.setAttribute('aria-expanded', 'false');
    nav.classList.remove('is-open');
    toggle.focus();
  }
});

const search = document.querySelector('[data-search]');
const filter = document.querySelector('[data-topic]');
const cards = [...document.querySelectorAll('[data-content-card]')];
function updateResults() {
  const query = search?.value.trim().toLocaleLowerCase() || '';
  const topic = filter?.value || '';
  let visible = 0;
  cards.forEach(card => {
    const match = card.dataset.search.includes(query) && (!topic || JSON.parse(card.dataset.tags).includes(topic));
    card.hidden = !match;
    if (match) visible++;
  });
  const count = document.querySelector('[data-count]');
  if (count) count.textContent = `${visible} ${visible === 1 ? 'entry' : 'entries'}`;
  const empty = document.querySelector('[data-no-results]');
  if (empty) empty.hidden = visible !== 0;
}
search?.addEventListener('input', updateResults);
filter?.addEventListener('change', updateResults);

document.querySelectorAll('.prose pre').forEach(pre => {
  const code = pre.querySelector('code');
  if (!code || code.classList.contains('language-mermaid')) return;
  const button = document.createElement('button');
  button.className = 'copy-code';
  button.textContent = 'Copy';
  button.type = 'button';
  button.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(code.textContent); button.textContent = 'Copied'; }
    catch { button.textContent = 'Select text to copy'; }
    setTimeout(() => button.textContent = 'Copy', 2000);
  });
  pre.append(button);
});

const diagramCodes = [...document.querySelectorAll('code.language-mermaid')];
if (diagramCodes.length) {
  // Only load the diagram renderer on pages that actually contain diagrams.
  import('https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.esm.min.mjs')
    .then(async ({default: mermaid}) => {
      mermaid.initialize({startOnLoad: false, securityLevel: 'strict', theme: 'base',
        themeVariables: {primaryColor:'#E4ECEA',primaryTextColor:'#182B35',primaryBorderColor:'#294753',
          lineColor:'#294753',secondaryColor:'#FAECD9',tertiaryColor:'#DCE9DF',fontFamily:'Inter, sans-serif'}});
      for (const [i, code] of diagramCodes.entries()) {
        try {
          const {svg} = await mermaid.render(`diagram-${i}`, code.textContent);
          const figure = document.createElement('figure');
          figure.className = 'diagram';
          figure.setAttribute('aria-label', 'Article diagram');
          figure.innerHTML = svg;
          code.parentElement.replaceWith(figure);
        } catch { /* Keep readable source visible if a diagram has invalid syntax. */ }
      }
    }).catch(() => { /* Diagram source remains available when offline. */ });
}
