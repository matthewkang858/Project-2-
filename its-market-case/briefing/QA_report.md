# QA pass: Public ITS deck (v7) and model (v2)

**46 verified findings were checked, which come to 33 distinct issues after merging duplicates. I fixed 28 of them on copies of your files: 13 in the deck and 15 in the model. 6 items are left for you below. Nothing you deleted was put back, and no Sources line was changed.**

The fixed files are in the `out` folder next to this report: `Public_ITS_Market_Case_7.pptx`, `Public_ITS_Market_Model_2.xlsx`, and slide renders in `render/`.

## Fixes made

| File | Where | Before → After | Why |
|---|---|---|---|
| pptx | Slide 1, cover line | `Alvarez & Marsal \|  Matthew Kang` → `Alvarez & Marsal  \|  Matthew Kang` | There was one space before the first pipe and two everywhere else, so the gap looked lopsided. Your wording is kept. |
| pptx | Slide 2, Investment thesis, bullet 2 | "while the ~1.6x paid for Clever barely returns capital" → "while exiting at Clever's ~1.6x barely returns capital" | Read literally, the old text said Hitachi's purchase barely returned capital. The intended point is that our deal returns 1.2x (Returns!B28) if it exits at Clever's multiple. The new text is the same length and still fits on one line. |
| pptx | Slides 2 and 7, Note lines | Trailing space after the final period → removed | Left over from splitting the notes and sources. It is invisible on screen but shows up when the text is copied. |
| pptx (reverted after QA) | Slide 4 chart, segment labels | Format `"$"0"B"` → `"$"0.0"B"` (2025: $21B / $3B / $5B → $20.8B / $3.2B / $4.6B) | The whole-billion labels added up to $40B in 2031E against a $39.3B total, and the 2025 labels disagreed with slide 3. The labels now tie to the totals and to slide 3, and they fit inside the bars in the render. The chart data is unchanged. |
| pptx | Slide 4, green callout box | Top 6.60in, height 0.39in → top 6.55in, height 0.44in (bottom unchanged) | The text touched the edges of the box. The text itself is unchanged. |
| pptx | Slide 5 title | "private long tail opportunity" → "private long-tail opportunity" | "Long-tail" modifies "opportunity", so it needs a hyphen. The wrap is unchanged. |
| pptx | Slide 5, SaaS / AI market position | "their existing system" → "their existing systems" | Agrees with the plural "agencies". The box is still four lines. |
| pptx | Slide 5, Implication box | "bid against us for targets" → "bid against an entrant for targets", and the final period is removed | "Us" was unclear in an advisor's deck. This was also the only box on the slide that ended with a period. Still four lines. |
| pptx | Slide 5, Exit benchmark | "Value the exit off INIT and IVU: recurring revenue lifts the price" → "INIT and IVU show that recurring revenue lifts the price" | Slide 7 and the model value the exit off Clever (1.58x) and IVU (2.6x), not INIT (0.98x). At INIT's multiple the deal returns about 0.7x. |
| pptx | Slide 5, right end of the scale arrow | "Smallest, newest to the market" → "Smaller, newer to the market" | Now parallel with the left end ("Larger, more entrenched"). "Smallest" is hard to defend with listed Via in the group. |
| pptx | Slide 5, alt text of the 16 logos | A local build path (`/home/user/.../siemens.png`) → "Siemens logo", "Hitachi logo" and so on | Screen readers read the path aloud, and it shows in the alt text pane. Nothing on screen changes. |
| pptx | Slide 6 title | "so buy an installed base, and near-term risks are…" → "so buy an installed base. Near-term risks are…" | The run-on joined a recommendation to an unrelated point about risks. The title keeps the same two-line wrap. |
| xlsx | Growth!A1 | "…2025-2031E, low / base / high" → "…2025-2031E, USD B, low / base / high" | The unit was only given in the A2 note you deleted, and the values show as plain numbers (20.82, 39.31). |
| xlsx | Growth!Q7 | "High: the 9th edition pace (6.3%)" → "High: faster than the 9th edition pace (6.3%)" | The high input in N7 is 7.0%, not 6.3%. No output changes. |
| xlsx | Growth!Q10 | "Base: SCI Verkehr signalling forecast (4.6% nominal) and UNIFE…" → "Base: a little above the SCI Verkehr signalling forecast (4.6% nominal), checked against UNIFE…" | The base input (M10) and slide 4 both show 5.0%, but the note cited only 4.6%. |
| xlsx | Growth!Q16 | "hardware share falls to 44.6% by 2031" → "hardware share implied to fall to 44.6% by 2031" | GMI publishes 2025 and 2035 only. The 2031 figure is derived. |
| xlsx | Growth!A24 | Adds "(column J)" | This check's result sits in J24, not in column B like the other two checks. |
| xlsx | Returns!D9 | "at about 11x EBITDA of debt" → "funded with debt of about 11x EBITDA" | The old wording could be read as an 11x purchase multiple. |
| xlsx | Returns!D11 | "well below Via and INIT (24-29%) (company reports)" → "well below Via and INIT, which grew 24-29% in 2025 (company reports)" | Removes the two parentheses in a row and dates the growth figure. |
| xlsx | Returns!A45 | "E. CHECKS (all should be 0)" → "E. CHECK (should be 0)" | There is only one check, and the wording now matches Bottom-up!A35. |
| xlsx | Bottom-up!A11 | "B. SPENDING POOLS, 2025: …" → "B. SPENDING POOLS, 2025, USD M A YEAR: …" | The pool values in F12:F22 had no unit on their rows. |
| xlsx | Bottom-up!C15 | "buses at mid-size and small agencies" → "buses at agencies with 50+ buses" | 66,700 is more than all North American buses outside the ten largest agencies. It matches agencies with 50 or more buses (54.7k US plus about 12k Canada). "50+" keeps the label on two lines in the fixed-height row. |
| xlsx | Bottom-up!H20 | "program budgets" → "programme budgets" | G20 on the same row and the rest of the model use British spelling. |
| xlsx | Bottom-up!G26 | "The two methods agree within a few per cent" → "The bottom-up is about 6% below the top-down" | F26 shows 93.9%. |
| xlsx | Inputs \| Market Funnel!A1 | "Market: 2025 market size and funnel" → "Inputs \| Market Funnel: 2025 market size and funnel" | The title still used the old sheet name, and the file opens on this tab. |
| xlsx | Inputs \| Market Funnel!D51 | "…− open pool (ties the S3 table to the funnel)" → "…− open pool" | This was the last deck pointer in the model, and "S3" reads like a cell reference. A reworded version would wrap and be clipped in the one-line row. |
| xlsx | Returns and Growth saved view | Returns opened scrolled to row 21 with the inputs hidden, and Growth had the empty block R4:T21 selected → both now open at B5 | Leftover editing state. This is not a cell change. |

