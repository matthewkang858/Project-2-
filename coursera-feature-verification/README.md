# Feature verification — COUR4 Competitive Research ("Features v2" tab)

Per-platform verification of the features claimed in `COUR4_Competitive_Research_v3_4.xlsx`,
sheet **Features v2**, against live web evidence.

| Platform | Report | Matrix | Screenshot manifest | Result |
|---|---|---|---|---|
| Coursera (rows 6–39) | `VERIFICATION.md` | `verification_matrix.csv` | `screenshot_manifest.json` | 33/34 verified, 1 partial |
| Udemy (rows 43–67) | `UDEMY_VERIFICATION.md` | `udemy_verification_matrix.csv` | `udemy_screenshot_manifest.json` | 24/25 verified, 1 partial |
| LinkedIn Learning (rows 71–101) | `LINKEDIN_LEARNING_VERIFICATION.md` | `linkedin_learning_verification_matrix.csv` | `linkedin_learning_screenshot_manifest.json` | 29/31 verified, 2 partial |

`features_from_sheet.json` / `udemy_features_from_sheet.json` / `linkedin_learning_features_from_sheet.json` are the raw rows extracted from the workbook.

## Capturing proof screenshots

Verification here is evidence-based (official product pages, help-center articles, blogs,
press releases — see each report). Screenshots could not be captured from the original
session because its network egress policy blocked coursera.org/udemy.com; run the capture
script from any machine with normal internet access:

```bash
npm install playwright && npx playwright install chromium   # once
node capture_screenshots.mjs screenshot_manifest.json screenshots-coursera/
node capture_screenshots.mjs udemy_screenshot_manifest.json screenshots-udemy/
node capture_screenshots.mjs linkedin_learning_screenshot_manifest.json screenshots-linkedin/
```

For each manifest entry the script loads the page, scrolls to and outlines the proof text,
saves viewport + full-page PNGs, and writes `capture_results.json` flagging any page where
the proof text was not found (those need a quick manual look — a few targets sit behind
login or inside apps, as called out in the reports).
