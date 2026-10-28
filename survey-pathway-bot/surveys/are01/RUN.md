# Running the bot through the ARE01 / COSM consumer survey (v8)

Each path is one walk through the survey in its own session (the survey has a CAPTCHA, so it cannot restart itself).
For each path:

1. Open the survey link in a fresh Chrome window (an incognito window is simplest — a used session resumes where it stopped).
2. Click past the intro and tick the CAPTCHA, so you are on the first question.
3. Open DevTools → Console, paste the whole of `dist/console-snippet.js`, press Enter. It prints its build stamp.
4. Paste the path's block below and press Enter. A small panel shows the walk; leave the tab in front until it finishes.
5. When it ends, two files download: the report (`…-REPORT.md`) and the full traces (`…-traces.json`). Send me both —
   the traces are what wording / formatting QA needs.

If a page stalls, run `spb.debug()` and send me what it prints, plus the page's HTML if you can.

## Paths

| Path | Who it plays | Opens | Closes |
|---|---|---|---|
| P1 | Cosm visitor, says yes to everything | Q15, Q16, Q18-Q23, Q25-Q28, Q30-Q35, Q36-Q44, Q46-Q59, Q61, Q63, Q67-Q76, Q79-Q90, Q92, Q93, Q97-Q99 | Q45 |
| P2 | Knows Cosm, never been, not interested | Q15, Q16, Q18, Q19, Q34, Q36, Q37, Q39, Q41-Q45, Q50-Q59, Q62, Q64-Q66, Q77, Q78, Q91 | Q20, Q21, Q30-Q33, Q35, Q38, Q40, Q46-Q49, Q61, Q63, Q67-Q76, Q79-Q90, Q92, Q93, Q97-Q99 |
| P3 | New to these venues, Dome only (boundary answers) | Q24, Q29, Q30, Q31, Q60-Q67, Q69, Q71, Q74-Q87, Q89, Q91, Q92, Q93, Q97-Q99 | Q15, Q16, Q18-Q23, Q25-Q28, Q32-Q59, Q68, Q70, Q72, Q73, Q88, Q90 |
| P4 | Cosm visitor, Hall only, boundary answers | Q15, Q16, Q18, Q19, Q20, Q36, Q37, Q39, Q41-Q44, Q46, Q49, Q50-Q58, Q60-Q66, Q68, Q70, Q72, Q73, Q87, Q88, Q89, Q90, Q92 | Q21, Q30-Q35, Q38, Q40, Q45, Q47, Q48, Q59, Q67, Q69, Q71, Q93 |

### P1 — Cosm visitor, says yes to everything

Opens every gate: Cosm + Sphere venue loops, Cosm-visitor block (Q46-49), sports/bar/in-person follow-ups, premium formats, all three Cosm spaces, Dome + Hall content, sports leagues, Cosm Club, merchandise, event hosting.

```js
// ARE01 P1: Cosm visitor, says yes to everything
spb.explore({ maxRuns: 1, config: {
  delay: 400,
  maxSteps: 400,
  answers: [
    {"match": "are\\W+you\\W+aware\\W+of", "_q": "Q13, Q14", "fixed": "^\\s*(Cosm|AMC Entertainment|Sphere|Topgolf)\\b", "limit": 2},
    {"match": "have\\W+you\\W+ever\\W+attended", "_q": "Q15", "fixed": "^\\s*(Cosm|Sphere)\\b", "limit": 2},
    {"match": "out\\W+of\\W+home\\W+entertainment\\W+activities\\W+have\\W+you\\W+participated", "_q": "Q17", "fixed": "live sports in person|sports at a bar|movies at a movie theater", "limit": 3},
    {"match": "ways\\W+have\\W+you\\W+watched\\W+sports", "_q": "Q30", "fixed": "bar or restaurant|stadium or arena", "limit": 2},
    {"match": "watched\\W+a\\W+movie\\W+in\\W+any\\W+of\\W+the\\W+following\\W+premium", "_q": "Q34", "fixed": "^\\s*IMAX\\b"},
    {"match": "total\\W+have\\W+you\\W+visited[\\s\\S]*\\bCosm\\b", "_q": "Q37 Cosm row", "fixed": "\\b(?:2|two)\\W+(?:to\\W+)?(?:3|three)\\b"},
    {"match": "total\\W+have\\W+you\\W+visited[\\s\\S]*\\bSphere\\b", "_q": "Q37 Sphere row", "fixed": "^\\s*Once\\b"},
    {"match": "visit\\W+each\\W+of\\W+the\\W+following\\W+again[\\s\\S]*\\bSphere\\b", "_q": "Q39 Sphere row", "fixed": "Not at all likely"},
    {"match": "past\\W+visits\\W+to\\W+Cosm\\W+replaced", "_q": "Q46", "fixed": "live sports in person|movies at a movie theater", "limit": 2},
    {"match": "types\\W+of\\W+content\\W+would\\W+you\\W+be\\W+interested\\W+in\\W+viewing", "_q": "Q67, Q68", "fixed": "my local team|New\\W*release\\W+movies|Live concert simulcasts|Performing arts", "limit": 4},
    {"match": "\\bvegetable\\b", "_q": "AC1", "fixed": "^\\s*Broccoli\\s*$"},
    {"match": "\\bnumber\\W+(?:four|4)\\b|paying\\W+attention|select\\W+(?:the\\W+)?(?:number\\W+)?(?:four|4)\\b", "_q": "AC2", "fixed": "^\\s*(?:4|four)\\s*$"},
    {"match": "\\ban?\\W+animal\\b", "_q": "AC3", "fixed": "^\\s*Dog\\s*$"},
    {"match": "What\\W+is\\W+your\\W+age", "_q": "Q1", "fixed": "\\b35\\b|^\\s*(?:2[5-9]|3\\d|4\\d)\\s*(?:-|–|to\\b)"},
    {"match": "What\\W+is\\W+your\\W+gender", "_q": "Q2", "options": "^\\s*(?:Male|Female|Other)\\s*$"},
    {"match": "state\\W+do\\W+you\\W+currently\\W+reside", "_q": "Q3", "fixed": "^\\s*California\\s*$"},
    {"match": "\\bzip|postal\\W*code", "_q": "Q4", "value": "90301"},
    {"match": "annual\\W+household\\W+income", "_q": "Q5", "fixed": "75,000"},
    {"match": "how\\W+much\\W+was\\W+spent\\W+per\\W+person", "_q": "Q21", "value": 25},
    {"match": "willing\\W+to\\W+pay\\W+per\\W+person\\W+to\\W+attend", "_q": "Q83, Q99", "skip": true, "value": 40},
    {"match": "willing\\W+to\\W+spend\\W+per\\W+person\\W+on\\W+food", "_q": "Q84", "fixed": "Amount\\W+per\\b", "value": 20},
    {"match": "Cosm\\W+Club\\W+is\\W+an\\W+annual\\W+membership", "_q": "Q88", "fixed": "Amount\\W+per\\b", "value": 120},
    {"match": "^\\s*(?:Q\\d[\\w.-]*\\s*)?(?:I\\W+would\\W+not\\W+(?:attend\\W+at\\W+any\\W+price|spend\\W+money\\W+on\\W+this|pay\\W+for\\W+this\\W+membership)\\b|$)", "_q": "Q83/Q84/Q88/Q99 'I would not …' box built as a question with no stem", "skip": true},
  ]
} }).then(() => { spb.download('ARE01-P1-REPORT.md'); spb.saveTraces('ARE01-P1-traces.json'); });
```