## For you to decide (not changed)

1. **Slide 7 chart header "RETURN MULTIPLE EXAMPLES, 5-YEAR EXAMPLE"** repeats "example". I left it because it is your own new wording. It fits on one line. If you want a fix, "RETURN MULTIPLE EXAMPLES, 5-YEAR HOLD" changes one word (the hold is 5 years, Returns!B14). "RETURN MULTIPLES (MOIC), 5-YEAR EXAMPLE" also stops the 1.2x / 2.0x bars from being read as exit multiples.
2. **Slide 5 sources** say "Berg Insight" with no year, while slides 2 to 4 say "Berg Insight (2026)". I left it because you asked that the sources stay as you set them. Add "(2026)" yourself if you want them consistent.
3. **Slide 4 sources** do not name MarketsandMarkets or Mordor Intelligence, which back the 7.0% other rail growth (Growth!Q11). They were only ever on the old appendix line, so nothing you deleted is involved. "Analysis" may be enough.
4. **Slide 2, "hardware is losing share to software"** has no exhibit on slides 3 to 7. The support is in the model: Growth row 16 shows the bus hardware share falling from 46.8% to 44.6%, and GMI has software growing 9.7% a year against 7.7% for hardware. Be ready to point there if asked.
5. **Slide 6 colours.** HIGH barriers sit on green, but slide 4 uses green for drivers that raise growth. Someone skimming could read green HIGH on slide 6 as good news. This is a design choice.
6. **Slide 4 chart, 2029E.** With one-decimal labels the segments add to $35.4B against the $35.3B total, which is rounding. Every other year ties exactly. Slide 4 carries no rounding note, so be ready to explain it if asked.

