/**
 * ed2go course scraper — paste into the Chrome DevTools console while on:
 * https://www.ed2go.com/search
 *
 * Repeatedly clicks the "Load More" button (with real pointer events),
 * harvesting every course card as it appears: name, duration (weeks),
 * course hours, price. Rows persist in localStorage after every round, so
 * a reload never loses progress — re-paste the script to resume.
 *
 * If it can't parse any cards, it prints the first card's markup on its
 * own — paste that output back to Claude for exact selectors.
 *
 * Controls:
 *   window.__E2_STOP = true   // stop clicking/collecting
 *   __E2_EXPORT()             // download CSV of everything collected so far
 *   __E2_RESET()              // wipe saved data and start fresh
 */
(async function scrapeEd2go() {
  const PAUSE_MS = 1800;      // wait after each Load More click
  const MAX_IDLE = 8;         // stop after this many rounds with nothing new
  const MAX_ROUNDS = 1000;
  const LS_KEY = 'e2_scrape_v1';
  window.__E2_STOP = false;

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
  window.__E2_RESET = () => { localStorage.removeItem(LS_KEY); data.clear(); console.log('Cleared saved data.'); };

  // ----- cards -----
  function getCards() {
    const cards = new Set();
    // Course links on ed2go contain /courses/ (category pages do too, but
    // those cards won't parse a duration and get filtered out).
    for (const a of document.querySelectorAll('a[href*="/courses/"], a[href*="/course/"]')) {
      const card = a.closest('li, article, [class*="card" i], [class*="result" i], [class*="tile" i], div');
      if (card && (card.innerText || '').trim().length > 20) cards.add(card);
    }
    return [...cards];
  }

  function parseCard(card) {
    const text = (card.innerText || '').replace(/\s+/g, ' ').trim();

    let name = '';
    const heading = card.querySelector('h1,h2,h3,h4,h5,[class*="title" i]');
    if (heading) name = (heading.innerText || '').trim().split('\n')[0];
    if (!name) {
      const link = card.querySelector('a[href*="/course"]');
      if (link) name = (link.innerText || '').trim().split('\n')[0];
    }
    name = name.trim();

    // "Duration: 6 Weeks" / "6 weeks"
    let weeks = '';
    const w = text.match(/(\d+(?:\.\d+)?)\s*weeks?\b/i);
    if (w) weeks = w[1];

    // "24 Course Hrs" / "24 hours" / "24 hrs"
    let hours = '';
    const h = text.match(/(\d+(?:\.\d+)?)\s*(?:course\s*)?(?:hrs?|hours?)\b/i);
    if (h) hours = h[1];

    // Months, for self-paced listings that use them
    let months = '';
    const mo = text.match(/(\d+(?:\.\d+)?)\s*months?\b/i);
    if (mo) months = mo[1];

    let price = '';
    const p = text.match(/\$\s?([\d,]+(?:\.\d{2})?)/);
    if (p) price = p[1].replace(/,/g, '');

    const link = card.querySelector('a[href*="/course"]');
    const url = link ? new URL(link.getAttribute('href'), location.origin).href.split('?')[0] : '';

    return { key: url || name, name, weeks, months, hours, price, url };
  }

  function harvest() {
    let added = 0;
    for (const card of getCards()) {
      const row = parseCard(card);
      // A real course card has a duration of some kind
      if (!row.name || (!row.weeks && !row.hours && !row.months)) continue;
      const existing = data.get(row.key);
      if (!existing) { data.set(row.key, row); added++; }
      else for (const f of ['weeks', 'months', 'hours', 'price', 'url'])
        if (!existing[f] && row[f]) existing[f] = row[f];
    }
    persist();
    return added;
  }

  // ----- load more -----
  function findLoadMore() {
    const els = [...document.querySelectorAll('button, a[role="button"], a[class*="load" i], input[type="button"], span[role="button"]')];
    const candidates = els.filter((el) => {
      const label = ((el.innerText || el.value || '') + ' ' + (el.getAttribute('aria-label') || '')).toLowerCase();
      if (/options|menu|filter|category|cart|search\b/.test(label)) return false;
      return /(load|show|view|see)\s*more|more results|more courses/.test(label);
    });
    return candidates[candidates.length - 1] || null;
  }

  function realClick(el) {
    el.scrollIntoView({ block: 'center' });
    const opts = { bubbles: true, cancelable: true, view: window };
    for (const type of ['pointerover', 'pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click']) {
      el.dispatchEvent(new PointerEvent(type, opts));
    }
  }

  // ----- self-diagnostic when parsing fails -----
  function dumpDiagnostic() {
    console.error('Parsed 0 courses. Diagnostic dump — paste ALL of this back to Claude:');
    const leaves = [...document.querySelectorAll('body *')].filter(
      (e) => e.children.length === 0 && /\d+\s*(weeks?|hrs?|hours?|months?)\b/i.test(e.textContent || '')
    );
    console.log(`Duration-looking elements: ${leaves.length}`);
    if (leaves.length) {
      let card = leaves[0];
      for (let i = 0; i < 6 && card.parentElement; i++) {
        card = card.parentElement;
        if ((card.innerText || '').length > 80) break;
      }
      console.log('=== CARD innerText ===\n' + card.innerText);
      console.log('=== CARD outerHTML (first 4000) ===\n' + card.outerHTML.slice(0, 4000));
      card.querySelectorAll('a').forEach((x) => console.log('link:', x.getAttribute('href')));
    } else {
      console.log('Sample links on page:');
      [...document.querySelectorAll('a[href]')].slice(0, 30).forEach((x) => console.log(x.getAttribute('href')));
    }
  }

  // ----- export -----
  window.__E2_EXPORT = async function () {
    const rows = [...data.values()];
    console.table(rows.slice(0, 30), ['name', 'weeks', 'months', 'hours', 'price']);
    const esc = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
    const csv = [
      ['Course Name', 'Weeks', 'Months', 'Course Hours', 'Price', 'URL'].join(','),
      ...rows.map((r) => [r.name, r.weeks, r.months, r.hours, r.price, r.url].map(esc).join(',')),
    ].join('\n');
    try { await navigator.clipboard.writeText(csv); console.log('CSV copied ✔'); } catch {}
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
    a.download = 'ed2go_courses.csv';
    document.body.appendChild(a); a.click(); a.remove();
    console.log(`Exported ${rows.length} courses.`);
    return rows;
  };

  // ----- main loop -----
  console.log('%cScraping ed2go… Stop: window.__E2_STOP = true   Export: __E2_EXPORT()', 'color:#fff;background:#0057b8;font-weight:bold');

  let added = harvest();
  console.log(`Initial page: +${added} (total ${data.size})`);
  if (data.size === 0) { dumpDiagnostic(); return; }

  let idle = 0;
  for (let round = 0; round < MAX_ROUNDS && !window.__E2_STOP; round++) {
    const btn = findLoadMore();
    if (btn) {
      if (round % 10 === 0) console.log('Clicking:', JSON.stringify((btn.innerText || btn.value || '').trim()));
      realClick(btn);
    } else {
      // No button — maybe infinite scroll, or everything is loaded
      window.scrollTo(0, document.body.scrollHeight);
    }
    await sleep(PAUSE_MS);

    added = harvest();
    if (added > 0) {
      idle = 0;
      console.log(`+${added} (total ${data.size})`);
    } else if (++idle >= MAX_IDLE) {
      console.log(btn ? 'Load More clicked but nothing new — done (or the site stopped serving).' : 'No Load More button and nothing new — done.');
      break;
    }
  }

  console.log(`%cFinished with ${data.size} courses.`, 'color:green;font-weight:bold');
  await window.__E2_EXPORT();
})();
