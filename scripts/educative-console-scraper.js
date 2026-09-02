/**
 * Educative course scraper — paste into the Chrome DevTools console while on:
 * https://www.educative.io/search?tab=courses
 *
 * Strategies, tried in order each round:
 *   1. __NEXT_DATA__ / embedded JSON scan (Educative is a Next.js app).
 *   2. DOM harvest of visible course cards (title + duration + level),
 *      clicking load-more/next controls and scrolling for more.
 *
 * Rows persist in localStorage — re-paste to resume, results accumulate
 * across searches/categories too. If nothing parses, it prints a
 * diagnostic dump to paste back to Claude.
 *
 * Controls:
 *   window.__ED_STOP = true   // stop
 *   __ED_EXPORT()             // download CSV of everything collected so far
 *   __ED_RESET()              // wipe saved data
 */
(async function scrapeEducative() {
  const PAUSE_MS = 1600;
  const MAX_IDLE = 8;
  const MAX_ROUNDS = 600;
  const LS_KEY = 'ed_scrape_v1';
  window.__ED_STOP = false;

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

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

  function put(row) {
    if (!row.name || !row.length) return 0;
    const existing = data.get(row.key);
    if (!existing) { data.set(row.key, row); return 1; }
    for (const f of ['length', 'hours', 'level', 'rating', 'url']) if (!existing[f] && row[f]) existing[f] = row[f];
    return 0;
  }

  // ----- duration parsing -----
  const DUR_RE = /(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)(?:\s*(\d+)\s*(?:minutes?|mins?))?|(\d+)\s*(?:minutes?|mins?)\b|(\d+)h(?:\s*(\d+)m)?\b|(\d+)m\b/i;
  function parseDuration(text) {
    const m = text.match(DUR_RE);
    if (!m) return { length: '', hours: '' };
    let h = 0, min = 0;
    if (m[1] != null) { h = parseFloat(m[1]); min = parseInt(m[2] || 0); }
    else if (m[3] != null) min = parseInt(m[3]);
    else if (m[4] != null) { h = parseInt(m[4]); min = parseInt(m[5] || 0); }
    else if (m[6] != null) min = parseInt(m[6]);
    const length = (h ? h + 'h' : '') + (h && min ? ' ' : '') + (min ? min + 'm' : '');
    return { length, hours: String(Math.round((h + min / 60) * 100) / 100) };
  }

  // ----- strategy 1: embedded JSON -----
  function scanNextData() {
    const tag = document.getElementById('__NEXT_DATA__');
    if (!tag) return 0;
    let root;
    try { root = JSON.parse(tag.textContent); } catch { return 0; }
    const TIME_KEYS = ['duration', 'durationHours', 'completionTime', 'estimatedTime', 'readingTime', 'total_time', 'time'];
    let found = 0;
    const seen = new Set();
    (function walk(node) {
      if (!node || typeof node !== 'object' || seen.has(node)) return;
      if (seen.size < 300000) seen.add(node);
      if (Array.isArray(node)) { node.forEach(walk); return; }
      const title = node.title || node.name;
      const timeKey = TIME_KEYS.find((k) => node[k] != null && node[k] !== '');
      if (typeof title === 'string' && title.length > 2 && timeKey) {
        const rawTime = String(node[timeKey]);
        const { length, hours } = parseDuration(rawTime.match(/[a-z]/i) ? rawTime : rawTime + ' hours');
        const slug = node.slug || node.url || node.urlPath || '';
        const url = slug ? new URL(String(slug).startsWith('/') ? slug : '/courses/' + slug, location.origin).href : '';
        if (length) found += put({
          key: url || title, name: title, length, hours,
          level: node.level || node.difficulty || '', rating: '', url,
          source: 'json:' + timeKey,
        });
      }
      for (const k of Object.keys(node)) walk(node[k]);
    })(root);
    if (found) {
      const sample = [...data.values()].find((r) => r.source);
      console.log(`__NEXT_DATA__ scan found ${found} entries (field "${sample?.source}") — verify a few in the table.`);
    }
    persist();
    return found;
  }

  // ----- strategy 2: DOM harvest -----
  const LINK_RE = /\/(courses|path|paths|module|projects|assessments|collection)\/[^/?#]+|\/courses\/[^/?#]+/;

  function getCourseLinks() {
    return [...document.querySelectorAll('a[href]')].filter((a) => {
      const h = a.getAttribute('href') || '';
      return LINK_RE.test(h) && !/\/search|\/signup|\/login|\/pricing/.test(h);
    });
  }

  function cardFor(link) {
    let el = link;
    for (let i = 0; i < 8 && el.parentElement; i++) {
      el = el.parentElement;
      const inside = getCourseLinks().filter((a) => el.contains(a));
      const distinct = new Set(inside.map((a) => a.getAttribute('href').split('?')[0]));
      if (distinct.size > 1) return null;
      if (DUR_RE.test(el.innerText || '')) return el;
    }
    return DUR_RE.test(link.innerText || '') ? link : null;
  }

  function harvest() {
    let added = 0;
    for (const link of getCourseLinks()) {
      const card = cardFor(link);
      if (!card) continue;
      const text = (card.innerText || '').replace(/\s+/g, ' ').trim();

      let name = '';
      const heading = card.querySelector('h1,h2,h3,h4,h5,[class*="title" i]');
      if (heading) name = (heading.innerText || '').trim().split('\n')[0];
      if (!name) name = (link.innerText || '').trim().split('\n')[0];
      name = name.trim();

      const { length, hours } = parseDuration(text);
      const level = (text.match(/\b(Beginner|Intermediate|Advanced)\b/i)?.[1]) || '';
      const rt = text.match(/(\d\.\d)\s*(?:\(|stars?|out of)/i);
      const rating = rt ? rt[1] : '';

      const url = new URL(link.getAttribute('href'), location.origin).href.split('?')[0];
      added += put({ key: url, name, length, hours, level, rating, url });
    }
    persist();
    return added;
  }

  function findMoreControl() {
    const els = [...document.querySelectorAll('button, a, [role="button"]')];
    const candidates = els.filter((el) => {
      const label = ((el.innerText || '') + ' ' + (el.getAttribute('aria-label') || '')).toLowerCase();
      if (/options|menu|filter|cart|sign|log|pricing/.test(label)) return false;
      return /(load|show|view|see)\s*more|more results|next page|go to next|^next$|›|→/.test(label);
    });
    return document.querySelector('[rel="next"]') || candidates[candidates.length - 1] || null;
  }

  function realClick(el) {
    el.scrollIntoView({ block: 'center' });
    const opts = { bubbles: true, cancelable: true, view: window };
    for (const type of ['pointerover', 'pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click']) {
      el.dispatchEvent(new PointerEvent(type, opts));
    }
  }

  function dumpDiagnostic() {
    console.error('Parsed 0 courses. Diagnostic dump — paste ALL of this back to Claude:');
    const els = [...document.querySelectorAll('body *')].filter(
      (e) => DUR_RE.test(e.textContent || '') && (e.textContent || '').length < 300
    );
    console.log(`Duration-mentioning elements: ${els.length}`);
    if (els.length) {
      let card = els[0];
      for (let i = 0; i < 6 && card.parentElement; i++) {
        card = card.parentElement;
        if ((card.innerText || '').length > 100) break;
      }
      console.log('=== CARD text ===\n' + (card.innerText || ''));
      console.log('=== CARD outerHTML (first 4000) ===\n' + card.outerHTML.slice(0, 4000));
      card.querySelectorAll('a').forEach((x) => console.log('card link:', x.getAttribute('href')));
    } else {
      const main = document.querySelector('main') || document.body;
      console.log('=== MAIN text (first 2000) ===\n' + (main.innerText || '').slice(0, 2000));
      [...document.querySelectorAll('a[href]')].slice(0, 30).forEach((x) => console.log(x.getAttribute('href')));
    }
  }

  // ----- export -----
  window.__ED_EXPORT = async function () {
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
    a.download = 'educative_courses.csv';
    document.body.appendChild(a); a.click(); a.remove();
    console.log(`Exported ${rows.length} courses.`);
    return rows;
  };

  // ----- main -----
  console.log('%cScraping Educative… Stop: window.__ED_STOP = true   Export: __ED_EXPORT()', 'color:#fff;background:#4951f5;font-weight:bold');

  const fromJson = scanNextData();
  let added = harvest();
  console.log(`Initial: ${fromJson} from embedded JSON, +${added} from the page (total ${data.size})`);
  if (data.size === 0) { dumpDiagnostic(); return; }

  let idle = 0;
  for (let round = 0; round < MAX_ROUNDS && !window.__ED_STOP; round++) {
    const btn = findMoreControl();
    if (btn) realClick(btn);
    else window.scrollTo(0, document.body.scrollHeight);
    await sleep(PAUSE_MS);

    added = harvest();
    if (added > 0) {
      idle = 0;
      console.log(`+${added} (total ${data.size})`);
    } else if (++idle >= MAX_IDLE) {
      console.log('Nothing new after several rounds — done with this view. (Other tabs/filters accumulate if you re-run there.)');
      break;
    }
  }

  console.log(`%cFinished with ${data.size} courses.`, 'color:green;font-weight:bold');
  await window.__ED_EXPORT();
})();