### P2 — Knows Cosm, never been, not interested

The 'no' side of every big gate: aware of Cosm but never visited (Q45); goes to movies but never in a premium format (Q35 closed on its own gate); someone else paid for every activity (Q20 closed on its own gate); not a sports fan; venues visited once and unlikely to return; not interested in Cosm; no substitutes; no event planning.

```js
// ARE01 P2: Knows Cosm, never been, not interested
spb.explore({ maxRuns: 1, config: {
  delay: 400,
  maxSteps: 400,
  answers: [
    {"match": "are\\W+you\\W+aware\\W+of", "_q": "Q13, Q14", "fixed": "^\\s*(Cosm|Cinemark|Meow Wolf)\\b", "limit": 2},
    {"match": "have\\W+you\\W+ever\\W+attended", "_q": "Q15", "fixed": "^\\s*(Cinemark|Meow Wolf)\\b", "limit": 2},
    {"match": "out\\W+of\\W+home\\W+entertainment\\W+activities\\W+have\\W+you\\W+participated", "_q": "Q17", "fixed": "live music events|interactive or themed exhibits|movies at a movie theater", "limit": 3},
    {"match": "who\\W+paid\\W+for\\W+you\\W+to\\W+attend", "_q": "Q19 (every row)", "fixed": "^\\s*My company"},
    {"match": "watched\\W+a\\W+movie\\W+in\\W+any\\W+of\\W+the\\W+following\\W+premium", "_q": "Q34", "fixed": "have not watched a movie in a premium|^\\s*N/A"},
    {"match": "level\\W+of\\W+fandom", "_q": "Q29 (every row)", "fixed": "^\\s*Not a fan"},
    {"match": "total\\W+have\\W+you\\W+visited", "_q": "Q37 (every row)", "fixed": "^\\s*Once\\b"},
    {"match": "visit\\W+each\\W+of\\W+the\\W+following\\W+again", "_q": "Q39 (every row)", "fixed": "Not at all likely"},
    {"match": "interested\\W+are\\W+you\\W+in\\W+attending\\W+Cosm", "_q": "Q60", "fixed": "Not at all interested"},
    {"match": "likely\\W+would\\W+you\\W+be\\W+to\\W+visit\\W+each\\W+of\\W+the\\W+following\\W+spaces", "_q": "Q62 (every row)", "fixed": "Not at all likely"},
    {"match": "substitutes\\W+for\\W+going\\W+to\\W+Cosm", "_q": "Q78", "fixed": "^\\s*None of the above"},
    {"match": "involved\\W+in\\W+planning", "_q": "Q91", "fixed": "^\\s*No\\b"},
    {"match": "\\bvegetable\\b", "_q": "AC1", "fixed": "^\\s*Broccoli\\s*$"},
    {"match": "\\bnumber\\W+(?:four|4)\\b|paying\\W+attention|select\\W+(?:the\\W+)?(?:number\\W+)?(?:four|4)\\b", "_q": "AC2", "fixed": "^\\s*(?:4|four)\\s*$"},
    {"match": "\\ban?\\W+animal\\b", "_q": "AC3", "fixed": "^\\s*Dog\\s*$"},
    {"match": "What\\W+is\\W+your\\W+age", "_q": "Q1", "fixed": "\\b35\\b|^\\s*(?:2[5-9]|3\\d|4\\d)\\s*(?:-|–|to\\b)"},
    {"match": "What\\W+is\\W+your\\W+gender", "_q": "Q2", "options": "^\\s*(?:Male|Female|Other)\\s*$"},
    {"match": "state\\W+do\\W+you\\W+currently\\W+reside", "_q": "Q3", "fixed": "^\\s*California\\s*$"},
    {"match": "\\bzip|postal\\W*code", "_q": "Q4", "value": "90301"},
    {"match": "annual\\W+household\\W+income", "_q": "Q5", "fixed": "75,000"},
    {"match": "how\\W+much\\W+was\\W+spent\\W+per\\W+person", "_q": "Q21", "value": 25},
    {"match": "willing\\W+to\\W+pay\\W+per\\W+person\\W+to\\W+attend", "_q": "Q83, Q99", "skip": true, "value": 40},
    {"match": "willing\\W+to\\W+spend\\W+per\\W+person\\W+on\\W+food", "_q": "Q84", "fixed": "Amount\\W+per\\b", "value": 20},
    {"match": "Cosm\\W+Club\\W+is\\W+an\\W+annual\\W+membership", "_q": "Q88", "fixed": "Amount\\W+per\\b", "value": 120},
    {"match": "^\\s*(?:Q\\d[\\w.-]*\\s*)?(?:I\\W+would\\W+not\\W+(?:attend\\W+at\\W+any\\W+price|spend\\W+money\\W+on\\W+this|pay\\W+for\\W+this\\W+membership)\\b|$)", "_q": "Q83/Q84/Q88/Q99 'I would not …' box built as a question with no stem", "skip": true},
  ]
} }).then(() => { spb.download('ARE01-P2-REPORT.md'); spb.saveTraces('ARE01-P2-traces.json'); });
```

