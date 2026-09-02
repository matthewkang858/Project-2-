/**
 * Google Skills catalog scraper (v2) — paste into the Chrome DevTools console on:
 * https://www.skills.google/catalog?format%5B%5D=courses
 *
 * How it works (built from the real page markup):
 *   The catalog's <ql-search-result-container> element carries a
 *   `pagedsearchresults` attribute containing JSON: searchResults[] (title,
 *   duration, level, path, credentialType), resultsCount, itemsPerPage, and
 *   the backend list URL (e.g. /catalog/list?format[]=courses&...).
 *   v2 fetches that URL with &page=N for every page and parses the same JSON
 *   out of each response — no clicking, no scrolling. If fetching fails, it
 *   falls back to clicking the next-page arrow inside the container's shadow
 *   DOM and harvesting each page as it renders.
 *
 * Controls:
 *   window.__GS_STOP = true   // stop
 *   __GS_EXPORT()             // download CSV of everything collected so far
 *   __GS_RESET()              // wipe saved data
 */
(async function scrapeGoogleSkillsV2() {
  const PAUSE_MS = 700;
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

  // ----- duration: "30 minutes", "45 minutes", "1 hour 15 minutes", "3 hours 45 minutes" -----
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

  // ----- read the live container's embedded JSON -----
  function containerJSON(doc) {
    const el = (doc || document).querySelector('ql-search-result-container');
    if (!el) return null;
    try { return JSON.parse(el.getAttribute('pagedsearchresults') || 'null'); }
    catch { return null; }
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
  const seed = containerJSON();
  if (!seed) {
    console.error('Could not find the results container. Are you on https://www.skills.google/catalog with results visible?');
    return;
  }
  const total = seed.resultsCount || 0;
  const perPage = seed.itemsPerPage || 8;
  const pages = Math.max(1, Math.ceil(total / perPage));
  const listPath = seed.path; // e.g. /catalog/list?format[]=courses&keywords=&level[]=__any__&locale=
  console.log(`%cScraping Google Skills: ${total} results, ${pages} pages of ${perPage}. Stop: window.__GS_STOP = true`, 'color:#fff;background:#1a73e8;font-weight:bold');

  let added = 0;
  for (const r of seed.searchResults || []) added += addResult(r);
  persist();
  console.log(`Page 1 (from live page): +${added} (total ${data.size}/${total})`);

  // --- primary: fetch each page's HTML fragment and read its embedded JSON ---
  let fetchWorks = true;
  for (let page = 1; page <= pages && !window.__GS_STOP; page++) {
    try {
      const sep = listPath.includes('?') ? '&' : '?';
      const res = await fetch(`${listPath}${sep}page=${page}`, {
        credentials: 'same-origin',
        headers: { 'Accept': 'text/html, */*' },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const html = await res.text();
      const doc = new DOMParser().parseFromString(html, 'text/html');
      let json = containerJSON(doc);
      if (!json) {
        // some deployments return bare JSON instead of an HTML fragment
        try { json = JSON.parse(html); } catch {}
      }
      const results = json?.searchResults || json?.results;
      if (!results || !results.length) throw new Error('no results parsed');
      let got = 0;
      for (const r of results) got += addResult(r);
      persist();
      if (page % 5 === 0 || page === pages) console.log(`Page ${page}/${pages}: total ${data.size}/${total}`);
      await sleep(PAUSE_MS);
    } catch (e) {
      console.warn(`Fetch mode failed on page ${page} (${e.message}) — switching to click-through mode.`);
      fetchWorks = false;
      break;
    }
  }

  // --- fallback: click the next-page arrow inside the shadow DOM ---
  if (!fetchWorks && !window.__GS_STOP) {
    const container = document.querySelector('ql-search-result-container');
    const sr = () => container.shadowRoot;
    const pageLabel = () => sr()?.querySelector('.pagination-page')?.textContent?.trim() || '';

    function harvestShadowCards() {
      let got = 0;
      for (const card of sr()?.querySelectorAll('ql-activity-card') || []) {
        const root = card.shadowRoot || card;
        const a = root.querySelector('a.wrapper-link');
        if (!a) continue;
        const durEl = root.querySelector('.duration span, .duration');
        got += addResult({
          title: a.getAttribute('title') || root.querySelector('h3.name')?.textContent || '',
          path: a.getAttribute('href') || '',
          duration: durEl ? durEl.textContent.replace(/^pace/i, '').trim() : '',
          type: 'course',
        });
      }
      persist();
      return got;
    }

    harvestShadowCards();
    for (let i = 0; i < pages + 5 && !window.__GS_STOP; i++) {
      if (data.size >= total) break;
      const before = pageLabel();
      const next = sr()?.querySelector('ql-icon-button.next-page');
      const nextBtn = next?.shadowRoot?.querySelector('button') || next;
      if (!next || next.hasAttribute('disabled')) { console.log('Next-page button disabled — reached the end.'); break; }
      nextBtn.dispatchEvent(new MouseEvent('click', { bubbles: true, composed: true }));
      // wait for the page label ("9 - 16 of 607") to change
      for (let w = 0; w < 40 && pageLabel() === before; w++) await sleep(250);
      await sleep(400);
      harvestShadowCards();
      if (i % 5 === 0) console.log(`${pageLabel()} — total ${data.size}/${total}`);
    }
  }

  console.log(`%cFinished with ${data.size} rows (site reported ${total}).`, 'color:green;font-weight:bold');
  await window.__GS_EXPORT();
})();
