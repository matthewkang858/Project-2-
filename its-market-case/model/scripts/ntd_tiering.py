#!/usr/bin/env python3
"""
ntd_tiering.py - compute US transit agency tiering, rail fleet by mode, capital-expense tables and
top-agency lists from FTA National Transit Database (NTD) CSVs downloaded with ntd_download.sh.

Usage:  python3 -I ntd_tiering.py <ntd_raw_dir> <out_dir>
Inputs are treated as untrusted data (read with pandas, dtype=str; nothing is executed).
Report year 2025 = agency fiscal years ending in 2025 (published by FTA Oct 2026).
"""
import os
import sys

import numpy as np
import pandas as pd

RAW, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

BUS_MODES = {"MB", "CB", "RB", "TB"}
RAIL_MODES = {"HR", "LR", "SR", "CR", "YR", "MG", "CC", "IP", "AR", "TR"}
DR_MODES = {"DR", "VP", "PB", "DT", "JT", "OR"}
FERRY_MODES = {"FB"}
BUS_TYPES = ["Bus", "Articulated Bus", "Over-the-road Bus", "Double Decker Bus", "Trolleybus"]
LOCO = "Commuter Rail Locomotive"
RAIL_TYPES = [
    "Heavy Rail Passenger Car", "Light Rail Vehicle", "Vintage Trolley",
    "Commuter Rail Passenger Coach", "Commuter Rail Self-Propelled Passenger Car", LOCO,
    "Automated Guideway Vehicle", "Monorail Vehicle", "Cable Car", "Inclined Plane Vehicle",
    "Aerial Tramway",
]
MODE_NAMES = {
    "MB": "Bus", "CB": "Commuter Bus", "RB": "Bus Rapid Transit", "TB": "Trolleybus",
    "HR": "Heavy Rail", "LR": "Light Rail", "SR": "Streetcar", "CR": "Commuter Rail",
    "YR": "Hybrid Rail", "MG": "Monorail/Automated Guideway", "CC": "Cable Car",
    "IP": "Inclined Plane", "AR": "Alaska Railroad", "TR": "Aerial Tramway",
    "DR": "Demand Response", "VP": "Vanpool", "PB": "Publico", "FB": "Ferryboat",
}
CAP_CATS = [
    "Guideway", "Stations", "Administrative Buildings", "Maintenance Buildings",
    "Passenger Vehicles", "Other Vehicles", "Fare Collection Equipment",
    "Communication & Information Systems", "Other", "Reduced Reporter Expenses", "Total",
]
TIER_ORDER = ["1: 1-49", "2: 50-249", "3: 250-999", "4: 1000+"]


def rd(name):
    return pd.read_csv(os.path.join(RAW, name), dtype=str, keep_default_na=False, encoding="utf-8-sig")


def num(s):
    return pd.to_numeric(s.replace("", np.nan), errors="coerce").fillna(0.0)


def mode_group(m):
    if m in BUS_MODES:
        return "Bus (MB/CB/RB/TB)"
    if m in RAIL_MODES:
        return "Rail"
    if m in DR_MODES:
        return "Demand response / vanpool"
    if m in FERRY_MODES:
        return "Ferry"
    return "Other"


def tier(n):
    if n >= 1000:
        return "4: 1000+"
    if n >= 250:
        return "3: 250-999"
    if n >= 50:
        return "2: 50-249"
    if n >= 1:
        return "1: 1-49"
    return "0: none"


def tier_table(df, count_col, label):
    """df: one row per agency with count_col. Returns tier summary."""
    d = df[df[count_col] > 0].copy()
    d["tier"] = d[count_col].apply(tier)
    g = d.groupby("tier").agg(agencies=(count_col, "size"), vehicles=(count_col, "sum")).reindex(TIER_ORDER).fillna(0)
    g["agencies"] = g["agencies"].astype(int)
    g["vehicles"] = g["vehicles"].astype(int)
    g["share_of_agencies_pct"] = (100 * g["agencies"] / g["agencies"].sum()).round(1)
    g["share_of_vehicles_pct"] = (100 * g["vehicles"] / g["vehicles"].sum()).round(1)
    g["avg_vehicles_per_agency"] = (g["vehicles"] / g["agencies"].replace(0, np.nan)).round(1)
    g.loc["Total"] = [g["agencies"].sum(), g["vehicles"].sum(), 100.0, 100.0, round(g["vehicles"].sum() / g["agencies"].sum(), 1)]
    g.insert(0, "definition", label)
    g.index.name = "tier"
    return g.reset_index()


def w(df, name):
    p = os.path.join(OUT, name)
    df.to_csv(p, index=False)
    print(f"  wrote {p} ({len(df)} rows)")