### P3 — New to these venues, Dome only (boundary answers)

Partial gates: no venue awareness (whole venue deep-dive skipped), no out-of-home activities, fan who only watches at home, only slightly likely to visit the Dome but not the Hall or Deck, movie/concert content only (no sports leagues), no Cosm Club, no merchandise, private events only — 'Slightly' answers test that the a-d gates include d.

```js
// ARE01 P3: New to these venues, Dome only (boundary answers)
spb.explore({ maxRuns: 1, config: {
  delay: 400,
  maxSteps: 400,
  answers: [
    {"match": "are\\W+you\\W+aware\\W+of", "_q": "Q13, Q14", "fixed": "^\\s*None of the above"},
    {"match": "out\\W+of\\W+home\\W+entertainment\\W+activities\\W+have\\W+you\\W+participated", "_q": "Q17", "fixed": "^\\s*None of the above"},
    {"match": "ways\\W+have\\W+you\\W+watched\\W+sports", "_q": "Q30", "fixed": "^\\s*At home"},
    {"match": "likely\\W+would\\W+you\\W+be\\W+to\\W+visit\\W+each\\W+of\\W+the\\W+following\\W+spaces[\\s\\S]*The\\W+(Hall|Deck)\\b", "_q": "Q62 Hall + Deck rows", "fixed": "Not at all likely"},
    {"match": "types\\W+of\\W+content\\W+would\\W+you\\W+be\\W+interested\\W+in\\W+viewing", "_q": "Q67", "fixed": "New\\W*release\\W+movies|Recorded concerts", "limit": 2},
    {"match": "ways\\W+to\\W+purchase\\W+tickets[\\s\\S]*Annual\\W+membership", "_q": "Q87 annual-membership row", "fixed": "Not at all interested"},
    {"match": "purchasing\\W+merchandise", "_q": "Q89", "fixed": "Not at all interested"},
    {"match": "involved\\W+in\\W+planning", "_q": "Q91", "fixed": "^\\s*Yes\\b[\\s\\S]*private\\W+event"},
    {"match": "likely\\W+would\\W+you\\W+be\\W+to\\W+visit\\W+each\\W+of\\W+the\\W+following\\W+spaces[\\s\\S]*The\\W+Dome\\b", "_q": "Q62 Dome row (tests the a-d boundary)", "fixed": "Slightly likely"},
    {"match": "hosting\\W+a\\W+corporate\\W+or\\W+private\\W+event", "_q": "Q92 (tests the a-d boundary)", "fixed": "Slightly interested"},
    {"match": "\\bvegetable\\b", "_q": "AC1", "fixed": "^\\s*Broccoli\\s*$"},
    {"match": "\\bnumber\\W+(?:four|4)\\b|paying\\W+attention|select\\W+(?:the\\W+)?(?:number\\W+)?(?:four|4)\\b", "_q": "AC2", "fixed": "^\\s*(?:4|four)\\s*$"},
    {"match": "\\ban?\\W+animal\\b", "_q": "AC3", "fixed": "^\\s*Dog\\s*$"},
    {"match": "What\\W+is\\W+your\\W+age", "_q": "Q1", "fixed": "\\b35\\b|^\\s*(?:2[5-9]|3\\d|4\\d)\\s*(?:-|–|to\\b)"},
    {"match": "What\\W+is\\W+your\\W+gender", "_q": "Q2", "options": "^\\s*(?:Male|Female|Other)\\s*$"},
    {"match": "state\\W+do\\W+you\\W+currently\\W+reside", "_q": "Q3", "fixed": "^\\s*California\\s*$"},
    {"match": "\\bzip|postal\\W*code", "_q": "Q4", "value": "90301"},
    {"match": "annual\\W+household\\W+income", "_q": "Q5", "fixed": "75,000"},
    {"match": "how\\W+much\\W+was\\W+spent\\W+per\\W+person", "_q": "Q21", "value": 25},
    {"match": "willing\\W+to\\W+pay\\W+per\\W+person\\W+to\\W+attend", "_q": "Q83, Q99", "skip": true, "value": 40},
    {"match": "willing\\W+to\\W+spend\\W+per\\W+person\\W+on\\W+food", "_q": "Q84", "fixed": "Amount\\W+per\\b", "value": 20},
    {"match": "Cosm\\W+Club\\W+is\\W+an\\W+annual\\W+membership", "_q": "Q88", "fixed": "Amount\\W+per\\b", "value": 120},
    {"match": "^\\s*(?:Q\\d[\\w.-]*\\s*)?(?:I\\W+would\\W+not\\W+(?:attend\\W+at\\W+any\\W+price|spend\\W+money\\W+on\\W+this|pay\\W+for\\W+this\\W+membership)\\b|$)", "_q": "Q83/Q84/Q88/Q99 'I would not …' box built as a question with no stem", "skip": true},
  ]
} }).then(() => { spb.download('ARE01-P3-REPORT.md'); spb.saveTraces('ARE01-P3-traces.json'); });
```

