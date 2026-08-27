# Questionnaire audit — outline.docx

84 questions · 272 programmed rules · **2 error(s), 3 warning(s)**

This checks the document against itself — numbering, cross-references, option lettering, emphasis and programmer syntax. Comparing it to the *live* survey is `compare.mjs`, which needs a captured run.

## Questions with issues

| Q | Issue |
|---|---|
| Q5 | warning: option h "Other" is a catch-all on a multi-punch question but is not tagged [Anchor]/[Exclusive] |
| Q6 | **error**: quota for "B2B" points at Q6 (Which of the following best describes the industry…), whose options never mention it — Q7 does |
| Q6 | **error**: quota for "B2C" points at Q6 (Which of the following best describes the industry…), whose options never mention it — Q7 does |
| Q43 | warning: has answer options but no [SP]/[MP]/[Grid] tag for the programmer |
| Q55 | warning: 4/5 options use underline, but option(s) e do not — emphasis is inconsistent within the question |

## Every question

| Q | Section | Type | Answers | Shown when | Feeds | Emphasis | Status |
|---|---|---|---|---|---|---|---|
| Q1 | Qualifiers | SP | 13 options | always |  | bold stem | ok |
| Q2 | Qualifiers | SP | 10 options | always |  | bold stem, underlined stem | ok |
| Q3 | Qualifiers | SP | 11 options | always |  | bold stem, underlined answers | ok |
| Q4 | Qualifiers | SP | 6 options | always |  | bold stem | ok |
| Q5 | Qualifiers | MP | 8 options | always |  | bold stem | warning |
| Q6 | Qualifiers | SP | 22 options | always |  | bold stem | **error** |
| Q7 | Qualifiers | SP | 3 options | always |  | bold stem | ok |
| Q8 | Technology Spend And Trends | SP | 5 options | always |  | bold stem, underlined stem, underlined answers | ok |
| Q9 | Technology Spend And Trends | unspecified | 1 options | always |  | bold stem | ok |
| Q10 | Technology Spend And Trends | SP | 3 options | always | Q11, Q12, Q13, Q14 | bold stem, underlined answers | ok |
| Q11 | Technology Spend And Trends | SP | 7 options | a is selected for Q10 |  | bold stem, underlined answers | ok |
| Q12 | Technology Spend And Trends | SP | 7 options | b is selected for Q10 |  | bold stem, underlined answers | ok |
| Q13 | Technology Spend And Trends | MP | 11 options | a is selected for Q10 |  | bold stem, underlined stem | ok |
| Q14 | Technology Spend And Trends | unspecified | 3 options | a is selected for Q10 |  | bold stem, underlined stem | ok |
| Q15 | Technology Spend And Trends | SP | 4 options | always | Q16 | bold stem | ok |
| Q16 | Technology Spend And Trends | SP | 5 options | a is selected for Q15 |  | bold stem | ok |
| Q17 | Technology Spend And Trends | SP | 4 options | always |  | bold stem | ok |
| Q18 | Procurement Processes | SP | 6 options | always |  | bold stem | ok |
| Q19 | Procurement Processes | SP | 10 options | always |  | bold stem, underlined stem | ok |
| Q20 | Procurement Processes | SP | grid 8×3 | always |  | bold stem | ok |
| Q21 | Procurement Processes | MP | 13 options | always |  | bold stem | ok |
| Q22 | Procurement Processes | MP | 18 options | always |  | bold stem, underlined stem | ok |
| Q23 | Procurement Processes | SP | 7 options | always |  | bold stem, underlined stem | ok |
| Q24 | Procurement Processes | SP | 7 options | always |  | bold stem, underlined stem | ok |
| Q25 | Software Purchasing Details | MP | 27 options | always | Q26, Q52, Q73, Q74, Q76, Q79 | bold stem | ok |
| Q26 | Software Purchasing Details | SP | grid 16×6 | a-z is selected for Q25 | Q27, Q28, Q29, Q30, Q31, Q32, Q33, Q34,  | bold stem | ok |
| Q27 | Software Purchasing Details | SP | grid 16×5 | i-v is selected for any row in Q26 |  | bold stem, underlined answers | ok |
| Q28 | Software Purchasing Details | SP | grid 16×5 | i-v is selected for any row in Q26 |  | bold stem, underlined answers | ok |
| Q29 | Software Purchasing Details | SP | grid 16×5 | i-v is selected for any row in Q26 |  | bold stem, underlined answers | ok |
| Q30 | Software Purchasing Details | SP | grid 16×5 | i-v is selected for any row in Q26 |  | bold stem, underlined answers | ok |
| Q31 | Software Purchasing Details | MP | 11 options | i-v is selected for row v in Q26 |  | bold stem | ok |
| Q32 | Software Purchasing Details | MP | 11 options | i-v is selected for row x in Q26 |  | bold stem | ok |
| Q33 | Software Purchasing Details | MP | 11 options | i-v is selected for row xi in Q26 |  | bold stem | ok |
| Q34 | Software Purchasing Details | MP | 11 options | i-v is selected for row xii in Q26 |  | bold stem | ok |
| Q35 | Software Purchasing Details | SP | 5 options | always |  | bold stem, underlined stem | ok |
| Q36 | Software Purchasing Details | MP | 11 options | always |  | bold stem, underlined stem | ok |
| Q37 | Software Purchasing Details | SP | grid 4×6 | i-v is selected for any of rows v, x, xi, xii in |  | bold stem | ok |
| Q38 | Software Purchasing Details | SP | 2 options | always | Q39, Q40 | bold stem, underlined stem | ok |
| Q39 | Software Purchasing Details | MP | 9 options | always |  | bold stem, underlined stem | ok |
| Q40 | Software Purchasing Details | MP | 9 options | always |  | bold stem, underlined stem | ok |
| Q41 | Software Purchasing Details | MP | 7 options | always | Q42 | bold stem | ok |
| Q42 | Software Purchasing Details | SP | 3 options | b-f is selected for Q41 |  | bold stem, underlined stem | ok |
| Q43 | Ai Adoption And Value | unspecified | 6 options | always | Q44, Q45, Q46, Q47, Q48, Q49, Q50, Q51,  | bold stem, underlined answers | warning |
| Q44 | Ai Adoption And Value | SP | 3 options | a-c is selected for Q43 |  | bold stem | ok |
| Q45 | Ai Adoption And Value | SP | 3 options | a-c is selected for Q43 |  | bold stem, underlined stem | ok |
| Q46 | Ai Adoption And Value | MP | 9 options | a-c is selected for Q43 |  | bold stem, underlined stem | ok |
| Q47 | Ai Adoption And Value | MP | 5 options | a-c is selected for Q43 |  | bold stem, underlined stem | ok |
| Q48 | Ai Adoption And Value | SP | 11 options | a-c is selected for Q43 |  | bold stem | ok |
| Q49 | Ai Adoption And Value | SP | 6 options | a-c is selected for Q43 |  | bold stem | ok |
| Q50 | Ai Adoption And Value | SP | 6 options | a-c is selected for Q43 |  | bold stem | ok |
| Q51 | Ai Adoption And Value | SP | 3 options | a-c is selected for Q43 |  | bold stem, underlined stem | ok |
| Q52 | Ai Adoption And Value | SP | grid 26×6 | a-c is selected for Q43 AND a-z is selected for  |  | bold stem, underlined stem | ok |
| Q53 | Ai Adoption And Value | MP | 12 options | always | Q54 | bold stem | ok |
| Q54 | Ai Adoption And Value | MP | 8 options | always |  | bold stem | ok |
| Q55 | Ai Operating Model And Governance | SP | 5 options | a-c is selected for Q43 |  | bold stem, underlined stem, underlined answers | warning |
| Q56 | Ai Operating Model And Governance | MP | 11 options | a-c is selected for Q43 | Q57 | bold stem | ok |
| Q57 | Ai Operating Model And Governance | SP | 5 options | a-c is selected for Q43 | Q58 | bold stem, underlined stem, underlined answers | ok |
| Q58 | Ai Operating Model And Governance | SP | grid 7×9 | always |  | bold stem, underlined stem | ok |
| Q59 | Ai Operating Model And Governance | MP | 4 options | a-c is selected for Q43 |  | bold stem | ok |
| Q60 | Ai Operating Model And Governance | SP | 3 options | a-c is selected for Q43 |  | bold stem | ok |
| Q61 | Ai Operating Model And Governance | MP | 7 options | a-c is selected for Q43 | Q62, Q63 | bold stem, underlined stem | ok |
| Q62 | Ai Operating Model And Governance | MP | grid 6×7 | a-f is selected at Q61 |  | bold stem, underlined stem | ok |
| Q63 | Ai Operating Model And Governance | SP | grid 6×11 | a-f is selected at Q61 |  | bold stem, underlined stem | ok |
| Q64 | Data Infrastructure / Ai Tech Stack | SP | 4 options | always |  | bold stem, underlined stem, underlined answers | ok |
| Q65 | Data Infrastructure / Ai Tech Stack | SP | 4 options | always |  | bold stem, underlined answers | ok |
| Q66 | Data Infrastructure / Ai Tech Stack | SP | 4 options | always |  | bold stem, underlined stem | ok |
| Q67 | Data Infrastructure / Ai Tech Stack | SP | 5 options | always |  | bold stem | ok |
| Q68 | Data Infrastructure / Ai Tech Stack | MP | 10 options | always |  | bold stem | ok |
| Q69 | Data Infrastructure / Ai Tech Stack | SP | 5 options | always |  | bold stem | ok |
| Q70 | Data Infrastructure / Ai Tech Stack | SP | 4 options | a-c is selected for Q43 |  | bold stem, underlined stem, underlined answers | ok |
| Q71 | Data Infrastructure / Ai Tech Stack | SP | 4 options | a-c is selected for Q43 | Q72 | bold stem, underlined stem, underlined answers | ok |
| Q72 | Data Infrastructure / Ai Tech Stack | SP | 10 options | a-c is selected for Q71 |  | bold stem, underlined stem | ok |
| Q73 | Cybersecurity | SP | 9 options | h is selected for Q25 |  | bold stem, underlined stem, underlined answers | ok |
| Q74 | Cybersecurity | SP | 3 options | h is selected for Q25 | Q75, Q80 | bold stem | ok |
| Q75 | Cybersecurity | MP | 17 options | c is selected for Q74 |  | bold stem, underlined stem | ok |
| Q76 | Cybersecurity | SP | 3 options | h is selected for Q25 | Q77, Q78 | bold stem, underlined stem | ok |
| Q77 | Cybersecurity | MP | 11 options | a is selected for Q76 |  | bold stem, underlined stem | ok |
| Q78 | Cybersecurity | MP | 11 options | b is selected for Q76 |  | bold stem, underlined stem | ok |
| Q79 | Cybersecurity | SP | grid 17×6 | h is selected for Q25 |  | bold stem, underlined stem | ok |
| Q80 | Cybersecurity | SP | 2 options | a or c is selected for Q74 | Q81, Q82 | bold stem | ok |
| Q81 | Cybersecurity | SP | 5 options | a is selected for Q80 |  | bold stem | ok |
| Q82 | Cybersecurity | SP | 5 options | b is selected for Q80 |  | bold stem | ok |
| Q83 | Cybersecurity | SP | 5 options | always |  | bold stem, underlined stem | ok |
| Q84 | Cybersecurity | SP | 4 options | a-c is selected for Q43 |  | bold stem, underlined stem | ok |