print("=== Loading ===")
rvi = rd("2025_revenue_vehicle_inventory__ifzt-j53d.csv")
veh = rd("2022_2025_vehicles_type_count_by_agency__nimp-626k.csv")
cap = rd("2022_2025_capital_expenses_by_capital_use__fphd-jyyj.csv")
cu25 = rd("2025_capital_use__8rr7-fd8y.csv")
ts = rd("2025_capital_expenditures_time_series_3_1__8ffu-2anj.csv")
ag = rd("2025_reporter_agency_information__jm7a-9hsy.csv")
age = rd("2022_2025_vehicles_age_distribution__6abt-uhgq.csv")
opf = rd("2022_2025_operating_expenses_by_function__dkxx-zjd6.csv")
opt = rd("2022_2025_operating_expenses_by_type__j5uj-anzx.csv")
svc = rd("2025_service__74ek-quhs.csv")
for n, d, exp in [("RVI", rvi, 35625), ("VEH", veh, 10858), ("CAP", cap, 17285), ("CU25", cu25, 5193),
                  ("TS", ts, 155408), ("AG", ag, 2897)]:
    assert len(d) == exp, (n, len(d), exp)
    print(f"  {n}: {len(d)} rows (matches API count)")

# ---------------------------------------------------------------- agency lookup
ag["Total VOMS"] = num(ag["Total VOMS"])
aglk = ag.drop_duplicates("NTD ID").set_index("NTD ID")[["Agency Name", "City", "State", "Reporter Type", "Organization Type", "UZA Name",
                               "Total VOMS", "TAM Tier", "Service Area Pop"]]

# ---------------------------------------------------------------- RVI prep
rvi["active"] = num(rvi["Active Fleet Vehicles"])
rvi["total"] = num(rvi["Total Fleet Vehicles"])
rvi["ada"] = num(rvi["ADA Fleet Vehicles"])
rvi["myear"] = num(rvi["Manufacture Year"])
rvi["ulb"] = num(rvi["Useful Life Benchmark"])
rvi["mode_list"] = rvi["Modes"].apply(lambda s: [t.strip().split("/")[0] for t in s.split(",") if t.strip()])
rvi["has_bus_mode"] = rvi["mode_list"].apply(lambda L: any(m in BUS_MODES for m in L))
rvi["has_rail_mode"] = rvi["mode_list"].apply(lambda L: any(m in RAIL_MODES for m in L))
rvi["rail_mode"] = rvi["mode_list"].apply(lambda L: next((m for m in L if m in RAIL_MODES), ""))
rvi["is_bus_type"] = rvi["Vehicle Type"].isin(BUS_TYPES)
rvi["is_rail_type"] = rvi["Vehicle Type"].isin(RAIL_TYPES)

print("\n=== RVI 2025 totals ===")
print(f"  all revenue vehicles: active {int(rvi['active'].sum()):,} / total {int(rvi['total'].sum()):,}")
print(f"  full-size bus types (any mode): active {int(rvi.loc[rvi.is_bus_type,'active'].sum()):,} / total {int(rvi.loc[rvi.is_bus_type,'total'].sum()):,}")
print(f"  all vehicles in bus modes MB/CB/RB/TB (any type): active {int(rvi.loc[rvi.has_bus_mode,'active'].sum()):,}")
print(f"  bus types in bus modes: active {int(rvi.loc[rvi.is_bus_type & rvi.has_bus_mode,'active'].sum()):,}")
print(f"  bus types in non-bus modes (DR etc): active {int(rvi.loc[rvi.is_bus_type & ~rvi.has_bus_mode,'active'].sum()):,}")
bt = rvi[rvi.is_bus_type].groupby("Vehicle Type")[["active", "total"]].sum().astype(int)
print(bt)

# ---------------------------------------------------------------- (1) bus tiering 2025
agb = rvi.groupby("NTD ID").agg(
    agency=("Agency Name", "first"), reporter_type=("Reporter Type", "first"),
    active_fullsize_bus=("active", lambda s: s[rvi.loc[s.index, "is_bus_type"]].sum()),
    total_fullsize_bus=("total", lambda s: s[rvi.loc[s.index, "is_bus_type"]].sum()),
    active_busmode_all_types=("active", lambda s: s[rvi.loc[s.index, "has_bus_mode"]].sum()),
    active_bustype_in_busmode=("active", lambda s: s[rvi.loc[s.index, "is_bus_type"] & rvi.loc[s.index, "has_bus_mode"]].sum()),
    active_all_vehicles=("active", "sum"),
).reset_index()
for c in ["Bus", "Articulated Bus", "Over-the-road Bus", "Double Decker Bus", "Trolleybus"]:
    sub = rvi[rvi["Vehicle Type"] == c].groupby("NTD ID")["active"].sum()
    agb["active_" + c.lower().replace(" ", "_").replace("-", "_")] = agb["NTD ID"].map(sub).fillna(0).astype(int)