### P4 — Cosm visitor, Hall only, boundary answers

Cosm visitor whose past visits replaced game/activity venues — the only path that exercises Q47's 'g not selected in Q46' clause, Q48's a-e gate and Q59 being skipped while their parents are on screen; likely to visit only the Hall, so Q68/Q70/Q72 show and Q67/Q69/Q71 do not, and Q73 opens from Q72; rooftop-bar goer who personally pays but spends on nothing (Q21 closed on its own gate); 'Slightly …' answers on Q60, Q87 annual membership and Q89 test the a-d boundary; not interested in hosting events (Q93 closed while Q92 is shown).

```js
// ARE01 P4: Cosm visitor, Hall only, boundary answers
spb.explore({ maxRuns: 1, config: {
  delay: 400,
  maxSteps: 400,
  answers: [
    {"match": "are\\W+you\\W+aware\\W+of", "_q": "Q13, Q14", "fixed": "^\\s*(Cosm|None of the above)\\b"},
    {"match": "have\\W+you\\W+ever\\W+attended", "_q": "Q15", "fixed": "^\\s*Cosm\\b"},
    {"match": "out\\W+of\\W+home\\W+entertainment\\W+activities\\W+have\\W+you\\W+participated", "_q": "Q17", "fixed": "rooftop bar"},
    {"match": "personally\\W+spend\\W+money\\W+on", "_q": "Q20 (every row)", "fixed": "I do not typically spend"},
    {"match": "level\\W+of\\W+fandom", "_q": "Q29 (every row)", "fixed": "^\\s*Not a fan"},
    {"match": "past\\W+visits\\W+to\\W+Cosm\\W+replaced", "_q": "Q46", "fixed": "game or activity venues"},
    {"match": "interested\\W+are\\W+you\\W+in\\W+attending\\W+Cosm", "_q": "Q60 (tests the a-d boundary)", "fixed": "Slightly interested"},
    {"match": "likely\\W+would\\W+you\\W+be\\W+to\\W+visit\\W+each\\W+of\\W+the\\W+following\\W+spaces[\\s\\S]*The\\W+(Dome|Deck)\\b", "_q": "Q62 Dome + Deck rows", "fixed": "Not at all likely"},
    {"match": "types\\W+of\\W+content\\W+would\\W+you\\W+be\\W+interested\\W+in\\W+viewing", "_q": "Q68", "fixed": "teams outside|Esports", "limit": 2},
    {"match": "ways\\W+to\\W+purchase\\W+tickets[\\s\\S]*Annual\\W+membership", "_q": "Q87 annual-membership row (tests the a-d boundary)", "fixed": "Slightly interested"},
    {"match": "purchasing\\W+merchandise", "_q": "Q89 (tests the a-d boundary)", "fixed": "Slightly interested"},
    {"match": "hosting\\W+a\\W+corporate\\W+or\\W+private\\W+event", "_q": "Q92 (closes Q93 while Q92 is shown)", "fixed": "Not at all interested"},
    {"match": "\\bvegetable\\b", "_q": "AC1", "fixed": "^\\s*Broccoli\\s*$"},
    {"match": "\\bnumber\\W+(?:four|4)\\b|paying\\W+attention|select\\W+(?:the\\W+)?(?:number\\W+)?(?:four|4)\\b", "_q": "AC2", "fixed": "^\\s*(?:4|four)\\s*$"},
    {"match": "\\ban?\\W+animal\\b", "_q": "AC3", "fixed": "^\\s*Dog\\s*$"},
    {"match": "What\\W+is\\W+your\\W+age", "_q": "Q1", "fixed": "\\b35\\b|^\\s*(?:2[5-9]|3\\d|4\\d)\\s*(?:-|–|to\\b)"},
    {"match": "What\\W+is\\W+your\\W+gender", "_q": "Q2", "options": "^\\s*(?:Male|Female|Other)\\s*$"},
    {"match": "state\\W+do\\W+you\\W+currently\\W+reside", "_q": "Q3", "fixed": "^\\s*California\\s*$"},
    {"match": "\\bzip|postal\\W*code", "_q": "Q4", "value": "90301"},
    {"match": "annual\\W+household\\W+income", "_q": "Q5", "fixed": "75,000"},
    {"match": "how\\W+much\\W+was\\W+spent\\W+per\\W+person", "_q": "Q21", "value": 25},
    {"match": "willing\\W+to\\W+pay\\W+per\\W+person\\W+to\\W+attend", "_q": "Q83, Q99", "skip": true, "value": 40},
    {"match": "willing\\W+to\\W+spend\\W+per\\W+person\\W+on\\W+food", "_q": "Q84", "fixed": "Amount\\W+per\\b", "value": 20},
    {"match": "Cosm\\W+Club\\W+is\\W+an\\W+annual\\W+membership", "_q": "Q88", "fixed": "Amount\\W+per\\b", "value": 120},
    {"match": "^\\s*(?:Q\\d[\\w.-]*\\s*)?(?:I\\W+would\\W+not\\W+(?:attend\\W+at\\W+any\\W+price|spend\\W+money\\W+on\\W+this|pay\\W+for\\W+this\\W+membership)\\b|$)", "_q": "Q83/Q84/Q88/Q99 'I would not …' box built as a question with no stem", "skip": true},
  ]
} }).then(() => { spb.download('ARE01-P4-REPORT.md'); spb.saveTraces('ARE01-P4-traces.json'); });
```

