/**
 * LinkedIn Learning course scraper — paste into the Chrome DevTools console
 * while on: https://www.linkedin.com/learning/search?entityType=COURSE
 *
 * What it does:
 *   1. Auto-scrolls the page (and clicks "Show more results" when present)
 *      until no new courses load.
 *   2. Extracts each course's name, length, rating, and learner count.
 *   3. Prints the results as a table, copies them to your clipboard as CSV,
 *      and downloads a linkedin_learning_courses.csv file.
 *
 * Notes:
 *   - LinkedIn changes its markup frequently, so the extraction is
 *     text-pattern based (duration like "1h 23m", "4.7" ratings,
 *     "12,345 learners") rather than relying on exact CSS class names.
 *   - Only courses that actually render in your browser can be captured.
 *   - Stop early any time with:  window.__LLS_STOP = true
 */
(async function scrapeLinkedInLearning() {
  const SCROLL_PAUSE_MS = 1500;   // wait after each scroll for results to load
  const MAX_IDLE_ROUNDS = 5;      // stop after this many scrolls with no new cards
  const MAX_ROUNDS = 300;         // absolute safety cap
  window.__LLS_STOP = false;

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  // A "card" is the nearest li/section ancestor of any link to a course page.
  function getCards() {
    const links = document.querySelectorAll('a[href*="/learning/"]');
    const cards = new Set();
    for (const a of links) {
      // Skip nav links, "skill" pages, etc. — course URLs look like /learning/<slug>
      const m = a.getAttribute('href').match(/\/learning\/([^/?#]+)/);
      if (!m) continue;
      const slug = m[1];
      if (['search', 'me', 'topics', 'browse', 'subscription', 'paths', 'instructors'].includes(slug)) continue;
      const card = a.closest('li, section, div[data-item-index]');
      if (card && card.innerText && card.innerText.trim().length > 10) {
        cards.add(card);
      }
    }
    return [...cards];
  }

  function parseCard(card) {
    const text = card.innerText.replace(/\s+/g, ' ').trim();

    // Course name: prefer a heading, then the course link text.
    let name = '';
    const heading = card.querySelector('h1,h2,h3,h4,[class*="title" i]');
    if (heading && heading.innerText.trim()) {
      name = heading.innerText.trim();
    } else {
      const link = card.querySelector('a[href*="/learning/"]');
      if (link) name = link.innerText.trim().split('\n')[0];
    }
    name = name.split('\n')[0].trim();

    // Length: "1h 23m", "2h", "38m", "1 hr 5 min", etc.
    let length = '';
    const dur = text.match(/\b(\d+\s*h(?:rs?)?(?:\s*\d+\s*m(?:in)?s?)?|\d+\s*m(?:in)?s?)\b/i);
    if (dur) length = dur[1].replace(/\s+/g, ' ').trim();

    // Rating: a "4.7"-style number, usually near a star or "out of 5".
    let rating = '';
    const ratingMatch =
      text.match(/(\d\.\d)\s*(?:out of 5|★|\/\s*5)/i) ||
      text.match(/(?:rating[:\s]*)(\d\.\d)/i) ||
      text.match(/(\d\.\d)(?=\s*\(?[\d,.]+\s*(?:ratings?|reviews?)\)?)/i) ||
      text.match(/\b([0-5]\.\d)\b/);
    if (ratingMatch) rating = ratingMatch[1];

    // Learners: "123,456 learners" or "1.2K learners" / "1M learners"
    let learners = '';
    const learnerMatch = text.match(/([\d,.]+\s*[KkMm]?)\s*learners?/);
    if (learnerMatch) learners = learnerMatch[1].replace(/\s+/g, '');

    // Course URL for deduping / reference
    const link = card.querySelector('a[href*="/learning/"]');
    let url = link ? link.href.split('?')[0] : '';

    return { name, length, rating, learners, url };
  }

  console.log('%cScrolling to load all courses… (set window.__LLS_STOP = true to stop early)', 'color:#0a66c2;font-weight:bold');

  let lastCount = 0;
  let idleRounds = 0;
  for (let round = 0; round < MAX_ROUNDS && !window.__LLS_STOP; round++) {
    window.scrollTo(0, document.body.scrollHeight);

    // Click "Show more results" if LinkedIn renders a button instead of infinite scroll.
    const btn = [...document.querySelectorAll('button')].find((b) =>
      /show more|see more|load more/i.test(b.innerText)
    );
    if (btn && btn.offsetParent !== null) btn.click();

    await sleep(SCROLL_PAUSE_MS);

    const count = getCards().length;
    if (count > lastCount) {
      console.log(`Loaded ${count} courses…`);
      lastCount = count;
      idleRounds = 0;
    } else {
      idleRounds++;
      if (idleRounds >= MAX_IDLE_ROUNDS) break;
    }
  }

  // Extract + dedupe by URL (fall back to name).
  const seen = new Set();
  const rows = [];
  for (const card of getCards()) {
    const row = parseCard(card);
    if (!row.name) continue;
    // Instructor/author sub-cards have none of the course metrics — skip them.
    if (!row.length && !row.rating && !row.learners) continue;
    const key = row.url || row.name;
    if (seen.has(key)) continue;
    seen.add(key);
    rows.push(row);
  }

  console.log(`%cDone. Extracted ${rows.length} courses.`, 'color:green;font-weight:bold');
  console.table(rows, ['name', 'length', 'rating', 'learners']);

  // Build CSV
  const esc = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
  const csv = [
    ['Course Name', 'Length', 'Rating', 'Learners', 'URL'].join(','),
    ...rows.map((r) => [r.name, r.length, r.rating, r.learners, r.url].map(esc).join(',')),
  ].join('\n');

  // Copy to clipboard (may require the page to be focused)
  try {
    await navigator.clipboard.writeText(csv);
    console.log('CSV copied to clipboard ✔');
  } catch (e) {
    console.warn('Clipboard copy failed (click the page and re-run, or use the downloaded file).');
  }

  // Download as a file
  const blob = new Blob([csv], { type: 'text/csv' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'linkedin_learning_courses.csv';
  document.body.appendChild(a);
  a.click();
  a.remove();

  // Keep the data available for further console work
  window.__LLS_RESULTS = rows;
  console.log('Rows also stored in window.__LLS_RESULTS');
})();
