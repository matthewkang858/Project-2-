/**
 * FutureLearn course scraper (v2) — paste into the Chrome DevTools console while on:
 * https://www.futurelearn.com/courses?filter_category=open&filter_course_type=unlimited&filter_availability=started
 *
 * Phase 1: fetches listing pages (?page=1,2,3...) and parses each course's
 *          name, weeks, hours per week, and rating.
 * Phase 2: for courses where the listing HTML didn't contain the weeks value
 *          (it's rendered by JS on the live page, so raw fetched HTML lacks it),
 *          fetches each course's own page and reads the duration/rating there.
 *
 * Total Hours = Weeks x Hours per Week. Exports CSV when done.
 *
 * Controls:
 *   window.__FL_STOP = true   // stop fetching (works in both phases)
 *   __FL_EXPORT()             // download CSV of everything collected so far
 */
(async function scrapeFutureLearnV2() {
  const PAGE_PAUSE_MS = 800;   // pause between listing pages
  const FILL_PAUSE_MS = 400;   // pause between course-page fetches (phase 2)
  const MAX_PAGES = 200;
  window.__FL_STOP = false;
  const data = (window.__FL_DATA = window.__FL_DATA || new Map());

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const params = new URLSearchParams(location.search);
  const parser = new DOMParser();

  function extractCourses(doc) {
    const cards = new Set();
    for (const a of doc.querySelectorAll('a[href*="/courses/"]')) {
      const m = a.getAttribute('href').match(/\/courses\/([^/?#]+)/);
      if (!m) continue;
      if (['collections', 'categories'].includes(m[1])) continue;
      const card = a.closest('li, article, [class*="card" i], div');
      if (card && (card.textContent || '').trim().length > 20) cards.add(card);
    }
    return [...cards];
  }

  function parseCard(card) {
    const text = (card.innerText || card.textContent || '').replace(/\s+/g, ' ').trim();
    const html = card.outerHTML || '';

    let name = '';
    const heading = card.querySelector('h1,h2,h3,h4,[class*="title" i],[class*="heading" i]');
    if (heading) name = (heading.innerText || heading.textContent || '').trim();
    if (!name) {
      const link = card.querySelector('a[href*="/courses/"]');
      if (link) name = (link.innerText || link.textContent || '').trim();
    }
    name = name.split('\n')[0].trim();

    // Weeks: try visible text first, then the raw markup (attributes, data-*, JSON)
    let weeks = '';
    const w =
      text.match(/(\d+(?:\.\d+)?)\s*weeks?\b/i) ||
      html.match(/(\d+(?:\.\d+)?)\s*weeks?\b/i) ||
      html.match(/"duration[^"]*"\s*:\s*"?(\d+)/i);
    if (w) weeks = w[1];

    let hoursPerWeek = '';
    const h =
      text.match(/(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)\s*(?:per|a|\/)\s*week/i) ||
      text.match(/weekly study\s*:?\s*(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)/i) ||
      text.match(/(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)\s*weekly/i) ||
      html.match(/(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)\s*(?:per|a|\/)\s*week/i);
    if (h) hoursPerWeek = h[1];

    let rating = '';
    const r =
      text.match(/(\d\.\d)\s*\(?\s*[\d,]*\s*reviews?/i) ||
      text.match(/(\d\.\d)\s*stars?/i) ||
      html.match(/"ratingValue"\s*:\s*"?([\d.]+)/i);
    if (r) rating = r[1];

    const link = card.querySelector('a[href*="/courses/"]');
    const url = link ? new URL(link.getAttribute('href'), location.origin).href.split('?')[0] : '';

    return { name, weeks, hoursPerWeek, rating, url };
  }

  function withTotal(row) {
    row.totalHours =
      row.weeks && row.hoursPerWeek ? String(Number(row.weeks) * Number(row.hoursPerWeek)) : '';
    return row;
  }

  function harvestDoc(doc) {
    let added = 0;
    for (const card of extractCourses(doc)) {
      const row = parseCard(card);
      if (!row.name || (!row.weeks && !row.hoursPerWeek)) continue;
      const key = row.url || row.name;
      const existing = data.get(key);
      if (!existing) { data.set(key, withTotal(row)); added++; }
      else {
        // Fill in fields an earlier pass missed
        for (const f of ['weeks', 'hoursPerWeek', 'rating']) if (!existing[f] && row[f]) existing[f] = row[f];
        withTotal(existing);
      }
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

  // ---------- Phase 1: listing pages ----------
  console.log('%cPhase 1: fetching listing pages… Stop: window.__FL_STOP = true', 'color:#de00a5;font-weight:bold');
  let total = harvestDoc(document);
  console.log(`Page 1 (current page): ${total} courses.`);

  for (let page = 2; page <= MAX_PAGES && !window.__FL_STOP; page++) {
    params.set('page', String(page));
    const url = `${location.pathname}?${params.toString()}`;
    let added = 0;
    try {
      const res = await fetch(url, { credentials: 'same-origin' });
      if (!res.ok) { console.log(`Page ${page}: HTTP ${res.status} — stopping.`); break; }
      added = harvestDoc(parser.parseFromString(await res.text(), 'text/html'));
    } catch (e) {
      console.warn(`Page ${page} failed (${e.message}) — stopping.`);
      break;
    }
    console.log(`Page ${page}: +${added} (total ${data.size})`);
    if (added === 0) { console.log('No new courses — listing done.'); break; }
    await sleep(PAGE_PAUSE_MS);
  }

  // ---------- Phase 2: fill missing weeks/ratings from course pages ----------
  const missing = [...data.values()].filter((r) => (!r.weeks || !r.rating) && r.url);
  const needWeeks = missing.filter((r) => !r.weeks).length;
  console.log(
    `%cPhase 2: fetching ${missing.length} course pages to fill gaps (${needWeeks} missing weeks). ` +
      `~${Math.ceil((missing.length * FILL_PAUSE_MS) / 60000)} min. Stop any time: window.__FL_STOP = true, then __FL_EXPORT()`,
    'color:#de00a5;font-weight:bold'
  );

  let i = 0;
  for (const row of missing) {
    if (window.__FL_STOP) break;
    i++;
    try {
      const res = await fetch(row.url, { credentials: 'same-origin' });
      if (res.ok) {
        const html = await res.text();
        if (!row.weeks) {
          const w =
            html.match(/(\d+)\s*weeks?\b/i) ||
            html.match(/"timeRequired"\s*:\s*"P(\d+)W/i);
          if (w) row.weeks = w[1];
        }
        if (!row.hoursPerWeek) {
          const h = html.match(/(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)\s*(?:per|a|\/)\s*week/i);
          if (h) row.hoursPerWeek = h[1];
        }
        if (!row.rating) {
          const r = html.match(/"ratingValue"\s*:\s*"?([\d.]+)/i) || html.match(/(\d\.\d)\s*stars?/i);
          if (r) row.rating = r[1];
        }
        withTotal(row);
      }
    } catch (e) {
      console.warn(`Course fetch failed for ${row.url}: ${e.message}`);
    }
    if (i % 25 === 0) console.log(`Phase 2: ${i}/${missing.length} done…`);
    await sleep(FILL_PAUSE_MS);
  }

  const stillMissing = [...data.values()].filter((r) => !r.weeks).length;
  console.log(`%cFinished: ${data.size} courses, ${stillMissing} still missing weeks.`, 'color:green;font-weight:bold');
  await window.__FL_EXPORT();
})();