zeb = rvi[rvi.is_bus_type & rvi["Fuel Type"].isin(["Electric Battery", "Hydrogen", "Hybrid Diesel/Electric Battery"])].groupby("NTD ID")["active"].sum()
agb["active_zero_emission_bus_bev_fcev"] = agb["NTD ID"].map(zeb).fillna(0).astype(int)
cutb = rvi[rvi.has_bus_mode & (rvi["Vehicle Type"] == "Cutaway")].groupby("NTD ID")["active"].sum()
agb["active_cutaways_in_bus_modes"] = agb["NTD ID"].map(cutb).fillna(0).astype(int)
# weighted average age of active full-size buses
bb = rvi[rvi.is_bus_type & (rvi.active > 0) & (rvi.myear > 1900)].copy()
bb["age_w"] = (2025 - bb["myear"]) * bb["active"]
agebus = bb.groupby("NTD ID").apply(lambda d: d["age_w"].sum() / d["active"].sum() if d["active"].sum() else np.nan, include_groups=False)
agb["avg_age_active_fullsize_bus_yrs"] = agb["NTD ID"].map(agebus).round(1)
bb["past_ulb"] = ((2025 - bb["myear"]) >= bb["ulb"]) & (bb["ulb"] > 0)
pulb = bb[bb.past_ulb].groupby("NTD ID")["active"].sum()
agb["active_fullsize_bus_at_or_past_ulb"] = agb["NTD ID"].map(pulb).fillna(0).astype(int)
for c in ["City", "State", "Organization Type", "UZA Name", "Total VOMS", "TAM Tier"]:
    agb[c.lower().replace(" ", "_")] = agb["NTD ID"].map(aglk[c])
for c in ["active_fullsize_bus", "total_fullsize_bus", "active_busmode_all_types", "active_bustype_in_busmode", "active_all_vehicles"]:
    agb[c] = agb[c].astype(int)
agb["tier_active_fullsize_bus"] = agb["active_fullsize_bus"].apply(tier)
agb["tier_active_busmode_all_types"] = agb["active_busmode_all_types"].apply(tier)

print("\n=== (1) Bus tiering, report year 2025 ===")
t1 = tier_table(agb, "active_fullsize_bus", "A: active full-size buses (Bus, Articulated, Over-the-road, Double-decker, Trolleybus), any mode - RVI 2025")
t2 = tier_table(agb, "active_busmode_all_types", "B: all active revenue vehicles in fixed-route bus modes MB/CB/RB/TB incl. cutaways/vans - RVI 2025")
t3 = tier_table(agb, "active_bustype_in_busmode", "C: active full-size buses operated in bus modes MB/CB/RB/TB only - RVI 2025")
t4 = tier_table(agb, "total_fullsize_bus", "D: total (active + inactive/contingency) full-size buses, any mode - RVI 2025")
tiers = pd.concat([t1, t2, t3, t4], ignore_index=True)
print(t1.to_string(index=False))
print(t2.to_string(index=False))
w(tiers, "ntd_2025_bus_agency_tiers.csv")
w(agb.sort_values("active_fullsize_bus", ascending=False), "ntd_2025_bus_fleet_by_agency.csv")

# tiering 2022-2025 from Vehicles (Type Count by Agency) table
for c in ["Bus", "Articulated Bus", "Over-the-Road Bus", "Double Decker Bus", "Trolleybus", "Cutaway", "Total Revenue Vehicles", "Agency VOMS",
          "Heavy Rail Passenger Car", "Light Rail Vehicle", "Streetcar", "Commuter Rail Passenger Coach", "Commuter Rail Self-Propelled", "Locomotive", "Vintage/Historic Trolley", "Automated Guideway Vehicle", "Monorail"]:
    if c in veh.columns:
        veh[c] = num(veh[c])
veh["fullsize_bus"] = veh[["Bus", "Articulated Bus", "Over-the-Road Bus", "Double Decker Bus", "Trolleybus"]].sum(axis=1)
rows = []
for y in ["2022", "2023", "2024", "2025"]:
    vy = veh[veh["Report Year"] == y].groupby("NTD ID").agg(fullsize_bus=("fullsize_bus", "sum")).reset_index()
    t = tier_table(vy, "fullsize_bus", f"full-size buses (Bus+Artic+OTR+DD+Trolleybus) from Vehicles Type Count table, report year {y}")
    t.insert(0, "report_year", y)
    rows.append(t)
    print(f"  year {y}: agencies w/ buses {int((vy.fullsize_bus>0).sum())}, buses {int(vy.fullsize_bus.sum()):,}")
tby = pd.concat(rows, ignore_index=True)
w(tby, "ntd_2022_2025_bus_agency_tiers_by_year.csv")
v25 = veh[veh["Report Year"] == "2025"]
print(f"  check: Vehicles table 2025 full-size bus = {int(v25.fullsize_bus.sum()):,} vs RVI total {int(rvi.loc[rvi.is_bus_type,'total'].sum()):,} / active {int(rvi.loc[rvi.is_bus_type,'active'].sum()):,}")

# ---------------------------------------------------------------- (2) rail vehicles by mode
rail = rvi[rvi.has_rail_mode | rvi.is_rail_type].copy()
rail.loc[rail.rail_mode == "", "rail_mode"] = rail.loc[rail.rail_mode == "", "Vehicle Type"].map({
    "Heavy Rail Passenger Car": "HR", "Light Rail Vehicle": "LR", "Vintage Trolley": "SR",
    "Commuter Rail Passenger Coach": "CR", "Commuter Rail Self-Propelled Passenger Car": "CR", LOCO: "CR",
    "Automated Guideway Vehicle": "MG", "Monorail Vehicle": "MG", "Cable Car": "CC", "Inclined Plane Vehicle": "IP",
    "Aerial Tramway": "TR"}).fillna("")
