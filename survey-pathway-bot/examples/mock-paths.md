<!-- Example output: `node run-paths.mjs --paths paths.example.json` against mock/server.mjs. -->

# Scripted pathway tests

Survey: `http://127.0.0.1:8101/`
Run: 2026-08-27T16:42:37.806Z
Result: **4/4 passed**

| Scenario | Result | Pages | Outcome | Questions shown | Failures |
|---|---|---:|---|---|---|
| Under 18 is screened out | PASS | 2 | terminate | S1 | — |
| California 55+ hits the quota | PASS | 3 | quota | S1, S2, S3 | — |
| Alpha buyers are asked the rating grid | PASS | 6 | complete | S1, S2, S3, Q1r1, Q1r2, Q1r3, Q2r1, Q2r2, Q3 | — |
| Non-Alpha buyers skip the rating grid | PASS | 5 | complete | S1, S2, S3, Q1r1, Q1r2, Q1r3, Q3 | — |
