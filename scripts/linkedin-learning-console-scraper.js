/**
 * LinkedIn Learning course scraper (v3) — paste into the Chrome DevTools console
 * while on: https://www.linkedin.com/learning/search?entityType=COURSE
 *
 * v3 changes:
 *   - Scrolls the LAST course card into view each round (trips
 *     IntersectionObserver-based infinite loaders that ignore scrollTop).
 *   - Clicks "Show more" buttons with a full pointer-event sequence
 *     (pointerdown/mousedown/pointerup/mouseup/click) — LinkedIn's framework
 *     often ignores a bare .click().
 *   - Logs which button it found/clicked so stalls are diagnosable.
 *   - Rows persist in window.__LLS_DATA across re-runs; manual scrolling is
 *     harvested too. Export any time with __LLS_EXPORT().
 *
 * Controls:
 *   window.__LLS_STOP = true   // stop auto-scrolling
 *   __LLS_EXPORT()             // download CSV of everything collected so far
 */
(async function scrapeLinkedInLearningV3() {
  const PAUSE_MS = 2000, MAX_IDLE = 10, MAX_ROUNDS = 400;
  window.__LLS_STOP = false;
  const data = (window.__LLS_DATA = window.__LLS_DATA || new Map());
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  function getCards() {
    const cards = new Set();
    for (const a of document.querySelectorAll('a[href*="/learning/"]')) {
      const m = a.getAttribute('href').match(/\/learning\/([^/?#]+)/);
      if (!m) continue;
      if (['search','me','topics','browse','subscription','paths','instructors'].includes(m[1])) continue;
      const card = a.closest('li, section, div[data-item-index]');
      if (card && card.innerText && card.innerText.trim().length > 10) cards.add(card);
    }
    return [...cards];
  }

  function parseCard(card) {
    const text = card.innerText.replace(/\s+/g, ' ').trim();
    let name = '';
    const heading = card.querySelector('h1,h2,h3,h4,[class*="title" i]');
    if (heading && heading.innerText.trim()) name = heading.innerText.trim();
    else { const l = card.querySelector('a[href*="/learning/"]'); if (l) name = l.innerText.trim(); }
    name = name.split('\n')[0].trim();
    const dur = text.match(/\b(\d+\s*h(?:rs?)?(?:\s*\d+\s*m(?:in)?s?)?|\d+\s*m(?:in)?s?)\b/i);
    const rat = text.match(/(\d\.\d)\s*(?:out of 5|★|\/\s*5)/i) || text.match(/\b([0-5]\.\d)\b/);
    const lrn = text.match(/([\d,.]+\s*[KkMm]?)\s*learners?/);
    const link = card.querySelector('a[href*="/learning/"]');
    return {
      name,
      length: dur ? dur[1].replace(/\s+/g, ' ').trim() : '',
      rating: rat ? rat[1] : '',
      learners: lrn ? lrn[1].replace(/\s+/g, '') : '',
      url: link ? link.href.split('?')[0] : '',
    };
  }

  function harvest() {
    for (const card of getCards()) {
      const row = parseCard(card);
      if (!row.name || (!row.length && !row.rating && !row.learners)) continue;
      const key = row.url || row.name;
      if (!data.has(key)) data.set(key, row);
    }
    return data.size;
  }

  function findMoreButton() {
    const els = [...document.querySelectorAll('button, a[role="button"], span[role="button"]')];
    const candidates = els.filter((el) => {
      const label = ((el.innerText || '') + ' ' + (el.getAttribute('aria-label') || '')).toLowerCase();
      // "Show more options for <course>" is each card's kebab menu — not pagination.
      if (/options|menu|filter|skill|save|share/.test(label)) return false;
      return /(show|load|see)\s*more|more results|show additional/.test(label);
    });
    // The pagination button sits at the bottom of the results — take the last one.
    return candidates[candidates.length - 1];
  }

  // Full pointer-event sequence — LinkedIn's framework often ignores bare .click()
  function realClick(el) {
    el.scrollIntoView({ block: 'center' });
    const opts = { bubbles: true, cancelable: true, view: window };
    for (const type of ['pointerover', 'pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click']) {
      el.dispatchEvent(new PointerEvent(type, opts));
    }
  }

  function triggerLoading() {
    const cards = getCards();
    // Scrolling the LAST card into view is what trips IntersectionObserver loaders.
    if (cards.length) cards[cards.length - 1].scrollIntoView({ block: 'end', behavior: 'instant' });
    window.scrollBy(0, 2000);
    const btn = findMoreButton();
    if (btn) { console.log('Clicking button:', JSON.stringify(btn.innerText.trim() || btn.getAttribute('aria-label'))); realClick(btn); }
    return btn;
  }

  window.__LLS_EXPORT = async function () {
    const rows = [...data.values()];
    console.table(rows, ['name', 'length', 'rating', 'learners']);
    const esc = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
    const csv = [['Course Name','Length','Rating','Learners','URL'].join(','),
      ...rows.map((r) => [r.name, r.length, r.rating, r.learners, r.url].map(esc).join(','))].join('\n');
    try { await navigator.clipboard.writeText(csv); console.log('CSV copied ✔'); } catch {}
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
    a.download = 'linkedin_learning_courses.csv';
    document.body.appendChild(a); a.click(); a.remove();
    console.log(`Exported ${rows.length} courses.`);
    return rows;
  };

  console.log('%cCollecting (v3). Manual scrolling also gets captured. Export any time: __LLS_EXPORT()', 'color:#0a66c2;font-weight:bold');
  let last = harvest(), idle = 0;
  console.log(`Starting with ${last} courses.`);
  for (let i = 0; i < MAX_ROUNDS && !window.__LLS_STOP; i++) {
    const btnFound = triggerLoading();
    await sleep(PAUSE_MS);
    const n = harvest();
    if (n > last) { console.log(`Collected ${n}…`); last = n; idle = 0; }
    else if (++idle >= MAX_IDLE) {
      console.warn(`Stalled at ${n}. Button on page: ${btnFound ? 'YES (clicked, no new results)' : 'none found'}.`);
      break;
    }
  }
  console.log(`%cFinished with ${data.size} courses.`, 'color:green;font-weight:bold');
  await window.__LLS_EXPORT();
})();