Where two reviewers proposed different wording for the same spot, I applied one version. The scale arrow change was made on the right end only. The Q10 note blends the two proposals and does not claim the base is "in line with" UNIFE, because UNIFE's signalling split was not retrieved.

The model was edited inside the xlsx itself: only the shared strings and the two sheet-view settings changed, so your Excel formatting is untouched. I recalculated a copy rather than re-saving your file through LibreOffice, because no number or formula changed.

## Checked and clean

- **Deck numbers vs the model.** I checked $28.6B, $14.0B, $7.8B, $4.2B, ~15% and the table rows on slide 3, every bar total and CAGR on slide 4, and 1.2x, 2.0x, 1.6x, 2.6x and ~$0.6B on slide 7.
- **Formulas.** All 187 formulas recalculate with 0 errors, all 8 check cells are 0, and the recalculated values match the saved ones (largest difference 1.5e-11).
- **Model cell diff.** Only the 14 cells above changed text, with no style, formula or value changes.
- **Your deletions.** The sheet names and order, the column layout, and the deleted README, Confidence / On slide / Deck key columns and A2 notes are all as you left them.
- **Deck text diff.** It shows only the intended edits.
- **Renders.** Slides 3 and 7 are pixel-identical, and the changed slides render without overflow or clipping.


## Changes made after the QA pass

These come from your talk-through. They were applied on top of the QA'd copy.

| Slide | Before | After |
| --- | --- | --- |
| 2 | Signalling is a closed club, while… | Signalling is a closed oligopoly, while… |
| 2 | Buy a privately held North American mid-market bus ITS vendor below a software multiple | Most attractive entry: a privately held North American mid-market bus ITS vendor, below a software multiple |
| 3 | Less urban signalling: a closed club of safety-certified suppliers | Less urban signalling: an oligopoly of safety-certified suppliers |
| 4 | Segment labels in one-decimal billions (QA change) | Back to whole billions ($21B), as you asked earlier. The segments still round to within $1B of each total |
| 6 | Title: Agencies rarely switch vendors and buy slowly, so buy an installed base… | Agencies keep systems for over a decade, so the way in is to own an installed base. The near-term risks are US funding and ETCS delays |
| 6 | Agencies favor vendors with proven customers / Shared purchasing contracts speed up software sales | Agencies trust vendors that already run systems elsewhere / Shared purchasing contracts let agencies skip a full tender |
| 6 | Signalling is a closed club | Signalling is an oligopoly |
| 7 | Title: Buy and build in North American bus ITS software, but returns need… | The most attractive entry is North American bus ITS software, but returns need a software exit multiple (~2.6x revenue), well above Clever's ~1.6x |
| 7 | Recommendation: Buy a privately held… | The most attractive entry is a private North American mid-market bus ITS vendor below a software multiple. Cloud, AI cameras and electric-bus software then make recurring revenue most of its sales. |
| 7 | RETURN MULTIPLE EXAMPLES, 5-YEAR EXAMPLE | RETURN MULTIPLE EXAMPLES, 5-YEAR HOLD |
