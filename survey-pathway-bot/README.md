# Survey pathway bot

Automated branching-logic testing for hosted surveys. It walks a survey, answers
every question it finds, and maps which pages, questions and end states
(complete / screen-out / quota) each combination of answers leads to.

Three ways to run it — all sharing one page-reading core, so they see a survey
identically and produce the same report:

| Where it runs | What you use | Best for |
|---|---|---|
| **Your Chrome, automatically** | `chrome-extension/` loaded unpacked | Driving whole pathways in your own logged-in browser. No install, no Node. |
| **Your Chrome, one page at a time** | `dist/console-snippet.js` pasted into DevTools | Seeing what the bot sees, filling a page by hand, capturing a pathway you walked yourself. |
| **Node + Playwright** | `explore.mjs`, `run-paths.mjs` | Batch runs, screenshots, CI assertions on your routing. |

> Point any of these at a **test/preview link for a survey you own or are
> authorised to QA**. Driving a live, in-field link puts fake interviews into
> real sample and burns respondent entries.

---

## 1. Chrome extension (recommended if you just want it to run in Chrome)

A pasted console script dies on every page navigation, so multi-page automation
needs an extension. This one is ~400 lines, uses no remote code, and needs no
build step.

1. Chrome ▸ `chrome://extensions` ▸ turn on **Developer mode**.
2. **Load unpacked** ▸ select the `chrome-extension/` folder.
3. Pin the extension, click it, and fill in:
   - **Survey start URL** — your test link.
   - **Max traversals** — how many complete walks to do (start at 15–20).
   - **Delay per page** — 600 ms is polite; raise it if the platform enforces
     minimum page times.
   - **Clear cookies between runs** — tick if the survey refuses re-entry.
   - **Config** (optional JSON) — the same options as the CLI, see below.
4. **Start.** It opens its own tab and walks the survey; you can keep working in
   other tabs. Closing the run tab stops it.
5. **Download report** gives you `REPORT.md` (pathway map, coverage, findings);
   **Download traces** gives the raw JSON, which the CLI can re-render with
   `node report.mjs --traces spb-traces.json`.

Run 1 takes the first option at every question. Each later run replays a
previous run's answers up to one decision, flips that decision, and continues —
breadth-first, so screener logic gets covered first. The status line shows how
many branches are still queued.

## 2. Console snippet (single page)

`dist/console-snippet.js` is the same core plus a small console API. Paste it
into DevTools on a survey page — or, better, save it as a **DevTools Snippet**
(Sources ▸ Snippets ▸ New), which persists across navigations so you can re-run
it on each page with Ctrl/Cmd+Enter.

```js
spb.inspect()                  // table of every question, its options and how many branches it creates
spb.fill()                     // answer the whole page with the first option everywhere
spb.fill({ S1: 2 })            // …but take option index 2 for S1
spb.fill({ S1: /55 or older/ }) // …or the option whose label matches
spb.fill({ Q3: 'free text' })  // text answers
spb.step()                     // fill, then click Next
spb.capture()                  // record the answers currently selected on this page
spb.scenario('Over-55 route')  // print the captured pages as a paths.json scenario
```

`spb.capture()` on each page then `spb.scenario(...)` at the end turns a pathway
you walked by hand into a scripted regression test for the CLI.

Rebuild the snippet after editing the core with `npm run build:snippet`.

## 3. Node CLI

```bash
cd survey-pathway-bot
npm install                       # playwright
npx playwright install chromium   # skip if Chromium is already provisioned
```

**Explore** — discover pathways:

```bash
node explore.mjs \
  --url "https://survey-host.example/survey/selfserve/abc/g123" \
  --config config.json --out ./out --max-runs 40 --screenshots --delay 800
```

```
out/
  runs/run-001.json     every page, question, option and answer of one traversal
  screenshots/          full-page PNGs (with --screenshots)
  REPORT.md             outcomes · traversal table · pathway map · coverage · findings
```

**Scripted** — assert pathways, exits non-zero on failure so it drops into CI:

```bash
node run-paths.mjs --url "<link>" --paths paths.json
```

```json
{
  "scenarios": [
    {
      "name": "Under 18 is screened out",
      "answers": [{ "match": "^S1$|age group", "fixed": "Under 18" }],
      "expect": { "outcome": "terminate", "notSees": ["^Q1"], "maxPages": 2,
                  "textContains": "do not qualify" }
    }
  ]
}
```

`expect` supports `outcome` (`complete` / `terminate` / `quota` / `stalled` /
`maxsteps` / `error`), `sees` and `notSees` (regexes against the question names
shown), `textContains` (regex against the end page), and `maxPages`.