## Terminate spot-checks (optional)

Each confirms one screen-out fires. Same steps as above; the walk should end on the screen-out page within the first few pages. These need a fresh session each, so do them only if you want them on record.

**Q1 → Under 18 (or any age below 18)**

```js
// ARE01 terminate check: Q1 = Under 18 (or any age below 18)
spb.explore({ maxRuns: 1, config: {
  delay: 400,
  maxSteps: 400,
  answers: [
    {"match": "What\\W+is\\W+your\\W+age", "fixed": "\\bunder\\b|younger|less than|below|<\\s*18|^\\s*\\d{1,2}\\s*[-–]\\s*17\\b|^\\s*(1[0-7]|[0-9])\\b(?!\\s*[-–+])", "_q": "Q1 — should terminate"},
    {"match": "\\bvegetable\\b", "_q": "AC1", "fixed": "^\\s*Broccoli\\s*$"},
    {"match": "\\bnumber\\W+(?:four|4)\\b|paying\\W+attention|select\\W+(?:the\\W+)?(?:number\\W+)?(?:four|4)\\b", "_q": "AC2", "fixed": "^\\s*(?:4|four)\\s*$"},
    {"match": "\\ban?\\W+animal\\b", "_q": "AC3", "fixed": "^\\s*Dog\\s*$"},
    {"match": "What\\W+is\\W+your\\W+age", "_q": "Q1", "fixed": "\\b35\\b|^\\s*(?:2[5-9]|3\\d|4\\d)\\s*(?:-|–|to\\b)"},
    {"match": "What\\W+is\\W+your\\W+gender", "_q": "Q2", "options": "^\\s*(?:Male|Female|Other)\\s*$"},
    {"match": "state\\W+do\\W+you\\W+currently\\W+reside", "_q": "Q3", "fixed": "^\\s*California\\s*$"},
    {"match": "\\bzip|postal\\W*code", "_q": "Q4", "value": "90301"},
    {"match": "annual\\W+household\\W+income", "_q": "Q5", "fixed": "75,000"},
    {"match": "how\\W+much\\W+was\\W+spent\\W+per\\W+person", "_q": "Q21", "value": 25},
    {"match": "willing\\W+to\\W+pay\\W+per\\W+person\\W+to\\W+attend", "_q": "Q83, Q99", "skip": true, "value": 40},
    {"match": "willing\\W+to\\W+spend\\W+per\\W+person\\W+on\\W+food", "_q": "Q84", "fixed": "Amount\\W+per\\b", "value": 20},
    {"match": "Cosm\\W+Club\\W+is\\W+an\\W+annual\\W+membership", "_q": "Q88", "fixed": "Amount\\W+per\\b", "value": 120},
    {"match": "^\\s*(?:Q\\d[\\w.-]*\\s*)?(?:I\\W+would\\W+not\\W+(?:attend\\W+at\\W+any\\W+price|spend\\W+money\\W+on\\W+this|pay\\W+for\\W+this\\W+membership)\\b|$)", "_q": "Q83/Q84/Q88/Q99 'I would not …' box built as a question with no stem", "skip": true},
  ]
} }).then(() => { spb.download('ARE01-terminate-Q1-REPORT.md'); });
```

**Q2 → Prefer not to answer**

