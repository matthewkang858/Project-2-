/**
 * Skillshare course scraper (v2) — paste into the Chrome DevTools console while on:
 * https://www.skillshare.com/en/browse?sort=popular&page=1
 *
 * Skillshare's browse page is a client-rendered app: fetching ?page=N returns
 * HTML without course cards, so v2 drives the app's own pagination instead —
 * it harvests the rendered cards, clicks the "next page" control, waits for
 * the new cards to render, and repeats until the last page.
 *
 * Extracts: class name (from the class link), length, teacher (from the
 * profile link), students if shown. Exports CSV when done.
 *
 * ~2s per page -> all 405 pages take roughly 15 minutes. Keep the tab open.
 *
 * Controls:
 *   window.__SS_STOP = true   // stop paging
 *   __SS_EXPORT()             // download CSV of everything collected so far
 *
 * Re-running in the same tab resumes from the page you're on; collected
 * rows persist in window.__SS_DATA.
 */
(async function scrapeSkillshareV2() {
  const MAX_PAGES = 405;
  const RENDER_TIMEOUT_MS = 15000; // max wait for a page of cards to render
  const SETTLE_MS = 600;           // extra settle time after cards change
  window.__SS_STOP = false;
  const data = (window.__SS_DATA = window.__SS_DATA || new Map());

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  function getCards() {
    const cards = new Set();
    for (const a of document.querySelectorAll('a[href*="/classes/"]')) {
      const card = a.closest('li, article, [class*="card" i], div');
      if (card && (card.innerText || '').trim().length > 15) cards.add(card);
    }
    return [...cards];
  }

  function parseCard(card) {
    const text = (card.innerText || '').replace(/\s+/g, ' ').trim();

    // Class name: the /classes/ link with the most text (skips thumbnail
    // links and "New" badges).
    let name = '';
    let best = '';
    for (const a of card.querySelectorAll('a[href*="/classes/"]')) {
      const t = (a.innerText || '').trim().split('\n')[0].trim();
      if (t.length > best.length) best = t;
    }
    name = best;
    if (!name || name.length < 4) {
      const heading = card.querySelector('h1,h2,h3,h4');
      if (heading) name = (heading.innerText || '').trim().split('\n')[0];
    }

    // Teacher: profile link text
    let teacher = '';
    const prof = card.querySelector('a[href*="/profile/"], a[href*="/user/"]');
    if (prof) teacher = (prof.innerText || '').trim().split('\n')[0];

    // Length: "1h 13m", "2h", "43m"
    let length = '';
    const dur = text.match(/\b(\d+h\s*\d+m|\d+\s*h(?:rs?)?\b|\d+\s*m(?:in)?s?\b)/i);
    if (dur) length = dur[1].replace(/\s+/g, ' ').trim();

    // Students if displayed
    let students = '';
    const st = text.match(/([\d,.]+\s*[KkMm]?)\s*students?/i);
    if (st) students = st[1].replace(/\s+/g, '');

    const link = card.querySelector('a[href*="/classes/"]');
    const url = link ? new URL(link.getAttribute('href'), location.origin).href.split('?')[0] : '';

    return { name, length, teacher, students, url };
  }

  function harvest() {
    let added = 0;
    for (const card of getCards()) {
      const row = parseCard(card);
      if (!row.name || !row.length) continue;
      const key = row.url || row.name;
      const existing = data.get(key);
      if (!existing) { data.set(key, row); added++; }
      else for (const f of ['length', 'teacher', 'students']) if (!existing[f] && row[f]) existing[f] = row[f];
    }
    return added;
  }

  // Signature of the currently rendered page, to detect when new cards arrive.
  function pageSignature() {
    const urls = getCards().map((c) => {
      const a = c.querySelector('a[href*="/classes/"]');
      return a ? a.getAttribute('href') : '';
    });
    return urls.slice(0, 5).join('|') + '::' + urls.slice(-5).join('|');
  }

  function findNextControl() {
    const els = [...document.querySelectorAll('button, a, [role="button"]')];
    return (
      document.querySelector('[rel="next"]') ||
      els.find((el) => /next page|^next$|›|→/i.test(((el.getAttribute('aria-label') || '') + ' ' + (el.innerText || '')).trim())) ||
      null
    );
  }

  function realClick(el) {
    el.scrollIntoView({ block: 'center' });
    const opts = { bubbles: true, cancelable: true, view: window };
    for (const type of ['pointerover', 'pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click']) {
      el.dispatchEvent(new PointerEvent(type, opts));
    }
  }

  window.__SS_EXPORT = async function () {
    const rows = [...data.values()];
    console.table(rows.slice(0, 30), ['name', 'length', 'teacher', 'students']);
    const esc = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
    const csv = [
      ['Course Name', 'Length', 'Teacher', 'Students', 'URL'].join(','),
      ...rows.map((r) => [r.name, r.length, r.teacher, r.students, r.url].map(esc).join(',')),
    ].join('\n');
    try { await navigator.clipboard.writeText(csv); console.log('CSV copied ✔'); } catch {}
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
    a.download = 'skillshare_courses.csv';
    document.body.appendChild(a); a.click(); a.remove();
    console.log(`Exported ${rows.length} courses.`);
    return rows;
  };

  console.log('%cScraping Skillshare (v2: clicks through pages). Stop: window.__SS_STOP = true   Export: __SS_EXPORT()', 'color:#00ff84;background:#002333;font-weight:bold');

  let added = harvest();
  console.log(`Current page: +${added} (total ${data.size})`);
  if (data.size === 0) {
    console.error('Parsed 0 courses from the live page — send Claude the outerHTML of one class card.');
    return;
  }

  for (let page = 2; page <= MAX_PAGES && !window.__SS_STOP; page++) {
    const next = findNextControl();
    if (!next) { console.log('No next-page control found — assuming last page. Done.'); break; }

    const before = pageSignature();
    realClick(next);

    // Wait for the new page of cards to render
    const deadline = Date.now() + RENDER_TIMEOUT_MS;
    let changed = false;
    while (Date.now() < deadline && !window.__SS_STOP) {
      await sleep(300);
      if (pageSignature() !== before) { changed = true; break; }
    }
    if (!changed) {
      console.warn(`Page ${page}: cards did not change within ${RENDER_TIMEOUT_MS / 1000}s — stopping. Re-run to resume from here.`);
      break;
    }
    await sleep(SETTLE_MS);

    added = harvest();
    console.log(`Page ${page}/${MAX_PAGES}: +${added} (total ${data.size})`);
  }

  const missingLen = [...data.values()].filter((r) => !r.length).length;
  console.log(`%cFinished: ${data.size} courses (${missingLen} missing length).`, 'color:green;font-weight:bold');
  await window.__SS_EXPORT();
})();