rail = rail[rail.rail_mode != ""]
rail["is_loco"] = rail["Vehicle Type"] == LOCO
rmt = rail.groupby(["rail_mode", "Vehicle Type"]).agg(active=("active", "sum"), total=("total", "sum"), ada=("ada", "sum"),
                                                     operators=("NTD ID", "nunique")).reset_index()
rmt["mode_name"] = rmt["rail_mode"].map(MODE_NAMES)
rmt[["active", "total", "ada"]] = rmt[["active", "total", "ada"]].astype(int)
w(rmt.sort_values(["rail_mode", "active"], ascending=[True, False]), "ntd_2025_rail_vehicles_by_mode_and_type.csv")
rm = rail.groupby("rail_mode").agg(
    active_vehicles_ex_locomotives=("active", lambda s: s[~rail.loc[s.index, "is_loco"]].sum()),
    total_vehicles_ex_locomotives=("total", lambda s: s[~rail.loc[s.index, "is_loco"]].sum()),
    active_locomotives=("active", lambda s: s[rail.loc[s.index, "is_loco"]].sum()),
    operators=("NTD ID", "nunique")).reset_index()
rm["mode_name"] = rm["rail_mode"].map(MODE_NAMES)
rm = rm[["rail_mode", "mode_name", "operators", "active_vehicles_ex_locomotives", "total_vehicles_ex_locomotives", "active_locomotives"]]
for c in rm.columns[2:]:
    rm[c] = rm[c].astype(int)
rm = rm.sort_values("active_vehicles_ex_locomotives", ascending=False)
tot = pd.DataFrame([{"rail_mode": "ALL", "mode_name": "All rail modes", "operators": rail["NTD ID"].nunique(),
                     "active_vehicles_ex_locomotives": rm.active_vehicles_ex_locomotives.sum(),
                     "total_vehicles_ex_locomotives": rm.total_vehicles_ex_locomotives.sum(),
                     "active_locomotives": rm.active_locomotives.sum()}])
rm = pd.concat([rm, tot], ignore_index=True)
print("\n=== (2) Rail vehicles by mode, RVI 2025 ===")
print(rm.to_string(index=False))
w(rm, "ntd_2025_rail_vehicles_by_mode.csv")

# top-20 rail operators
piv = rail[~rail.is_loco].pivot_table(index="NTD ID", columns="rail_mode", values="active", aggfunc="sum", fill_value=0)
for m in ["HR", "LR", "SR", "CR", "YR", "MG", "CC", "IP", "AR", "TR"]:
    if m not in piv.columns:
        piv[m] = 0
piv = piv[["HR", "LR", "SR", "CR", "YR", "MG", "CC", "IP", "AR", "TR"]]
piv.columns = ["active_" + c + "_" + MODE_NAMES[c].lower().replace(" ", "_").replace("/", "_") for c in piv.columns]
piv["active_rail_vehicles_ex_locomotives"] = piv.sum(axis=1)
piv["active_locomotives"] = rail[rail.is_loco].groupby("NTD ID")["active"].sum().reindex(piv.index).fillna(0)
piv["total_rail_vehicles_ex_locomotives_incl_inactive"] = rail[~rail.is_loco].groupby("NTD ID")["total"].sum().reindex(piv.index).fillna(0)
piv = piv.astype(int).reset_index()
piv.insert(1, "agency", piv["NTD ID"].map(aglk["Agency Name"]))
piv.insert(2, "city", piv["NTD ID"].map(aglk["City"]))
piv.insert(3, "state", piv["NTD ID"].map(aglk["State"]))
piv["rail_modes_operated"] = piv["NTD ID"].map(rail.groupby("NTD ID")["rail_mode"].agg(lambda s: ",".join(sorted(set(s)))))
piv = piv.sort_values("active_rail_vehicles_ex_locomotives", ascending=False).reset_index(drop=True)
piv.insert(0, "rank", piv.index + 1)
top20 = piv.head(20).copy()
top20["cum_share_of_active_rail_vehicles_pct"] = (100 * top20["active_rail_vehicles_ex_locomotives"].cumsum() / piv["active_rail_vehicles_ex_locomotives"].sum()).round(1)
print("\n=== Top-20 rail operators by active rail vehicles (ex-locomotives), RVI 2025 ===")
print(top20[["rank", "agency", "state", "active_HR_heavy_rail", "active_LR_light_rail", "active_SR_streetcar", "active_CR_commuter_rail", "active_rail_vehicles_ex_locomotives", "active_locomotives", "cum_share_of_active_rail_vehicles_pct"]].to_string(index=False))
w(top20, "ntd_2025_top20_rail_operators.csv")
w(piv, "ntd_2025_rail_fleet_by_operator_all.csv")

# ---------------------------------------------------------------- (3) capital expenses by category and mode
for c in CAP_CATS:
    cap[c] = num(cap[c])