```js
// ARE01 terminate check: Q2 = Prefer not to answer
spb.explore({ maxRuns: 1, config: {
  delay: 400,
  maxSteps: 400,
  answers: [
    {"match": "What\\W+is\\W+your\\W+gender", "fixed": "Prefer not", "_q": "Q2 — should terminate"},
    {"match": "\\bvegetable\\b", "_q": "AC1", "fixed": "^\\s*Broccoli\\s*$"},
    {"match": "\\bnumber\\W+(?:four|4)\\b|paying\\W+attention|select\\W+(?:the\\W+)?(?:number\\W+)?(?:four|4)\\b", "_q": "AC2", "fixed": "^\\s*(?:4|four)\\s*$"},
    {"match": "\\ban?\\W+animal\\b", "_q": "AC3", "fixed": "^\\s*Dog\\s*$"},
    {"match": "What\\W+is\\W+your\\W+age", "_q": "Q1", "fixed": "\\b35\\b|^\\s*(?:2[5-9]|3\\d|4\\d)\\s*(?:-|–|to\\b)"},
    {"match": "What\\W+is\\W+your\\W+gender", "_q": "Q2", "options": "^\\s*(?:Male|Female|Other)\\s*$"},
    {"match": "state\\W+do\\W+you\\W+currently\\W+reside", "_q": "Q3", "fixed": "^\\s*California\\s*$"},
    {"match": "\\bzip|postal\\W*code", "_q": "Q4", "value": "90301"},
    {"match": "annual\\W+household\\W+income", "_q": "Q5", "fixed": "75,000"},
    {"match": "how\\W+much\\W+was\\W+spent\\W+per\\W+person", "_q": "Q21", "value": 25},
    {"match": "willing\\W+to\\W+pay\\W+per\\W+person\\W+to\\W+attend", "_q": "Q83, Q99", "skip": true, "value": 40},
    {"match": "willing\\W+to\\W+spend\\W+per\\W+person\\W+on\\W+food", "_q": "Q84", "fixed": "Amount\\W+per\\b", "value": 20},
    {"match": "Cosm\\W+Club\\W+is\\W+an\\W+annual\\W+membership", "_q": "Q88", "fixed": "Amount\\W+per\\b", "value": 120},
    {"match": "^\\s*(?:Q\\d[\\w.-]*\\s*)?(?:I\\W+would\\W+not\\W+(?:attend\\W+at\\W+any\\W+price|spend\\W+money\\W+on\\W+this|pay\\W+for\\W+this\\W+membership)\\b|$)", "_q": "Q83/Q84/Q88/Q99 'I would not …' box built as a question with no stem", "skip": true},
  ]
} }).then(() => { spb.download('ARE01-terminate-Q2-REPORT.md'); });
```

**Q3 → I do not live in the United States**

```js
// ARE01 terminate check: Q3 = I do not live in the United States
spb.explore({ maxRuns: 1, config: {
  delay: 400,
  maxSteps: 400,
  answers: [
    {"match": "state\\W+do\\W+you\\W+currently\\W+reside", "fixed": "do not live", "_q": "Q3 — should terminate"},
    {"match": "\\bvegetable\\b", "_q": "AC1", "fixed": "^\\s*Broccoli\\s*$"},
    {"match": "\\bnumber\\W+(?:four|4)\\b|paying\\W+attention|select\\W+(?:the\\W+)?(?:number\\W+)?(?:four|4)\\b", "_q": "AC2", "fixed": "^\\s*(?:4|four)\\s*$"},
    {"match": "\\ban?\\W+animal\\b", "_q": "AC3", "fixed": "^\\s*Dog\\s*$"},
    {"match": "What\\W+is\\W+your\\W+age", "_q": "Q1", "fixed": "\\b35\\b|^\\s*(?:2[5-9]|3\\d|4\\d)\\s*(?:-|–|to\\b)"},
    {"match": "What\\W+is\\W+your\\W+gender", "_q": "Q2", "options": "^\\s*(?:Male|Female|Other)\\s*$"},
    {"match": "state\\W+do\\W+you\\W+currently\\W+reside", "_q": "Q3", "fixed": "^\\s*California\\s*$"},
    {"match": "\\bzip|postal\\W*code", "_q": "Q4", "value": "90301"},
    {"match": "annual\\W+household\\W+income", "_q": "Q5", "fixed": "75,000"},
    {"match": "how\\W+much\\W+was\\W+spent\\W+per\\W+person", "_q": "Q21", "value": 25},
    {"match": "willing\\W+to\\W+pay\\W+per\\W+person\\W+to\\W+attend", "_q": "Q83, Q99", "skip": true, "value": 40},
    {"match": "willing\\W+to\\W+spend\\W+per\\W+person\\W+on\\W+food", "_q": "Q84", "fixed": "Amount\\W+per\\b", "value": 20},
    {"match": "Cosm\\W+Club\\W+is\\W+an\\W+annual\\W+membership", "_q": "Q88", "fixed": "Amount\\W+per\\b", "value": 120},
    {"match": "^\\s*(?:Q\\d[\\w.-]*\\s*)?(?:I\\W+would\\W+not\\W+(?:attend\\W+at\\W+any\\W+price|spend\\W+money\\W+on\\W+this|pay\\W+for\\W+this\\W+membership)\\b|$)", "_q": "Q83/Q84/Q88/Q99 'I would not …' box built as a question with no stem", "skip": true},
  ]
} }).then(() => { spb.download('ARE01-terminate-Q3-REPORT.md'); });
```

**Q5 → Prefer not to answer**

