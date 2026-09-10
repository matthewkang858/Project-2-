"""
Extend the UMG2 Video P&L model's MAU sheet from 2032 out to 2036.

The sheet is already laid out with year columns through 2036 (column O) but is
only populated to 2032. This fills the gap by continuing each row's own
formula, so the workbook stays live and auditable rather than having values
pasted into it.

    python fill_pl_model_10yr.py [source.xlsx] [dest.xlsx]

Re-point it at a newer workbook version when one lands; verify_pl_model_10yr.py
checks the result.
"""
import shutil
import sys
from copy import copy
import openpyxl
from openpyxl.utils import get_column_letter as CL

SRC = sys.argv[1] if len(sys.argv) > 1 else "UMG2_Video_PL_Model_v135MK.xlsx"
OUT = sys.argv[2] if len(sys.argv) > 2 else "UMG2_Video_PL_Model_v135MK_10yr.xlsx"

shutil.copyfile(SRC, OUT)
wb = openpyxl.load_workbook(OUT, data_only=False)
ws = wb.active

COUNTRY_BLOCKS = {            # label -> first data row
    "US": 19, "UK": 29, "France": 39, "Germany": 49, "Japan": 59,
}
# Every block's Gen Pop / SOM formula reads the year label off row 18 (the US
# block's header), not its own. Rows 28/38/48/58 carry identical years, so this
# is a fidelity choice rather than a numeric one - match what the workbook does.
YEAR_HEADER_ROW = 18
NEW_COUNTRY_COLS = range(12, 16)   # L:O  = 2033..2036
NEW_GLOBAL_COLS  = range(11, 16)   # K:O  = 2032..2036
LAST_FILLED = {"country": 11, "global": 10}   # K, J

def style_from(row, src_col, dst_col):
    s, d = ws.cell(row, src_col), ws.cell(row, dst_col)
    d._style = copy(s._style)
    d.number_format = s.number_format

def fill(row, col, formula, src_col):
    ws.cell(row, col).value = formula
    style_from(row, src_col, col)

# ---------------------------------------------------------------- countries
for name, base in COUNTRY_BLOCKS.items():
    r_pop, r_som, r_aware, r_awarepop, r_share, r_conv, r_users = (base + i for i in range(7))
    for col in NEW_COUNTRY_COLS:
        c, p = CL(col), CL(col - 1)
        c1, c2, c3, c4 = (CL(col - i) for i in (1, 2, 3, 4))

        # Gen pop and SOM: grow the prior year at the population growth table.
        # The ranges are widened to column O; the originals stop at J/2032.
        for r in (r_pop, r_som):
            fill(r, col,
                 f"={p}{r}*(1+(INDEX($D$81:$O$85,MATCH($B{r},$B$81:$B$85,0),"
                 f"MATCH({c}${YEAR_HEADER_ROW},$D$80:$O$80,0))))", LAST_FILLED["country"])

        # %Aware: the workbook's own decaying-growth extrapolation, continued.
        fill(r_aware, col,
             f"={c1}{r_aware}*(1+(1+_xlfn.RRI(1,{c3}{r_aware}/{c4}{r_aware}-1,"
             f"{c2}{r_aware}/{c3}{r_aware}-1))*({c1}{r_aware}/{c2}{r_aware}-1))",
             LAST_FILLED["country"])

        fill(r_awarepop, col, f"={c}{r_som}*{c}{r_aware}",   LAST_FILLED["country"])
        fill(r_share,    col, f"={c}{r_awarepop}/{c}{r_pop}", LAST_FILLED["country"])
        fill(r_conv,     col,
             f"=_xlfn.XLOOKUP($B{r_conv},$B$113:$B$117,$E$113:$E$117)",
             LAST_FILLED["country"])
        fill(r_users,    col, f"={c}{r_awarepop}*{c}{r_conv}", LAST_FILLED["country"])

# ------------------------------------------------------------------- global
USER_ROWS = [25, 35, 45, 55, 65]          # Total User Population per country
for col in NEW_GLOBAL_COLS:
    c = CL(col)
    fill(9, col, "=" + "+".join(f"{c}{r}" for r in USER_ROWS), LAST_FILLED["global"])
    for offset, r in enumerate(USER_ROWS):
        fill(10 + offset, col, f'=IFERROR({c}{r}/{c}$9,"N/A")', LAST_FILLED["global"])

wb.save(OUT)
print(f"wrote {OUT}")
print(f"country blocks: filled L:O (2033-2036) x {len(COUNTRY_BLOCKS)} countries x 7 rows")
print("global block:   filled K:O (2032-2036) for total + 5 shares")
