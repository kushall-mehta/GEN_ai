/* paste inside the DOMContentLoaded callback in main.js */
  // chat: scroll to latest, quick prompts, sending state
  const thread = document.getElementById('thread'), box = document.getElementById('message'), composer = document.getElementById('composer');
  if (thread) thread.scrollTop = thread.scrollHeight;
  document.querySelectorAll('[data-prompt]').forEach(b => b.addEventListener('click', () => { box.value = b.dataset.prompt; composer.requestSubmit(); }));
  if (composer) composer.addEventListener('submit', () => {
    const send = composer.querySelector('button'); send.disabled = true; send.textContent = 'Thinking…';
  });


  document.addEventListener('DOMContentLoaded', () => {
  // mobile nav
  const toggle = document.querySelector('.nav-toggle'), links = document.querySelector('.nav-links');
  if (toggle) toggle.addEventListener('click', () => {
    const open = links.classList.toggle('open');
    toggle.setAttribute('aria-expanded', open);
  });

  // show/hide password
  document.querySelectorAll('.pw button').forEach(btn => btn.addEventListener('click', () => {
    const input = btn.parentElement.querySelector('input');
    const show = input.type === 'password';
    input.type = show ? 'text' : 'password';
    btn.textContent = show ? 'Hide' : 'Show';
  }));

  // auto-dismiss messages
  document.querySelectorAll('.msg').forEach(m => setTimeout(() => { m.style.opacity = 0; setTimeout(() => m.remove(), 400); }, 5000));

  // hero plate turns as you scroll
  const plate = document.querySelector('.plate-art svg');
  if (plate && !matchMedia('(prefers-reduced-motion: reduce)').matches)
    addEventListener('scroll', () => { plate.style.transform = `rotate(${scrollY * 0.25}deg)`; }, { passive: true });

  // chat
  const thread = document.getElementById('thread'), form = document.getElementById('composer'), box = document.getElementById('message');
  if (thread && form) {
    const el = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text) n.textContent = text; return n; };
    const inline = (parent, t) => t.split(/(\*\*[^*]+\*\*)/).forEach(p =>
      /^\*\*.+\*\*$/.test(p) ? parent.append(el('strong', '', p.slice(2, -2))) : parent.append(p));

    // turn plain coach text (paragraphs, - lists, 1. lists, **bold**) into safe DOM
    const render = box => {
      const raw = box.textContent; box.dataset.raw = raw; box.textContent = '';
      let list = null;
      raw.split('\n').forEach(line => {
        const m = line.match(/^\s*(?:[-*\u2022]|\d+[.)])\s+(.*)/);
        if (m) {
          const tag = /^\s*\d/.test(line) ? 'ol' : 'ul';
          if (!list || list.tagName.toLowerCase() !== tag) { list = el(tag); box.append(list); }
          const li = el('li'); inline(li, m[1]); list.append(li);
        } else if (line.trim()) { list = null; const p = el('p'); inline(p, line); box.append(p); }
        else list = null;
      });
      box.classList.add('done');
      const copy = el('button', 'copy', 'Copy'); copy.type = 'button';
      copy.addEventListener('click', () => navigator.clipboard.writeText(box.dataset.raw).then(() => {
        copy.textContent = 'Copied'; setTimeout(() => copy.textContent = 'Copy', 1500); }));
      box.parentElement.append(copy);
    };
    document.querySelectorAll('.bubble.coach .txt').forEach(render);

    const toEnd = () => thread.scrollTop = thread.scrollHeight;
    toEnd();

    // grow with content, Enter sends, Shift+Enter adds a line
    const grow = () => { box.style.height = 'auto'; box.style.height = box.scrollHeight + 'px'; };
    box.addEventListener('input', grow);
    box.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); form.requestSubmit(); } });

    document.querySelectorAll('[data-prompt]').forEach(b => b.addEventListener('click', () => { box.value = b.dataset.prompt; form.requestSubmit(); }));

    // show your message and a typing indicator while the coach answers
    form.addEventListener('submit', () => {
      const text = box.value.trim(); if (!text) return;
      document.getElementById('empty')?.remove();
      const me = el('div', 'bubble me'); me.append(el('small', '', 'You'), el('div', 'txt', text));
      const coach = el('div', 'bubble coach'); coach.append(el('small', '', 'Coach'));
      const dots = el('div', 'typing'); dots.setAttribute('aria-label', 'Coach is typing'); dots.append(el('i'), el('i'), el('i'));
      coach.append(dots); thread.append(me, coach); toEnd();
      const send = form.querySelector('button[type=submit]'); send.disabled = true; send.textContent = 'Thinking…';
    });
  }
});