```js
// ARE01 terminate check: Q5 = Prefer not to answer
spb.explore({ maxRuns: 1, config: {
  delay: 400,
  maxSteps: 400,
  answers: [
    {"match": "annual\\W+household\\W+income", "fixed": "Prefer not", "_q": "Q5 — should terminate"},
    {"match": "\\bvegetable\\b", "_q": "AC1", "fixed": "^\\s*Broccoli\\s*$"},
    {"match": "\\bnumber\\W+(?:four|4)\\b|paying\\W+attention|select\\W+(?:the\\W+)?(?:number\\W+)?(?:four|4)\\b", "_q": "AC2", "fixed": "^\\s*(?:4|four)\\s*$"},
    {"match": "\\ban?\\W+animal\\b", "_q": "AC3", "fixed": "^\\s*Dog\\s*$"},
    {"match": "What\\W+is\\W+your\\W+age", "_q": "Q1", "fixed": "\\b35\\b|^\\s*(?:2[5-9]|3\\d|4\\d)\\s*(?:-|–|to\\b)"},
    {"match": "What\\W+is\\W+your\\W+gender", "_q": "Q2", "options": "^\\s*(?:Male|Female|Other)\\s*$"},
    {"match": "state\\W+do\\W+you\\W+currently\\W+reside", "_q": "Q3", "fixed": "^\\s*California\\s*$"},
    {"match": "\\bzip|postal\\W*code", "_q": "Q4", "value": "90301"},
    {"match": "annual\\W+household\\W+income", "_q": "Q5", "fixed": "75,000"},
    {"match": "how\\W+much\\W+was\\W+spent\\W+per\\W+person", "_q": "Q21", "value": 25},
    {"match": "willing\\W+to\\W+pay\\W+per\\W+person\\W+to\\W+attend", "_q": "Q83, Q99", "skip": true, "value": 40},
    {"match": "willing\\W+to\\W+spend\\W+per\\W+person\\W+on\\W+food", "_q": "Q84", "fixed": "Amount\\W+per\\b", "value": 20},
    {"match": "Cosm\\W+Club\\W+is\\W+an\\W+annual\\W+membership", "_q": "Q88", "fixed": "Amount\\W+per\\b", "value": 120},
    {"match": "^\\s*(?:Q\\d[\\w.-]*\\s*)?(?:I\\W+would\\W+not\\W+(?:attend\\W+at\\W+any\\W+price|spend\\W+money\\W+on\\W+this|pay\\W+for\\W+this\\W+membership)\\b|$)", "_q": "Q83/Q84/Q88/Q99 'I would not …' box built as a question with no stem", "skip": true},
  ]
} }).then(() => { spb.download('ARE01-terminate-Q5-REPORT.md'); });
```

**AC1 → Egg**

```js
// ARE01 terminate check: AC1 = Egg
spb.explore({ maxRuns: 1, config: {
  delay: 400,
  maxSteps: 400,
  answers: [
    {"match": "\\bvegetable\\b", "fixed": "^Egg$", "_q": "AC1 — should terminate"},
    {"match": "\\bvegetable\\b", "_q": "AC1", "fixed": "^\\s*Broccoli\\s*$"},
    {"match": "\\bnumber\\W+(?:four|4)\\b|paying\\W+attention|select\\W+(?:the\\W+)?(?:number\\W+)?(?:four|4)\\b", "_q": "AC2", "fixed": "^\\s*(?:4|four)\\s*$"},
    {"match": "\\ban?\\W+animal\\b", "_q": "AC3", "fixed": "^\\s*Dog\\s*$"},
    {"match": "What\\W+is\\W+your\\W+age", "_q": "Q1", "fixed": "\\b35\\b|^\\s*(?:2[5-9]|3\\d|4\\d)\\s*(?:-|–|to\\b)"},
    {"match": "What\\W+is\\W+your\\W+gender", "_q": "Q2", "options": "^\\s*(?:Male|Female|Other)\\s*$"},
    {"match": "state\\W+do\\W+you\\W+currently\\W+reside", "_q": "Q3", "fixed": "^\\s*California\\s*$"},
    {"match": "\\bzip|postal\\W*code", "_q": "Q4", "value": "90301"},
    {"match": "annual\\W+household\\W+income", "_q": "Q5", "fixed": "75,000"},
    {"match": "how\\W+much\\W+was\\W+spent\\W+per\\W+person", "_q": "Q21", "value": 25},
    {"match": "willing\\W+to\\W+pay\\W+per\\W+person\\W+to\\W+attend", "_q": "Q83, Q99", "skip": true, "value": 40},
    {"match": "willing\\W+to\\W+spend\\W+per\\W+person\\W+on\\W+food", "_q": "Q84", "fixed": "Amount\\W+per\\b", "value": 20},
    {"match": "Cosm\\W+Club\\W+is\\W+an\\W+annual\\W+membership", "_q": "Q88", "fixed": "Amount\\W+per\\b", "value": 120},
    {"match": "^\\s*(?:Q\\d[\\w.-]*\\s*)?(?:I\\W+would\\W+not\\W+(?:attend\\W+at\\W+any\\W+price|spend\\W+money\\W+on\\W+this|pay\\W+for\\W+this\\W+membership)\\b|$)", "_q": "Q83/Q84/Q88/Q99 'I would not …' box built as a question with no stem", "skip": true},
  ]
} }).then(() => { spb.download('ARE01-terminate-AC1-REPORT.md'); });
```

**AC2 → 44**

