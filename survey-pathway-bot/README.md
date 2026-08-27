# Survey pathway bot

Automated branching-logic testing for hosted surveys. It walks a survey in a
real browser, answers every question it finds, and maps which pages, questions
and end states (complete / screen-out / quota) each combination of answers
leads to.

Two ways to use it:

| Mode | Command | Use it for |
|---|---|---|
| **Explore** — discover pathways | `node explore.mjs --url "<link>"` | "What routes exist? Which options were never testable? Does anything dead-end?" |
| **Scripted** — assert pathways | `node run-paths.mjs --url "<link>" --paths paths.json` | "Under-18 must terminate; non-buyers must skip Q7." Exits non-zero on failure, so it drops into CI. |

Both produce JSON traces plus a Markdown report with a Mermaid flow map,
per-option coverage, and a findings list.

> Point this at a **test/preview link for a survey you own or are authorised to
> QA**. Driving a live, in-field link puts fake interviews into real sample and
> burns respondent entries.

## Install

```bash
cd survey-pathway-bot
npm install                       # playwright
npx playwright install chromium   # skip if a Chromium is already provisioned
```

## Try it on the bundled mock first

`mock/server.mjs` is a small branching survey (screen-out, quota, a
conditionally-shown page) that renders the same DOM shape hosted survey engines
do. It is the fastest way to see the output format and to sanity-check config
changes offline:

```bash
node selftest.mjs                     # spins up the mock, explores it, runs the scripted paths
node mock/server.mjs &                # or drive it by hand on :8099
node explore.mjs --url http://127.0.0.1:8099/ --out ./out --max-runs 14
```

## Explore mode

```bash
node explore.mjs \
  --url "https://survey-host.example/survey/selfserve/abc/g123" \
  --config config.json \
  --out ./out \
  --max-runs 40 \
  --screenshots \
  --delay 800
```

Run 1 takes the first option at every question. Each later run replays a
previous run's answers up to one decision, flips that decision, and continues —
breadth-first, so screener logic (where most branching lives) is covered first.
`--max-runs` caps the work; the report says how many branches were left untried.

Output:

```
out/
  runs/run-001.json     every page, question, option and answer of one traversal
  screenshots/          full-page PNGs (with --screenshots)
  summary.json
  REPORT.md             outcomes · traversal table · pathway map · coverage · findings
```

Re-render the report from existing traces with `node report.mjs ./out`.

Sample output from the mock survey: [`examples/mock-report.md`](examples/mock-report.md)
and [`examples/mock-paths.md`](examples/mock-paths.md).

## Scripted mode

`paths.json` pins answers and asserts what should happen:

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
`maxsteps` / `error`), `sees` and `notSees` (regexes matched against the
question names shown), `textContains` (regex against the end page), and
`maxPages`. See `paths.example.json` — it runs against the mock and passes.

## Config reference (`config.example.json`)

| Key | Meaning |
|---|---|
| `answers[]` | Rules applied in order, first match wins. `match` is a regex tested against the question's `name` **and** its wording. |
| `answers[].fixed` | Always choose the option matching this regex (no branching here). |
| `answers[].options` | Only branch across options matching this regex. |
| `answers[].value` / `values[]` | Text/number answer, or several values to branch across. |
| `answers[].skip` | Leave this checkbox unticked. |
| `branchOn` / `noBranch` | Regexes deciding which questions are allowed to branch at all. Everything else takes its first option — the main lever for keeping run counts sane. |
| `maxOptionsPerQuestion` | Try at most N options per question (e.g. 3 of a 10-point scale). |
| `values` | Defaults per input type (`text`, `textarea`, `number`). |
| `maxRuns`, `maxSteps`, `stepTimeout`, `delay` | Budget and pacing. |

Anchor your regexes (`"^18"`, not `"18"`) — `"18"` also matches "Under 18".

## How it finds questions

`lib/extract.mjs` groups the visible form controls on each page by their `name`
attribute, which is how every hosted engine (Decipher/Forsta, Qualtrics,
Confirmit, Alchemer, SurveyMonkey) renders radios, checkboxes, dropdowns, grids
and open ends — so nothing is hard-coded to one platform. Grid rows come out as
separate questions (`Q2r1`, `Q2r2`), which is exactly what you want for coverage.
Question wording, option labels, the forward button and end-state detection are
all selector/keyword driven and overridable via `selectors` in the config.

A standalone checkbox is treated as a two-way branch (ticked / deliberately left
blank), because that is usually where "did you buy any of these" skip logic
hangs.

## Practical notes

- **Check the platform's own tooling first.** Most enterprise survey platforms
  (including the Decipher/Forsta engine behind `*.dynata.com/survey/selfserve/…`
  links) ship a QA harness: preview/test links that can be re-entered, a flow or
  logic map, and a "generate test data" feature that fires N random completes.
  If your project has that, use it for bulk data and use this bot for the parts
  it does not do — asserting specific routes in CI, screenshots per page, and a
  coverage list of options never exercised.
- **Pacing.** Use `--delay` (and `--max-runs`) rather than hammering the host;
  some platforms enforce minimum page times and will flag or drop suspiciously
  fast interviews.
- **Re-entry.** Test links normally allow repeat entries; live links usually do
  not, and a run that dies mid-interview can leave a partial in the data.
- **Quotas move.** A pathway that hit `complete` yesterday can hit `quota` today.
  Assert `quota` only where you mean to.
- **Exotic widgets.** Sliders, drag-and-drop ranking, card sorts and canvas-based
  questions are not plain form controls; the bot records them but cannot answer
  them. Extend `lib/answer.mjs` if your survey uses them.
- **Traps.** Attention checks and red-herring items ("select 'Gamma' here") will
  be answered mechanically and can route the bot to a terminate — pin them with
  a `fixed` rule.
- **Combinatorics.** Full coverage is exponential in the number of questions.
  `branchOn`, `maxOptionsPerQuestion` and `--max-runs` are how you keep a run
  finite; the report tells you what was left untested.

## Layout

```
explore.mjs        pathway discovery CLI
run-paths.mjs      scripted scenario CLI (CI-friendly exit code)
report.mjs         traces -> REPORT.md (also a standalone CLI)
selftest.mjs       end-to-end check against the mock
lib/extract.mjs    page model: questions, options, next button, end states
lib/answer.mjs     candidate answers per question, and applying one
lib/run.mjs        one traversal, driven by a replayable plan
lib/browser.mjs    Chromium launch helper
mock/server.mjs    local branching survey for offline development
```
