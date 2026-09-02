/**
 * Skillshare course scraper (v3) — paste into the Chrome DevTools console while on:
 * https://www.skillshare.com/en/browse?sort=popular&page=1
 *
 * Selectors are based on Skillshare's actual card markup:
 *   card:    [data-testid="class-card-content"]   (cards contain NO links)
 *   title:   .class-link
 *   teacher: first .sk-line-clamp-1 span
 *   rating:  [data-testid="class-rating"] .sk-font-bold, reviews in the next span
 *   level:   [data-testid="level-indicator"]
 *   students + duration: bottom-row leaf text ("30.5k", "5h 57m")
 *
 * Pages by clicking the ?page=N+1 pagination link. Collected rows are saved
 * to localStorage after every page, so nothing is lost even if the site does
 * a full page reload — if the console goes quiet/clears after a page change,
 * just paste the script again and it resumes where it left off.
 *
 * Controls:
 *   window.__SS_STOP = true   // stop paging
 *   __SS_EXPORT()             // download CSV of everything collected so far
 *   __SS_RESET()              // wipe the saved data and start fresh
 */
(async function scrapeSkillshareV3() {
  const MAX_PAGES = 405;
  const RENDER_TIMEOUT_MS = 15000;
  const SETTLE_MS = 500;
  const LS_KEY = 'ss_scrape_v3';
  window.__SS_STOP = false;

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  // ----- persistent store (localStorage-backed) -----
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
  window.__SS_RESET = () => { localStorage.removeItem(LS_KEY); data.clear(); console.log('Cleared saved data.'); };

  // ----- parsing -----
  function getCards() {
    return [...document.querySelectorAll('[data-testid="class-card-content"]')];
  }

  function parseCard(card) {
    const title = (card.querySelector('.class-link')?.innerText || '').trim();

    let teacher = (card.querySelector('.sk-line-clamp-1')?.innerText || '').trim().split('\n')[0];

    const rating = (card.querySelector('[data-testid="class-rating"] .sk-font-bold')?.innerText || '').trim();
    const reviewsRaw = (card.querySelector('[data-testid="class-rating"] span:last-child')?.innerText || '').trim();
    const reviews = reviewsRaw.replace(/[()]/g, '');

    const level = (card.querySelector('[data-testid="level-indicator"]')?.innerText || '').trim();

    // Duration and students live in leaf elements at the bottom of the card
    let length = '', students = '';
    for (const el of card.querySelectorAll('*')) {
      if (el.children.length !== 0) continue;
      if (el.closest('[data-testid="class-rating"]')) continue;
      const t = (el.textContent || '').trim();
      if (/^\d+h\s*\d*m?$|^\d+\s*m(?:in)?$/i.test(t)) length = t;
      else if (/^[\d,]+(?:\.\d+)?\s*[kKmM]?$/.test(t) && !t.startsWith('+')) students = t.replace(/\s+/g, '');
    }

    // Cards contain no links; try an ancestor anchor for the URL, else blank
    const wrap = card.closest('a[href]');
    const url = wrap ? new URL(wrap.getAttribute('href'), location.origin).href.split('?')[0] : '';

    return { key: `${title}|${teacher}`, name: title, length, teacher, students, rating, reviews, level, url };
  }

  function harvest() {
    let added = 0;
    for (const card of getCards()) {
      const row = parseCard(card);
      if (!row.name || !row.length) continue;
      const existing = data.get(row.key);
      if (!existing) { data.set(row.key, row); added++; }
      else for (const f of ['length', 'teacher', 'students', 'rating', 'reviews', 'level', 'url'])
        if (!existing[f] && row[f]) existing[f] = row[f];
    }
    persist();
    return added;
  }

  function pageSignature() {
    const cards = getCards();
    return cards.length + '::' + (cards[0]?.querySelector('.class-link')?.innerText || '') +
      '::' + (cards[cards.length - 1]?.querySelector('.class-link')?.innerText || '');
  }

  function currentPage() {
    return Number(new URLSearchParams(location.search).get('page') || '1');
  }

  function findPageLink(page) {
    for (const a of document.querySelectorAll('a[href*="page="]')) {
      try {
        const u = new URL(a.getAttribute('href'), location.origin);
        if (u.pathname.includes('/browse') && Number(u.searchParams.get('page')) === page) return a;
      } catch {}
    }
    // fallback: an explicit next control
    return (
      document.querySelector('[rel="next"]') ||
      [...document.querySelectorAll('button, a, [role="button"]')].find((el) =>
        /next page|^next$/i.test(((el.getAttribute('aria-label') || '') + ' ' + (el.innerText || '')).trim())
      ) || null
    );
  }

  function realClick(el) {
    el.scrollIntoView({ block: 'center' });
    const opts = { bubbles: true, cancelable: true, view: window };
    for (const type of ['pointerover', 'pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click']) {
      el.dispatchEvent(new PointerEvent(type, opts));
    }
  }

  // ----- export -----
  window.__SS_EXPORT = async function () {
    const rows = [...data.values()];
    console.table(rows.slice(0, 30), ['name', 'length', 'teacher', 'students', 'rating', 'level']);
    const esc = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
    const csv = [
      ['Course Name', 'Length', 'Teacher', 'Students', 'Rating', 'Reviews', 'Level', 'URL'].join(','),
      ...rows.map((r) => [r.name, r.length, r.teacher, r.students, r.rating, r.reviews, r.level, r.url].map(esc).join(',')),
    ].join('\n');
    try { await navigator.clipboard.writeText(csv); console.log('CSV copied ✔'); } catch {}
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
    a.download = 'skillshare_courses.csv';
    document.body.appendChild(a); a.click(); a.remove();
    console.log(`Exported ${rows.length} courses.`);
    return rows;
  };

  // ----- main loop -----
  console.log('%cScraping Skillshare (v3). Stop: window.__SS_STOP = true   Export: __SS_EXPORT()', 'color:#00ff84;background:#002333;font-weight:bold');

  let added = harvest();
  console.log(`Page ${currentPage()}: +${added} (total ${data.size})`);
  if (getCards().length === 0) {
    console.error('No [data-testid="class-card-content"] cards found — is the course grid on screen?');
    return;
  }

  while (currentPage() < MAX_PAGES && !window.__SS_STOP) {
    const target = currentPage() + 1;
    const link = findPageLink(target);
    if (!link) { console.log(`No link to page ${target} — assuming last page. Done.`); break; }

    const before = pageSignature();
    realClick(link);

    const deadline = Date.now() + RENDER_TIMEOUT_MS;
    let changed = false;
    while (Date.now() < deadline && !window.__SS_STOP) {
      await sleep(300);
      if (pageSignature() !== before) { changed = true; break; }
    }
    if (!changed) {
      console.warn(`Cards did not change within ${RENDER_TIMEOUT_MS / 1000}s of clicking to page ${target} — stopping. Progress is saved; re-paste the script to resume.`);
      break;
    }
    await sleep(SETTLE_MS);

    added = harvest();
    console.log(`Page ${currentPage()}/${MAX_PAGES}: +${added} (total ${data.size})`);
  }

  const missingLen = [...data.values()].filter((r) => !r.length).length;
  console.log(`%cFinished: ${data.size} courses (${missingLen} missing length).`, 'color:green;font-weight:bold');
  await window.__SS_EXPORT();
})();
