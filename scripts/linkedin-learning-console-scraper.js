/**
 * LinkedIn Learning course scraper (v2) — paste into the Chrome DevTools console
 * while on: https://www.linkedin.com/learning/search?entityType=COURSE
 *
 * v2 changes:
 *   - Scrolls every scrollable container (LinkedIn sometimes puts results in
 *     an inner pane where window.scrollTo does nothing).
 *   - Continuously harvests rows into a persistent store (window.__LLS_DATA),
 *     so you can scroll manually while it runs and re-run it after a page
 *     reload without losing earlier rows.
 *   - Waits longer (idle 10 rounds x 2s) before giving up.
 *
 * Controls:
 *   window.__LLS_STOP = true   // stop auto-scrolling
 *   __LLS_EXPORT()             // download CSV of everything collected so far
 */
(async function scrapeLinkedInLearning() {
  const SCROLL_PAUSE_MS = 2000;
  const MAX_IDLE_ROUNDS = 10;
  const MAX_ROUNDS = 400;
  window.__LLS_STOP = false;

  // Persistent store: survives re-runs in the same tab.
  const data = (window.__LLS_DATA = window.__LLS_DATA || new Map());

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  function getCards() {
    const links = document.querySelectorAll('a[href*="/learning/"]');
    const cards = new Set();
    for (const a of links) {
      const m = a.getAttribute('href').match(/\/learning\/([^/?#]+)/);
      if (!m) continue;
      const slug = m[1];
      if (['search', 'me', 'topics', 'browse', 'subscription', 'paths', 'instructors'].includes(slug)) continue;
      const card = a.closest('li, section, div[data-item-index]');
      if (card && card.innerText && card.innerText.trim().length > 10) cards.add(card);
    }
    return [...cards];
  }

  function parseCard(card) {
    const text = card.innerText.replace(/\s+/g, ' ').trim();

    let name = '';
    const heading = card.querySelector('h1,h2,h3,h4,[class*="title" i]');
    if (heading && heading.innerText.trim()) {
      name = heading.innerText.trim();
    } else {
      const link = card.querySelector('a[href*="/learning/"]');
      if (link) name = link.innerText.trim();
    }
    name = name.split('\n')[0].trim();

    let length = '';
    const dur = text.match(/\b(\d+\s*h(?:rs?)?(?:\s*\d+\s*m(?:in)?s?)?|\d+\s*m(?:in)?s?)\b/i);
    if (dur) length = dur[1].replace(/\s+/g, ' ').trim();

    let rating = '';
    const ratingMatch =
      text.match(/(\d\.\d)\s*(?:out of 5|★|\/\s*5)/i) ||
      text.match(/(?:rating[:\s]*)(\d\.\d)/i) ||
      text.match(/(\d\.\d)(?=\s*\(?[\d,.]+\s*(?:ratings?|reviews?)\)?)/i) ||
      text.match(/\b([0-5]\.\d)\b/);
    if (ratingMatch) rating = ratingMatch[1];

    let learners = '';
    const learnerMatch = text.match(/([\d,.]+\s*[KkMm]?)\s*learners?/);
    if (learnerMatch) learners = learnerMatch[1].replace(/\s+/g, '');

    const link = card.querySelector('a[href*="/learning/"]');
    const url = link ? link.href.split('?')[0] : '';

    return { name, length, rating, learners, url };
  }

  function harvest() {
    for (const card of getCards()) {
      const row = parseCard(card);
      if (!row.name) continue;
      if (!row.length && !row.rating && !row.learners) continue; // instructor sub-cards
      const key = row.url || row.name;
      if (!data.has(key)) data.set(key, row);
    }
    return data.size;
  }

  // Every element that can actually scroll, plus the document itself.
  function scrollables() {
    const els = [document.scrollingElement || document.documentElement];
    for (const el of document.querySelectorAll('div, main, section, ul')) {
      const s = getComputedStyle(el);
      if (/(auto|scroll)/.test(s.overflowY) && el.scrollHeight > el.clientHeight + 200) {
        els.push(el);
      }
    }
    return els;
  }

  function scrollEverything() {
    for (const el of scrollables()) el.scrollTop = el.scrollHeight;
    window.scrollTo(0, document.body.scrollHeight);
    // Nudge lazy-loaders that listen for keyboard/scroll events.
    window.dispatchEvent(new Event('scroll'));
    const btn = [...document.querySelectorAll('button')].find((b) =>
      /show more|see more|load more/i.test(b.innerText)
    );
    if (btn && btn.offsetParent !== null) btn.click();
  }

  window.__LLS_EXPORT = async function exportCsv() {
    const rows = [...data.values()];
    console.table(rows, ['name', 'length', 'rating', 'learners']);
    const esc = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
    const csv = [
      ['Course Name', 'Length', 'Rating', 'Learners', 'URL'].join(','),
      ...rows.map((r) => [r.name, r.length, r.rating, r.learners, r.url].map(esc).join(',')),
    ].join('\n');
    try {
      await navigator.clipboard.writeText(csv);
      console.log('CSV copied to clipboard ✔');
    } catch {
      console.warn('Clipboard blocked — use the downloaded file.');
    }
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
    a.download = 'linkedin_learning_courses.csv';
    document.body.appendChild(a);
    a.click();
    a.remove();
    console.log(`Exported ${rows.length} courses.`);
    return rows;
  };

  console.log(
    '%cCollecting… You can ALSO scroll manually — everything that appears gets captured.\n' +
      'Stop: window.__LLS_STOP = true   Export any time: __LLS_EXPORT()',
    'color:#0a66c2;font-weight:bold'
  );

  let lastCount = harvest();
  console.log(`Starting with ${lastCount} courses already collected.`);
  let idleRounds = 0;
  for (let round = 0; round < MAX_ROUNDS && !window.__LLS_STOP; round++) {
    scrollEverything();
    await sleep(SCROLL_PAUSE_MS);
    const count = harvest();
    if (count > lastCount) {
      console.log(`Collected ${count} courses…`);
      lastCount = count;
      idleRounds = 0;
    } else {
      idleRounds++;
      if (idleRounds >= MAX_IDLE_ROUNDS) break;
    }
  }

  console.log(`%cAuto-scroll finished with ${data.size} courses.`, 'color:green;font-weight:bold');
  await window.__LLS_EXPORT();
})();
