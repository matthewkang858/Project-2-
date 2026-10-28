// A Qualtrics-style survey generated from a parsed questionnaire
// (surveys/<id>/outline-spec.json), so a survey's run configs can be rehearsed
// end to end — real snippet, real Chromium — before anyone opens the live link.
//
//   GET /spec/<id>   e.g. /spec/are01
//
// One question per page, client-side navigation (like JFE), Qualtrics control
// names (QR~QID62~1 radios per grid row, QR~QID19~1~2 matrix checkboxes,
// ~TEXT boxes), recode values, a seeded shuffle for every [Randomize] (anchors
// stay last), forced response, "up to N" limits, exclusive options, ZIP and
// dollar validation, terminates and attention checks. Display gates are the
// questionnaire's own, evaluated in the page with a port of outline/gates.py.

import { readFileSync } from 'node:fs';

export function specSurvey(req, res) {
  const id = (req.url.split('?')[0].split('/')[2] || '').replace(/[^a-z0-9_-]/gi, '');
  let spec;
  try {
    spec = JSON.parse(readFileSync(new URL(`../surveys/${id}/outline-spec.json`, import.meta.url), 'utf8'));
  } catch {
    res.writeHead(404, { 'content-type': 'text/plain' });
    res.end(`no spec for ${id}`);
    return;
  }
  const gates = {};
  for (const r of spec.rules) if (r.type === 'display') (gates[r.q] = gates[r.q] || new Set()).add(r.rule);
  const data = {
    questions: spec.questions,
    checks: spec.attentionChecks || [],
    blocks: (spec.textBlocks || []).filter((b) => b.kind === 'text'),
    gates: Object.fromEntries(Object.entries(gates).map(([k, v]) => [k, [...v]])),
  };
  res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
  res.end(`<!doctype html><html><head><meta charset="utf-8"><title>Qualtrics Survey</title>
<style>body{font-family:sans-serif;max-width:900px;margin:20px auto}td,th{padding:3px 6px;border-bottom:1px solid #ddd}
.ValidationError{color:#c00;font-weight:bold}</style></head><body>
<form id="Page" name="Page" onsubmit="return false"><div id="Questions"></div>
<div id="Buttons"><input id="PreviousButton" type="button" value="←" aria-label="Previous"> <input id="NextButton" type="button" value="→" aria-label="Next"></div></form>
<script>window.SPEC = ${JSON.stringify(data).replace(/</g, '\\u003c')};</script>
<script>${CLIENT}</script></body></html>`);
}

