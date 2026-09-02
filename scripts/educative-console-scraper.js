/**
 * Educative course scraper (v2) — paste into the Chrome DevTools console on:
 * https://www.educative.io/search?tab=courses
 *
 * Built against Educative's real search-results markup:
 *   - each result is [data-testid^="search-result-tile-"] wrapping one
 *     <a href="/courses/...">
 *   - durations render as "26 h", "9 h 30 m", "45 m"
 *   - level (Beginner/Intermediate/Advanced), rating "4.7", lesson counts
 *   - the list loads more via an infinite-scroll sentinel
 *     [data-testid="infinite-scroll-sentinel"] — so v2 ONLY scrolls, it never
 *     clicks anything (v1 accidentally clicked the "Show more (382)" topics
 *     filter, which opened the Filter-by-Topics modal).
 *
 * If that modal is open, this closes it first. Rows persist in localStorage —
 * re-paste to resume; results accumulate across tabs/filters too.
 *
 * Controls:
 *   window.__ED_STOP = true   // stop
 *   __ED_EXPORT()             // download CSV of everything collected so far
 *   __ED_RESET()              // wipe saved data
 */
(async function scrapeEducativeV2() {
  const PAUSE_MS = 1500;
  const MAX_IDLE = 10;
  const MAX_ROUNDS = 1500;
  const LS_KEY = 'ed_scrape_v1';
  window.__ED_STOP = false;

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  // ----- close any open filter/topics modal (the v1 "weird popup") -----
  document.querySelectorAll('div.fixed.inset-0 svg line').forEach((line) => {
    const modal = line.closest('div.fixed.inset-0');
    if (modal && /Filter by Topics|Filters/i.test(modal.innerText || '')) {
      const closer = line.closest('svg');
      closer?.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    }
  });

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
  window.__ED_RESET = () => { localStorage.removeItem(LS_KEY); data.clear(); console.log('Cleared saved data.'); };

  // ----- duration parsing: "26 h", "9 h 30 m", "45 m", "1.5 hours" -----
  const DUR_RE = /(\d+(?:\.\d+)?)\s*h(?:ours?|rs?)?\b(?:\s*(\d+)\s*m(?:in(?:ute)?s?)?\b)?|(\d+)\s*m(?:in(?:ute)?s?)?\b/i;
  function parseDuration(text) {
    const m = text.match(DUR_RE);
    if (!m) return { length: '', hours: '' };
    let h = 0, min = 0;
    if (m[1] != null) { h = parseFloat(m[1]); min = parseInt(m[2] || 0); }
    else if (m[3] != null) min = parseInt(m[3]);
    const length = (h ? h + 'h' : '') + (h && min ? ' ' : '') + (min ? min + 'm' : '');
    return { length, hours: String(Math.round((h + min / 60) * 100) / 100) };
  }

  // ----- harvest the exact result tiles -----
  function getTiles() {
    return [...document.querySelectorAll('[data-testid^="search-result-tile-"]')];
  }

  function harvest() {
    let added = 0;
    for (const tile of getTiles()) {
      const link = tile.querySelector('a[href]');
      if (!link) continue;
      const href = link.getAttribute('href') || '';
      const url = new URL(href, location.origin).href.split('?')[0];

      const titleEl = tile.querySelector('.content-emphasis.line-clamp-2, [class*="line-clamp"][class*="text-xl"], h1,h2,h3');
      const name = ((titleEl?.innerText || link.innerText || '').trim()).split('\n')[0].trim();
      if (!name) continue;

      const text = (tile.innerText || '').replace(/\s+/g, ' ').trim();
      const { length, hours } = parseDuration(text);
      if (!length) continue;

      const kind = (text.match(/^(Course|Cloud Lab|Project|Path|Assessment|Mock Interview)\b/i)?.[1]) || '';
      const level = (text.match(/\b(Beginner|Intermediate|Advanced)\b/)?.[1]) || '';
      const rating = (text.match(/\b(\d\.\d)\b/)?.[1]) || '';
      const free = /\bFree\b/.test(text) ? 'Free' : '';

      const existing = data.get(url);
      if (!existing) {
        data.set(url, { key: url, name, length, hours, level, rating, kind, free, url });
        added++;
      } else {
        for (const f of ['length', 'hours', 'level', 'rating', 'kind', 'free'])
          if (!existing[f]) existing[f] = { length, hours, level, rating, kind, free }[f] || existing[f];
      }
    }
    persist();
    return added;
  }

  function totalResults() {
    const m = (document.body.innerText || '').match(/Search Results\s*\(([\d,]+)\)/i);
    return m ? Number(m[1].replace(/,/g, '')) : null;
  }

  // ----- scroll-only loading (no clicks!) -----
  function nudgeScroll() {
    const sentinel = document.querySelector('[data-testid="infinite-scroll-sentinel"]');
    if (sentinel) sentinel.scrollIntoView({ block: 'center' });
    const tiles = getTiles();
    if (tiles.length) tiles[tiles.length - 1].scrollIntoView({ block: 'end' });
    window.scrollTo(0, document.body.scrollHeight);
  }

  // ----- export -----
  window.__ED_EXPORT = async function () {
    const rows = [...data.values()];
    console.table(rows.slice(0, 30), ['name', 'length', 'hours', 'level', 'rating', 'free']);
    const esc = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
    const csv = [
      ['Course Name', 'Length', 'Hours', 'Level', 'Rating', 'Type', 'Free', 'URL'].join(','),
      ...rows.map((r) => [r.name, r.length, r.hours, r.level, r.rating, r.kind, r.free, r.url].map(esc).join(',')),
    ].join('\n');
    try { await navigator.clipboard.writeText(csv); console.log('CSV copied ✔'); } catch {}
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
    a.download = 'educative_courses.csv';
    document.body.appendChild(a); a.click(); a.remove();
    console.log(`Exported ${rows.length} courses.`);
    return rows;
  };

  // ----- main -----
  const target = totalResults();
  console.log(`%cScraping Educative… ${target ? target + ' results reported.' : ''} Stop: window.__ED_STOP = true   Export: __ED_EXPORT()`, 'color:#fff;background:#4951f5;font-weight:bold');

  let added = harvest();
  console.log(`Initial: +${added} (total ${data.size}${target ? '/' + target : ''})`);
  if (data.size === 0) {
    console.error('Parsed 0 tiles — are you on https://www.educative.io/search?tab=courses with results visible? If yes, paste this back to Claude:');
    console.log('tiles found:', getTiles().length);
    const first = document.querySelector('[data-testid="search-result-tile-0"]');
    if (first) console.log(first.outerHTML.slice(0, 3000));
    return;
  }

  let idle = 0;
  for (let round = 0; round < MAX_ROUNDS && !window.__ED_STOP; round++) {
    if (target && data.size >= target) { console.log('All results collected.'); break; }
    nudgeScroll();
    await sleep(PAUSE_MS);
    added = harvest();
    if (added > 0) {
      idle = 0;
      if (data.size % 100 < added) console.log(`+${added} (total ${data.size}${target ? '/' + target : ''})`);
    } else if (++idle >= MAX_IDLE) {
      console.log(`Nothing new after ${MAX_IDLE} scrolls — done with this view (${data.size}${target ? '/' + target : ''}).`);
      break;
    }
  }

  console.log(`%cFinished with ${data.size} courses.`, 'color:green;font-weight:bold');
  await window.__ED_EXPORT();
})();
