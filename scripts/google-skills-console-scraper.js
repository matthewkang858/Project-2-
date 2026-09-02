/**
 * Google Skills (skills.google) catalog scraper — paste into the Chrome
 * DevTools console while on your filtered catalog page, e.g.:
 * https://www.skills.google/catalog?format%5B%5D=courses&...
 *
 * Strategy: the catalog is served page by page via a &page=N parameter, so
 * this fetches page 1, 2, 3, ... in the background (keeping your current
 * filters) and parses each course's name, duration, level, and rating.
 * If fetched pages come back without cards (client-rendered), it tells you
 * and harvests the live page instead — and if it can't parse anything at
 * all, it prints a diagnostic dump to paste back to Claude.
 *
 * Rows persist in localStorage — re-paste to resume after any interruption.
 *
 * Controls:
 *   window.__GS_STOP = true   // stop fetching
 *   __GS_EXPORT()             // download CSV of everything collected so far
 *   __GS_RESET()              // wipe saved data
 */
(async function scrapeGoogleSkills() {
  const PAGE_PAUSE_MS = 700;
  const MAX_PAGES = 300;
  const LS_KEY = 'gs_scrape_v1';
  window.__GS_STOP = false;

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const parser = new DOMParser();
  const params = new URLSearchParams(location.search);

  // ----- persistent store -----
  const data = new Map();
  try {
    const saved = JSON.parse(localStorage.getItem(LS_KEY) || '[]');
    for (const row of saved) data.set(row.key, row);
    if (saved.length) console.log(`Resumed with ${saved.length} courses from a previous run.`);
  } catch {}
  function persist() {
    try { localStorage.setItem(LS_KEY, JSON.stringify([...data.values()])); }
    catch (e) { console.warn('localStorage save failed:', e.message); }
  }
  window.__GS_RESET = () => { localStorage.removeItem(LS_KEY); data.clear(); console.log('Cleared saved data.'); };

  // ----- parsing -----
  const LINK_RE = /\/(course_templates|courses|paths|catalog_item|focuses)\/[^/?#]+/;
  const DUR_RE = /(\d+(?:\.\d+)?)\s*hours?(?:\s*(\d+)\s*min(?:ute)?s?)?|(\d+)\s*min(?:ute)?s?\b|(\d+)h(?:\s*(\d+)m)?\b|(\d+)m\b/i;
  const LEVEL_RE = /\b(Introductory|Fundamental|Beginner|Intermediate|Advanced|Expert)\b/;

  function textOf(el) {
    return (el.innerText ?? el.textContent ?? '').replace(/\s+/g, ' ').trim();
  }

  function getCourseLinks(doc) {
    return [...doc.querySelectorAll('a[href]')].filter((a) => LINK_RE.test(a.getAttribute('href') || ''));
  }

  function cardFor(link) {
    let el = link;
    for (let i = 0; i < 8 && el.parentElement; i++) {
      el = el.parentElement;
      const inside = getCourseLinks(el);
      const distinct = new Set(inside.map((a) => a.getAttribute('href').split('?')[0]));
      if (distinct.size > 1) return null;
      if (DUR_RE.test(textOf(el))) return el;
    }
    return null;
  }

  function parseDuration(text) {
    const m = text.match(DUR_RE);
    if (!m) return { length: '', hours: '' };
    let h = 0, min = 0;
    if (m[1] != null) { h = parseFloat(m[1]); min = parseInt(m[2] || 0); }
    else if (m[3] != null) { min = parseInt(m[3]); }
    else if (m[4] != null) { h = parseInt(m[4]); min = parseInt(m[5] || 0); }
    else if (m[6] != null) { min = parseInt(m[6]); }
    const length = (h ? h + 'h' : '') + (h && min ? ' ' : '') + (min ? min + 'm' : '');
    return { length, hours: String(Math.round((h + min / 60) * 100) / 100) };
  }

  function harvestDoc(doc) {
    let added = 0;
    for (const link of getCourseLinks(doc)) {
      const card = cardFor(link);
      if (!card) continue;
      const text = textOf(card);

      let name = '';
      const heading = card.querySelector('h1,h2,h3,h4,h5,[class*="title" i]');
      if (heading) name = textOf(heading);
      if (!name) name = textOf(link);
      name = name.split('\n')[0].trim();
      if (!name) continue;

      const { length, hours } = parseDuration(text);
      if (!length) continue;

      const level = (text.match(LEVEL_RE)?.[1]) || '';
      const rt = text.match(/(\d\.\d)\s*(?:stars?|\(|out of)/i) || text.match(/\b(\d\.\d)\b/);
      const rating = rt ? rt[1] : '';

      const url = new URL(link.getAttribute('href'), location.origin).href.split('?')[0];
      const existing = data.get(url);
      if (!existing) { data.set(url, { key: url, name, length, hours, level, rating, url }); added++; }
      else for (const f of ['length', 'hours', 'level', 'rating']) if (!existing[f]) existing[f] = { length, hours, level, rating }[f] || existing[f];
    }
    persist();
    return added;
  }

  function dumpDiagnostic() {
    console.error('Parsed 0 courses. Diagnostic dump — paste ALL of this back to Claude:');
    const els = [...document.querySelectorAll('body *')].filter(
      (e) => /\d+\s*(hours?|min)/i.test(e.textContent || '') && (e.textContent || '').length < 300
    );
    console.log(`Duration-mentioning elements: ${els.length}`);
    if (els.length) {
      let card = els[0];
      for (let i = 0; i < 6 && card.parentElement; i++) {
        card = card.parentElement;
        if ((card.textContent || '').length > 100) break;
      }
      console.log('=== CARD text ===\n' + textOf(card));
      console.log('=== CARD outerHTML (first 4000) ===\n' + card.outerHTML.slice(0, 4000));
      card.querySelectorAll('a').forEach((x) => console.log('card link:', x.getAttribute('href')));
    } else {
      const main = document.querySelector('main') || document.body;
      console.log('=== MAIN text (first 2000) ===\n' + textOf(main).slice(0, 2000));
      [...document.querySelectorAll('a[href]')].slice(0, 30).forEach((x) => console.log(x.getAttribute('href')));
    }
  }

  // ----- export -----
  window.__GS_EXPORT = async function () {
    const rows = [...data.values()];
    console.table(rows.slice(0, 30), ['name', 'length', 'hours', 'level', 'rating']);
    const esc = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
    const csv = [
      ['Course Name', 'Length', 'Hours', 'Level', 'Rating', 'URL'].join(','),
      ...rows.map((r) => [r.name, r.length, r.hours, r.level, r.rating, r.url].map(esc).join(',')),
    ].join('\n');
    try { await navigator.clipboard.writeText(csv); console.log('CSV copied ✔'); } catch {}
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
    a.download = 'google_skills_courses.csv';
    document.body.appendChild(a); a.click(); a.remove();
    console.log(`Exported ${rows.length} courses.`);
    return rows;
  };

  // ----- main -----
  console.log('%cScraping Google Skills… Stop: window.__GS_STOP = true   Export: __GS_EXPORT()', 'color:#fff;background:#1a73e8;font-weight:bold');

  let added = harvestDoc(document);
  console.log(`Current page: +${added} (total ${data.size})`);
  if (data.size === 0) { dumpDiagnostic(); return; }

  const startPage = Number(params.get('page') || '1');
  for (let page = startPage + 1; page <= MAX_PAGES && !window.__GS_STOP; page++) {
    params.set('page', String(page));
    const url = `${location.pathname}?${params.toString()}`;
    let pageAdded = 0;
    try {
      const res = await fetch(url, { credentials: 'same-origin' });
      if (!res.ok) { console.log(`Page ${page}: HTTP ${res.status} — stopping.`); break; }
      const doc = parser.parseFromString(await res.text(), 'text/html');
      const linksThere = getCourseLinks(doc).length;
      pageAdded = harvestDoc(doc);
      if (page === startPage + 1 && linksThere === 0) {
        console.error('Fetched page has no course links — the catalog must be client-rendered. Navigate to each page manually and re-paste the script (results accumulate), and tell Claude so the script can be adapted.');
        break;
      }
    } catch (e) {
      console.warn(`Page ${page} failed (${e.message}) — stopping. Re-paste later to resume; data is kept.`);
      break;
    }
    console.log(`Page ${page}: +${pageAdded} (total ${data.size})`);
    if (pageAdded === 0) { console.log('No new courses on this page — done.'); break; }
    await sleep(PAGE_PAUSE_MS);
  }

  console.log(`%cFinished with ${data.size} courses.`, 'color:green;font-weight:bold');
  await window.__GS_EXPORT();
})();
