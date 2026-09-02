/**
 * ed2go course scraper (v2) — paste into the Chrome DevTools console while on:
 * https://www.ed2go.com/search  (with results visible)
 *
 * Built against ed2go's real search results:
 *   - course links have 4+ path segments: /courses/<cat>/<sub>/<ilc|ctp>/<slug>
 *   - durations appear as "6 Weeks / 24 Course Hours" or "3 Months / 24 Course Hours"
 *   - "Course type: Fundamentals", "Open Enrollment" or "Starting <dates>"
 *
 * Clicks Load More until all ~987 results are collected, harvesting every
 * round and persisting to localStorage (a reload never loses progress —
 * re-paste to resume). Exports CSV at the end.
 *
 * Controls:
 *   window.__E2_STOP = true   // stop
 *   __E2_EXPORT()             // download CSV of everything collected so far
 *   __E2_RESET()              // wipe saved data
 */
(async function scrapeEd2goV2() {
  const PAUSE_MS = 1800;
  const MAX_IDLE = 8;
  const MAX_ROUNDS = 1000;
  const LS_KEY = 'e2_scrape_v2';
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

  // Course links: /courses/ + at least 3 more path segments
  const COURSE_HREF = /^\/courses\/[^/]+\/[^/]+\/[^/]+\/[^/?#]+/;
  const DURATION_RE = /(\d+(?:\.\d+)?)\s*(Weeks?|Months?)\s*\/\s*([\d,]+(?:\.\d+)?)\s*Course\s*Hours?/i;

  function getCourseLinks() {
    return [...document.querySelectorAll('a[href]')].filter((a) =>
      COURSE_HREF.test(a.getAttribute('href') || '')
    );
  }

  function cardFor(link) {
    // Climb until the container's text includes the duration line, but stop
    // if it starts spanning multiple courses.
    let el = link;
    for (let i = 0; i < 8 && el.parentElement; i++) {
      el = el.parentElement;
      const linksInside = [...el.querySelectorAll('a[href]')].filter((a) =>
        COURSE_HREF.test(a.getAttribute('href') || '')
      ).length;
      if (linksInside > 1) return null; // overshot into the results list
      if (DURATION_RE.test(el.innerText || '')) return el;
    }
    return null;
  }

  function parseCard(link, card) {
    const text = (card.innerText || '').replace(/\s+/g, ' ').trim();
    const name = (link.innerText || '').trim();

    let weeks = '', months = '', hours = '';
    const d = text.match(DURATION_RE);
    if (d) {
      const n = d[1], unit = d[2].toLowerCase(), h = d[3].replace(/,/g, '');
      if (unit.startsWith('week')) weeks = n; else months = n;
      hours = h;
    }

    const typeMatch = text.match(/Course type:\s*(.+?)(?:\s{2,}|\s(?=[A-Z0-9].{30,}))/);
    let courseType = '';
    const t = text.match(/Course type:\s*([A-Za-z ]+?)(?=\s*[A-Z0-9].*)/);
    courseType = (typeMatch?.[1] || t?.[1] || '').trim();

    const schedule = /Open Enrollment/i.test(text)
      ? 'Open Enrollment'
      : (text.match(/Starting\s+([^|]+(?:\|[^|]+)*)/i)?.[0] || '').trim().slice(0, 80);

    const url = new URL(link.getAttribute('href'), location.origin).href.split('?')[0];
    return { key: url, name, weeks, months, hours, courseType, schedule, url };
  }

  function harvest() {
    let added = 0;
    for (const link of getCourseLinks()) {
      const card = cardFor(link);
      if (!card) continue;
      const row = parseCard(link, card);
      if (!row.name || (!row.weeks && !row.months)) continue;
      const existing = data.get(row.key);
      if (!existing) { data.set(row.key, row); added++; }
      else for (const f of ['weeks', 'months', 'hours', 'courseType', 'schedule'])
        if (!existing[f] && row[f]) existing[f] = row[f];
    }
    persist();
    return added;
  }

  function totalResults() {
    const m = (document.body.innerText || '').match(/([\d,]+)\s*Results/i);
    return m ? Number(m[1].replace(/,/g, '')) : null;
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

  // ----- export -----
  window.__E2_EXPORT = async function () {
    const rows = [...data.values()];
    console.table(rows.slice(0, 30), ['name', 'weeks', 'months', 'hours', 'courseType']);
    const esc = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
    const csv = [
      ['Course Name', 'Weeks', 'Months', 'Course Hours', 'Course Type', 'Schedule', 'URL'].join(','),
      ...rows.map((r) => [r.name, r.weeks, r.months, r.hours, r.courseType, r.schedule, r.url].map(esc).join(',')),
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
  const target = totalResults();
  console.log(`%cScraping ed2go… ${target ? target + ' results reported by the page.' : ''} Stop: window.__E2_STOP = true   Export: __E2_EXPORT()`, 'color:#fff;background:#0057b8;font-weight:bold');

  let added = harvest();
  console.log(`Initial page: +${added} (total ${data.size}${target ? '/' + target : ''})`);
  if (data.size === 0) {
    console.error('Still parsed 0 courses — are the search results visible on this page?');
    return;
  }

  let idle = 0;
  for (let round = 0; round < MAX_ROUNDS && !window.__E2_STOP; round++) {
    if (target && data.size >= target) { console.log('All results collected.'); break; }

    const btn = findLoadMore();
    if (btn) realClick(btn);
    else window.scrollTo(0, document.body.scrollHeight);
    await sleep(PAUSE_MS);

    added = harvest();
    if (added > 0) {
      idle = 0;
      console.log(`+${added} (total ${data.size}${target ? '/' + target : ''})`);
    } else if (++idle >= MAX_IDLE) {
      console.log(btn ? 'Load More clicked but nothing new — stopping.' : 'No Load More button and nothing new — stopping.');
      break;
    }
  }

  const missing = [...data.values()].filter((r) => !r.hours).length;
  console.log(`%cFinished with ${data.size} courses (${missing} missing hours).`, 'color:green;font-weight:bold');
  await window.__E2_EXPORT();
})();