```js
// ARE01 terminate check: AC2 = 44
spb.explore({ maxRuns: 1, config: {
  delay: 400,
  maxSteps: 400,
  answers: [
    {"match": "\\bnumber\\W+(?:four|4)\\b|paying\\W+attention|select\\W+(?:the\\W+)?(?:number\\W+)?(?:four|4)\\b", "fixed": "^44$", "_q": "AC2 — should terminate"},
    {"match": "\\bvegetable\\b", "_q": "AC1", "fixed": "^\\s*Broccoli\\s*$"},
    {"match": "\\bnumber\\W+(?:four|4)\\b|paying\\W+attention|select\\W+(?:the\\W+)?(?:number\\W+)?(?:four|4)\\b", "_q": "AC2", "fixed": "^\\s*(?:4|four)\\s*$"},
    {"match": "\\ban?\\W+animal\\b", "_q": "AC3", "fixed": "^\\s*Dog\\s*$"},
    {"match": "What\\W+is\\W+your\\W+age", "_q": "Q1", "fixed": "\\b35\\b|^\\s*(?:2[5-9]|3\\d|4\\d)\\s*(?:-|–|to\\b)"},
    {"match": "What\\W+is\\W+your\\W+gender", "_q": "Q2", "options": "^\\s*(?:Male|Female|Other)\\s*$"},
    {"match": "state\\W+do\\W+you\\W+currently\\W+reside", "_q": "Q3", "fixed": "^\\s*California\\s*$"},
    {"match": "\\bzip|postal\\W*code", "_q": "Q4", "value": "90301"},
    {"match": "annual\\W+household\\W+income", "_q": "Q5", "fixed": "75,000"},
    {"match": "how\\W+much\\W+was\\W+spent\\W+per\\W+person", "_q": "Q21", "value": 25},
    {"match": "willing\\W+to\\W+pay\\W+per\\W+person\\W+to\\W+attend", "_q": "Q83, Q99", "skip": true, "value": 40},
    {"match": "willing\\W+to\\W+spend\\W+per\\W+person\\W+on\\W+food", "_q": "Q84", "fixed": "Amount\\W+per\\b", "value": 20},
    {"match": "Cosm\\W+Club\\W+is\\W+an\\W+annual\\W+membership", "_q": "Q88", "fixed": "Amount\\W+per\\b", "value": 120},
    {"match": "^\\s*(?:Q\\d[\\w.-]*\\s*)?(?:I\\W+would\\W+not\\W+(?:attend\\W+at\\W+any\\W+price|spend\\W+money\\W+on\\W+this|pay\\W+for\\W+this\\W+membership)\\b|$)", "_q": "Q83/Q84/Q88/Q99 'I would not …' box built as a question with no stem", "skip": true},
  ]
} }).then(() => { spb.download('ARE01-terminate-AC2-REPORT.md'); });
```

**AC3 → Chair**

```js
// ARE01 terminate check: AC3 = Chair
spb.explore({ maxRuns: 1, config: {
  delay: 400,
  maxSteps: 400,
  answers: [
    {"match": "\\ban?\\W+animal\\b", "fixed": "^Chair$", "_q": "AC3 — should terminate"},
    {"match": "\\bvegetable\\b", "_q": "AC1", "fixed": "^\\s*Broccoli\\s*$"},
    {"match": "\\bnumber\\W+(?:four|4)\\b|paying\\W+attention|select\\W+(?:the\\W+)?(?:number\\W+)?(?:four|4)\\b", "_q": "AC2", "fixed": "^\\s*(?:4|four)\\s*$"},
    {"match": "\\ban?\\W+animal\\b", "_q": "AC3", "fixed": "^\\s*Dog\\s*$"},
    {"match": "What\\W+is\\W+your\\W+age", "_q": "Q1", "fixed": "\\b35\\b|^\\s*(?:2[5-9]|3\\d|4\\d)\\s*(?:-|–|to\\b)"},
    {"match": "What\\W+is\\W+your\\W+gender", "_q": "Q2", "options": "^\\s*(?:Male|Female|Other)\\s*$"},
    {"match": "state\\W+do\\W+you\\W+currently\\W+reside", "_q": "Q3", "fixed": "^\\s*California\\s*$"},
    {"match": "\\bzip|postal\\W*code", "_q": "Q4", "value": "90301"},
    {"match": "annual\\W+household\\W+income", "_q": "Q5", "fixed": "75,000"},
    {"match": "how\\W+much\\W+was\\W+spent\\W+per\\W+person", "_q": "Q21", "value": 25},
    {"match": "willing\\W+to\\W+pay\\W+per\\W+person\\W+to\\W+attend", "_q": "Q83, Q99", "skip": true, "value": 40},
    {"match": "willing\\W+to\\W+spend\\W+per\\W+person\\W+on\\W+food", "_q": "Q84", "fixed": "Amount\\W+per\\b", "value": 20},
    {"match": "Cosm\\W+Club\\W+is\\W+an\\W+annual\\W+membership", "_q": "Q88", "fixed": "Amount\\W+per\\b", "value": 120},
    {"match": "^\\s*(?:Q\\d[\\w.-]*\\s*)?(?:I\\W+would\\W+not\\W+(?:attend\\W+at\\W+any\\W+price|spend\\W+money\\W+on\\W+this|pay\\W+for\\W+this\\W+membership)\\b|$)", "_q": "Q83/Q84/Q88/Q99 'I would not …' box built as a question with no stem", "skip": true},
  ]
} }).then(() => { spb.download('ARE01-terminate-AC3-REPORT.md'); });
```
