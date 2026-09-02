/**
 * DataCamp course-catalog scraper (v1) — paste into the Chrome DevTools
 * console on: https://www.datacamp.com/courses-all?page=1
 *
 * Strategy (DataCamp is a server-rendered Next.js site):
 *   1. For each page (?page=1, 2, 3, ...) fetch the full HTML.
 *   2. Prefer the embedded __NEXT_DATA__ JSON: deep-scan it for course
 *      objects (anything with a title plus a duration/time field).
 *   3. Fall back to DOM parsing: /courses/... links climbed to their card,
 *      duration matched as "4 hours" / "4 hr" / "45 min".
 *   4. Stop when pages stop yielding anything new.
 *
 * If page 1 parses to zero rows it prints diagnostics — paste those back
 * to Claude for a one-round fix.
 *
 * Controls:
 *   window.__DC_STOP = true   // stop
 *   __DC_EXPORT()             // download CSV of everything collected so far
 *   __DC_RESET()              // wipe saved data
 */
(async function scrapeDataCampV1() {
  const PAUSE_MS = 900;
  const MAX_PAGES = 200;
  const LS_KEY = 'dc_scrape_v1';
  window.__DC_STOP = false;

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
  window.__DC_RESET = () => { localStorage.removeItem(LS_KEY); data.clear(); console.log('Cleared saved data.'); };

  // ----- duration parsing: "4 hours", "4 hr", "1.5 hours", "45 min", numeric hours -----
  function parseDuration(val) {
    if (val == null || val === '') return { length: '', hours: '' };
    if (typeof val === 'number') {
      // Next.js data sometimes stores raw hours (4) or minutes (240)
      const hours = val > 30 ? val / 60 : val;
      return { length: `${Math.round(hours * 100) / 100} hours`, hours: String(Math.round(hours * 100) / 100) };
    }
    const text = String(val);
    const h = text.match(/(\d+(?:\.\d+)?)\s*h(?:ou)?rs?\b/i);
    const m = text.match(/(\d+)\s*m(?:in(?:ute)?s?)?\b/i);
    if (!h && !m) return { length: text.trim(), hours: '' };
    const hours = (h ? parseFloat(h[1]) : 0) + (m ? parseInt(m[1]) / 60 : 0);
    return { length: text.trim(), hours: String(Math.round(hours * 100) / 100) };
  }

  function addRow({ name, duration, level, tech, url }) {
    name = (name || '').trim();
    if (!name) return 0;
    const key = url || name.toLowerCase();
    const { length, hours } = parseDuration(duration);
    const existing = data.get(key);
    if (existing) {
      if (!existing.length && length) { existing.length = length; existing.hours = hours; }
      if (!existing.level && level) existing.level = level;
      if (!existing.tech && tech) existing.tech = tech;
      return 0;
    }
    data.set(key, { key, name, length, hours, level: level || '', tech: tech || '', url: url || '' });
    return 1;
  }

  // ----- strategy A: deep-scan __NEXT_DATA__ (or any embedded JSON) -----
  function scanJSON(root) {
    let added = 0;
    const seen = new Set();
    const stack = [root];
    while (stack.length) {
      const node = stack.pop();
      if (!node || typeof node !== 'object' || seen.has(node)) continue;
      seen.add(node);
      const title = node.title || node.name;
      const dur = node.duration ?? node.time ?? node.timeNeeded ?? node.hours ?? node.length_in_hours ?? node.nb_of_hours;
      const slug = node.slug || node.link || node.url || node.path || node.href;
      const looksLikeCourse =
        typeof title === 'string' && title.length > 3 && dur != null &&
        (typeof dur === 'number' || /\d/.test(String(dur)));
      if (looksLikeCourse) {
        let url = '';
        if (typeof slug === 'string') {
          url = slug.startsWith('http') ? slug
            : slug.startsWith('/') ? location.origin + slug
            : location.origin + '/courses/' + slug;
          url = url.split('?')[0];
        }
        added += addRow({
          name: title,
          duration: dur,
          level: node.difficultyLevel || node.difficulty || node.level || '',
          tech: node.technology || node.technology_slug || (node.technologies?.[0]?.name) || '',
          url,
        });
      }
      for (const k in node) {
        const v = node[k];
        if (v && typeof v === 'object') stack.push(v);
      }
    }
    return added;
  }

  function harvestNextData(doc) {
    const script = doc.querySelector('#__NEXT_DATA__') ||
      [...doc.querySelectorAll('script[type="application/json"]')].find((s) => /"props"|courses/i.test(s.textContent || ''));
    if (!script) return -1; // no embedded JSON found at all
    try { return scanJSON(JSON.parse(script.textContent)); }
    catch { return -1; }
  }

  // ----- strategy B: DOM cards -----
  const DUR_RE = /(\d+(?:\.\d+)?)\s*h(?:ou)?rs?\b|\b(\d+)\s*min(?:ute)?s?\b/i;
  function harvestDOM(doc) {
    let added = 0;
    const links = [...doc.querySelectorAll('a[href*="/courses/"]')].filter((a) => {
      const href = a.getAttribute('href') || '';
      return /\/courses\/[a-z0-9-]{3,}/i.test(href) && !/courses-all/.test(href);
    });
    for (const link of links) {
      // climb to the card that contains a duration
      let card = link;
      for (let i = 0; i < 6 && card; i++) {
        const t = card.innerText || card.textContent || '';
        if (DUR_RE.test(t)) break;
        card = card.parentElement;
      }
      if (!card) continue;
      const text = (card.innerText || card.textContent || '').replace(/\s+/g, ' ').trim();
      const dm = text.match(DUR_RE);
      if (!dm) continue;
      const name = (link.querySelector('h1,h2,h3,h4,[class*="title"]')?.textContent ||
        card.querySelector('h1,h2,h3,h4,[class*="title"]')?.textContent ||
        link.textContent || '').replace(/\s+/g, ' ').trim().split(/ {2,}/)[0];
      const level = (text.match(/\b(Beginner|Intermediate|Advanced)\b/i)?.[1]) || '';
      added += addRow({
        name,
        duration: dm[0],
        level,
        url: new URL(link.getAttribute('href'), location.origin).href.split('?')[0],
      });
    }
    return added;
  }

  function harvestDoc(doc) {
    const fromJSON = harvestNextData(doc);
    const fromDOM = harvestDOM(doc);
    return { added: Math.max(fromJSON, 0) + fromDOM, hadJSON: fromJSON >= 0 };
  }

  // ----- export -----
  window.__DC_EXPORT = async function () {
    const rows = [...data.values()];
    console.table(rows.slice(0, 30), ['name', 'length', 'hours', 'level', 'tech']);
    const esc = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
    const csv = [
      ['Course Name', 'Length', 'Hours', 'Level', 'Technology', 'URL'].join(','),
      ...rows.map((r) => [r.name, r.length, r.hours, r.level, r.tech, r.url].map(esc).join(',')),
    ].join('\n');
    try { await navigator.clipboard.writeText(csv); console.log('CSV copied ✔'); } catch {}
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
    a.download = 'datacamp_courses.csv';
    document.body.appendChild(a); a.click(); a.remove();
    console.log(`Exported ${rows.length} courses.`);
    return rows;
  };

  // ----- main -----
  console.log('%cScraping DataCamp catalog… Stop: window.__DC_STOP = true   Export: __DC_EXPORT()', 'color:#fff;background:#03ef62;color:#05192d;font-weight:bold');

  // page 1: use the live document
  const first = harvestDoc(document);
  console.log(`Page 1 (live page): +${first.added} (total ${data.size})`);
  if (data.size === 0) {
    console.error('Parsed 0 courses from the live page. Diagnostics — paste ALL of this back to Claude:');
    console.log('__NEXT_DATA__ present:', !!document.querySelector('#__NEXT_DATA__'));
    console.log('course links found:', document.querySelectorAll('a[href*="/courses/"]').length);
    const anyLink = document.querySelector('a[href*="/courses/"]');
    if (anyLink) {
      let card = anyLink;
      for (let i = 0; i < 3 && card.parentElement; i++) card = card.parentElement;
      console.log(card.outerHTML.slice(0, 3000));
    }
    return;
  }

  let emptyStreak = 0;
  for (let page = 2; page <= MAX_PAGES && !window.__DC_STOP; page++) {
    let added = 0;
    try {
      const res = await fetch(`/courses-all?page=${page}`, { credentials: 'same-origin' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const html = await res.text();
      const doc = new DOMParser().parseFromString(html, 'text/html');
      added = harvestDoc(doc).added;
      persist();
    } catch (e) {
      console.warn(`Page ${page} failed: ${e.message}`);
    }
    if (added === 0) {
      if (++emptyStreak >= 2) { console.log(`Two pages with nothing new — assuming page ${page} is past the end.`); break; }
    } else emptyStreak = 0;
    if (page % 5 === 0) console.log(`Page ${page}: total ${data.size} courses`);
    await sleep(PAUSE_MS);
  }
  persist();

  console.log(`%cFinished with ${data.size} courses.`, 'color:green;font-weight:bold');
  await window.__DC_EXPORT();
})();
