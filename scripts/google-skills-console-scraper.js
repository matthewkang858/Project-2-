/**
 * Google Skills catalog scraper (v3) — paste into the Chrome DevTools console on:
 * https://www.skills.google/catalog?format%5B%5D=courses
 *
 * How it works: the catalog page embeds each page's results as JSON in the
 * `pagedsearchresults` attribute of <ql-search-result-container> (title,
 * duration, level, path, credentialType, resultsCount, itemsPerPage).
 * v3 fetches the CATALOG PAGE ITSELF with ?page=2, ?page=3, ... and reads
 * that same attribute out of each response — the one place the data is
 * guaranteed to exist, since it's exactly what the live page renders from.
 * (v2 hit the internal /catalog/list endpoint, which answers in a different
 * format and parsed as empty.)
 *
 * Controls:
 *   window.__GS_STOP = true   // stop
 *   __GS_EXPORT()             // download CSV of everything collected so far
 *   __GS_RESET()              // wipe saved data
 */
(async function scrapeGoogleSkillsV3() {
  const PAUSE_MS = 800;
  const LS_KEY = 'gs_scrape_v1';
  window.__GS_STOP = false;

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  // ----- persistent store -----
  const data = new Map();
  try {
    const saved = JSON.parse(localStorage.getItem(LS_KEY) || '[]');
    for (const row of saved) data.set(row.key, row);
    if (saved.length) console.log(`Resumed with ${saved.length} rows from a previous run.`);
  } catch {}
  function persist() {
    try { localStorage.setItem(LS_KEY, JSON.stringify([...data.values()])); }
    catch (e) { console.warn('localStorage save failed:', e.message); }
  }
  window.__GS_RESET = () => { localStorage.removeItem(LS_KEY); data.clear(); console.log('Cleared saved data.'); };

  // ----- duration: "30 minutes", "1 hour 15 minutes", "3 hours 45 minutes" -----
  function parseDuration(text) {
    if (!text) return { length: '', hours: '' };
    const h = text.match(/(\d+(?:\.\d+)?)\s*hours?/i);
    const m = text.match(/(\d+)\s*min(?:ute)?s?/i);
    if (!h && !m) return { length: String(text).trim(), hours: '' };
    const hours = (h ? parseFloat(h[1]) : 0) + (m ? parseInt(m[1]) / 60 : 0);
    return { length: String(text).trim(), hours: String(Math.round(hours * 100) / 100) };
  }

  function addResult(r) {
    const url = new URL(r.path || '', location.origin);
    const key = url.origin + url.pathname; // drop catalog_rank query noise
    const { length, hours } = parseDuration(r.duration);
    const row = {
      key,
      name: (r.title || '').trim(),
      length, hours,
      level: r.level || '',
      type: r.type || '',
      credential: r.credentialType || '',
      url: key,
    };
    if (!row.name) return 0;
    if (!data.has(key)) { data.set(key, row); return 1; }
    return 0;
  }

  // ----- pull the embedded JSON out of a document or raw HTML string -----
  function extractJSON(docOrHtml) {
    if (typeof docOrHtml !== 'string') {
      const el = docOrHtml.querySelector('ql-search-result-container');
      if (el) {
        try { return JSON.parse(el.getAttribute('pagedsearchresults') || 'null'); } catch {}
      }
      return null;
    }
    // raw-text fallback: find the attribute and decode HTML entities
    const m = docOrHtml.match(/pagedsearchresults="([^"]*)"/i);
    if (!m) return null;
    const decoded = m[1]
      .replace(/&quot;/g, '"').replace(/&#39;/g, "'")
      .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');
    try { return JSON.parse(decoded); } catch { return null; }
  }

  // ----- export -----
  window.__GS_EXPORT = async function () {
    const rows = [...data.values()];
    console.table(rows.slice(0, 30), ['name', 'length', 'hours', 'level', 'credential']);
    const esc = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
    const csv = [
      ['Course Name', 'Length', 'Hours', 'Level', 'Type', 'Credential', 'URL'].join(','),
      ...rows.map((r) => [r.name, r.length, r.hours, r.level, r.type, r.credential, r.url].map(esc).join(',')),
    ].join('\n');
    try { await navigator.clipboard.writeText(csv); console.log('CSV copied ✔'); } catch {}
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
    a.download = 'google_skills_courses.csv';
    document.body.appendChild(a); a.click(); a.remove();
    console.log(`Exported ${rows.length} rows.`);
    return rows;
  };

  // ----- main -----
  const seed = extractJSON(document);
  if (!seed) {
    console.error('Could not find the results container. Are you on https://www.skills.google/catalog with results visible?');
    return;
  }
  const total = seed.resultsCount || 0;
  const perPage = seed.itemsPerPage || 8;
  const pages = Math.max(1, Math.ceil(total / perPage));
  console.log(`%cScraping Google Skills: ${total} results, ${pages} pages of ${perPage}. Stop: window.__GS_STOP = true`, 'color:#fff;background:#1a73e8;font-weight:bold');

  let added = 0;
  for (const r of seed.searchResults || []) added += addResult(r);
  persist();
  console.log(`Page 1 (from live page): +${added} (total ${data.size}/${total})`);

  // fetch the catalog page itself with ?page=N — same URL you're on now
  function pageURL(n) {
    const u = new URL(location.href);
    u.searchParams.set('page', String(n));
    return u.pathname + u.search;
  }

  let emptyStreak = 0;
  for (let page = 2; page <= pages && !window.__GS_STOP; page++) {
    let got = 0;
    try {
      const res = await fetch(pageURL(page), { credentials: 'same-origin' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const html = await res.text();
      let json = extractJSON(new DOMParser().parseFromString(html, 'text/html')) || extractJSON(html);
      const results = json?.searchResults;
      if (!results || !results.length) {
        console.warn(`Page ${page}: could not parse results. First 1200 chars of response (paste back to Claude if this keeps happening):`);
        console.log(html.slice(0, 1200));
        throw new Error('no results parsed');
      }
      for (const r of results) got += addResult(r);
      persist();
    } catch (e) {
      console.warn(`Page ${page} failed: ${e.message}`);
    }
    if (got === 0) {
      if (++emptyStreak >= 3) {
        console.error('3 pages in a row added nothing — the ?page= parameter may be ignored or the session is being rate-limited. Stopping; paste the warnings above back to Claude.');
        break;
      }
    } else emptyStreak = 0;
    if (page % 5 === 0 || page === pages) console.log(`Page ${page}/${pages}: total ${data.size}/${total}`);
    await sleep(PAUSE_MS);
  }

  console.log(`%cFinished with ${data.size} rows (site reported ${total}).`, 'color:green;font-weight:bold');
  await window.__GS_EXPORT();
})();
