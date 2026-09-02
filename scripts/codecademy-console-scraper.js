/**
 * Codecademy catalog scraper — paste into the Chrome DevTools console while on:
 * https://www.codecademy.com/catalog  (or better: a "browse all" catalog page)
 *
 * Two strategies, tried in order:
 *   1. __NEXT_DATA__: Codecademy is a Next.js site and may embed the catalog
 *      as JSON — if found, courses (title + hours) are extracted directly.
 *   2. DOM harvest: parses visible cards (title, type, level, "N hours"),
 *      clicking load-more/next controls and scrolling to load more.
 *
 * Rows persist in localStorage — re-paste to resume after a reload.
 * If nothing parses, it prints a diagnostic dump to paste back to Claude.
 *
 * Controls:
 *   window.__CC_STOP = true   // stop
 *   __CC_EXPORT()             // download CSV of everything collected so far
 *   __CC_RESET()              // wipe saved data
 */
(async function scrapeCodecademy() {
  const PAUSE_MS = 1500;
  const MAX_IDLE = 8;
  const MAX_ROUNDS = 500;
  const LS_KEY = 'cc_scrape_v1';
  window.__CC_STOP = false;

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  // ----- persistent store -----
  const data = new Map();
  try {
    const saved = JSON.parse(localStorage.getItem(LS_KEY) || '[]');
    for (const row of saved) data.set(row.key, row);
    if (saved.length) console.log(`Resumed with ${saved.length} entries from a previous run.`);
  } catch {}
  function persist() {
    try { localStorage.setItem(LS_KEY, JSON.stringify([...data.values()])); }
    catch (e) { console.warn('localStorage save failed:', e.message); }
  }
  window.__CC_RESET = () => { localStorage.removeItem(LS_KEY); data.clear(); console.log('Cleared saved data.'); };

  function put(row) {
    if (!row.name) return 0;
    const existing = data.get(row.key);
    if (!existing) { data.set(row.key, row); return 1; }
    for (const f of ['hours', 'type', 'level', 'url']) if (!existing[f] && row[f]) existing[f] = row[f];
    return 0;
  }

  // ----- strategy 1: __NEXT_DATA__ JSON -----
  function scanNextData() {
    const tag = document.getElementById('__NEXT_DATA__');
    if (!tag) { console.log('No __NEXT_DATA__ tag — using DOM harvesting.'); return 0; }
    let root;
    try { root = JSON.parse(tag.textContent); } catch { return 0; }

    const TIME_KEYS = ['timeToComplete', 'durationHours', 'hoursToComplete', 'duration', 'hours', 'enrollmentHours', 'lessonHours'];
    let found = 0;
    const seen = new Set();
    (function walk(node) {
      if (!node || typeof node !== 'object' || seen.has(node)) return;
      if (seen.size < 200000) seen.add(node);
      if (Array.isArray(node)) { node.forEach(walk); return; }

      const title = node.title || node.name;
      let timeKey = TIME_KEYS.find((k) => node[k] != null && node[k] !== '');
      if (typeof title === 'string' && title.length > 2 && timeKey) {
        let hours = String(node[timeKey]);
        // normalize things like "10 hours", {hours: 10}, 600 (minutes?) — keep raw + number
        const num = hours.match(/(\d+(?:\.\d+)?)/);
        const slug = node.slug || node.urlPath || node.path || '';
        const url = slug ? new URL(String(slug).startsWith('/') ? slug : '/learn/' + slug, location.origin).href : '';
        found += put({
          key: url || title,
          name: title,
          hours: num ? num[1] : hours,
          hoursRaw: hours,
          type: node.type || node.contentType || node.courseType || '',
          level: node.difficulty || node.level || '',
          url,
          source: 'next-data:' + timeKey,
        });
      }
      for (const k of Object.keys(node)) walk(node[k]);
    })(root);

    if (found) {
      const sample = [...data.values()].find((r) => r.source);
      console.log(`__NEXT_DATA__ scan found ${found} entries (e.g. field "${sample?.source}"). Verify a few in the table before trusting all of them.`);
    } else {
      console.log('__NEXT_DATA__ present but no title+duration objects found — using DOM harvesting.');
    }
    persist();
    return found;
  }

  // ----- strategy 2: DOM harvest -----
  const CARD_LINK = 'a[href*="/learn/"], a[href*="/career-journey/"], a[href*="/paths/"], a[href*="/courses/"]';
  const HOURS_RE = /(?:<\s*)?(\d+(?:\.\d+)?)\s*hours?\b|<\s*1\s*hour/i;

  function cardFor(link) {
    let el = link;
    for (let i = 0; i < 8 && el.parentElement; i++) {
      el = el.parentElement;
      const linksInside = el.querySelectorAll(CARD_LINK).length;
      if (linksInside > 1) return null;
      if (HOURS_RE.test(el.innerText || '')) return el;
    }
    // Some cards put the hours inside the link itself
    return HOURS_RE.test(link.innerText || '') ? link : null;
  }

  function parseCard(link, card) {
    const text = (card.innerText || '').replace(/\s+/g, ' ').trim();

    let name = '';
    const heading = card.querySelector('h1,h2,h3,h4,h5,[class*="title" i]');
    if (heading) name = (heading.innerText || '').trim().split('\n')[0];
    if (!name) name = (link.innerText || '').trim().split('\n')[0];

    let hours = '';
    const h = text.match(HOURS_RE);
    if (h) hours = h[1] || '<1';

    const type = (text.match(/\b(Free course|Course|Skill path|Career path|Certification path|Case study|Project|Docs?)\b/i)?.[1] || '').trim();
    const level = (text.match(/\b(Beginner friendly|Beginner|Intermediate|Advanced)\b/i)?.[1] || '').trim();

    const url = new URL(link.getAttribute('href'), location.origin).href.split('?')[0];
    return { key: url, name, hours, type, level, url };
  }

  function harvest() {
    let added = 0;
    for (const link of document.querySelectorAll(CARD_LINK)) {
      const card = cardFor(link);
      if (!card) continue;
      const row = parseCard(link, card);
      if (!row.hours) continue;
      added += put(row);
    }
    persist();
    return added;
  }

  function findMoreControl() {
    const els = [...document.querySelectorAll('button, a[role="button"], [role="button"]')];
    const candidates = els.filter((el) => {
      const label = ((el.innerText || '') + ' ' + (el.getAttribute('aria-label') || '')).toLowerCase();
      if (/options|menu|filter|cart|search\b|sign|log/.test(label)) return false;
      return /(load|show|view|see)\s*more|more results|next page|^next$/.test(label);
    });
    return candidates[candidates.length - 1] || document.querySelector('[rel="next"]') || null;
  }

  function realClick(el) {
    el.scrollIntoView({ block: 'center' });
    const opts = { bubbles: true, cancelable: true, view: window };
    for (const type of ['pointerover', 'pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click']) {
      el.dispatchEvent(new PointerEvent(type, opts));
    }
  }

  function dumpDiagnostic() {
    console.error('Parsed 0 entries. Diagnostic dump — paste ALL of this back to Claude:');
    const leaves = [...document.querySelectorAll('body *')].filter(
      (e) => /\d+\s*hours?\b|<\s*1\s*hour/i.test(e.textContent || '') && (e.innerText || '').length < 200
    );
    console.log(`Elements mentioning hours: ${leaves.length}`);
    if (leaves.length) {
      let card = leaves[0];
      for (let i = 0; i < 6 && card.parentElement; i++) {
        card = card.parentElement;
        if ((card.innerText || '').length > 80) break;
      }
      console.log('=== CARD innerText ===\n' + card.innerText);
      console.log('=== CARD outerHTML (first 4000) ===\n' + card.outerHTML.slice(0, 4000));
      card.querySelectorAll('a').forEach((x) => console.log('card link:', x.getAttribute('href')));
    } else {
      const main = document.querySelector('main') || document.body;
      console.log('=== MAIN innerText (first 2000) ===\n' + main.innerText.slice(0, 2000));
      [...main.querySelectorAll('a[href]')].slice(0, 30).forEach((x) => console.log(x.getAttribute('href')));
    }
  }

  // ----- export -----
  window.__CC_EXPORT = async function () {
    const rows = [...data.values()];
    console.table(rows.slice(0, 30), ['name', 'hours', 'type', 'level']);
    const esc = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
    const csv = [
      ['Course Name', 'Hours', 'Type', 'Level', 'URL'].join(','),
      ...rows.map((r) => [r.name, r.hours, r.type, r.level, r.url].map(esc).join(',')),
    ].join('\n');
    try { await navigator.clipboard.writeText(csv); console.log('CSV copied ✔'); } catch {}
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
    a.download = 'codecademy_courses.csv';
    document.body.appendChild(a); a.click(); a.remove();
    console.log(`Exported ${rows.length} entries.`);
    return rows;
  };

  // ----- main -----
  console.log('%cScraping Codecademy… Stop: window.__CC_STOP = true   Export: __CC_EXPORT()', 'color:#fff;background:#10162f;font-weight:bold');

  const fromJson = scanNextData();
  let added = harvest();
  console.log(`Initial: ${fromJson} from embedded JSON, +${added} from the page (total ${data.size})`);
  if (data.size === 0) { dumpDiagnostic(); return; }

  let idle = 0;
  for (let round = 0; round < MAX_ROUNDS && !window.__CC_STOP; round++) {
    const btn = findMoreControl();
    if (btn) realClick(btn);
    else window.scrollTo(0, document.body.scrollHeight);
    await sleep(PAUSE_MS);

    added = harvest();
    if (added > 0) {
      idle = 0;
      console.log(`+${added} (total ${data.size})`);
    } else if (++idle >= MAX_IDLE) {
      console.log('Nothing new after several rounds — done with this page/view.');
      break;
    }
  }

  console.log(`%cFinished with ${data.size} entries. If the catalog has more sections/categories, open one and re-run — results accumulate.`, 'color:green;font-weight:bold');
  await window.__CC_EXPORT();
})();
