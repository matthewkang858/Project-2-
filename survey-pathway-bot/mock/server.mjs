// A small branching survey that mimics the DOM a hosted survey engine emits
// (Decipher/Forsta-style: div.question wrappers, label[for], a `continue`
// submit button, one form POST per page).
//
//   node mock/server.mjs [port]        # default 8099
//
// It exists so you can develop and smoke-test the bot without pointing it at a
// live survey. Its logic on purpose contains the things pathway testing is
// meant to catch: a screen-out, a quota, a conditionally-shown page, and a
// question that some routes never reach.

import { createServer } from 'node:http';

const PORT = Number(process.argv[2] ?? 8099);
const enc = (o) => Buffer.from(JSON.stringify(o)).toString('base64url');
const dec = (s) => { try { return JSON.parse(Buffer.from(s ?? '', 'base64url').toString()); } catch { return {}; } };

const page = (body, state, pageNo) => `<!doctype html><html><head><title>Pathway Mock Survey</title>
<style>body{font-family:system-ui;margin:40px auto;max-width:720px}.question{margin:24px 0}
.qtitle{font-weight:600;margin-bottom:8px}label{display:block;margin:4px 0}</style></head><body>
<form method="POST" action="/">
<input type="hidden" name="state" value="${enc(state)}">
<input type="hidden" name="page" value="${pageNo}">
${body}
<p><input type="submit" name="continue" id="continue" value="Next"></p>
</form></body></html>`;

const end = (heading, text) => `<!doctype html><html><head><title>${heading}</title></head><body>
<h1>${heading}</h1><p>${text}</p></body></html>`;

const radio = (name, title, opts) => `<div class="question" id="${name}"><div class="qtitle">${title}</div>` +
  opts.map((o, i) => `<label for="${name}_${i + 1}"><input type="radio" name="${name}" id="${name}_${i + 1}" value="${i + 1}"> ${o}</label>`).join('') +
  '</div>';

const checkbox = (name, title, opts) => `<div class="question" id="${name}"><div class="qtitle">${title}</div>` +
  opts.map((o, i) => `<label for="${name}r${i + 1}"><input type="checkbox" name="${name}r${i + 1}" id="${name}r${i + 1}" value="1"> ${o}</label>`).join('') +
  '</div>';

const dropdown = (name, title, opts) => `<div class="question" id="${name}"><div class="qtitle">${title}</div>` +
  `<select name="${name}" id="${name}"><option value="">Select...</option>` +
  opts.map((o, i) => `<option value="${i + 1}">${o}</option>`).join('') + '</select></div>';

const grid = (name, title, rows, scale) => `<div class="question" id="${name}"><div class="qtitle">${title}</div><table>` +
  rows.map((r, ri) => `<tr><th>${r}</th>` + scale.map((s, si) =>
    `<td><label for="${name}r${ri + 1}c${si + 1}"><input type="radio" name="${name}r${ri + 1}" id="${name}r${ri + 1}c${si + 1}" value="${si + 1}"> ${s}</label></td>`).join('') + '</tr>').join('') +
  '</table></div>';

function render(pageNo, st) {
  switch (pageNo) {
    case 1:
      return page(
        radio('S1', 'Which <b>age group</b> are you <u>in</u>?', ['Under 18', '18–34', '35–54', '55 or older']),
        st, 1
      );
    case 2:
      return page(
        radio('S2', 'What is your gender?', ['Male', 'Female', 'Prefer not to say']) +
          dropdown('S3', 'Which state do you live in?', ['California', 'New York', 'Texas']),
        st, 2
      );
    case 3:
      return page(checkbox('Q1', 'Which of these brands have you bought in the last 6 months?', ['Alpha', 'Beta', 'Gamma']), st, 3);
    case 4:
      return page(grid('Q2', 'How would you rate Alpha on each of these?', ['Value for money', 'Quality'], ['Poor', 'OK', 'Good']), st, 4);
    case 5:
      return page(`<div class="question" id="Q3"><div class="qtitle">Anything else you would like to tell us?</div>
        <textarea name="Q3" id="Q3_t" rows="4" cols="50"></textarea></div>`, st, 5);
    default:
      return end('Thank you for completing this survey', 'Your responses have been recorded.');
  }
}

// Routing logic — the branching the bot is supposed to discover.
function nextPage(submitted, st) {
  switch (submitted) {
    case 1:
      if (st.S1 === '1') return 'TERMINATE';          // under 18 screens out
      return 2;
    case 2:
      if (st.S3 === '1' && st.S1 === '4') return 'QUOTA'; // California 55+ is full
      return 3;
    case 3:
      return st.Q1r1 === '1' ? 4 : 5;                 // Alpha buyers get the grid
    case 4:
      return 5;
    case 5:
      return 'COMPLETE';
    default:
      return 'COMPLETE';
  }
}

createServer((req, res) => {
  if (req.method === 'GET') {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    res.end(render(1, {}));
    return;
  }
  let body = '';
  req.on('data', (c) => (body += c));
  req.on('end', () => {
    const form = new URLSearchParams(body);
    const st = { ...dec(form.get('state')) };
    for (const [k, v] of form) if (!['state', 'page', 'continue'].includes(k)) st[k] = v;
    const submitted = Number(form.get('page') ?? 1);
    const next = nextPage(submitted, st);
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    if (next === 'TERMINATE') res.end(end("We're sorry", 'Based on your answers you do not qualify for this survey.'));
    else if (next === 'QUOTA') res.end(end('Quota full', 'We have enough responses from your group. Thank you for your interest.'));
    else if (next === 'COMPLETE') res.end(end('Thank you for completing this survey', 'Your responses have been recorded.'));
    else res.end(render(next, st));
  });
}).listen(PORT, () => console.log(`mock survey on http://127.0.0.1:${PORT}/`));