Sample output: [`examples/mock-report.md`](examples/mock-report.md) and
[`examples/mock-paths.md`](examples/mock-paths.md).

## Config reference

Used by all three runners (`config.example.json`, the CLI's `--config`, the
extension's Config box):

| Key | Meaning |
|---|---|
| `answers[]` | Rules applied in order, first match wins. `match` is a regex tested against the question's `name` **and** its wording. |
| `answers[].fixed` | Always choose the option matching this regex (no branching here). |
| `answers[].options` | Only branch across options matching this regex. |
| `answers[].value` / `values[]` | Text/number answer, or several values to branch across. |
| `answers[].skip` | Leave this checkbox unticked. |
| `branchOn` / `noBranch` | Regexes deciding which questions may branch at all. Everything else takes its first option — the main lever for keeping run counts sane. |
| `maxOptionsPerQuestion` | Try at most N options per question (e.g. 3 of a 10-point scale). |
| `values` | Defaults per input type (`text`, `textarea`, `number`). |
| `maxRuns`, `maxSteps`, `stepTimeout`, `delay` | Budget and pacing. |
| `selectors` | Override question containers, forward-button candidates, or the end-state keyword lists. |

Anchor your regexes (`"^18"`, not `"18"`) — `"18"` also matches "Under 18".

## How it finds questions

`chrome-extension/core.js` is the single source of truth, loaded by all three
runners. It groups the visible form controls on each page by their `name`
attribute, which is how every hosted engine (Decipher/Forsta, Qualtrics,
Confirmit, Alchemer, SurveyMonkey) renders radios, checkboxes, dropdowns, grids
and open ends — so nothing is hard-coded to one platform. Grid rows come out as
separate questions (`Q2r1`, `Q2r2`), which is what you want for coverage, and a
standalone checkbox is treated as a two-way branch (ticked / deliberately left
blank), because that is where "did you buy any of these" skip logic usually
hangs.

## Testing it offline

`mock/server.mjs` is a small branching survey (screen-out, quota,
conditionally-shown page) rendered the way hosted engines render:

```bash
node selftest.mjs           # CLI: explores the mock, then runs the scripted scenarios
node selftest-browser.mjs   # loads the extension into a real Chromium and drives the mock; also tests the snippet
node mock/server.mjs        # or poke at it yourself on :8099
```

## Practical notes

- **Check the platform's own tooling first.** Most enterprise survey platforms
  (including the Decipher/Forsta engine behind `*.dynata.com/survey/selfserve/…`
  links) ship a QA harness: preview/test links that can be re-entered, a flow or
  logic map, and a "generate test data" feature that fires N random completes.
  Use that for bulk data and this bot for what it does not do — asserting
  specific routes in CI, screenshots per page, and a coverage list of options
  never exercised.
- **Pacing.** Use the delay setting rather than hammering the host; some
  platforms enforce minimum page times and flag suspiciously fast interviews.
- **Re-entry.** Test links normally allow repeat entries; live links usually do
  not, and a run that dies mid-interview can leave a partial in the data.
- **Quotas move.** A pathway that hit `complete` yesterday can hit `quota` today.
  Assert `quota` only where you mean to.
- **Exotic widgets.** Sliders, drag-and-drop ranking, card sorts and canvas
  questions are not plain form controls; the bot records them but cannot answer
  them. Extend `candidates`/`applyAnswer` in `core.js` if your survey uses them.
- **Traps.** Attention checks and red-herring items ("select 'Gamma' here") get
  answered mechanically and can route the bot to a terminate — pin them with a
  `fixed` rule.
- **Combinatorics.** Full coverage is exponential in the number of questions.
  `branchOn`, `maxOptionsPerQuestion` and the max-run cap keep a run finite; the
  report tells you what was left untested.

## Layout

```
chrome-extension/
  core.js            shared page logic: questions, options, answers, end states
  report-core.js     shared report rendering (Markdown + Mermaid)
  manifest.json      MV3 extension
  background.js      run queue, breadth-first branch expansion, trace storage
  content.js         answers one page, then advances
  popup.html/.js     start/stop, config, downloads
dist/console-snippet.js   built: core.js + console API (npm run build:snippet)
explore.mjs          pathway discovery CLI
run-paths.mjs        scripted scenario CLI (CI-friendly exit code)
report.mjs           traces -> REPORT.md (also reads extension exports)
selftest.mjs         CLI end-to-end check against the mock
selftest-browser.mjs extension + snippet end-to-end check in a real Chromium
lib/                 Playwright glue (page injection, answering, one traversal)
mock/server.mjs      local branching survey for offline development
```
