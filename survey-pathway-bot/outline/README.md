# Checking a live survey against the questionnaire

Two steps: turn the Word questionnaire into a machine-readable spec, then diff a
captured run against it.

```bash
# 1. parse the questionnaire (also audits the document's own consistency)
python3 outline/parse_outline.py "2026.08.21_Activate_B2B_Survey_Outline.docx" outline/outline-spec.json

# 2. after capturing runs (extension, snippet or CLI), compare
node compare.mjs --spec outline/outline-spec.json --traces out/runs
node compare.mjs --spec outline/outline-spec.json --traces spb-traces.json   # extension export
```

`parse_outline.py` also writes `outline-spec-AUDIT.md` — a question-by-question
audit of the document on its own (no live survey needed): cross-references,
option lettering, emphasis conventions and programmer syntax.

`COMPARE.md` reports, question by question:

- **Coverage** — which of the outline's questions were reached, which were never
  reached (with the gate that would have shown them), and which live questions
  have no counterpart in the outline.
- **Option lists** — count mismatches, options in the outline but missing live,
  and options live that the outline does not contain.
- **Question type** — anything the outline tags `[SP]` that renders as
  checkboxes, or `[MP]` that renders as radios.
- **Routing** — every `[Display if …]` rule the traces contradict (a gated
  question shown to a respondent who did not give the gating answer), and every
  `[Terminate …]` rule a run walked straight past.
- **Wording** — word-level differences between the outline's question text and
  what the survey actually renders.
- **Emphasis** — every phrase the outline bolds or underlines that the live page
  does not. Underlining is load-bearing here: `[INSERT ANSWER FROM 71 - INITIAL
  UNDERLINED PHRASE]` pipes the underlined part of the chosen answer.
- **Option order** — options that render in a different position than the
  outline lists them, unless the question is tagged `[Randomize]`.
- **Leaked syntax** — programmer instructions (`[SP]`, `[Display if …]`,
  `[Randomize]`) or unsubstituted pipes visible to respondents.
- **Outline findings** — problems inside the document itself: references to
  questions or option letters that do not exist, display rules that depend on a
  later question, multi-punch limits on single-punch questions, questions with
  no programmer type tag, catch-all options missing `[Anchor]`/`[Exclusive]`,
  emphasis that is inconsistent within a question, and quota references that
  point at the wrong question.

Grid questions are parsed as rows and columns numbered in roman numerals, which
is how this questionnaire's own rules refer to them ("[Display if i-v is
selected for row v in Q26]").

Matching is by question wording (Dice coefficient on content words, one-to-one,
0.6 threshold), because the live form names (`Q43`, `QA7r1`, …) are the
programmer's, not the outline's. Check the "Matched questions" table at the
bottom of the report before trusting a mismatch — a low score there means the
wording drifted, not that the question is wrong.

`expected-paths.json` encodes the outline's terminates and its biggest routing
gate as assertions for `run-paths.mjs`.