cap["mode_group"] = cap["Mode"].apply(mode_group)
cap["use_type"] = cap["Capital Use Type"].map(lambda s: "Expansion of service" if "Expansion" in s else ("Existing service (rehab/replace/improve)" if "Existing" in s else "Reduced reporter (not itemised)"))
long = cap.melt(id_vars=["Report Year", "Mode", "Mode Name", "mode_group", "use_type"], value_vars=CAP_CATS, var_name="category", value_name="usd")
long = long.groupby(["Report Year", "mode_group", "Mode", "Mode Name", "category"], as_index=False)["usd"].sum()
long["usd"] = long["usd"].round(0).astype(np.int64)
long = long[long["Report Year"].isin(["2022", "2023", "2024", "2025"])]
w(long.sort_values(["Report Year", "mode_group", "Mode", "category"]), "ntd_capex_by_year_mode_category.csv")

wide = cap.groupby(["Report Year", "mode_group"])[CAP_CATS].sum().round(0).astype(np.int64).reset_index()
tot = cap.groupby(["Report Year"])[CAP_CATS].sum().round(0).astype(np.int64).reset_index()
tot.insert(1, "mode_group", "ALL MODES")
wide = pd.concat([wide, tot], ignore_index=True).sort_values(["Report Year", "mode_group"])
wide["Comm & Info share of Total pct"] = (100 * wide["Communication & Information Systems"] / wide["Total"].replace(0, np.nan)).round(1)
print("\n=== (3) Capital expenses by mode group and category (USD), report years 2022-2025 ===")
print(wide[wide["Report Year"].isin(["2023", "2024", "2025"])][["Report Year", "mode_group", "Guideway", "Stations", "Passenger Vehicles", "Fare Collection Equipment", "Communication & Information Systems", "Total", "Comm & Info share of Total pct"]].to_string(index=False))
w(wide, "ntd_capex_by_year_modegroup_category.csv")

# by individual mode: Comm & Info and Total, years as columns
ci = cap.pivot_table(index=["mode_group", "Mode", "Mode Name"], columns="Report Year", values="Communication & Information Systems", aggfunc="sum", fill_value=0)
ci.columns = ["comm_info_capex_usd_" + c for c in ci.columns]
tt = cap.pivot_table(index=["mode_group", "Mode", "Mode Name"], columns="Report Year", values="Total", aggfunc="sum", fill_value=0)
tt.columns = ["total_capex_usd_" + c for c in tt.columns]
cim = ci.join(tt).round(0).astype(np.int64).reset_index().sort_values(["mode_group", "comm_info_capex_usd_2025"], ascending=[True, False])
w(cim, "ntd_capex_comm_info_by_mode_year.csv")
print("\n  Comm & Info Systems capex by mode (USD m): ")
print((cim.set_index("Mode Name")[["comm_info_capex_usd_2023", "comm_info_capex_usd_2024", "comm_info_capex_usd_2025"]] / 1e6).round(1).to_string())

# existing vs expansion 2025 by mode group
ue = cap[cap["Report Year"] == "2025"].groupby(["mode_group", "use_type"])[["Passenger Vehicles", "Communication & Information Systems", "Total"]].sum().round(0).astype(np.int64).reset_index()
w(ue, "ntd_2025_capex_existing_vs_expansion_by_modegroup.csv")

# cross-check vs 2025 Capital Use file
for c in ["Communication Information Systems", "Total Capital Funds", "Revenue Vehicles", "Fare Revenue Collection Equipment"]:
    cu25[c] = num(cu25[c])
print(f"\n  cross-check 2025 Capital Use file: total {cu25['Total Capital Funds'].sum()/1e9:.3f} $B, comm&info {cu25['Communication Information Systems'].sum()/1e9:.3f} $B, revenue vehicles {cu25['Revenue Vehicles'].sum()/1e9:.3f} $B, fare {cu25['Fare Revenue Collection Equipment'].sum()/1e9:.3f} $B")
c25 = cap[cap["Report Year"] == "2025"]
print(f"  vs Capital Expenses (by Capital Use) 2025: total {c25['Total'].sum()/1e9:.3f} $B, comm&info {c25['Communication & Information Systems'].sum()/1e9:.3f} $B, passenger vehicles {c25['Passenger Vehicles'].sum()/1e9:.3f} $B, fare {c25['Fare Collection Equipment'].sum()/1e9:.3f} $B")

# concentration of Comm & Info capex 2025 by agency
cia = c25.groupby("NTD ID").agg(agency=("Agency", "first"), state=("State", "first"), comm_info_2025=("Communication & Information Systems", "sum"), total_capex_2025=("Total", "sum")).reset_index()
cia3 = cap[cap["Report Year"].isin(["2023", "2024", "2025"])].groupby("NTD ID")["Communication & Information Systems"].sum()
cia["comm_info_2023_2025"] = cia["NTD ID"].map(cia3).fillna(0)
busci = c25[c25["Mode"].isin(BUS_MODES)].groupby("NTD ID")["Communication & Information Systems"].sum()
railci = c25[c25["Mode"].isin(RAIL_MODES)].groupby("NTD ID")["Communication & Information Systems"].sum()
cia["comm_info_2025_bus_modes"] = cia["NTD ID"].map(busci).fillna(0)
cia["comm_info_2025_rail_modes"] = cia["NTD ID"].map(railci).fillna(0)
cia = cia.sort_values("comm_info_2025", ascending=False)
for c in ["comm_info_2025", "total_capex_2025", "comm_info_2023_2025", "comm_info_2025_bus_modes", "comm_info_2025_rail_modes"]:
    cia[c] = cia[c].round(0).astype(np.int64)
