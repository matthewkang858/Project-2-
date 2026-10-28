# Questionnaire audit — ARE01_v8.pdf

102 questions · 261 programmed rules · **0 error(s), 5 warning(s)**

This checks the document against itself — numbering, cross-references, option lettering, emphasis and programmer syntax. Comparing it to the *live* survey is `compare.mjs`, which needs a captured run.

## Questions with issues

| Q | Issue |
|---|---|
| Q9 | warning: option f "Other race" is a catch-all on a multi-punch question but is not tagged [Anchor]/[Exclusive] |
| Q45 | warning: option d "I am not sure what the experience is lik" is a catch-all on a multi-punch question but is not tagged [Anchor]/[Exclusive] |
| Q46 | warning: 12/14 options use underline, but option(s) m, n do not — emphasis is inconsistent within the question |
| Q48 | warning: is shown when a-e is selected in Q46 but populates its rows from a-n selected in Q46 — the gate and the row list disagree |
| Q99 | warning: column b has a stray "i" right after a programmer tag ("…[Exclusive]i") — it may show up in the answer text |

## Every question

| Q | Section | Type | Answers | Shown when | Feeds | Emphasis | Status |
|---|---|---|---|---|---|---|---|
| Q1 | Screeners | SP | 1 options | always |  | bold stem | ok |
| Q2 | Screeners | SP | 4 options | always |  | bold stem | ok |
| Q3 | Screeners | SP | 2 options | always |  | bold stem | ok |
| Q4 | Screeners | SP | 1 options | always |  | bold stem | ok |
| Q5 | Screeners | SP | 10 options | always |  | bold stem | ok |
| Q6 | Screeners | SP | 9 options | always |  | bold stem, underlined stem | ok |
| Q7 | Screeners | SP | 4 options | always |  | bold stem, underlined stem | ok |
| Q8 | Screeners | SP | 3 options | always |  | bold stem | ok |
| Q9 | Screeners | MP | 7 options | always |  | bold stem, underlined stem | warning |
| Q10 | Screeners | SP | 6 options | always |  | bold stem | ok |
| Q11 | Screeners | MP | 5 options | always |  | bold stem, underlined stem, underlined answers | ok |
| Q12 | Awareness & Past Experience | Open | 10 options | always |  | bold stem, underlined stem | ok |
| Q13 | Awareness & Past Experience | MP | 17 options | always | Q15, Q45 | bold stem, underlined stem | ok |
| Q14 | Awareness & Past Experience | MP | 17 options | always | Q15 | bold stem, underlined stem | ok |
| Q15 | Awareness & Past Experience | MP | 29 options | b-j, l-m, or o-p selected in Q13 OR a-k or m-p s | Q16, Q36, Q37, Q39, Q42, Q43, Q44, Q45,  | bold stem, underlined stem | ok |
| Q16 | Awareness & Past Experience | MP | 2 options | a-bb selected in Q15 |  | bold stem, underlined stem | ok |
| Q17 | Out-Of-Home Entertainment Behavior | MP | 12 options | always | Q18, Q19, Q22, Q23, Q25, Q26, Q27, Q28,  | bold stem, underlined stem, underlined answers | ok |
| Q18 | Out-Of-Home Entertainment Behavior | SP | grid 1×6 | a-j selected in Q17 |  | bold stem, underlined stem | ok |
| Q19 | Out-Of-Home Entertainment Behavior | MP | grid 1×3 | a-j selected in Q17 | Q20 | bold stem, underlined stem | ok |
| Q20 | Out-Of-Home Entertainment Behavior | MP | grid 1×5 | a selected for 1+ row in Q19 | Q21 | bold stem, underlined stem | ok |
| Q21 | Out-Of-Home Entertainment Behavior | Numeric | grid 1×4 | a-d selected for 1+ row in Q20 |  | bold stem, underlined stem | ok |
| Q22 | Out-Of-Home Entertainment Behavior | MP | grid 1×10 | a-j selected in Q17 |  | bold stem, underlined stem | ok |
| Q23 | Out-Of-Home Entertainment Behavior | SP | grid 1×6 | a-j selected in Q17 |  | bold stem, underlined stem | ok |
| Q24 | Out-Of-Home Entertainment Behavior | MP | 10 options | always |  | bold stem, underlined stem, underlined answers | ok |
| Q25 | Out-Of-Home Entertainment Behavior | SP | grid 1×6 | a-j selected in Q17 |  | bold stem, underlined stem, underlined answers | ok |
| Q26 | Out-Of-Home Entertainment Behavior | MP | grid 1×13 | a-j selected in Q17 |  | bold stem, underlined stem | ok |
| Q27 | Out-Of-Home Entertainment Behavior | MP | grid 1×8 | a-j selected in Q17 |  | bold stem, underlined stem | ok |
| Q28 | Out-Of-Home Entertainment Behavior | SP | grid 1×2 | a-j selected in Q17 |  | bold stem, underlined stem | ok |
| Q29 | Sports & Movie Behavior | SP | grid 9×3 | always | Q30, Q31 | bold stem, underlined stem | ok |
| Q30 | Sports & Movie Behavior | MP | 5 options | a-b selected for 1+ row in Q29 | Q32, Q33 | bold stem, underlined stem | ok |
| Q31 | Sports & Movie Behavior | SP | grid 1×8 | a-b selected for 1+ row in Q29 |  | bold stem, underlined stem | ok |
| Q32 | Sports & Movie Behavior | MP | 7 options | d selected in Q30 |  | bold stem, underlined stem | ok |
| Q33 | Sports & Movie Behavior | MP | 7 options | c selected in Q30 |  | bold stem, underlined stem | ok |
| Q34 | Sports & Movie Behavior | MP | 6 options | c selected in Q17 | Q35 | bold stem, underlined stem | ok |
| Q35 | Sports & Movie Behavior | SP | 5 options | a-e selected in Q34 |  | bold stem, underlined stem | ok |
| Q36 | Deep Dive On Analog Attendance | SP | grid 1×4 | a-bb selected in Q15 |  | bold stem, underlined stem | ok |
| Q37 | Deep Dive On Analog Attendance | SP | grid 1×5 | a-bb selected in Q15 | Q38, Q40, Q41 | bold stem, underlined stem | ok |
| Q38 | Deep Dive On Analog Attendance | SP | grid 1×5 | b-e selected for 1+ row in Q37 |  | bold stem, underlined stem, underlined answers | ok |
| Q39 | Deep Dive On Analog Attendance | SP | grid 1×5 | a-bb selected in Q15 | Q59 | bold stem, underlined stem | ok |
| Q40 | Deep Dive On Analog Attendance | MP | grid 1×12 | b-e selected for 1+ row in Q37 |  | bold stem, underlined stem | ok |
| Q41 | Deep Dive On Analog Attendance | MP | grid 1×15 | a selected for 1+ row in Q37 |  | bold stem, underlined stem | ok |
| Q42 | Deep Dive On Analog Attendance | MP | grid 1×8 | a-bb selected in Q15 |  | bold stem, underlined stem | ok |
| Q43 | Deep Dive On Analog Attendance | SP | grid 1×3 | a-bb selected in Q15 |  | bold stem, underlined stem, underlined answers | ok |
| Q44 | Deep Dive On Analog Attendance | SP | grid 1×6 | a-bb selected in Q15 |  | bold stem, underlined stem | ok |
| Q45 | Deep Dive On Analog Attendance | MP | 11 options | i selected in Q13 AND h NOT selected in Q15 |  | bold stem, underlined stem | warning |
| Q46 | Deep Dive On Analog Attendance | MP | 16 options | h selected in Q15 | Q47, Q48 | bold stem, underlined stem, underlined answers | warning |
| Q47 | Deep Dive On Analog Attendance | SP | 5 options | h selected in Q15 AND g not selected in Q46 |  | bold stem, underlined stem, underlined answers | ok |
| Q48 | Deep Dive On Analog Attendance | MP | grid 1×13 | a-e selected in Q46 |  | bold stem, underlined stem | warning |
| Q49 | Deep Dive On Analog Attendance | MP | 4 options | h selected in Q15 |  | bold stem, underlined stem | ok |
| Q50 | Deep Dive On Analog Attendance | SP | grid 1×14 | a-bb selected in Q15 |  | bold stem, underlined stem | ok |
| Q51 | Deep Dive On Analog Attendance | SP | grid 1×5 | a-bb selected in Q15 |  | bold stem, underlined stem | ok |
| Q52 | Deep Dive On Analog Attendance | SP | grid 1×5 | a-bb selected in Q15 |  | bold stem, underlined stem | ok |
| Q53 | Deep Dive On Analog Attendance | SP | grid 1×11 | a-bb selected in Q15 |  | bold stem, underlined stem | ok |
| Q54 | Deep Dive On Analog Attendance | SP | grid 1×6 | a-bb selected in Q15 |  | bold stem, underlined stem | ok |
| Q55 | Deep Dive On Analog Attendance | SP | grid 1×5 | a-bb selected in Q15 |  | bold stem, underlined stem | ok |
| Q56 | Deep Dive On Analog Attendance | SP | grid 1×5 | a-bb selected in Q15 |  | bold stem, underlined stem | ok |
| Q57 | Deep Dive On Analog Attendance | SP | grid 1×5 | a-bb selected in Q15 |  | bold stem, underlined stem | ok |
| Q58 | Deep Dive On Analog Attendance | SP | grid 1×5 | a-bb selected in Q15 |  | bold stem, underlined stem | ok |
| Q59 | Deep Dive On Analog Attendance | MP | grid 1×8 | e selected for 1+ row in Q39 |  | bold stem, underlined stem | ok |
| Q60 | Cosm Sentiment Evaluation | SP | 5 options | always | Q61 | bold stem | ok |
| Q61 | Cosm Sentiment Evaluation | SP | 7 options | a-d selected in Q60 |  | bold stem, underlined stem | ok |
| Q62 | Cosm Sentiment Evaluation | SP | grid 3×5 | always | Q63, Q67, Q68, Q74, Q75, Q76, Q82, Q83,  | bold stem, underlined stem | ok |
| Q63 | Cosm Sentiment Evaluation | SP | grid 1×6 | a-d selected for 1+ row in Q62 |  | bold stem, underlined stem | ok |
| Q64 | Cosm Sentiment Evaluation | SP | grid 3×5 | always |  | bold stem, underlined stem | ok |
| Q65 | Cosm Sentiment Evaluation | MP | 11 options | always |  | bold stem, underlined stem | ok |
| Q66 | Cosm Sentiment Evaluation | MP | 11 options | always |  | bold stem, underlined stem | ok |
| Q67 | Cosm Sentiment Evaluation | MP | 11 options | a-d selected for row a in Q62 | Q69, Q71 | bold stem, underlined stem | ok |
| Q68 | Cosm Sentiment Evaluation | MP | 11 options | a-d selected for row b in Q62 | Q70, Q72 | bold stem, underlined stem | ok |
| Q69 | Cosm Sentiment Evaluation | SP | grid 5×6 | a-g selected in Q67 |  | bold stem, underlined stem | ok |
| Q70 | Cosm Sentiment Evaluation | SP | grid 5×6 | a-g selected in Q68 |  | bold stem, underlined stem | ok |
| Q71 | Cosm Sentiment Evaluation | SP | grid 5×4 | a-g selected in Q67 | Q73 | bold stem, underlined stem, underlined answers | ok |
| Q72 | Cosm Sentiment Evaluation | SP | grid 5×4 | a-g selected in Q68 |  | bold stem, underlined stem, underlined answers | ok |
| Q73 | Cosm Sentiment Evaluation | MP | 20 options | a-c selected for row a or b in Q71 or Q72 |  | bold stem, underlined stem | ok |
| Q74 | Cosm Sentiment Evaluation | MP | 9 options | a-d selected for 1+ row in Q62 |  | bold stem, underlined stem | ok |
| Q75 | Cosm Sentiment Evaluation | MP | 8 options | a-d selected for 1+ row in Q62 |  | bold stem, underlined stem | ok |
| Q76 | Cosm Sentiment Evaluation | SP | grid 2×6 | a-d selected for 1+ row in Q62 |  | bold stem, underlined stem | ok |
| Q77 | Cosm Sentiment Evaluation | SP | 6 options | always |  | bold stem, underlined stem | ok |
| Q78 | Substitutes & Alternatives | MP | 17 options | always | Q79, Q80, Q81 | bold stem, underlined stem | ok |
| Q79 | Substitutes & Alternatives | SP | grid 1×7 | a-o selected in Q78 |  | bold stem, underlined stem | ok |
| Q80 | Substitutes & Alternatives | SP | grid 1×5 | a-o selected in Q78 |  | bold stem, underlined stem, underlined answers | ok |
| Q81 | Substitutes & Alternatives | SP | grid 1×5 | a-o selected in Q78 |  | bold stem, underlined stem | ok |
| Q82 | Substitutes & Alternatives | SP | 5 options | a-d selected for 1+ row in Q62 |  | bold stem, underlined stem, underlined answers | ok |
| Q83 | Purchase Behavior | Numeric | grid 3×2 | a-d selected for 1+ row in Q62 |  | bold stem, underlined stem | ok |
| Q84 | Purchase Behavior | Numeric | 2 options | a-d selected for 1+ row in Q62 |  | bold stem, underlined stem | ok |
| Q85 | Purchase Behavior | SP | 8 options | a-d selected for 1+ row in Q62 |  | bold stem, underlined stem | ok |
| Q86 | Purchase Behavior | SP | grid 3×8 | a-d selected for 1+ row in Q62 |  | bold stem, underlined stem | ok |
| Q87 | Purchase Behavior | SP | grid 4×5 | a-d selected for 1+ row in Q62 | Q88 | bold stem, underlined stem | ok |
| Q88 | Purchase Behavior | Numeric | 2 options | a-d selected for row c in Q87 |  | bold stem, underlined stem | ok |
| Q89 | Purchase Behavior | SP | 5 options | a-d selected for 1+ row in Q62 | Q90 | bold stem | ok |
| Q90 | Purchase Behavior | MP | 6 options | a-d selected in Q89 |  | bold stem, underlined stem | ok |
| Q91 | Purchase Behavior | MP | 3 options | always | Q92 | bold stem, underlined stem, underlined answers | ok |
| Q92 | Purchase Behavior | SP | grid 2×5 | a-b selected in Q91 | Q93 | bold stem, underlined stem | ok |
| Q93 | Purchase Behavior | SP | grid 2×8 | a-d selected for 1+ row in Q92 |  | bold stem, underlined stem | ok |
| Q94 | Sensitivity To Macroeconomic Conditions | SP | 5 options | always |  | bold stem, underlined stem | ok |
| Q95 | Sensitivity To Macroeconomic Conditions | SP | 5 options | always |  | bold stem, underlined stem | ok |
| Q96 | Sensitivity To Macroeconomic Conditions | MP | 13 options | always |  | bold stem, underlined stem | ok |
| Q97 | Sensitivity To Macroeconomic Conditions | SP | 5 options | a-d selected for 1+ row in Q62 |  | bold stem, underlined answers | ok |
| Q98 | Sensitivity To Macroeconomic Conditions | SP | 7 options | a-d selected for 1+ row in Q62 |  | bold stem, underlined stem, underlined answers | ok |
| Q99 | Sensitivity To Macroeconomic Conditions | Numeric | grid 3×2 | a-d selected for 1+ row in Q62 |  | bold stem, underlined stem | warning |
| Q100 | Media & Technology Behaviors | SP | grid 8×7 | always |  | bold stem, underlined stem | ok |
| Q101 | Media & Technology Behaviors | MP | 7 options | always |  | bold stem, underlined stem | ok |
| Q102 | Media & Technology Behaviors | MP | 8 options | always |  | bold stem, underlined stem | ok |