const CLIENT = String.raw`
(function () {
  var S = window.SPEC;
  var Q = {}; S.questions.forEach(function (q) { Q[q.q] = q; });
  var ANS = {};
  var ROWS = {};   // rows each grid actually showed: chained pipes read these
  var POOL = {};
  S.questions.forEach(function (q) { POOL[q.q] = (q.options.length ? q.options : (q.columns || [])).map(function (o) { return o.letter; }); });

  // ---- gates (port of outline/gates.py) ----
  var CLAUSE = /^([a-z]{1,2}(?:\s*[-–]\s*[a-z]{1,2})?(?:\s*(?:,|,?\s*\bor\b)\s*[a-z]{1,2}(?:\s*[-–]\s*[a-z]{1,2})?)*)\s+(?:is\s+|are\s+)?(not\s+)?selected(?:\s+for\s+(1\+\s*rows?|rows?\s+[a-z]{1,2}(?:\s*(?:,|\bor\b|\band\b)\s*[a-z]{1,2})*))?\s+(?:in|for)\s+(Q\d+(?:\s*(?:,|\bor\b)\s*Q\d+)*)\s*$/i;
  function parseGate(t) {
    t = t.trim().replace(/^\s*\[?\s*(?:display\s+|show\s+|ask\s+)?if\s+/i, '').replace(/[\]\s]+$/, '');
    var parts = t.split(/\s+(AND|OR)\s+/), clauses = [], op = null;
    for (var k = 0; k < parts.length; k++) {
      if (k % 2) { op = parts[k]; continue; }
      var m = parts[k].trim().match(CLAUSE);
      if (!m) throw new Error('gate not understood: ' + t);
      clauses.push({ letters: m[1], neg: !!m[2], qs: m[4].match(/Q\d+/g),
        rows: !m[3] ? null : (/^1/.test(m[3].trim()) ? 'any' : (m[3].replace(/^rows?\s+/i, '').replace(/\b(or|and)\b/g, ' ').match(/\b[a-z]{1,2}\b/g) || [])) });
    }
    return { op: op, clauses: clauses };
  }
  function expand(spec, pool) {
    var out = [];
    spec.replace(/–/g, '-').split(/\s*,\s*(?:or\s+)?|\s+or\s+/).forEach(function (part) {
      part = part.trim(); if (!part) return;
      var e = part.split('-').map(function (x) { return x.trim(); });
      if (e.length === 2 && pool.indexOf(e[0]) >= 0 && pool.indexOf(e[1]) >= 0) out = out.concat(pool.slice(pool.indexOf(e[0]), pool.indexOf(e[1]) + 1));
      else if (e.length === 1) out.push(e[0]);
      else e.forEach(function (x) { if (pool.indexOf(x) >= 0) out.push(x); });
    });
    return out;
  }
  function gateOk(text) {
    var g = parseGate(text);
    var res = g.clauses.map(function (c) {
      var hit = false;
      c.qs.forEach(function (q) {
        var want = expand(c.letters, POOL[q] || []), got = ANS[q];
        if (!got) return;
        if (Array.isArray(got)) hit = hit || got.some(function (x) { return want.indexOf(x) >= 0; });
        else Object.keys(got).forEach(function (r) {
          if (c.rows && c.rows !== 'any' && c.rows.indexOf(r) < 0) return;
          hit = hit || got[r].some(function (x) { return want.indexOf(x) >= 0; });
        });
      });
      return c.neg ? !hit : hit;
    });
    return g.op === 'AND' ? res.every(Boolean) : res.some(Boolean);
  }
  function tagged(o, re) { return (o.tags || []).some(function (t) { return re.test(t); }); }
  function gateOf(o) { return (o.tags || []).filter(function (t) { return /^if\s/i.test(t); })[0]; }

  // ---- seeded shuffle, anchors kept last (like Qualtrics randomization) ----
  function seeded(seed) { var s = 0; for (var i = 0; i < seed.length; i++) s = (s * 31 + seed.charCodeAt(i)) >>> 0; return function () { s = (s * 1103515245 + 12345) >>> 0; return s / 4294967296; }; }
  function shuffle(list, seed) {
    var free = list.filter(function (o) { return !tagged(o, /^(Anchor|Exclusive)/i); });
    var fixed = list.filter(function (o) { return tagged(o, /^(Anchor|Exclusive)/i); });
    var rnd = seeded(seed);
    for (var i = free.length - 1; i > 0; i--) { var j = Math.floor(rnd() * (i + 1)); var t = free[i]; free[i] = free[j]; free[j] = t; }
    return free.concat(fixed);
  }
  function randomized(q, where) {
    if (where === 'options') return (q.tags || []).indexOf('Randomize') >= 0;
    var g = (q.gridTags || []).join(' ');
    return where === 'columns' ? /Columns\]?\s*\[?Randomize/i.test(g) || (q.gridTags || []).indexOf('Randomize') >= 0 && /Columns/.test(g) && !/Rows/.test(g)
                               : /Rows/.test(g) && (q.gridTags || []).indexOf('Randomize') >= 0;
  }

  // ---- flow: intro text, questions with their attention checks and text blocks ----
  var FLOW = [];
  S.blocks.filter(function (b) { return !b.afterQ; }).forEach(function (b) { FLOW.push({ kind: 'text', text: b.text }); });
  S.questions.forEach(function (q) {
    FLOW.push({ kind: 'q', q: q });
    S.checks.filter(function (c) { return c.afterQ === q.q; }).forEach(function (c) { FLOW.push({ kind: 'ac', q: c }); });
    S.blocks.filter(function (b) { return b.afterQ === q.q; }).forEach(function (b) { FLOW.push({ kind: 'text', text: b.text }); });
  });
  var at = -1, hist = [];

  function visible(item) {
    if (item.kind !== 'q') return true;
    return (S.gates[item.q.q] || []).every(gateOk);
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function rowsOf(q) {
    var out = [];
    (q.rows || []).forEach(function (r) {
      var pipe = (r.tags || []).filter(function (t) { return /^populate/i.test(t); })[0];
      if (pipe) {
        var m = pipe.match(/Populate with rows (?:where )?(.+?) selected in (Q\d+)/i);
        var src = m && Q[m[2]], got = m && ANS[m[2]];
        if (!src || !got) return;
        if (!Array.isArray(got)) {
          var want = expand(m[1], (src.columns || []).map(function (c) { return c.letter; }));
          (ROWS[src.q] || (src.rows || []).map(function (sr) { return { key: sr.letter, text: sr.text }; })).forEach(function (sr) {
            if ((got[sr.key] || []).some(function (x) { return want.indexOf(x) >= 0; })) out.push({ key: sr.key, text: sr.text });
          });
        } else {
          var want2 = expand(m[1], src.options.map(function (o) { return o.letter; }));
          src.options.forEach(function (o) { if (got.indexOf(o.letter) >= 0 && want2.indexOf(o.letter) >= 0) out.push({ key: o.letter, text: o.text }); });
        }
        return;
      }
      var g = gateOf(r);
      if (g && !gateOk(g)) return;
      out.push({ key: r.letter, text: r.text });
    });
    return out;
  }
  function limitOf(q) { var m = (q.raw || '').match(/select up to (\w+)/i); return m ? ({ one: 1, two: 2, three: 3, four: 4, five: 5 }[m[1].toLowerCase()] || Number(m[1]) || 99) : 99; }
  function maxOf(q, o) {
    var t = ((q.tags || []).concat(o ? o.tags || [] : [])).join(' ');
    var m = t.match(/\$0\s*(?:-|to)\s*\$([\d,]+)/i);
    return m ? Number(m[1].replace(/,/g, '')) : 1e9;
  }
  var STATES = ['Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut','Delaware','District of Columbia','Florida','Georgia','Hawaii','Idaho','Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland','Massachusetts','Michigan','Minnesota','Mississippi','Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey','New Mexico','New York','North Carolina','North Dakota','Ohio','Oklahoma','Oregon','Pennsylvania','Rhode Island','South Carolina','South Dakota','Tennessee','Texas','Utah','Vermont','Virginia','Washington','West Virginia','Wisconsin','Wyoming','I do not live in the United States'];

  // ---- render ----
  var CUR = null;
  function head(q, label) {
    return '<div class="QuestionOuter" id="QID' + q.q + '"><fieldset><legend><div class="QuestionText">' + label + '</div></legend>';
  }
  function cellLabel(id, text) { return '<label for="' + id + '" class="q-radio"></label><label for="' + id + '" class="SingleAnswer"><span>' + esc(text) + '</span></label>'; }
  function render() {
    var item = FLOW[at], box = document.getElementById('Questions'), h = '';
    var old = document.querySelector('.ValidationError'); if (old) old.remove();
    CUR = { item: item, rows: null, opts: null, cols: null };
    if (item.kind === 'text') {
      h = '<div class="QuestionOuter"><div class="QuestionText">' + esc(item.text).replace(/\n/g, '<br>') + '</div></div>';
    } else {
      var q = item.q, n = item.kind === 'ac' ? q.q : q.q.slice(1), base = 'QR~QID' + n;
      var label = item.kind === 'ac' ? esc(q.text) : '<label class="ExportTag">' + q.q + '.</label> ' + esc(q.text);
      h = head(q, label);
      if (q.columns && q.columns.length && q.rows && q.rows.length) {
        var rows = rowsOf(q); if (randomized(q, 'rows')) rows = shuffle(rows.map(function (r) { return { letter: r.key, text: r.text, tags: [], key: r.key }; }), q.q + 'r');
        var cols = q.columns.map(function (c, i) { return Object.assign({ v: i + 1 }, c); });
        if (randomized(q, 'columns')) cols = shuffle(cols, q.q + 'c');
        var numeric = q.type === 'Numeric', mp = /MP per row|all that apply per|per column/i.test((q.tags || []).join(' ') + ' ' + q.raw);
        CUR.rows = rows; CUR.cols = cols;
        h += '<table class="ChoiceStructure"><tr><td></td>' + cols.map(function (c) { return '<td class="Answers">' + esc(c.text) + '</td>'; }).join('') + '</tr>';
        rows.forEach(function (r, ri) {
          h += '<tr class="ChoiceRow"><th class="c1"><span class="LabelWrapper"><label>' + esc(r.text) + '</label></span></th>';
          if (q.dropdowns && q.dropdowns.length) {
            q.dropdowns.forEach(function (d, di) {
              var id = base + '~' + (ri + 1) + '~' + (di + 1);
              h += '<td><select name="' + id + '" id="' + id + '"><option value="' + id + '~null"></option>' + (d.choices || []).map(function (c, k) { return '<option value="' + (k + 1) + '">' + esc(c.text) + '</option>'; }).join('') + '</select></td>';
            });
          } else cols.forEach(function (c) {
            var id = base + '~' + (ri + 1) + '~' + c.v;
            if (numeric && !tagged(c, /^Exclusive/i)) h += '<td><label for="' + id + '~TEXT">' + esc(c.text) + '</label><input type="text" name="' + id + '~TEXT" id="' + id + '~TEXT"></td>';
            else if (numeric || mp) h += '<td><input type="checkbox" name="' + id + '" id="' + id + '" value="' + c.v + '">' + cellLabel(id, c.text) + '</td>';
            else h += '<td><input type="radio" name="' + base + '~' + (ri + 1) + '" id="' + id + '" value="' + c.v + '">' + cellLabel(id, c.text) + '</td>';
          });
          h += '</tr>';
        });
        h += '</table>';
      } else {
        var opts = q.options.map(function (o, i) { return Object.assign({ v: i + 1 }, o); }).filter(function (o) { var g = gateOf(o); return !g || gateOk(g); });
        if (item.kind === 'q' && randomized(q, 'options') || item.kind === 'ac') opts = shuffle(opts, q.q);
        CUR.opts = opts;
        var dropdown = (q.tags || []).indexOf('Dropdown') >= 0;
        if (dropdown) {
          var choices = /age/i.test(q.text) ? ['Under 18'].concat(Array.from({ length: 83 }, function (_, k) { return String(18 + k); })) : STATES;
          h += '<select name="' + base + '" id="' + base + '"><option value="' + base + '~null"></option>' + choices.map(function (c, k) { return '<option value="' + (k + 1) + '">' + esc(c) + '</option>'; }).join('') + '</select>';
        } else if (q.type === 'Open' || (q.tags || []).indexOf('Write-in') >= 0 || q.type === 'Numeric') {
          opts.forEach(function (o) {
            var id = base + '~' + o.v;
            if (tagged(o, /^Exclusive/i)) h += '<div><input type="checkbox" name="' + id + '" id="' + id + '" value="' + o.v + '">' + cellLabel(id, o.text) + '</div>';
            else h += '<div><label for="' + id + '~TEXT">' + esc(o.text || '') + '</label> <input type="text" name="' + id + '~TEXT" id="' + id + '~TEXT"></div>';
          });
        } else {
          var multi = q.type === 'MP' || /all that apply|select up to/i.test(q.raw || '');
          opts.forEach(function (o) {
            var id = base + '~' + o.v;
            h += '<li><input type="' + (multi ? 'checkbox' : 'radio') + '" name="' + (multi ? id : base) + '" id="' + id + '" value="' + o.v + '">' + cellLabel(id, o.text) + '</li>';
          });
          h = h.replace('</legend>', '</legend><ul class="ChoiceStructure">') + '</ul>';
        }
      }
      h += '</fieldset></div>';
    }
    box.innerHTML = h;
  }

  // ---- read + validate the current page ----
  function err(msg) {
    if (!document.querySelector('.ValidationError')) document.body.insertAdjacentHTML('afterbegin', '<div class="ValidationError">' + esc(msg) + '</div>');
    return false;
  }
  function end(html) { document.open(); document.write('<!doctype html><title>Qualtrics Survey</title><body>' + html + '</body>'); document.close(); }
  function terminate() { end('<h2>Unfortunately, you do not qualify for this survey.</h2>'); return 'end'; }
  function collect() {
    var item = CUR.item; if (item.kind === 'text') return true;
    var q = item.q, n = item.kind === 'ac' ? q.q : q.q.slice(1), base = 'QR~QID' + n;
    var el = function (id) { return document.getElementById(id); };
    if (CUR.rows) {
      var grid = {}, limit = limitOf(q);
      for (var ri = 0; ri < CUR.rows.length; ri++) {
        var r = CUR.rows[ri], picked = [];
        if (q.dropdowns && q.dropdowns.length) {
          for (var di = 0; di < q.dropdowns.length; di++) { var s = el(base + '~' + (ri + 1) + '~' + (di + 1)); if (!s || /null$/.test(s.value)) return err('Please answer every dropdown.'); }
          grid[r.key] = []; continue;
        }
        var num = 0, excl = false;
        for (var ci = 0; ci < CUR.cols.length; ci++) {
          var c = CUR.cols[ci], id = base + '~' + (ri + 1) + '~' + c.v;
          var t = el(id + '~TEXT');
          if (t) { if (t.value.trim() !== '') { if (!/^\d+(\.\d+)?$/.test(t.value.trim()) || Number(t.value) > maxOf(q, c)) return err('Please enter a valid amount.'); num++; picked.push(c.letter); } continue; }
          var b = el(id); if (b && b.checked) { picked.push(c.letter); if (tagged(c, /^Exclusive/i)) excl = true; }
        }
        if (!picked.length) return err('Please answer every row.');
        if (excl && picked.length > 1) return err('That answer cannot be combined with others.');
        if (q.type === 'Numeric' && q.columns.some(function (c) { return !tagged(c, /^Exclusive/i); }) && !num && !excl && q.columns.length > 1 && !q.columns.every(function (c) { return !tagged(c, /^Exclusive/i); })) return err('Please enter an amount.');
        if (picked.length > limit) return err('Please select no more than ' + limit + '.');
        grid[r.key] = picked;
      }
      ANS[q.q] = grid;
      ROWS[q.q] = CUR.rows.map(function (r) { return { key: r.key, text: r.text }; });
      return true;
    }
    var dd = el(base);
    if (dd && dd.tagName === 'SELECT') {
      if (/null$/.test(dd.value)) return err('Please choose an answer.');
      var txt = dd.options[dd.selectedIndex].text;
      if (/^Under 18$|do not live/i.test(txt)) return terminate();
      ANS[q.q] = ['a']; return true;
    }
    var chosen = [], typed = 0, excl2 = false, zip = /ZIP/i.test(q.text);
    for (var k = 0; k < CUR.opts.length; k++) {
      var o = CUR.opts[k], oid = base + '~' + o.v;
      var tb = el(oid + '~TEXT');
      if (tb) {
        var v = tb.value.trim();
        if (v) {
          if (zip && !/^\d{5}$/.test(v)) return err('Please enter a valid 5-digit ZIP code.');
          if (q.type === 'Numeric' && (!/^\d+(\.\d+)?$/.test(v) || Number(v) > maxOf(q, o))) return err('Please enter a valid amount.');
          typed++; chosen.push(o.letter);
        }
        continue;
      }
      var inp = el(oid);
      if (inp && inp.checked) { chosen.push(o.letter); if (tagged(o, /^Exclusive/i)) excl2 = true; }
    }
    if (!chosen.length) return err('Please answer this question.');
    if (excl2 && chosen.length > 1) return err('That answer cannot be combined with others.');
    if (chosen.length > limitOf(q) && !typed) return err('Please select no more than ' + limitOf(q) + '.');
    var opt = function (l) { return q.options.filter(function (o) { return o.letter === l; })[0]; };
    if (chosen.some(function (l) { return tagged(opt(l), /^TERMINATE/i); })) return terminate();
    ANS[q.q] = chosen;
    return true;
  }

  function forward() {
    if (at >= 0) { var ok = collect(); if (ok === 'end' || !ok) return; hist.push(at); }
    do { at++; } while (at < FLOW.length && !visible(FLOW[at]));
    if (at >= FLOW.length) return end('<h2>We thank you for your time spent taking this survey.</h2><p>Your response has been recorded.</p>');
    render();
  }
  document.getElementById('NextButton').addEventListener('click', forward);
  document.getElementById('PreviousButton').addEventListener('click', function () { if (hist.length) { at = hist.pop(); render(); } });
  forward();
})();
`;
