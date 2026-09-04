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
    case 0:
      return 1;  // welcome page
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
  // A stand-in for the login/interstitial wall a real survey host puts in front
  // of a test link: a page with no questions and no forward button.
  if (req.url && req.url.startsWith('/wall')) {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    res.end(`<!doctype html><html><head><title>Survey</title></head><body>
      <h1>Please login to see additional testing options</h1>
      <p>You must be signed in to view this survey.</p></body></html>`);
    return;
  }
  // The welcome page real survey players show first: no questions, and a
  // forward control that matches none of the classic selectors — a plain
  // <button> whose only clue is the word "Continue".
  if (req.url && req.url.startsWith('/intro')) {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    res.end(`<!doctype html><html><head><title>Survey</title></head><body>
      <div class="banner">Please login to see additional testing features</div>
      <form method="POST" action="/">
        <input type="hidden" name="state" value="${enc({})}">
        <input type="hidden" name="page" value="0">
        <p>Click "Continue" to begin.</p>
        <button class="btn-continue" onclick="this.form.submit()">Continue</button>
      </form></body></html>`);
    return;
  }
  // The same survey embedded in a host page, as players that frame the
  // questionnaire do.
  if (req.url && req.url.startsWith('/framed')) {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    res.end(`<!doctype html><html><head><title>Survey host</title></head><body>
      <h1>Survey</h1>
      <iframe id="surveyFrame" src="/intro" style="width:900px;height:700px;border:0"></iframe>
      </body></html>`);
    return;
  }
  // Two widget shapes that a plain form-control reader cannot answer: a native
  // range slider plus a custom keyboard/pointer-driven one, and a carousel that
  // reveals its questions one at a time without a page load.
  if (req.url && req.url.startsWith('/slider')) {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    res.end(`<!doctype html><html><head><title>Survey</title></head><body>
      <form method="POST" action="/">
        <input type="hidden" name="state" value="${enc({ S1: '2', S2: '1', S3: '1' })}">
        <input type="hidden" name="page" value="4">
        <div class="question" id="SL1"><div class="qtitle">What share of revenue goes to technology?</div>
          <input type="range" name="SL1" id="SL1_r" min="0" max="100" step="5" value="0">
        </div>
        <div class="question" id="SL2"><div class="qtitle">How impactful has AI been?</div>
          <div id="SL2_s" role="slider" tabindex="0" aria-valuemin="0" aria-valuemax="10" aria-valuenow="0"
               style="width:300px;height:24px;background:#eee">handle</div>
          <input type="hidden" name="SL2" id="SL2_v" value="">
        </div>
        <p><input type="submit" name="continue" id="continue" value="Next"></p>
      </form>
      <script>
        var s = document.getElementById('SL2_s'), v = document.getElementById('SL2_v');
        function set(n) { n = Math.max(0, Math.min(10, n)); s.setAttribute('aria-valuenow', n); v.value = String(n); }
        s.addEventListener('keydown', function (e) {
          var now = Number(s.getAttribute('aria-valuenow'));
          if (e.key === 'ArrowRight' || e.key === 'ArrowUp') set(now + 1);
          if (e.key === 'ArrowLeft' || e.key === 'ArrowDown') set(now - 1);
          if (e.key === 'End') set(10);
        });
        s.addEventListener('mouseup', function (e) {
          var r = s.getBoundingClientRect();
          set(Math.round(((e.clientX - r.left) / r.width) * 10));
        });
      </script>
      </body></html>`);
    return;
  }
  if (req.url && req.url.startsWith('/carousel')) {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    res.end(`<!doctype html><html><head><title>Survey</title></head><body>
      <form method="POST" action="/">
        <input type="hidden" name="state" value="${enc({ S1: '2', S2: '1', S3: '1' })}">
        <input type="hidden" name="page" value="4">
        <div class="card" data-card="0">${radio('C1', 'Card one: how satisfied are you?', ['Low', 'Medium', 'High'])}</div>
        <div class="card" data-card="1" style="display:none">${radio('C2', 'Card two: how likely to renew?', ['Low', 'Medium', 'High'])}</div>
        <div class="card" data-card="2" style="display:none">${radio('C3', 'Card three: how likely to recommend?', ['Low', 'Medium', 'High'])}</div>
        <p id="submitWrap" style="display:none"><input type="submit" name="continue" id="continue" value="Next"></p>
      </form>
      <script>
        var shown = 0;
        document.addEventListener('change', function () {
          var cards = document.querySelectorAll('.card');
          if (shown < cards.length - 1) { shown++; cards[shown].style.display = ''; }
          else { document.getElementById('submitWrap').style.display = ''; }
        });
      </script>
      </body></html>`);
    return;
  }
  // How modern survey players render answers: the real <input> is hidden and a
  // styled label stands in for it, and the question body arrives a moment after
  // the page does.
  if (req.url && req.url.startsWith('/styled')) {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    res.end(`<!doctype html><html><head><title>Survey</title>
      <style>.choice input{position:absolute;opacity:0;width:1px;height:1px}
             .choice{display:block;padding:8px;border:1px solid #ccc;margin:4px 0;cursor:pointer}</style>
      </head><body>
      <form method="POST" action="/">
        <input type="hidden" name="state" value="${enc({ S1: '2', S2: '1', S3: '1' })}">
        <input type="hidden" name="page" value="4">
        <div id="host"><p>Loading…</p></div>
        <p><button class="btn-continue" onclick="this.form.submit()">Continue</button></p>
      </form>
      <script>
        setTimeout(function () {
          document.getElementById('host').innerHTML =
            '<div class="question" id="ST1"><div class="qtitle">How satisfied are you overall?</div>' +
            ['Very satisfied', 'Satisfied', 'Neutral', 'Dissatisfied'].map(function (t, i) {
              return '<label class="choice" for="ST1_' + (i + 1) + '">' +
                     '<input type="radio" name="ST1" id="ST1_' + (i + 1) + '" value="' + (i + 1) + '"> ' + t + '</label>';
            }).join('') + '</div>';
        }, 900);
      </script>
      </body></html>`);
    return;
  }
  // "Please select up to two" — each checkbox carries its own name, and the
  // server rejects more than two, exactly as Decipher does.
  // A button-driven card carousel: one card at a time, three shared answer
  // buttons that are plain divs (no form controls anywhere visible), a pager,
  // and Continue only after every card is answered.
  if (req.url && req.url.split('?')[0] === '/cards') {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    const rows = ['IT (e.g., CIO, members of the technology team)', 'Executive Management (e.g., CEO)', 'Finance (e.g., CFO)'];
    res.end(`<!doctype html><html><head><title>Survey</title>
      <style>.abtn{display:inline-block;padding:14px;border:1px solid #ccc;border-radius:8px;margin:6px;cursor:pointer}
             .abtn.sel{background:#dde}.cardface{padding:30px;border:1px solid #ddd;border-radius:8px;width:300px;margin:10px auto;text-align:center}</style>
      </head><body>
      <form method="POST" action="/cardscheck">
        <div class="qtitle">Which of the following best describes the role that is typically played by the following departments/members of your company?</div>
        <div class="cardface" id="face"></div>
        <div class="pager"><button type="button" id="prev" aria-label="Previous">&lsaquo;</button>
          <span id="pos"></span>
          <button type="button" id="nextCard" aria-label="Next">&rsaquo;</button></div>
        <div id="answers">
          <div class="abtn" data-a="1">Key decision-maker</div>
          <div class="abtn" data-a="2">Influencer</div>
          <div class="abtn" data-a="3">No role in the process</div>
        </div>
        ${rows.map((_, i) => `<input type="hidden" name="ans32900.0.${i}" id="h${i}" value="">`).join('')}
        <p id="submitWrap" style="display:none"><button class="btn-continue" onclick="this.form.submit()">Continue</button></p>
      </form>
      <script>
        var rows = ${JSON.stringify(rows)};
        var at = 0;
        function paint() {
          document.getElementById('face').textContent = rows[at];
          document.getElementById('pos').textContent = (at + 1) + ' / ' + rows.length;
          var val = document.getElementById('h' + at).value;
          [].forEach.call(document.querySelectorAll('.abtn'), function (b) {
            b.className = 'abtn' + (b.getAttribute('data-a') === val ? ' sel' : '');
          });
          var done = rows.every(function (_, i) { return document.getElementById('h' + i).value; });
          document.getElementById('submitWrap').style.display = done ? '' : 'none';
        }
        [].forEach.call(document.querySelectorAll('.abtn'), function (b) {
          b.addEventListener('click', function () {
            document.getElementById('h' + at).value = b.getAttribute('data-a');
            if (at < rows.length - 1) at++;
            paint();
          });
        });
        document.getElementById('nextCard').addEventListener('click', function () { if (at < rows.length - 1) { at++; paint(); } });
        document.getElementById('prev').addEventListener('click', function () { if (at > 0) { at--; paint(); } });
        paint();
      </script>
      </body></html>`);
    return;
  }
  // The same card carousel built the hostile way: the "1 / 8" readout and the
  // card title are nested spans (no single leaf element carries the text), the
  // arrows are icon buttons whose only text is an entity, and the answer
  // buttons wrap their labels in inner spans.
  if (req.url && req.url.split('?')[0] === '/cards2') {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    const rows = ['IT (e.g., CIO, members of the technology team)', 'Executive Management (e.g., CEO)', 'Finance (e.g., CFO)'];
    res.end(`<!doctype html><html><head><title>Survey</title>
      <style>.abtn{display:inline-block;padding:14px;border:1px solid #ccc;border-radius:8px;margin:6px;cursor:pointer}
             .abtn.sel{background:#dde}.cardface{padding:30px;border:1px solid #ddd;width:300px;margin:10px auto;text-align:center}</style>
      </head><body>
      <form method="POST" action="/cardscheck">
        <div class="qtitle">Which of the following best describes the role that is typically played by the following departments/members of your company?</div>
        <div class="cardface"><span class="cf-inner"><span id="face"></span></span></div>
        <div class="pager">
          <button type="button" id="prev" aria-label="Previous slide"><span>&lsaquo;</span></button>
          <span class="pos"><span id="posA"></span><span class="sep"> / </span><span id="posB"></span></span>
          <button type="button" id="nextCard" aria-label="Next slide"><span>&rsaquo;</span></button>
        </div>
        <div id="answers">
          <div class="abtn" data-a="1"><span><span>Key decision-maker</span></span></div>
          <div class="abtn" data-a="2"><span><span>Influencer</span></span></div>
          <div class="abtn" data-a="3"><span><span>No role in the process</span></span></div>
        </div>
        ${rows.map((_, i) => `<input type="hidden" name="ans32900.0.${i}" id="h${i}" value="">`).join('')}
        <p id="submitWrap" style="display:none"><button class="btn-continue" onclick="this.form.submit()">Continue</button></p>
      </form>
      <script>
        var rows = ${JSON.stringify(rows)};
        var at = 0;
        function paint() {
          document.getElementById('face').textContent = rows[at];
          document.getElementById('posA').textContent = at + 1;
          document.getElementById('posB').textContent = rows.length;
          var val = document.getElementById('h' + at).value;
          [].forEach.call(document.querySelectorAll('.abtn'), function (b) {
            b.className = 'abtn' + (b.getAttribute('data-a') === val ? ' sel' : '');
          });
          var done = rows.every(function (_, i) { return document.getElementById('h' + i).value; });
          document.getElementById('submitWrap').style.display = done ? '' : 'none';
        }
        [].forEach.call(document.querySelectorAll('.abtn'), function (b) {
          b.addEventListener('click', function () {
            document.getElementById('h' + at).value = b.getAttribute('data-a');
            if (at < rows.length - 1) at++;
            paint();
          });
        });
        document.getElementById('nextCard').addEventListener('click', function () { if (at < rows.length - 1) { at++; paint(); } });
        document.getElementById('prev').addEventListener('click', function () { if (at > 0) { at--; paint(); } });
        paint();
      </script>
      </body></html>`);
    return;
  }
  if (req.url && req.url.split('?')[0] === '/cards3') {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    const rows = ['Legal (e.g., general counsel, outside law firm)', 'Executive Management (e.g., CEO)', 'End Users (i.e., employees who will be using the software)'];
    res.end(`<!doctype html><html><head><title>Survey</title>
      <style>.abtn{display:inline-block;padding:14px;border:1px solid #ccc;border-radius:8px;margin:6px;cursor:pointer}
             .abtn.sel{background:#dde}
             .track{display:flex;overflow:hidden;width:420px;margin:10px auto}
             .face{min-width:300px;padding:30px;border:1px solid #ddd;margin-right:12px}
             .navbtn{border:none;background:none;width:28px;height:28px}
             .navbtn svg{width:16px;height:16px}
             input[type=radio]{display:none}</style>
      </head><body>
      <form method="POST" action="/cardscheck">
        <div class="qtitle">Which of the following best describes the role that is typically played by the following departments/members of your company?</div>
        <div class="track" id="track"></div>
        <div class="pager" style="display:flex;align-items:center;justify-content:center;gap:8px">
          <button type="button" class="navbtn car-left" id="prev"><svg viewBox="0 0 10 10"><path d="M7 1 3 5l4 4"/></svg></button>
          <span class="pos"><span id="posA"></span><span> / </span><span id="posB"></span></span>
          <button type="button" class="navbtn car-right" id="nextCard"><svg viewBox="0 0 10 10"><path d="M3 1l4 4-4 4"/></svg></button>
        </div>
        <div id="answers">
          <div class="abtn" data-a="1">Key decision-maker</div>
          <div class="abtn" data-a="2">Influencer</div>
          <div class="abtn" data-a="3">No role in the process</div>
        </div>
        ${rows.map((_, i) => [1,2,3].map((v) =>
          `<input type="radio" name="ans32900.0.${i}" value="${v}">`).join('')).join('')}
        ${rows.map((_, i) => `<input type="hidden" name="h${i}" id="h${i}" value="">`).join('')}
        <p id="submitWrap" style="display:none"><button class="btn-continue" onclick="this.form.submit()">Continue</button></p>
      </form>
      <script>
        var rows = ${JSON.stringify(rows)};
        var at = 0;
        function paint() {
          // current card plus a peek of the next one, like the real player
          var track = document.getElementById('track');
          track.innerHTML = rows.slice(at, at + 2).map(function (t, i) {
            return '<div class="face' + (i ? ' peek' : '') + '">' + t + '</div>';
          }).join('');
          document.getElementById('posA').textContent = at + 1;
          document.getElementById('posB').textContent = rows.length;
          var val = document.getElementById('h' + at).value;
          [].forEach.call(document.querySelectorAll('.abtn'), function (b) {
            b.className = 'abtn' + (b.getAttribute('data-a') === val ? ' sel' : '');
          });
          var done = rows.every(function (_, i) { return document.getElementById('h' + i).value; });
          document.getElementById('submitWrap').style.display = done ? '' : 'none';
        }
        [].forEach.call(document.querySelectorAll('.abtn'), function (b) {
          b.addEventListener('click', function () {
            var v = b.getAttribute('data-a');
            document.getElementById('h' + at).value = v;
            var radios = document.querySelectorAll('input[name="ans32900.0.' + at + '"]');
            [].forEach.call(radios, function (r) { r.checked = r.value === v; });
            if (at < rows.length - 1) at++;
            paint();
          });
        });
        document.getElementById('nextCard').addEventListener('click', function () { if (at < rows.length - 1) { at++; paint(); } });
        document.getElementById('prev').addEventListener('click', function () { if (at > 0) { at--; paint(); } });
        paint();
      </script>
      </body></html>`);
    return;
  }
  // The field's exact carousel per the second debug dump: each answer is a
  // five-deep tower of divs, every level pointer-cursored, the click handler
  // on a MIDDLE level (mx-card), the shared row's own text under 60 chars,
  // swiper-style arrows (role=button, aria-label, no text), three card faces
  // in the DOM at once, and hidden radios as state.
  if (req.url && req.url.split('?')[0] === '/cards4') {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    const rows = ['Finance (e.g., CFO, financial planning & analysis team)', 'Executive Management (e.g., CEO)', 'IT (e.g., CIO, members of the technology team)'];
    res.end(`<!doctype html><html><head><title>Survey</title>
      <style>.content-container{cursor:pointer;display:flex;justify-content:center}
             .box{margin:6px}.middle{padding:2px}.mx-card{border:1px solid #ccc;border-radius:8px;padding:12px}
             .mx-card.sel{background:#dde}.mx-carouselapp-scale{font-size:14px}
             .faces{display:flex;overflow:hidden;width:520px;margin:10px auto}
             .face{min-width:240px;padding:24px;border:1px solid #eee;margin-right:8px}
             .swiper-button-prev,.swiper-button-next{width:28px;height:28px;background:#eee;border-radius:50%}
             .cell{display:inline-block}
             .face{cursor:pointer}
             input[type=radio]{display:none}</style>
      </head><body>
      <form method="POST" action="/cardscheck">
        <div class="qtitle">Which of the following best describes the role that is typically played by the following departments/members of your company when evaluating and selecting software or technology?</div>
        <div class="faces" id="faces"></div>
        <div class="pager" style="display:flex;align-items:center;justify-content:center;gap:10px">
          <div class="swiper-button-prev swiper-button-disable" role="button" aria-label="Previous slide"></div>
          <span class="pos"><span id="posA"></span> / <span id="posB"></span></span>
          <div class="swiper-button-next swiper-button-disable" role="button" aria-label="Next slide"></div>
        </div>
        <div class="content-container">
          ${['Key decision-maker', 'Influencer', 'No role in the process', 'Chief AI Officer (CAIO)', 'Chief Technology Officer (CTO)', 'Chief Information Officer (CIO)', 'Chief Operating Officer (COO)', 'Chief Financial Officer (CFO)', 'Other'].map((t, i) =>
            `<div class="cell"><div class="box">${rows.map((_, r) => `<input type="radio" name="ans32900.0.${r}" value="${i + 1}">`).join('')}<div class="middle"><div class="mx-card" data-a="${i + 1}"><div class="mx-carouselapp-scale">${t}</div></div></div></div></div>`
          ).join('')}
        </div>
        ${rows.map((_, i) => `<input type="hidden" name="h${i}" id="h${i}" value="">`).join('')}
        <p id="submitWrap" style="display:none"><button class="btn-continue" onclick="this.form.submit()">Continue</button></p>
      </form>
      <script>
        var rows = ${JSON.stringify(rows)};
        var at = 0;
        function paint() {
          document.getElementById('faces').innerHTML = rows
            .slice(Math.max(0, at - 1), at + 2)
            .map(function (t) { return '<div class="face">' + t.slice(0, 40) + '</div>'; })
            .join('');
          document.getElementById('posA').textContent = at + 1;
          document.getElementById('posB').textContent = rows.length;
          var val = document.getElementById('h' + at).value;
          [].forEach.call(document.querySelectorAll('.mx-card'), function (b) {
            b.className = 'mx-card' + (b.getAttribute('data-a') === val ? ' sel' : '');
          });
          var done = rows.every(function (_, i) { return document.getElementById('h' + i).value; });
          document.getElementById('submitWrap').style.display = done ? '' : 'none';
        }
        // Handler on the MIDDLE level only — a click dispatched on an outer
        // level never reaches it, exactly like the real player.
        [].forEach.call(document.querySelectorAll('.mx-card'), function (b) {
          b.addEventListener('click', function () {
            var v = b.getAttribute('data-a');
            document.getElementById('h' + at).value = v;
            [].forEach.call(document.querySelectorAll('input[name="ans32900.0.' + at + '"]'), function (r) { r.checked = r.value === v; });
            if (at < rows.length - 1) at++;
            paint();
          });
        });
        paint();
      </script>
      </body></html>`);
    return;
  }
  if (req.url && req.url.split('?')[0] === '/cards5') {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    const opts = [
      'Remain As-Is: Keep our current provider and not adopt significant new AI capabilities',
      'Upgrade with Current Provider: Adopt the AI capabilities our current provider offers',
      'Supplement with Point Solutions: Keep the provider but add standalone AI tools alongside',
      'Switch to an AI-Native Provider: Replace the current provider with an AI-native alternative',
      'Replace with In-House Build: Build our own AI-enabled replacement internally',
      'I am not sure',
    ];
    res.end(`<!doctype html><html><head><title>Survey</title>
      <style>.abtn{display:block;padding:12px;border:1px solid #ccc;border-radius:8px;margin:6px;cursor:pointer;max-width:520px}
             .abtn.sel{background:#dde}input[type=radio]{display:none}</style>
      </head><body>
      <form method="POST" action="/cards5check">
        <div class="qtitle">Over the next three years, what is most likely to be your company's approach to AI capability adoption for each of the following types of software?</div>
        <div class="face">Human Resources Management / Human Capital Management Software (i.e., HRM/HCM)</div>
        <div class="pager" style="display:flex;align-items:center;gap:8px;justify-content:center">
          <div class="swiper-button-prev swiper-button-disable" role="button" aria-label="Previous slide"></div>
          <span>1 / 1</span>
          <div class="swiper-button-next swiper-button-disable" role="button" aria-label="Next slide"></div>
        </div>
        ${opts.map((t, i) => `<div class="abtn" data-a="${i + 1}"><input type="radio" name="ans33053.0.2" value="${i + 1}">${t}</div>`).join('')}
        <input type="hidden" name="h0" id="h0" value="">
        <p id="submitWrap" style="display:none"><button class="btn-continue" onclick="this.form.submit()">Continue</button></p>
      </form>
      <script>
        [].forEach.call(document.querySelectorAll('.abtn'), function (b) {
          b.addEventListener('click', function () {
            document.getElementById('h0').value = b.getAttribute('data-a');
            [].forEach.call(document.querySelectorAll('.abtn'), function (x) { x.className = 'abtn' + (x === b ? ' sel' : ''); });
            document.getElementById('submitWrap').style.display = '';
          });
        });
      </script>
      </body></html>`);
    return;
  }
  // Five consecutive pages with IDENTICAL card keys — the shape of Q27–Q30,
  // which must not be mistaken for a loop.
  if (req.url && req.url.split('?')[0] === '/repeat') {
    const step = Number((req.url.match(/step=(\d+)/) || [, 1])[1]);
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    res.end(`<!doctype html><html><head><title>Survey</title>
      <style>.abtn{display:inline-block;padding:12px;border:1px solid #ccc;margin:6px;cursor:pointer}.abtn.sel{background:#dde}</style>
      </head><body>
      <form method="POST" action="/repeatcheck?step=${step}">
        <div class="qtitle">To what extent would you face challenge ${step} for each software area?</div>
        <div class="face">Verticalized Software and Applications (i.e., specialized tools)</div>
        <div class="pager" style="display:flex;align-items:center;gap:8px;justify-content:center">
          <button type="button" id="prev" aria-label="Previous slide">&lsaquo;</button>
          <span id="pos">1 / 2</span>
          <button type="button" id="nextCard" aria-label="Next slide">&rsaquo;</button>
        </div>
        <div id="answers">
          <div class="abtn" data-a="1">Major challenge</div>
          <div class="abtn" data-a="2">Minor challenge</div>
          <div class="abtn" data-a="3">No challenge</div>
        </div>
        <input type="hidden" name="h0" id="h0" value=""><input type="hidden" name="h1" id="h1" value="">
        <p id="submitWrap" style="display:none"><button class="btn-continue" onclick="this.form.submit()">Continue</button></p>
      </form>
      <script>
        var faces = ['Verticalized Software and Applications (i.e., specialized tools)', 'Data Storage and Infrastructure'];
        var at = 0;
        function paint() {
          document.querySelector('.face').textContent = faces[at];
          document.getElementById('pos').textContent = (at + 1) + ' / 2';
          var done = ['h0', 'h1'].every(function (id) { return document.getElementById(id).value; });
          document.getElementById('submitWrap').style.display = done ? '' : 'none';
        }
        [].forEach.call(document.querySelectorAll('.abtn'), function (b) {
          b.addEventListener('click', function () {
            document.getElementById('h' + at).value = b.getAttribute('data-a');
            if (at < 1) at++;
            paint();
          });
        });
        document.getElementById('nextCard').addEventListener('click', function () { if (at < 1) { at++; paint(); } });
        document.getElementById('prev').addEventListener('click', function () { if (at > 0) { at--; paint(); } });
        paint();
      </script>
      </body></html>`);
    return;
  }
  if (req.url && req.url.split('?')[0] === '/offscreen') {
    const nonce = Math.floor(Math.random() * 900000 + 100000);
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    res.end(`<!doctype html><html><head><title>Survey</title>
      <style>.answer{display:block;padding:12px;border:1px solid #ccd;margin:6px;background:#eef}
             .answer input{position:absolute;left:-9999px}</style>
      </head><body>
      <form method="POST" action="/offscreencheck">
        <div class="question" id="ans32477"><div class="qtitle">Approximately how many full-time employees work for your current company?</div>
        ${['1-50 employees', '51-100 employees', '101-200 employees', '201-300 employees']
          .map((t, i) => `<label class="answer" for="a${i}"><input type="radio" name="ans32477.0.0" id="a${i}" value="${i + 1}"> ${t}</label>`)
          .join('')}
        </div>
        <input type="text" name="ra__${nonce}" style="position:absolute;left:-9999px" value="">
        <p><button class="btn-continue" onclick="this.form.submit()">Continue</button></p>
      </form></body></html>`);
    return;
  }
  if (req.url && req.url.split('?')[0] === '/dotted') {
    const nonce = Math.floor(Math.random() * 900000 + 100000);
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    res.end(`<!doctype html><html><head><title>Survey</title></head><body>
      <form method="POST" action="/dottedcheck">
        <div class="question" id="ans32645"><div class="qtitle">What are the top two reasons you expect spend to increase?<br>Please select up to two.</div>
        ${['Upgrading legacy systems', 'Adoption of AI', 'Business intelligence', 'Revenue growth', 'Cybersecurity']
          .map((t, i) => `<label class="choice" for="ans32645.0.${i}"><input type="checkbox" name="ans32645.0.${i}" id="ans32645.0.${i}" value="1"> ${t}</label>`)
          .join('')}
        <label class="choice" for="ans32645.0.9"><input type="checkbox" name="ans32645.0.9" id="ans32645.0.9" value="1"> Other (please specify)
          <input type="text" name="oe32645.0" id="oe32645.0" value=""></label>
        </div>
        <input type="text" name="ra__${nonce}" style="position:absolute;left:-9999px" value="">
        <p><button class="btn-continue" onclick="this.form.submit()">Continue</button></p>
      </form></body></html>`);
    return;
  }
  if (req.url && req.url.split('?')[0] === '/limit') {
    const checked = Number((req.url.match(/checked=(\d+)/) || [, 0])[1]);
    const err = checked > 2 ? `<p class="error">Please check at most 2 boxes in this column (you checked ${checked}).</p>` : '';
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    res.end(`<!doctype html><html><head><title>Survey</title></head><body>
      <form method="POST" action="/limitcheck">
        <div class="question" id="LM1"><div class="qtitle">What are the top two reasons you expect spend to increase?<br>Please select up to two.</div>
        ${err}
        ${['Upgrading legacy systems', 'Adoption of AI', 'Business intelligence', 'Revenue growth', 'Cybersecurity']
          .map((t, i) => `<label class="choice" for="LM1r${i + 1}"><input type="checkbox" name="LM1r${i + 1}" id="LM1r${i + 1}" value="1"> ${t}</label>`)
          .join('')}
        </div>
        <p><button class="btn-continue" onclick="this.form.submit()">Continue</button></p>
      </form></body></html>`);
    return;
  }
  // Percentages that must total exactly 100.
  if (req.url && req.url.split('?')[0] === '/sum100') {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    res.end(`<!doctype html><html><head><title>Survey</title></head><body>
      <form method="POST" action="/sumcheck">
        <div class="question" id="SM1"><div class="qtitle">Split your incremental spend across the following categories.</div>
        <table>
          <tr><td>Direct AI Spend</td><td><input type="number" name="SM1r1" id="SM1r1" value=""> %</td></tr>
          <tr><td>AI Enablement Spend</td><td><input type="number" name="SM1r2" id="SM1r2" value=""> %</td></tr>
          <tr><td>Non-AI Spend</td><td><input type="number" name="SM1r3" id="SM1r3" value=""> %</td></tr>
        </table></div>
        <p><button class="btn-continue" onclick="this.form.submit()">Continue</button></p>
      </form></body></html>`);
    return;
  }
  // A carousel grid: one row per card, its own pager, Continue only once every
  // card is answered.
  if (req.url && req.url.startsWith('/pager')) {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    const rows = ['Executive Management', 'IT', 'Finance'];
    res.end(`<!doctype html><html><head><title>Survey</title>
      <style>.choice input{position:absolute;opacity:0}.card{display:none}.card.on{display:block}</style>
      </head><body>
      <form method="POST" action="/">
        <input type="hidden" name="state" value="${enc({ S1: '2', S2: '1', S3: '1' })}">
        <input type="hidden" name="page" value="4">
        <div class="question" id="PG1"><div class="qtitle">Which role is played by each department?</div>
          ${rows.map((r, i) => `<div class="card ${i === 0 ? 'on' : ''}" data-i="${i}"><p class="rowlabel">${r}</p>
            ${['Key decision-maker', 'Influencer', 'No role'].map((t, j) =>
              `<label class="choice" for="PG1r${i + 1}_${j + 1}"><input type="checkbox" name="PG1r${i + 1}" id="PG1r${i + 1}_${j + 1}" value="${j + 1}"> ${t}</label>`).join('')}
            </div>`).join('')}
          <div class="pager"><button type="button" id="prev" aria-label="Previous">&lsaquo;</button>
            <span id="pos">1 / ${rows.length}</span>
            <button type="button" id="nextCard" aria-label="Next">&rsaquo;</button></div>
        </div>
        <p id="submitWrap" style="display:none"><button class="btn-continue" onclick="this.form.submit()">Continue</button></p>
      </form>
      <script>
        var at = 0, cards = document.querySelectorAll('.card');
        function show(n) {
          at = Math.max(0, Math.min(cards.length - 1, n));
          cards.forEach(function (c, i) { c.className = 'card' + (i === at ? ' on' : ''); });
          document.getElementById('pos').textContent = (at + 1) + ' / ' + cards.length;
          var done = [].every.call(cards, function (c) { return c.querySelector('input:checked'); });
          document.getElementById('submitWrap').style.display = done ? '' : 'none';
        }
        document.getElementById('nextCard').addEventListener('click', function () { show(at + 1); });
        document.getElementById('prev').addEventListener('click', function () { show(at - 1); });
        document.addEventListener('change', function () { show(at); });
      </script>
      </body></html>`);
    return;
  }
  // A player that re-renders its answer list after the page settles (so any
  // selector captured a moment earlier is stale), and whose click handler sits
  // on the wrapper div rather than a <label>.
  if (req.url && req.url.split('?')[0] === '/rerender') {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    res.end(`<!doctype html><html><head><title>Survey</title>
      <style>.ans input{position:absolute;opacity:0}.ans{display:block;padding:10px;border:1px solid #ccc;margin:4px}</style>
      </head><body>
      <form method="POST" action="/rerendercheck">
        <div class="question" id="RR1"><div class="qtitle">Approximately how many full-time employees work for your company?</div>
          <div id="answers"></div></div>
        <p><button class="btn-continue" onclick="this.form.submit()">Continue</button></p>
      </form>
      <script>
        var labels = ['1-50 employees', '51-100 employees', '101-200 employees', '201-300 employees'];
        function paint() {
          document.getElementById('answers').innerHTML = labels.map(function (t, i) {
            return '<div class="ans" data-v="' + (i + 1) + '">' +
              '<input type="radio" name="RR1" value="' + (i + 1) + '"> ' + t + '</div>';
          }).join('');
          [].forEach.call(document.querySelectorAll('.ans'), function (d) {
            d.addEventListener('click', function () {
              var input = d.querySelector('input');
              input.checked = true;
              input.dispatchEvent(new Event('change', { bubbles: true }));
            });
          });
        }
        paint();
        // The player repaints once more a moment later — anything captured
        // before this point is stale.
        setTimeout(paint, 700);   // wipes any selection made before this
      </script>
      </body></html>`);
    return;
  }
  if (req.url && req.url.split('?')[0] === '/other') {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    res.end(`<!doctype html><html><head><title>Survey</title></head><body>
      <form method="POST" action="/othercheck">
        <div class="question" id="OT1"><div class="qtitle">Which industry does your company operate in?</div>
          <label class="choice" for="OT1_1"><input type="radio" name="OT1" id="OT1_1" value="1"> Technology</label>
          <label class="choice" for="OT1_2"><input type="radio" name="OT1" id="OT1_2" value="2"> Finance</label>
          <label class="choice" for="OT1_3"><input type="radio" name="OT1" id="OT1_3" value="3"> Other (please specify)
            <input type="text" name="oeOT1" id="oeOT1" value=""></label>
        </div>
        <p><button class="btn-continue" onclick="this.form.submit()">Continue</button></p>
      </form></body></html>`);
    return;
  }
  // Qualtrics JFE markup, as captured from a live survey: tilde-separated
  // names (QR~QID1, checkbox rows QR~QID3~1, other-specify QR~QID2~3~TEXT), a
  // dropdown whose blank placeholder carries a real value ("…~null"), and
  // arrow-labelled #NextButton / #PreviousButton inputs.
  if (req.url && req.url.split('?')[0] === '/qualtrics') {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    res.end(`<!doctype html><html><head><title>Qualtrics Survey</title></head><body>
      <form method="POST" action="/qualtricscheck" id="Page">
        <div class="QuestionOuter MC" id="QID1">
          <label class="QuestionText" for="QR~QID1"><label class="ExportTag">Q1.</label> In which <b>state</b> do you reside?</label>
          <div class="QuestionBody"><select class="Selection" name="QR~QID1" id="QR~QID1">
            <option aria-label="Blank" value="QR~QID1~null"></option>
            <option value="5">California</option><option value="44">Texas</option>
            <option value="52">I do not live in the United States</option>
          </select></div>
        </div>
        <div class="QuestionOuter MC" id="QID2">
          <fieldset><legend><label class="QuestionText">Q2. What is your gender?</label></legend>
          <label for="QR~QID2~1"><input type="radio" name="QR~QID2" id="QR~QID2~1" value="1"> Male</label>
          <label for="QR~QID2~2"><input type="radio" name="QR~QID2" id="QR~QID2~2" value="2"> Female</label>
          <label for="QR~QID2~3"><input type="radio" name="QR~QID2" id="QR~QID2~3" value="3"> Other (please specify)
            <input type="text" name="QR~QID2~3~TEXT" id="QR~QID2~3~TEXT" value=""></label>
          </fieldset>
        </div>
        <div class="QuestionOuter MC" id="QID3">
          <fieldset><legend><label class="QuestionText">Q3. Which apply to you?</label></legend>
          <label for="QR~QID3~1"><input type="checkbox" name="QR~QID3~1" id="QR~QID3~1" value="1"> I learn online</label>
          <label for="QR~QID3~2"><input type="checkbox" name="QR~QID3~2" id="QR~QID3~2" value="2"> I take in-person classes</label>
          <label for="QR~QID3~3"><input type="checkbox" name="QR~QID3~3" id="QR~QID3~3" value="3"> Neither</label>
          </fieldset>
        </div>
        <div id="Buttons">
          <input id="PreviousButton" class="PreviousButton Button" type="button" value="←" aria-label="Previous">
          <input id="NextButton" class="NextButton Button" type="button" value="→" aria-label="Next" onclick="this.form.submit()">
        </div>
      </form></body></html>`);
    return;
  }
  // Faithful Qualtrics radio-list page (SAVR): real input overlaid by an empty
  // label.q-radio, answer text in a separate SingleAnswer label, input hidden
  // by opacity, and — like the live engine — the page validates against its OWN
  // runtime state (updated on the input's change event), not input.checked.
  if (req.url && req.url.split('?')[0] === '/qradio') {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    const choices = [
      [1, 'Less than $20,000'], [2, '$20,000 to $39,999'], [3, '$40,000 to $59,999'],
      [8, 'More than $200,000'], [11, 'Prefer not to answer'],
    ];
    const li = choices.map(([v, t]) => `
      <li class="Selection"> <input class="radio QWatchTimer" type="radio" name="QR~QID99" id="QR~QID99~${v}" value="${v}">
        <label for="QR~QID99~${v}" class="q-radio" aria-hidden="true"></label>
        <span class="LabelWrapper"><label for="QR~QID99~${v}" class="SingleAnswer ChoiceTextPositionLeft"><span>${t}</span></label></span>
        <div class="clear"></div> </li>`).join('');
    res.end(`<!doctype html><html><head><title>Qualtrics Survey</title>
      <style>input.radio{opacity:0;position:absolute;left:-5px;width:20px;height:20px}
             /* like the real JFE overlay: a 0-box label whose circle is drawn
                by a pseudo-element, so the label itself is not "visible" and the
                only on-screen stand-in is the SingleAnswer text label */
             .q-radio{position:absolute;width:0;height:0;overflow:hidden}
             .q-radio::before{content:'';position:absolute;width:16px;height:16px;border:1px solid #999;border-radius:50%}
             .SingleAnswer{display:inline-block;padding-left:26px}</style></head><body>
      <form id="Page" name="Page">
        <div class="QuestionOuter MC" id="QID99"><fieldset><legend>
          <div class="QuestionText"><label class="ExportTag">Q4.</label> What is your <b>annual household income before tax</b>?</div></legend>
          <div class="QuestionBody"><ul class="ChoiceStructure">${li}</ul></div>
        </fieldset></div>
        <div id="Buttons"><input id="PreviousButton" type="button" value="←" aria-label="Previous">
          <input id="NextButton" type="button" value="→" aria-label="Next"></div>
      </form>
      <script>
        // Qualtrics-like runtime: track selection in JS state on change, mirror
        // the q-checked class, and gate Next on that state (not on .checked).
        var picked = null;
        [].forEach.call(document.querySelectorAll('input.radio'), function(inp){
          inp.addEventListener('change', function(){
            picked = inp.value;
            [].forEach.call(document.querySelectorAll('.q-radio'), function(l){ l.classList.remove('q-checked'); });
            var vis = document.querySelector('label.q-radio[for="'+inp.id+'"]');
            if (vis) vis.classList.add('q-checked');
          });
        });
        // Like JFE, the Next control is driven by its own pointer handler, not
        // by a bare synthetic click — bind on mousedown so a plain .click()
        // alone does NOT advance (that was the real stuck bug).
        document.getElementById('NextButton').addEventListener('mousedown', function(){
          if (!picked) {
            document.body.insertAdjacentHTML('afterbegin','<div class="ValidationError" style="color:#e9730c">Please answer this question.</div>');
            return;
          }
          document.open(); document.write('<!doctype html><title>Qualtrics Survey</title><body><h2>We thank you for your time spent taking this survey.</h2><p>Your response has been recorded.</p>'); document.close();
        });
      </script></body></html>`);
    return;
  }
  // Qualtrics numeric money write-in (two ~TEXT boxes, plain type=text but the
  // wording + validation banner cap the value). A word or an over-max number
  // is rejected, mirroring the live Q34 that stalled the bot.
  if (req.url && req.url.split('?')[0] === '/qnumeric') {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    res.end(`<!doctype html><html><head><title>Qualtrics Survey</title></head><body>
      <form id="Page" name="Page">
        <!-- cap stated in a separate banner, and a scenario stem with no money
             words: only the page-level numeric cue can mark these boxes numeric -->
        <div class="PageNote">You cannot enter a value over $10,000. If you would go higher, please write "10000" in the box.</div>
        <div class="QuestionOuter" id="QID90"><fieldset><legend>
          <div class="QuestionText"><label class="ExportTag">Q34.</label> Imagine two platforms came together into one experience. What would you put here, today and looking ahead?</div></legend>
          <div class="QuestionBody">
            <span class="LabelWrapper">Today</span> <input type="text" name="QR~QID90~1~TEXT" id="QR~QID90~1~TEXT" value="">
            <span class="LabelWrapper">Ahead</span> <input type="text" name="QR~QID90~2~TEXT" id="QR~QID90~2~TEXT" value="">
          </div></fieldset></div>
        <div id="Buttons"><input id="PreviousButton" type="button" value="←" aria-label="Previous">
          <input id="NextButton" type="button" value="→" aria-label="Next"></div>
      </form>
      <script>
        // Like JFE: the engine keeps its own copy of each answer, updated from
        // the input event — a bare el.value= without a real input event is not
        // seen, so Next stays blocked (the actual Q55 stuck bug).
        var state = {};
        ['QR~QID90~1~TEXT','QR~QID90~2~TEXT'].forEach(function(id){
          var el = document.getElementById(id);
          el.addEventListener('input', function(){ state[id] = el.value; });
        });
        document.getElementById('NextButton').addEventListener('mousedown', function(){
          var a = (state['QR~QID90~1~TEXT']||'').trim();
          var b = (state['QR~QID90~2~TEXT']||'').trim();
          function ok(x){ return /^\\d+(\\.\\d+)?$/.test(x) && Number(x) <= 10000; }
          if (!ok(a) || !ok(b)) {
            if (!document.querySelector('.ValidationError'))
              document.body.insertAdjacentHTML('afterbegin','<div class="ValidationError" style="color:#e9730c">Please enter a valid number no greater than $10,000.</div>');
            return;
          }
          document.open(); document.write('<!doctype html><title>Qualtrics Survey</title><body><h2>We thank you for your time spent taking this survey.</h2><p>Your response has been recorded.</p>'); document.close();
        });
      </script></body></html>`);
    return;
  }
  if (req.url === '/qualtricscheck') {
    let raw = '';
    req.on('data', (c) => (raw += c));
    req.on('end', () => {
      const form = new URLSearchParams(raw);
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      const state = form.get('QR~QID1') || '';
      if (!state || /~null$/.test(state))
        res.end(`<!doctype html><html><head><title>Qualtrics Survey</title></head><body><div class="ValidationError">Please answer this question.</div></body></html>`);
      else if (form.get('QR~QID2~3~TEXT') && form.get('QR~QID2') !== '3')
        res.end(`<!doctype html><html><head><title>Qualtrics Survey</title></head><body><div class="ValidationError">Please only specify text for the option you selected.</div></body></html>`);
      else res.end(end('Thank you for completing this survey', 'Your responses have been recorded.'));
    });
    return;
  }
  if (req.method === 'GET') {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    res.end(render(1, {}));
    return;
  }
  if (req.url === '/rerendercheck') {
    let raw = '';
    req.on('data', (c) => (raw += c));
    req.on('end', () => {
      const form = new URLSearchParams(raw);
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      if (!form.get('RR1'))
        res.end(`<!doctype html><html><body><p class="error">There were problems with some of the data you entered. Please select an answer.</p></body></html>`);
      else res.end(end('Thank you for completing this survey', 'Your responses have been recorded.'));
    });
    return;
  }
  if (req.url && req.url.startsWith('/cards5check')) {
    let raw = '';
    req.on('data', (c) => (raw += c));
    req.on('end', () => {
      const form = new URLSearchParams(raw);
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      if (!form.get('h0')) res.end(`<!doctype html><html><body><p class="error">Please select an answer.</p></body></html>`);
      else res.end(end('Thank you for completing this survey', 'Your responses have been recorded.'));
    });
    return;
  }
  if (req.url && req.url.startsWith('/repeatcheck')) {
    const step = Number((req.url.match(/step=(\d+)/) || [, 1])[1]);
    let raw = '';
    req.on('data', (c) => (raw += c));
    req.on('end', () => {
      const form = new URLSearchParams(raw);
      if (!form.get('h0') || !form.get('h1')) {
        res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
        res.end(`<!doctype html><html><body><p class="error">Please provide an answer for each item.</p></body></html>`);
        return;
      }
      if (step < 5) {
        res.writeHead(302, { location: `/repeat?step=${step + 1}` });
        res.end();
        return;
      }
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(end('Thank you for completing this survey', 'Your responses have been recorded.'));
    });
    return;
  }
  if (req.url === '/cardscheck') {
    let raw = '';
    req.on('data', (c) => (raw += c));
    req.on('end', () => {
      const form = new URLSearchParams(raw);
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      const all = [0, 1, 2].every((i) => form.get(`ans32900.0.${i}`) || form.get(`h${i}`));
      if (!all) res.end(`<!doctype html><html><body><p class="error">There were problems with some of the data you entered. Please provide an answer for each item.</p></body></html>`);
      else res.end(end('Thank you for completing this survey', 'Your responses have been recorded.'));
    });
    return;
  }
  if (req.url === '/offscreencheck') {
    let raw = '';
    req.on('data', (c) => (raw += c));
    req.on('end', () => {
      const form = new URLSearchParams(raw);
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      if (!form.get('ans32477.0.0'))
        res.end(`<!doctype html><html><body><p class="error">There were problems with some of the data you entered. Please select an answer.</p></body></html>`);
      else if ([...form.keys()].some((k) => k.startsWith('ra__') && form.get(k)))
        res.end(`<!doctype html><html><body><p class="error">Automated response detected.</p></body></html>`);
      else res.end(end('Thank you for completing this survey', 'Your responses have been recorded.'));
    });
    return;
  }
  if (req.url === '/dottedcheck') {
    let raw = '';
    req.on('data', (c) => (raw += c));
    req.on('end', () => {
      const form = new URLSearchParams(raw);
      const checked = [...form.keys()].filter((k) => k.startsWith('ans32645')).length;
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      if (checked > 2 || checked === 0) {
        // Decipher re-renders the page with a fresh machine field on every error
        const nonce = Math.floor(Math.random() * 900000 + 100000);
        res.end(`<!doctype html><html><head><title>Survey</title></head><body>
          <p class="error">Please check at most 2 boxes in this column (you checked ${checked}).</p>
          <form method="POST" action="/dottedcheck">
            ${['Upgrading legacy systems', 'Adoption of AI', 'Business intelligence', 'Revenue growth', 'Cybersecurity']
              .map((t, i) => `<label class="choice" for="ans32645.0.${i}"><input type="checkbox" name="ans32645.0.${i}" id="ans32645.0.${i}" value="1"> ${t}</label>`)
              .join('')}
            <input type="text" name="ra__${nonce}" style="position:absolute;left:-9999px" value="">
            <p><button class="btn-continue" onclick="this.form.submit()">Continue</button></p>
          </form></body></html>`);
        return;
      }
      res.end(end('Thank you for completing this survey', 'Your responses have been recorded.'));
    });
    return;
  }
  if (req.url === '/othercheck') {
    let raw = '';
    req.on('data', (c) => (raw += c));
    req.on('end', () => {
      const form = new URLSearchParams(raw);
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      // Typing in the "other" box without picking "Other" is the error Decipher
      // raises, and vice versa.
      if (form.get('oeOT1') && form.get('OT1') !== '3')
        res.end(`<!doctype html><html><body><p class="error">There were problems with some of the data you entered. You typed a response for "Other" but did not select it.</p></body></html>`);
      else if (form.get('OT1') === '3' && !form.get('oeOT1'))
        res.end(`<!doctype html><html><body><p class="error">Please specify your answer for "Other".</p></body></html>`);
      else res.end(end('Thank you for completing this survey', 'Your responses have been recorded.'));
    });
    return;
  }
  if (req.url === '/limitcheck' || req.url === '/sumcheck') {
    let raw = '';
    req.on('data', (c) => (raw += c));
    req.on('end', () => {
      const form = new URLSearchParams(raw);
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      if (req.url === '/limitcheck') {
        const checked = [...form.keys()].filter((k) => k.startsWith('LM1r')).length;
        if (checked > 2 || checked === 0) {
          res.end(`<!doctype html><html><head><title>Survey</title></head><body>
            <p class="error">Please check at most 2 boxes in this column (you checked ${checked}).</p>
            <form method="POST" action="/limitcheck">
              ${['Upgrading legacy systems', 'Adoption of AI', 'Business intelligence', 'Revenue growth', 'Cybersecurity']
                .map((t, i) => `<label class="choice" for="LM1r${i + 1}"><input type="checkbox" name="LM1r${i + 1}" id="LM1r${i + 1}" value="1"> ${t}</label>`)
                .join('')}
              <p><button class="btn-continue" onclick="this.form.submit()">Continue</button></p>
            </form></body></html>`);
          return;
        }
      } else {
        const total = ['SM1r1', 'SM1r2', 'SM1r3'].reduce((n, k) => n + Number(form.get(k) || 0), 0);
        if (total !== 100) {
          res.end(`<!doctype html><html><head><title>Survey</title></head><body>
            <p class="error">Your total must equal 100 exactly. You have entered ${total}.</p>
            <form method="POST" action="/sumcheck"><div class="question" id="SM1">
              <div class="qtitle">Split your incremental spend. Your total must equal 100 exactly.</div>
              <table><tr><td>Direct AI Spend</td><td><input type="number" name="SM1r1" value="${form.get('SM1r1') || ''}"></td></tr>
              <tr><td>AI Enablement Spend</td><td><input type="number" name="SM1r2" value="${form.get('SM1r2') || ''}"></td></tr>
              <tr><td>Non-AI Spend</td><td><input type="number" name="SM1r3" value="${form.get('SM1r3') || ''}"></td></tr></table></div>
              <p><button class="btn-continue" onclick="this.form.submit()">Continue</button></p>
            </form></body></html>`);
          return;
        }
      }
      res.end(end('Thank you for completing this survey', 'Your responses have been recorded.'));
    });
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