cia["cum_share_pct"] = (100 * cia["comm_info_2025"].cumsum() / cia["comm_info_2025"].sum()).round(1)
print(f"  agencies with any Comm&Info capex 2025: {(cia.comm_info_2025>0).sum()} of {len(cia)}; top-10 share {cia.head(10).cum_share_pct.iloc[-1]}%, top-25 share {cia.head(25).cum_share_pct.iloc[-1]}%")
print(cia.head(15)[["agency", "state", "comm_info_2025", "comm_info_2025_bus_modes", "comm_info_2025_rail_modes", "cum_share_pct"]].to_string(index=False))
w(cia.head(100), "ntd_2025_top100_agencies_comm_info_capex.csv")

# time series 2015-2025 (TS 3.1)
ts["Value"] = num(ts["Value"])
ts["mode_group"] = ts["Mode"].apply(mode_group)
tsg = ts.pivot_table(index=["Capital Use Type", "mode_group"], columns="Report Year", values="Value", aggfunc="sum", fill_value=0)
tsa = ts.pivot_table(index=["Capital Use Type"], columns="Report Year", values="Value", aggfunc="sum", fill_value=0)
tsa.index = pd.MultiIndex.from_tuples([(i, "ALL MODES") for i in tsa.index], names=["Capital Use Type", "mode_group"])
tsg = pd.concat([tsg, tsa]).round(0).astype(np.int64).reset_index().sort_values(["Capital Use Type", "mode_group"])
w(tsg, "ntd_capex_time_series_2015_2025_by_modegroup.csv")
print("\n  Capex time series (Total, $B) 2015-2025:")
print((tsg[tsg["Capital Use Type"] == "Total"].set_index("mode_group").drop(columns="Capital Use Type") / 1e9).round(2).to_string())

# ---------------------------------------------------------------- (4) top-50 bus agencies
v22 = veh[veh["Report Year"] == "2022"].groupby("NTD ID")["fullsize_bus"].sum()
v25g = veh[veh["Report Year"] == "2025"].groupby("NTD ID")["fullsize_bus"].sum()
agb["fullsize_bus_2022_vehicles_table"] = agb["NTD ID"].map(v22).fillna(0).astype(int)
agb["fullsize_bus_2025_vehicles_table"] = agb["NTD ID"].map(v25g).fillna(0).astype(int)
agb["comm_info_capex_2025_bus_modes_usd"] = agb["NTD ID"].map(busci).fillna(0).round(0).astype(np.int64)
agb["comm_info_capex_2023_2025_all_modes_usd"] = agb["NTD ID"].map(cia3).fillna(0).round(0).astype(np.int64)
# bus-mode VOMS and UPT from 2025 service file
svc["voms"] = num(svc["Vehicles/Passenger Cars Operated in Maximum Service"])
svc["upt"] = num(svc["Unlinked Passenger Trips (UPT)"])
sa = svc[(svc["Time Period"] == "Annual Total") & svc["Mode"].isin(BUS_MODES)].groupby("NTD ID").agg(bus_mode_voms=("voms", "sum"), bus_mode_upt=("upt", "sum"))
agb["bus_modes_voms_2025"] = agb["NTD ID"].map(sa["bus_mode_voms"]).fillna(0).astype(int)
agb["bus_modes_upt_2025"] = agb["NTD ID"].map(sa["bus_mode_upt"]).fillna(0).astype(np.int64)
agb["has_rail"] = agb["NTD ID"].isin(set(rail["NTD ID"]))
top50 = agb.sort_values("active_fullsize_bus", ascending=False).head(50).reset_index(drop=True)
top50.insert(0, "rank", top50.index + 1)
top50["cum_share_of_active_fullsize_buses_pct"] = (100 * top50["active_fullsize_bus"].cumsum() / agb["active_fullsize_bus"].sum()).round(1)
cols = ["rank", "NTD ID", "agency", "city", "state", "reporter_type", "organization_type", "uza_name", "tier_active_fullsize_bus",
        "active_fullsize_bus", "active_bus", "active_articulated_bus", "active_over_the_road_bus", "active_double_decker_bus", "active_trolleybus",
        "total_fullsize_bus", "active_cutaways_in_bus_modes", "active_busmode_all_types", "active_all_vehicles", "total_voms", "bus_modes_voms_2025", "bus_modes_upt_2025",
        "active_zero_emission_bus_bev_fcev", "avg_age_active_fullsize_bus_yrs", "active_fullsize_bus_at_or_past_ulb",
        "fullsize_bus_2022_vehicles_table", "fullsize_bus_2025_vehicles_table", "comm_info_capex_2025_bus_modes_usd", "comm_info_capex_2023_2025_all_modes_usd", "has_rail",
        "cum_share_of_active_fullsize_buses_pct"]
