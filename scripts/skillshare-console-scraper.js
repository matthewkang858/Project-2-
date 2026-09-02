/**
 * Skillshare course scraper — paste into the Chrome DevTools console while on:
 * https://www.skillshare.com/en/browse?sort=popular&page=1
 *
 * Fetches ?page=1..405 directly (keeping your current sort/filters) and
 * parses each class's name, length, teacher, and student count.
 *
 * At ~1.3s per page, all 405 pages take roughly 9 minutes. Progress is
 * logged as it goes; if Skillshare rate-limits (HTTP 403/429), the script
 * backs off and retries before giving up.
 *
 * Controls:
 *   window.__SS_STOP = true   // stop fetching
 *   __SS_EXPORT()             // download CSV of everything collected so far
 *
 * Re-running in the same tab resumes: already-seen classes are kept and
 * fetching restarts from page 1 (pages with nothing new are cheap).
 */
(async function scrapeSkillshare() {
  const MAX_PAGES = 405;
  const PAGE_PAUSE_MS = 800;
  const BACKOFFS_MS = [5000, 15000, 30000]; // retry waits on 403/429
  window.__SS_STOP = false;
  const data = (window.__SS_DATA = window.__SS_DATA || new Map());

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const params = new URLSearchParams(location.search);
  const parser = new DOMParser();

  function extractCards(doc) {
    const cards = new Set();
    for (const a of doc.querySelectorAll('a[href*="/classes/"]')) {
      const card = a.closest('li, article, [class*="card" i], div');
      if (card && (card.textContent || '').trim().length > 15) cards.add(card);
    }
    return [...cards];
  }

  function parseCard(card) {
    const text = (card.innerText || card.textContent || '').replace(/\s+/g, ' ').trim();
    const html = card.outerHTML || '';

    let name = '';
    const heading = card.querySelector('h1,h2,h3,h4,[class*="title" i]');
    if (heading) name = (heading.innerText || heading.textContent || '').trim();
    if (!name) {
      const link = card.querySelector('a[href*="/classes/"]');
      if (link) name = (link.innerText || link.textContent || '').trim();
    }
    name = name.split('\n')[0].trim();

    // Length: "1h 13m", "2h", "43m" — visible text first, then raw markup
    let length = '';
    const dur =
      text.match(/\b(\d+h\s*\d+m|\d+\s*h(?:rs?)?\b|\d+\s*m(?:in)?s?\b)/i) ||
      html.match(/\b(\d+h\s*\d+m|\d+\s*h(?:rs?)?\b|\d+\s*m(?:in)?s?\b)/i);
    if (dur) length = dur[1].replace(/\s+/g, ' ').trim();

    // Students: "12,345 students" / "1.2K students"
    let students = '';
    const st = text.match(/([\d,.]+\s*[KkMm]?)\s*students?/i) || html.match(/([\d,.]+\s*[KkMm]?)\s*students?/i);
    if (st) students = st[1].replace(/\s+/g, '');

    // Teacher: the line that isn't the title/length/students, if identifiable
    let teacher = '';
    const t = card.querySelector('[class*="teacher" i], [class*="author" i], [class*="instructor" i]');
    if (t) teacher = (t.innerText || t.textContent || '').trim().split('\n')[0];

    const link = card.querySelector('a[href*="/classes/"]');
    const url = link ? new URL(link.getAttribute('href'), location.origin).href.split('?')[0] : '';

    return { name, length, teacher, students, url };
  }

  function harvestDoc(doc) {
    let added = 0;
    for (const card of extractCards(doc)) {
      const row = parseCard(card);
      if (!row.name || (!row.length && !row.students)) continue;
      const key = row.url || row.name;
      const existing = data.get(key);
      if (!existing) { data.set(key, row); added++; }
      else for (const f of ['length', 'teacher', 'students']) if (!existing[f] && row[f]) existing[f] = row[f];
    }
    return added;
  }

  window.__SS_EXPORT = async function () {
    const rows = [...data.values()];
    console.table(rows.slice(0, 50), ['name', 'length', 'teacher', 'students']);
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

  async function fetchPage(page) {
    params.set('page', String(page));
    const url = `${location.pathname}?${params.toString()}`;
    for (let attempt = 0; attempt <= BACKOFFS_MS.length; attempt++) {
      const res = await fetch(url, { credentials: 'same-origin' });
      if (res.ok) return res.text();
      if ((res.status === 403 || res.status === 429) && attempt < BACKOFFS_MS.length) {
        console.warn(`Page ${page}: HTTP ${res.status} — backing off ${BACKOFFS_MS[attempt] / 1000}s…`);
        await sleep(BACKOFFS_MS[attempt]);
        continue;
      }
      throw new Error(`HTTP ${res.status}`);
    }
  }

  console.log('%cScraping Skillshare… Stop: window.__SS_STOP = true   Export: __SS_EXPORT()', 'color:#00ff84;background:#002333;font-weight:bold');

  // Page 1: use the live DOM in front of you, and sanity-check the parser.
  const first = harvestDoc(document);
  console.log(`Page 1 (current page): ${first} courses.`);
  if (first === 0) {
    console.error('Parsed 0 courses from the live page — the selectors need fixing. Send the outerHTML of one class card.');
    return;
  }

  let emptyStreak = 0;
  for (let page = 2; page <= MAX_PAGES && !window.__SS_STOP; page++) {
    let added = 0;
    try {
      const doc = parser.parseFromString(await fetchPage(page), 'text/html');
      added = harvestDoc(doc);
    } catch (e) {
      console.warn(`Page ${page} failed (${e.message}) — stopping. Re-run later to resume; data is kept.`);
      break;
    }
    if (page === 2 && added === 0) {
      console.error('Page 2 fetched but yielded 0 courses — fetched HTML differs from the live page. Tell Claude; meanwhile everything visible as you browse manually still gets captured if you re-run on each page.');
      break;
    }
    console.log(`Page ${page}/${MAX_PAGES}: +${added} (total ${data.size})`);
    if (added === 0 && ++emptyStreak >= 3) { console.log('3 empty pages in a row — done.'); break; }
    if (added > 0) emptyStreak = 0;
    await sleep(PAGE_PAUSE_MS);
  }

  const missingLen = [...data.values()].filter((r) => !r.length).length;
  console.log(`%cFinished: ${data.size} courses (${missingLen} missing length).`, 'color:green;font-weight:bold');
  await window.__SS_EXPORT();
})();
