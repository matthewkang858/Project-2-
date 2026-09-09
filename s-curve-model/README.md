# S-Curve MAU Model

`S_Curve_Parameter_Search.ipynb` — the original 3-year parameter search plus a
new **Ten Year** section at the bottom.

## The Ten Year cell

Extends the horizon from 12 periods to **40 periods (10 years, quarterly)** and
shapes the path as a real S-curve: slow launch, steep middle, flattening top.

![10-year S-curve](ten_year_s_curve.png)

Exit-quarter MAUs (millions):

| Year | Period | US | UK | France | Germany | Japan |
|-----:|-------:|-----:|-----:|-------:|--------:|------:|
| 1 | 4 | 0.78 | — | — | — | — |
| 2 | 8 | 4.26 | 0.45 | 0.28 | 0.39 | 0.62 |
| 3 | 12 | 8.58 | 0.90 | 0.56 | 0.77 | 1.24 |
| 4 | 16 | 13.27 | 1.58 | 1.01 | 1.36 | 2.23 |
| 5 | 20 | 19.28 | 2.42 | 1.60 | 2.11 | 3.57 |
| 6 | 24 | 26.34 | 3.24 | 2.20 | 2.87 | 4.97 |
| 7 | 28 | 32.88 | 3.87 | 2.68 | 3.46 | 6.09 |
| 8 | 32 | 37.38 | 4.27 | 2.98 | 3.83 | 6.79 |
| 9 | 36 | 39.73 | 4.48 | 3.13 | 4.03 | 7.16 |
| 10 | 40 | 40.75 | 4.58 | 3.21 | 4.13 | 7.33 |

Years 1–3 are unchanged: the existing targets at periods 4, 8 and 12 are still
hit to within 0.1%.

## Knobs

All at the top of the cell.

| Setting | Default | What it does |
|---|---|---|
| `TOTAL_PERIODS` | `40` | Horizon in quarters |
| `mau_ceiling` (per country) | 45 / 5 / 3.5 / 4.5 / 8 M | Year-10 saturation level |
| `CEILING_APPROACH` | `0.92` | Share of the ceiling reached at period 40 |
| `TERMINAL_GROWTH` | `0.004` | Quarterly growth at period 40 — flattens the top |
| `MAX_GROWTH` | `1.50` | Cap on any single quarter's growth |
| `MONO_LAMBDA` | `30.0` | Forces growth rates to decay, never re-accelerate |
| `SMOOTH_LAMBDA` | `3.0` | Curvature penalty on the *log* rate |
| `USE_SEASONALITY` | `False` | Quarterly wobble on top of the trend |

## Two things worth knowing

**The ceilings are the one assumed input.** They are population x a plausible
mature penetration rate (~15% US, 6–8% elsewhere). Everything else is either an
existing commitment or solved. Swap in real TAM numbers when we have them — the
Year 4–10 path moves roughly proportionally, Years 1–3 do not move at all.

**Why log space.** The unknowns are solved as logs, and the smoothness penalty
is applied to the log growth rate rather than the rate itself. Penalizing
curvature of the raw rate forces a straight-line decay, which cannot both hold
the Year-3 target and land on the Year-10 ceiling; the solver resolves that by
crashing growth around period 16 and re-accelerating through the late 20s — a
double hump, not an S. In log space a constant-percentage decay is
curvature-free, so a clean monotone S is the natural answer.

## Output

`growth_model_s_curve_P40_US_UK_FR_DE_JP.xlsx`, four sheets:
`Growth_Percentages`, `MAUs_Absolute`, `Starting_Acq_Rates` (all 40 periods,
same layout as before) and a new `Yearly_Summary`.