top50 = top50[cols]
print("\n=== (4) Top-50 bus agencies by active full-size buses, RVI 2025 ===")
print(top50[["rank", "agency", "state", "active_fullsize_bus", "active_articulated_bus", "active_zero_emission_bus_bev_fcev", "avg_age_active_fullsize_bus_yrs", "comm_info_capex_2025_bus_modes_usd", "cum_share_of_active_fullsize_buses_pct"]].to_string(index=False))
w(top50, "ntd_2025_top50_bus_agencies.csv")
# re-write full agency file with the added columns
w(agb.sort_values("active_fullsize_bus", ascending=False), "ntd_2025_bus_fleet_by_agency.csv")

# ---------------------------------------------------------------- agency universe
print("\n=== Agency universe (2025 Reporter Agency Information) ===")
uni = ag.groupby("Reporter Type").agg(agencies=("NTD ID", "nunique"), total_voms=("Total VOMS", "sum")).reset_index()
uni["total_voms"] = uni["total_voms"].astype(int)
busag = set(agb.loc[agb.active_fullsize_bus > 0, "NTD ID"])
railag = set(rail["NTD ID"])
uni["agencies_with_active_fullsize_bus"] = uni["Reporter Type"].map(ag[ag["NTD ID"].isin(busag)].groupby("Reporter Type")["NTD ID"].nunique()).fillna(0).astype(int)
uni["agencies_with_rail"] = uni["Reporter Type"].map(ag[ag["NTD ID"].isin(railag)].groupby("Reporter Type")["NTD ID"].nunique()).fillna(0).astype(int)
uni.loc[len(uni)] = ["ALL", uni.agencies.sum(), uni.total_voms.sum(), uni.agencies_with_active_fullsize_bus.sum(), uni.agencies_with_rail.sum()]
print(uni.to_string(index=False))
w(uni, "ntd_2025_agency_universe.csv")
tam = ag.groupby("TAM Tier").agg(agencies=("NTD ID", "nunique"), total_voms=("Total VOMS", "sum")).reset_index()
print(tam.to_string(index=False))
w(tam, "ntd_2025_agency_tam_tiers.csv")

# ---------------------------------------------------------------- bus fuel mix and age
fm = rvi[rvi.is_bus_type].groupby("Fuel Type").agg(active=("active", "sum"), total=("total", "sum"), agencies=("NTD ID", "nunique")).reset_index().sort_values("active", ascending=False)
fm[["active", "total"]] = fm[["active", "total"]].astype(int)
fm["share_active_pct"] = (100 * fm["active"] / fm["active"].sum()).round(1)
print("\n=== Full-size bus fuel mix 2025 (active) ===")
print(fm.to_string(index=False))
w(fm, "ntd_2025_bus_fuel_mix.csv")
age["Total Vehicles"] = num(age["Total Vehicles"])
age["avg_age"] = num(age["Average Age of Fleet (in Years)"])
age["age_w"] = age["avg_age"] * age["Total Vehicles"]
ad = age[age["Vehicle Type"].isin(BUS_TYPES + RAIL_TYPES + ["Cutaway", "Van", "Minivan"])].groupby(["Report Year", "Vehicle Type"]).agg(vehicles=("Total Vehicles", "sum"), age_w=("age_w", "sum")).reset_index()
ad["weighted_avg_age_yrs"] = (ad["age_w"] / ad["vehicles"].replace(0, np.nan)).round(2)
ad["vehicles"] = ad["vehicles"].astype(int)
ad = ad.drop(columns="age_w")
w(ad, "ntd_2022_2025_fleet_age_by_vehicle_type.csv")
print("\n  Weighted avg fleet age 2025 by type:")
print(ad[ad["Report Year"] == "2025"].to_string(index=False))

# ---------------------------------------------------------------- opex by mode group
for c in ["Total", "Purchased Transportation Reported Separately"]:
    opf[c] = num(opf[c])
for c in ["Services", "Purchased Transportation in Report", "Total"]:
    opt[c] = num(opt[c])
opf["mode_group"] = opf["Mode"].apply(mode_group)
opt["mode_group"] = opt["Mode"].apply(mode_group)
o1 = opf.groupby(["Report Year", "mode_group"]).agg(total_opex_usd=("Total", "sum")).reset_index()
o2 = opt.groupby(["Report Year", "mode_group"]).agg(services_usd=("Services", "sum"), purchased_transportation_usd=("Purchased Transportation in Report", "sum")).reset_index()
ox = o1.merge(o2, on=["Report Year", "mode_group"], how="left")
oa = ox.groupby("Report Year")[["total_opex_usd", "services_usd", "purchased_transportation_usd"]].sum().reset_index()
oa.insert(1, "mode_group", "ALL MODES")
ox = pd.concat([ox, oa], ignore_index=True)
for c in ["total_opex_usd", "services_usd", "purchased_transportation_usd"]:
    ox[c] = ox[c].fillna(0).round(0).astype(np.int64)
ox["services_share_pct"] = (100 * ox["services_usd"] / ox["total_opex_usd"].replace(0, np.nan)).round(1)
print("\n=== Operating expenses by mode group ($B) ===")
print(ox.assign(total_opex_bn=(ox.total_opex_usd / 1e9).round(2), services_bn=(ox.services_usd / 1e9).round(2))[["Report Year", "mode_group", "total_opex_bn", "services_bn", "services_share_pct"]].to_string(index=False))
w(ox, "ntd_2022_2025_opex_by_modegroup.csv")

