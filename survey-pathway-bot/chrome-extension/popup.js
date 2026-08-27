// Popup: start/stop a run and download the results. All orchestration lives in
// background.js, so closing the popup does not interrupt anything.

const $ = (id) => document.getElementById(id);
const send = (msg) => new Promise((resolve) => chrome.runtime.sendMessage(msg, resolve));

const PREFS = 'spb-prefs';

async function loadPrefs() {
  const p = (await chrome.storage.local.get(PREFS))[PREFS] || {};
  if (p.url) $('url').value = p.url;
  if (p.maxRuns) $('maxRuns').value = p.maxRuns;
  if (p.delay != null) $('delay').value = p.delay;
  if (p.config) $('config').value = p.config;
  $('clearCookies').checked = !!p.clearCookies;
}

const savePrefs = () =>
  chrome.storage.local.set({
    [PREFS]: {
      url: $('url').value.trim(),
      maxRuns: $('maxRuns').value,
      delay: $('delay').value,
      config: $('config').value,
      clearCookies: $('clearCookies').checked,
    },
  });

function download(name, text, mime) {
  const url = URL.createObjectURL(new Blob([text], { type: mime }));
  const a = document.createElement('a');
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 5000);
}

async function refresh() {
  const s = await send({ type: 'status' });
  if (!s) return;
  $('status').textContent =
    `${s.running ? '● running' : '○ idle'}\n${s.status || ''}\n` +
    `${s.runs} traversal(s) recorded · ${s.queued} branch(es) queued`;
}

$('start').onclick = async () => {
  const url = $('url').value.trim();
  if (!url) return ($('status').textContent = 'Enter a survey URL first.');
  let config = {};
  const raw = $('config').value.trim();
  if (raw) {
    try {
      config = JSON.parse(raw);
    } catch (e) {
      return ($('status').textContent = `Config is not valid JSON: ${e.message}`);
    }
  }
  config.delay = Number($('delay').value || 0);
  await savePrefs();
  await send({ type: 'start', startUrl: url, config, maxRuns: Number($('maxRuns').value || 20), clearCookies: $('clearCookies').checked });
  refresh();
};

$('stop').onclick = async () => {
  await send({ type: 'stop' });
  refresh();
};

$('report').onclick = async () => {
  const s = await send({ type: 'status', withTraces: true });
  const traces = s?.traces || [];
  if (!traces.length) return ($('status').textContent = 'No runs recorded yet.');
  const md = SPB_REPORT.buildReport(traces, {
    url: s.startUrl,
    generatedAt: new Date().toISOString(),
    plansQueuedButNotRun: s.queued,
  });
  download('survey-pathway-REPORT.md', md, 'text/markdown');
};

$('traces').onclick = async () => {
  const s = await send({ type: 'status', withTraces: true });
  const traces = s?.traces || [];
  if (!traces.length) return ($('status').textContent = 'No runs recorded yet.');
  download(
    'spb-traces.json',
    JSON.stringify({ summary: { url: s.startUrl, generatedAt: new Date().toISOString(), plansQueuedButNotRun: s.queued }, traces }, null, 2),
    'application/json'
  );
};

loadPrefs();
refresh();
setInterval(refresh, 900);
