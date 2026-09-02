/**
 * FutureLearn course scraper — paste into the Chrome DevTools console while on:
 * https://www.futurelearn.com/courses?filter_category=open&filter_course_type=unlimited&filter_availability=started
 *
 * Unlike LinkedIn, FutureLearn uses server-rendered pages with numbered
 * pagination, so this script fetches ?page=1, ?page=2, ... directly and
 * parses the HTML — no scrolling or clicking needed.
 *
 * For each course it extracts: name, weeks, hours per week, and
 * total hours = weeks x hours per week. Exports CSV when done.
 *
 * Controls:
 *   window.__FL_STOP = true   // stop fetching further pages
 *   __FL_EXPORT()             // download CSV of everything collected so far
 */
(async function scrapeFutureLearn() {
  const PAGE_PAUSE_MS = 800;  // be polite between page fetches
  const MAX_PAGES = 200;      // safety cap
  window.__FL_STOP = false;
  const data = (window.__FL_DATA = window.__FL_DATA || new Map());

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  // Keep the current filters, drive only the page number.
  const params = new URLSearchParams(location.search);

  function extractCourses(doc) {
    const cards = new Set();
    for (const a of doc.querySelectorAll('a[href*="/courses/"]')) {
      const m = a.getAttribute('href').match(/\/courses\/([^/?#]+)/);
      if (!m) continue;
      // Skip the listing page itself and category-style links
      if (['collections', 'categories'].includes(m[1])) continue;
      const card = a.closest('li, article, [class*="card" i], div');
      if (card && card.innerText && card.innerText.trim().length > 20) cards.add(card);
    }
    return [...cards];
  }

  function parseCard(card) {
    const text = card.innerText.replace(/\s+/g, ' ').trim();

    let name = '';
    const heading = card.querySelector('h1,h2,h3,h4,[class*="title" i],[class*="heading" i]');
    if (heading && heading.innerText.trim()) name = heading.innerText.trim();
    else {
      const link = card.querySelector('a[href*="/courses/"]');
      if (link) name = link.innerText.trim();
    }
    name = name.split('\n')[0].trim();

    // "4 weeks" / "Duration 4 weeks"
    let weeks = '';
    const w = text.match(/(\d+(?:\.\d+)?)\s*weeks?\b/i);
    if (w) weeks = w[1];

    // "3 hours per week" / "Weekly study 3 hours" / "3 hrs/week"
    let hoursPerWeek = '';
    const h =
      text.match(/(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)\s*(?:per|a|\/)\s*week/i) ||
      text.match(/weekly study\s*:?\s*(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)/i) ||
      text.match(/(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)\s*weekly/i);
    if (h) hoursPerWeek = h[1];

    // Rating if shown, e.g. "4.7 (365 reviews)"
    let rating = '';
    const r = text.match(/(\d\.\d)\s*\(?\s*[\d,]*\s*reviews?/i) || text.match(/(\d\.\d)\s*stars?/i);
    if (r) rating = r[1];

    const totalHours =
      weeks && hoursPerWeek ? String(Number(weeks) * Number(hoursPerWeek)) : '';

    const link = card.querySelector('a[href*="/courses/"]');
    const url = link ? new URL(link.getAttribute('href'), location.origin).href.split('?')[0] : '';

    return { name, weeks, hoursPerWeek, totalHours, rating, url };
  }

  function harvestDoc(doc) {
    let added = 0;
    for (const card of extractCourses(doc)) {
      const row = parseCard(card);
      if (!row.name || (!row.weeks && !row.hoursPerWeek)) continue;
      const key = row.url || row.name;
      if (!data.has(key)) { data.set(key, row); added++; }
    }
    return added;
  }

  window.__FL_EXPORT = async function () {
    const rows = [...data.values()];
    console.table(rows, ['name', 'weeks', 'hoursPerWeek', 'totalHours', 'rating']);
    const esc = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
    const csv = [
      ['Course Name', 'Weeks', 'Hours per Week', 'Total Hours', 'Rating', 'URL'].join(','),
      ...rows.map((r) => [r.name, r.weeks, r.hoursPerWeek, r.totalHours, r.rating, r.url].map(esc).join(',')),
    ].join('\n');
    try { await navigator.clipboard.writeText(csv); console.log('CSV copied ✔'); } catch {}
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
    a.download = 'futurelearn_courses.csv';
    document.body.appendChild(a); a.click(); a.remove();
    console.log(`Exported ${rows.length} courses.`);
    return rows;
  };

  console.log('%cFetching FutureLearn pages… Stop: window.__FL_STOP = true', 'color:#de00a5;font-weight:bold');

  // Page 1: use the DOM that's already rendered in front of you.
  let total = harvestDoc(document);
  console.log(`Page 1 (current page): ${total} courses.`);

  const parser = new DOMParser();
  for (let page = 2; page <= MAX_PAGES && !window.__FL_STOP; page++) {
    params.set('page', String(page));
    const url = `${location.pathname}?${params.toString()}`;
    let added = 0;
    try {
      const res = await fetch(url, { credentials: 'same-origin' });
      if (!res.ok) { console.log(`Page ${page}: HTTP ${res.status} — stopping.`); break; }
      const doc = parser.parseFromString(await res.text(), 'text/html');
      added = harvestDoc(doc);
    } catch (e) {
      console.warn(`Page ${page} failed (${e.message}) — stopping.`);
      break;
    }
    total = data.size;
    console.log(`Page ${page}: +${added} (total ${total})`);
    if (added === 0) { console.log('No new courses on this page — done.'); break; }
    await sleep(PAGE_PAUSE_MS);
  }

  console.log(`%cFinished with ${data.size} courses.`, 'color:green;font-weight:bold');
  await window.__FL_EXPORT();
})();