# concentration summary for bus
s = agb.sort_values("active_fullsize_bus", ascending=False)["active_fullsize_bus"]
tot_b = s.sum()
print("\n=== Bus concentration (active full-size buses) ===")
for k in [10, 20, 50, 100, 200]:
    print(f"  top-{k}: {int(s.head(k).sum()):,} buses = {100*s.head(k).sum()/tot_b:.1f}%")
print(f"  agencies with >=1 active full-size bus: {(s>0).sum()}")
# ---------------------------------------------------------------- ITS-proxy capex intensity by bus tier and rail operator size
busci3 = cap[cap["Report Year"].isin(["2023", "2024", "2025"]) & cap["Mode"].isin(BUS_MODES)].groupby("NTD ID")["Communication & Information Systems"].sum() / 3
agb["comm_info_capex_bus_modes_avg_2023_2025_usd"] = agb["NTD ID"].map(busci3).fillna(0).round(0).astype(np.int64)
d = agb[agb.active_fullsize_bus > 0]
ti = d.groupby("tier_active_fullsize_bus").agg(
    agencies=("NTD ID", "size"), active_fullsize_bus=("active_fullsize_bus", "sum"),
    agencies_with_bus_comm_info_capex_2025=("comm_info_capex_2025_bus_modes_usd", lambda s: int((s > 0).sum())),
    comm_info_capex_2025_bus_modes_usd=("comm_info_capex_2025_bus_modes_usd", "sum"),
    comm_info_capex_bus_modes_avg_2023_2025_usd=("comm_info_capex_bus_modes_avg_2023_2025_usd", "sum")).reset_index()
ti["capex_per_active_bus_2025_usd"] = (ti.comm_info_capex_2025_bus_modes_usd / ti.active_fullsize_bus).round(0)
ti["capex_per_active_bus_avg_2023_2025_usd"] = (ti.comm_info_capex_bus_modes_avg_2023_2025_usd / ti.active_fullsize_bus).round(0)
excl = agb[agb.active_fullsize_bus == 0]["comm_info_capex_2025_bus_modes_usd"].sum()
ti.loc[len(ti)] = ["0: no full-size bus (cutaway/van-only agencies)", int((agb.active_fullsize_bus == 0).sum()), 0,
                   int((agb[agb.active_fullsize_bus == 0]["comm_info_capex_2025_bus_modes_usd"] > 0).sum()), int(excl),
                   int(agb[agb.active_fullsize_bus == 0]["comm_info_capex_bus_modes_avg_2023_2025_usd"].sum()), np.nan, np.nan]
print("\n=== Bus-mode Comm & Info capex intensity by bus fleet tier ===")
print(ti.to_string(index=False))
w(ti, "ntd_2025_bus_tier_comm_info_capex_intensity.csv")

railci3 = cap[cap["Report Year"].isin(["2023", "2024", "2025"]) & cap["Mode"].isin(RAIL_MODES)].groupby("NTD ID")["Communication & Information Systems"].sum() / 3
piv["comm_info_capex_2025_rail_modes_usd"] = piv["NTD ID"].map(railci).fillna(0).round(0).astype(np.int64)
piv["comm_info_capex_rail_modes_avg_2023_2025_usd"] = piv["NTD ID"].map(railci3).fillna(0).round(0).astype(np.int64)
def rtier(n):
    return "4: 1000+" if n >= 1000 else ("3: 500-999" if n >= 500 else ("2: 100-499" if n >= 100 else "1: 1-99"))
piv["rail_fleet_tier"] = piv["active_rail_vehicles_ex_locomotives"].apply(rtier)
rt = piv.groupby("rail_fleet_tier").agg(operators=("NTD ID", "size"), active_rail_vehicles_ex_loco=("active_rail_vehicles_ex_locomotives", "sum"),
                                        comm_info_capex_2025_rail_modes_usd=("comm_info_capex_2025_rail_modes_usd", "sum"),
                                        comm_info_capex_rail_modes_avg_2023_2025_usd=("comm_info_capex_rail_modes_avg_2023_2025_usd", "sum")).reset_index()
rt["capex_per_active_vehicle_2025_usd"] = (rt.comm_info_capex_2025_rail_modes_usd / rt.active_rail_vehicles_ex_loco).round(0)
rt["capex_per_active_vehicle_avg_2023_2025_usd"] = (rt.comm_info_capex_rail_modes_avg_2023_2025_usd / rt.active_rail_vehicles_ex_loco).round(0)
print("\n=== Rail-mode Comm & Info capex intensity by operator fleet size ===")
print(rt.to_string(index=False))
w(rt, "ntd_2025_rail_tier_comm_info_capex_intensity.csv")
w(piv, "ntd_2025_rail_fleet_by_operator_all.csv")
w(agb.sort_values("active_fullsize_bus", ascending=False), "ntd_2025_bus_fleet_by_agency.csv")

print("done")
