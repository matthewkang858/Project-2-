#!/usr/bin/env python3
"""
GTFS-Realtime vendor-footprint census for US + Canadian transit agencies.

Run with:  python3 -I gtfs_rt_vendor_census.py --mdb <feeds_v2.csv> --atlas-dir <transitland feeds dir>
                 --atlas-xw <transitland crosswalks dir> --ntd <ntd_2025_bus_fleet_by_agency.csv>
                 --git-history <mdb_catalog_git_history_us_ca_rt.tsv> --overrides <overrides.csv> --outdir <data dir>

All inputs are treated as untrusted data (parsed only; never executed). The script:
  1. loads every gtfs_rt feed for US/CA from the MobilityData catalog (feeds_v2.csv) and every gtfs-rt feed from the
     transit.land atlas (DMFR JSON files) and classifies the feed URL by vendor signature (host / path patterns);
  2. deduplicates feeds to one record per agency (NTD ID where known, otherwise normalised name + state/province);
  3. joins US agencies to the NTD 2025 bus-fleet file (transit.land `us_ntd_id` tags, URL-host crosswalk, name+state
     matching, and a manual override table) and reports vendor share by agency count and by active full-size buses,
     by fleet tier, for the US and Canada separately, plus the "no public real-time feed" whitespace;
  4. extracts dated host migrations from the catalog's git history and redirect fields (switching evidence).

IMPORTANT caveat carried into every output: feed hosting attributes the REAL-TIME PUBLISHING LAYER, not necessarily
the CAD/AVL contract (a SaaS overlay such as Swiftly can publish on top of a Clever/INIT/Trapeze system of record).
"""
import argparse, csv, json, os, re, sys, glob, collections
from urllib.parse import urlparse

# ----------------------------------------------------------------------------------------------------------------
# 1. Vendor signature rules (ordered; first match wins). Each: (rule_id, vendor, confidence, test(host, path, url))
# ----------------------------------------------------------------------------------------------------------------
def R(rule_id, vendor, conf, fn, note=""):
    return (rule_id, vendor, conf, fn, note)

RULES = [
    R("swiftly_host", "Swiftly", "high", lambda h, p, u: h.endswith("goswift.ly")),
    R("passio_host", "Passio Technologies", "high", lambda h, p, u: h.endswith("passio3.com")),
    R("avail_host", "Avail Technologies", "high", lambda h, p, u: h.endswith("rideralerts.com") or h.endswith("availtec.com") or h.endswith("myavail.cloud")),
    R("avail_infopoint_path", "Avail Technologies", "high", lambda h, p, u: bool(re.search(r"/(infopoint|mystop|tripplanner)/gtfs-?realtime\.ashx", p))),
    R("trapeze_tm_cloud_host", "Trapeze / Vontas (TransitMaster)", "high", lambda h, p, u: h.endswith("trpcloud.com") or h.endswith("vontascloud.com") or h.startswith("tmweb.")),
    R("trapeze_tm_path", "Trapeze / Vontas (TransitMaster)", "high", lambda h, p, u: "tmgtfsrealtimewebservice" in p or "/realtimefeed/" in p),
    R("consat_tmix_host", "Consat Telematics", "high", lambda h, p, u: h.endswith("tmix.se")),
    R("systrans_cadavl_host", "Equans / Ineo Systrans (Navineo)", "high", lambda h, p, u: h.endswith("cadavl.com")),
    R("systrans_profil_path", "Equans / Ineo Systrans (Navineo)", "medium", lambda h, p, u: "profilgtfsrt" in p),
    R("connexionz_host", "Connexionz", "high", lambda h, p, u: h.endswith("connexionz.net")),
    R("connexionz_rtt_path", "Connexionz", "high", lambda h, p, u: "/rtt/public/utility/gtfsrealtime.aspx" in p),
    R("gmv_host", "GMV Syncromatics", "high", lambda h, p, u: h.endswith("syncromatics.com") or h.endswith("gmv.com") or h.endswith("gmvsync.com")),
    R("mapstrat_host", "Strategic Mapping (Mapstrat)", "high", lambda h, p, u: h.endswith("mapstrat.com")),
    R("tripspark_host", "TripSpark (Modaxo)", "high", lambda h, p, u: h.endswith("tripsparkhost.com")),
    R("clever_bustime_host", "Clever Devices (BusTime) / Hitachi MMS", "high", lambda h, p, u: h.startswith("bustime.") or h.startswith("truetime.") or h.startswith("cleverapi.") or "/bustime/" in p),
    R("clever_bustime_path", "Clever Devices (BusTime) / Hitachi MMS", "medium", lambda h, p, u: bool(re.search(r"/gtfsrt(-bus|-train|-rail)?/(alerts|trips|vehicles)$", p))),
    R("eta_host", "ETA Transit Systems", "high", lambda h, p, u: "etaspot.net" in u or h.endswith("etatransit.com")),
    R("peak_host", "Peak Transit", "high", lambda h, p, u: h.endswith("peaktransit.com")),
    R("tripshot_host", "TripShot", "high", lambda h, p, u: h.endswith("tripshot.com")),
    R("mecatran_host", "Mecatran", "high", lambda h, p, u: h.endswith("mecatran.com")),
    R("zenbus_host", "Zenbus", "high", lambda h, p, u: h.endswith("zenbus.net")),
    R("trillium_host", "Trillium (Optibus) - alerts", "high", lambda h, p, u: h.endswith("trilliumtransit.com")),
    R("civilia_host", "Civilia", "high", lambda h, p, u: h.endswith("civilia.ca")),
    R("hubup_host", "Hub'Up", "high", lambda h, p, u: h.endswith("infra-hubup.fr")),
    R("transloc_host", "TransLoc (Modaxo)", "high", lambda h, p, u: "transloc.com" in h),
    R("doublemap_host", "DoubleMap (Ford/Modaxo lineage)", "high", lambda h, p, u: "doublemap.com" in h),
    R("ridesystems_host", "Ride Systems", "high", lambda h, p, u: "ridesystems.net" in h),
    R("cubic_umo_host", "Cubic Umo / NextBus", "high", lambda h, p, u: "nextbus" in h or "umoiq" in h),
    R("simplifytransit_host", "SimplifyTransit (alerts)", "high", lambda h, p, u: h.endswith("simplifytransit.com")),
    R("oba_host", "OneBusAway / TheTransitClock (open source)", "high", lambda h, p, u: "onebusaway" in h or h.endswith("obaweb.org") or h.endswith("obanyc.com") or h.endswith("transitime.org")),
    R("oba_path", "OneBusAway / TheTransitClock (open source)", "medium", lambda h, p, u: "-for-agency/" in p),
    R("exo_chrono", "exo (agency) - Chrono SAEIV", "high", lambda h, p, u: h.endswith("chrono-saeiv.com") or h.endswith("opendata.exo.quebec")),
    R("mtc511_aggregator", "MTC 511 (regional aggregator)", "high", lambda h, p, u: h.endswith("511.org")),
    R("mta_inhouse", "MTA NY in-house (camsys / OBA-derived)", "high", lambda h, p, u: h.endswith("mta.info")),
    R("swiftly_s3_pattern", "Swiftly (probable: S3 '-realtime-prod' bucket pattern)", "low", lambda h, p, u: "amazonaws.com" in h and bool(re.search(r"/[a-z0-9-]+-(realtime|alerts)-prod/", u))),
    R("gmv_gtfs_rt_path", "GMV Syncromatics (probable: '/gtfs-rt/vehiclepositions' path pattern)", "medium", lambda h, p, u: bool(re.search(r"/gtfs-rt/(alerts|tripupdates|vehiclepositions)$", p))),
    R("init_path", "INIT (probable: '/gtfsrealtime/TripUpdates|VehiclePositions' path pattern)", "medium", lambda h, p, u: bool(re.search(r"/gtfsrealtime/(TripUpdates|VehiclePositions|ServiceAlerts)$", urlparse(u).path))),
    R("tm_dir_naming", "Trapeze / Vontas (probable: 'Alert/Alerts.pb' directory naming)", "medium", lambda h, p, u: bool(re.search(r"/(alert/alerts|tripupdate/tripupdates|vehicle/vehiclepositions)\.pb$", p))),
    R("gtfs_underscore_naming", "Modaxo TripSpark/Trapeze (probable: 'GTFS_TripUpdates.pb' naming)", "low", lambda h, p, u: bool(re.search(r"gtfs_(serviceAlerts|tripupdates|vehiclepositions)\.pb$", p))),
    R("consat_vehicleupdates_naming", "Consat Telematics (probable: 'vehicleupdates.pb' naming)", "low", lambda h, p, u: p.endswith("/gtfs-realtime/vehicleupdates.pb") or p.endswith("/gtfs-realtime/tripupdates.pb") or p.endswith("/gtfs-realtime/alerts.pb")),
]

# atlas DMFR file names that are vendor domains => corroborating attribution
ATLAS_GROUP_VENDOR = {
    "passio3.com": "Passio Technologies", "tu-vp.goswift.ly": "Swiftly", "alerts.goswift.ly": "Swiftly",
    "availtec.com": "Avail Technologies", "cadavl.com": "Equans / Ineo Systrans (Navineo)",
    "connexionz.net": "Connexionz", "syncromatics.com": "GMV Syncromatics", "mapstrat.com": "Strategic Mapping (Mapstrat)",
    "metrolinx.tmix.se": "Consat Telematics", "bct.tmix.se": "Consat Telematics", "saguenay.tmix.se": "Consat Telematics",
    "fredericton.tmix.se": "Consat Telematics", "obaweb.org": "OneBusAway / TheTransitClock (open source)",
}

def classify(url, atlas_group=None):
    u = (url or "").strip()
    if not u:
        return ("", "no_url", "", "")
    uu = u if "://" in u else "http://" + u
    pr = urlparse(uu)
    host = pr.netloc.lower().split("@")[-1]
    path = pr.path.lower()
    for rule_id, vendor, conf, fn, _ in RULES:
        try:
            if fn(host, path, uu):
                return (vendor, rule_id, conf, host)
        except Exception:
            continue
    if atlas_group:
        g = atlas_group.replace(".dmfr.json", "")
        for k, v in ATLAS_GROUP_VENDOR.items():
            if g.endswith(k):
                return (v, "atlas_group_" + k, "medium", host)
    return ("Agency-hosted / unattributed", "none", "n/a", host)

# ----------------------------------------------------------------------------------------------------------------
# 2. Helpers
# ----------------------------------------------------------------------------------------------------------------
STATE_NAMES = {"Alabama":"AL","Alaska":"AK","Arizona":"AZ","Arkansas":"AR","California":"CA","Colorado":"CO","Connecticut":"CT","Delaware":"DE","District of Columbia":"DC","Florida":"FL","Georgia":"GA","Hawaii":"HI","Idaho":"ID","Illinois":"IL","Indiana":"IN","Iowa":"IA","Kansas":"KS","Kentucky":"KY","Louisiana":"LA","Maine":"ME","Maryland":"MD","Massachusetts":"MA","Michigan":"MI","Minnesota":"MN","Mississippi":"MS","Missouri":"MO","Montana":"MT","Nebraska":"NE","Nevada":"NV","New Hampshire":"NH","New Jersey":"NJ","New Mexico":"NM","New York":"NY","North Carolina":"NC","North Dakota":"ND","Ohio":"OH","Oklahoma":"OK","Oregon":"OR","Pennsylvania":"PA","Rhode Island":"RI","South Carolina":"SC","South Dakota":"SD","Tennessee":"TN","Texas":"TX","Utah":"UT","Vermont":"VT","Virginia":"VA","Washington":"WA","West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY","Puerto Rico":"PR","Guam":"GU","Virgin Islands":"VI","American Samoa":"AS","Northern Mariana Islands":"MP",
 "Alberta":"AB","British Columbia":"BC","Manitoba":"MB","New Brunswick":"NB","Newfoundland and Labrador":"NL","Nova Scotia":"NS","Ontario":"ON","Prince Edward Island":"PE","Quebec":"QC","Québec":"QC","Saskatchewan":"SK","Yukon":"YT","Northwest Territories":"NT","Nunavut":"NU"}
CA_PROV = {"AB","BC","MB","NB","NL","NS","ON","PE","QC","SK","YT","NT","NU"}
STOP = set("the of and for transit authority district regional transportation county city metropolitan area public system systems services service commission corporation agency inc llc co board commissioners benefit greater inter intercounty dept department municipal mass rapid company".split())

def norm_name(s):
    s = (s or "").lower()
    s = re.sub(r"\(.*?\)", " ", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    toks = [t for t in s.split() if t not in STOP]
    return " ".join(toks)

def tokens(s):
    return set(norm_name(s).split())

def host_of(u):
    uu = u if "://" in (u or "") else "http://" + (u or "")
    return urlparse(uu).netloc.lower()

SHARED_HOSTS_PREFIX = ("api.goswift.ly","passio3.com","s3.amazonaws.com","api.511.org","bct.tmix.se","metrolinx.tmix.se","gtfs-realtime.trilliumtransit.com","api.pugetsound.onebusaway.org","app.mecatran.com","mna.mecatran.com","data.peaktransit.com","zenbus.net","api-endpoint.mta.info","gtfs-rt.infra-hubup.fr","exo.chrono-saeiv.com","opendata.exo.quebec","api.transitime.org","drive.google.com","realtime.prod.dash.obaweb.org","cdn.simplifytransit.com","gtfs-rt.myavail.cloud","data.texas.gov","data.calgary.ca")

def is_shared_host(h):
    return any(h == s or h.endswith("." + s) for s in SHARED_HOSTS_PREFIX) or h.endswith("tmix.se") or h.endswith("cadavl.com") or h.endswith("rideralerts.com") or h.endswith("availtec.com") or h.endswith("connexionz.net") or h.endswith("syncromatics.com") or h.endswith("mapstrat.com") or h.endswith("tripsparkhost.com") or h.endswith("tripshot.com")

# ----------------------------------------------------------------------------------------------------------------
# 3. Main
# ----------------------------------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mdb", required=True); ap.add_argument("--atlas-dir", required=True); ap.add_argument("--atlas-xw", required=True)
    ap.add_argument("--ntd", required=True); ap.add_argument("--git-history", required=True); ap.add_argument("--overrides", required=False)
    ap.add_argument("--outdir", required=True); ap.add_argument("--review-dir", required=False)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    review_dir = a.review_dir or a.outdir
    os.makedirs(review_dir, exist_ok=True)

    # ---- overrides ----
    ov_provider_ntd = {}   # (source, key) -> ntd_id   key = provider name (mdb) or feed id (atlas)
    ov_vendor = {}         # agency_key -> vendor label override
    ov_country = {}        # atlas feed id -> country
    ov_exclude = set()     # agency keys to exclude (non-transit shuttles etc.)
    ov_sor = {}            # ntd_id or agency key -> (system_of_record, source)
    ov_alias = {}          # provider/operator name -> canonical agency name (merge sub-systems)
    ov_exclude_provider = set()  # (scope,key) feed records to drop entirely (non-transit shuttles, ferries, foreign)
    if a.overrides and os.path.exists(a.overrides):
        for r in csv.DictReader(open(a.overrides, encoding="utf-8")):
            sc, key, field, val = r["scope"].strip(), r["key"].strip(), r["field"].strip(), r["value"].strip()
            if field == "ntd_id": ov_provider_ntd[(sc, key)] = "NONE" if val.upper() == "NONE" else "|".join(v.strip().zfill(5) for v in val.split("|") if v.strip())
            elif field == "exclude_record": ov_exclude_provider.add((sc, key))
            elif field == "vendor": ov_vendor[key] = val
            elif field == "country": ov_country[key] = val
            elif field == "exclude": ov_exclude.add(key)
            elif field == "system_of_record": ov_sor[key] = (val, r.get("source_url",""), r.get("note",""))
            elif field == "alias": ov_alias[key] = val

    # ---- NTD ----
    ntd = {}
    for r in csv.DictReader(open(a.ntd, encoding="utf-8")):
        nid = r["NTD ID"].strip().zfill(5)
        ntd[nid] = r
    ntd_by_state = collections.defaultdict(list)
    for nid, r in ntd.items():
        ntd_by_state[r["state"]].append(nid)

    # ---- MobilityData feeds ----
    mdb_rows = list(csv.DictReader(open(a.mdb, encoding="utf-8")))
    mdb_rt = [r for r in mdb_rows if r["data_type"] == "gtfs_rt" and r["location.country_code"] in ("US", "CA")]
    mdb_by_id = {r["id"]: r for r in mdb_rows}

    # ---- transit.land atlas feeds ----
    atlas_feeds = {}   # feed_id -> dict
    atlas_ops = {}     # onestop_id -> dict(name, ntd, feeds)
    for f in sorted(glob.glob(os.path.join(a.atlas_dir, "*.dmfr.json"))):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        grp = os.path.basename(f)
        for fd in d.get("feeds", []):
            fid = fd.get("id")
            atlas_feeds[fid] = {"id": fid, "spec": fd.get("spec"), "urls": fd.get("urls", {}) or {}, "group": grp, "operators": []}
            for op in fd.get("operators", []) or []:
                oid = op.get("onestop_id") or op.get("name")
                o = atlas_ops.setdefault(oid, {"name": op.get("name"), "ntd": (op.get("tags") or {}).get("us_ntd_id"), "feeds": set()})
                o["feeds"].add(fid)
                for af in op.get("associated_feeds", []) or []:
                    if af.get("feed_onestop_id"): o["feeds"].add(af["feed_onestop_id"])
        for op in d.get("operators", []) or []:
            oid = op.get("onestop_id") or op.get("name")
            o = atlas_ops.setdefault(oid, {"name": op.get("name"), "ntd": (op.get("tags") or {}).get("us_ntd_id"), "feeds": set()})
            if not o.get("ntd"): o["ntd"] = (op.get("tags") or {}).get("us_ntd_id")
            for af in op.get("associated_feeds", []) or []:
                if af.get("feed_onestop_id"): o["feeds"].add(af["feed_onestop_id"])
    feed_ops = collections.defaultdict(list)
    for oid, o in atlas_ops.items():
        for fid in o["feeds"]:
            feed_ops[fid].append(oid)
    # crosswalk us-ntd.csv (operator -> feeds)
    xw_path = os.path.join(a.atlas_xw, "us-ntd.csv")
    if os.path.exists(xw_path):
        for r in csv.DictReader(open(xw_path, encoding="utf-8")):
            oid = r["onestop_id"]
            o = atlas_ops.setdefault(oid, {"name": r["name"], "ntd": None, "feeds": set()})
            o["ntd"] = o.get("ntd") or r["external_id"].zfill(5)
            for fid in r["related"].split(";"):
                if fid:
                    o["feeds"].add(fid); feed_ops[fid].append(oid)
    # rt feed -> static feed sibling (f-xxx~rt -> f-xxx) for operator lookup
    def ops_for_feed(fid):
        oids = list(dict.fromkeys(feed_ops.get(fid, [])))
        if not oids and fid.endswith("~rt"):
            oids = list(dict.fromkeys(feed_ops.get(fid[:-3], [])))
        return oids

    # US/CA host set from MDB for atlas country inference
    mdb_hosts_country = {}
    for r in mdb_rt:
        mdb_hosts_country.setdefault(host_of(r["urls.direct_download"]), r["location.country_code"])
    mdb_url_country = {r["urls.direct_download"].strip().lower().rstrip("/"): r for r in mdb_rt}

    # ---- classify feeds ----
    feed_records = []
    # MDB
    for r in mdb_rt:
        vendor, rule, conf, host = classify(r["urls.direct_download"])
        feed_records.append({
            "source": "mobilitydata", "feed_id": r["id"], "agency_name_raw": r["provider"], "country": r["location.country_code"],
            "state": STATE_NAMES.get(r["location.subdivision_name"], r["location.subdivision_name"]), "municipality": r["location.municipality"],
            "entity_type": r["entity_type"], "status": r["status"], "is_official": r["is_official"], "url": r["urls.direct_download"],
            "host": host, "vendor_publishing_layer": vendor, "rule": rule, "rule_confidence": conf, "atlas_group": "",
            "static_reference": r["static_reference"], "redirect_id": r["redirect.id"], "contact_email_domain": (r["feed_contact_email"].split("@")[-1].lower() if "@" in r["feed_contact_email"] else ""),
            "ntd_id_atlas": "", "atlas_operator": "",
        })
    # atlas (one record per URL entity)
    atlas_unresolved = []
    for fid, fd in atlas_feeds.items():
        if fd["spec"] != "gtfs-rt":
            continue
        oids = ops_for_feed(fid)
        # one logical "operator slot" per operator; each operator may carry several NTD IDs (comma-separated tag)
        op_slots = []
        for o in oids:
            op = atlas_ops.get(o, {})
            raw = (op.get("ntd") or "").replace(";", ",")
            ids = [x.strip().zfill(5) for x in raw.split(",") if x.strip()]
            if ids:
                for nid_ in ids: op_slots.append((o, op.get("name") or o, nid_))
            else:
                op_slots.append((o, op.get("name") or o, ""))
        if not op_slots: op_slots = [("", fid, "")]
        ntd_ids = [x[2] for x in op_slots if x[2]]
        opnames = [x[1] for x in op_slots]
        US_ONLY_GROUPS = ("passio3.com", "tripshot.com", "ridesystems.net", "syncromatics.com", "availtec.com", "rideralerts.com", "connexionz.net", "cadavl.com")
        for k in ("realtime_vehicle_positions", "realtime_trip_updates", "realtime_alerts"):
          u = fd["urls"].get(k)
          if not u:
              continue
          for (oid_slot, opname_slot, nid_slot) in op_slots:
            ent = {"realtime_vehicle_positions": "vp", "realtime_trip_updates": "tu", "realtime_alerts": "sa"}[k]
            vendor, rule, conf, host = classify(u, fd["group"])
            # country inference
            country = ov_country.get(fid, "")
            if not country:
                if nid_slot: country = "US"
                elif any(fd["group"].endswith(g + ".dmfr.json") for g in US_ONLY_GROUPS) and "~ca" not in fid: country = "US"
                elif u.strip().lower().rstrip("/") in mdb_url_country: country = mdb_url_country[u.strip().lower().rstrip("/")]["location.country_code"]
                elif host in mdb_hosts_country and not is_shared_host(host): country = mdb_hosts_country[host]
                elif re.search(r"~(on|qc|bc|ab|mb|sk|ns|nb|nl|pe|yt|nt|nu)~ca(~rt)?$", fid) or fid.endswith("~ca~rt") or fid.endswith("~ca") or host.endswith(".ca") or fd["group"].endswith(".ca.dmfr.json"): country = "CA"
                elif host.endswith(".gov") or host.endswith(".us") or re.search(r"~(us)(~rt)?$", fid) or re.search(r"~[a-z]{2}~us", fid): country = "US"
                elif host.endswith("tmix.se") and ("metrolinx" in host or "bct" in host or "bowvalley" in host or "saguenay" in host or "fredericton" in host): country = "CA"
                else: country = ""
            if not country:
                atlas_unresolved.append((fid, host, fd["group"], ";".join(opnames)))
            feed_records.append({
                "source": "transitland_atlas", "feed_id": fid, "agency_name_raw": opname_slot, "country": country,
                "state": "", "municipality": "", "entity_type": ent, "status": "active", "is_official": "", "url": u, "host": host,
                "vendor_publishing_layer": vendor, "rule": rule, "rule_confidence": conf, "atlas_group": fd["group"],
                "static_reference": "", "redirect_id": "", "contact_email_domain": "", "ntd_id_atlas": nid_slot, "atlas_operator": oid_slot,
            })
    with open(os.path.join(review_dir, "review_atlas_unresolved_country.tsv"), "w", encoding="utf-8") as fh:
        for x in atlas_unresolved: fh.write("\t".join(x) + "\n")

    # ---- agency key assignment ----
    # Step A: MDB provider -> NTD via overrides, via URL/host match to atlas records with ntd, via name+state.
    atlas_url_ntd = {}
    atlas_host_ntd = collections.defaultdict(set)
    for fr in feed_records:
        if fr["source"] == "transitland_atlas" and fr["ntd_id_atlas"]:
            atlas_url_ntd[fr["url"].strip().lower().rstrip("/")] = fr["ntd_id_atlas"].split("|")[0]
            if not is_shared_host(fr["host"]): atlas_host_ntd[fr["host"]].add(fr["ntd_id_atlas"].split("|")[0])
    ntd_tokens = {nid: tokens(r["agency"]) for nid, r in ntd.items()}
    def match_ntd_by_name(name, state, municipality):
        cands = ntd_by_state.get(state, [])
        t = tokens(name)
        if not t: return ("", "")
        best = ("", 0.0)
        for nid in cands:
            nt = ntd_tokens[nid]
            if not nt: continue
            inter = len(t & nt); jac = inter / len(t | nt)
            score = jac
            city = (ntd[nid]["city"] or "").lower()
            if municipality and city and municipality.lower() == city: score += 0.25
            if inter >= 2: score += 0.1
            if score > best[1]: best = (nid, score)
        if best[1] >= 0.55: return (best[0], "name_state_match_%.2f" % best[1])
        return ("", "")
    match_log = []
    def canon_name(name):
        n = ov_alias.get(name, name)
        if re.match(r"^BC ?Transit\b", n): n = "BC Transit"
        if re.match(r"^Exo\b", n, re.I): n = "exo"
        if re.match(r"^Maryland Transit Administration", n): n = "Maryland Transit Administration"
        if re.match(r"^Toronto Transit Commission", n): n = "Toronto Transit Commission"
        return n
    # fan-out: a provider override "A|B" duplicates the feed record for each NTD id
    expanded = []
    for fr in feed_records:
        key = ("mdb_provider", fr["agency_name_raw"]) if fr["source"] == "mobilitydata" else ("atlas_feed", fr["feed_id"])
        key_st = ("mdb_provider", fr["agency_name_raw"] + "||" + (fr["state"] or "")) if fr["source"] == "mobilitydata" else key
        if key in ov_exclude_provider or key_st in ov_exclude_provider: continue
        ov = ov_provider_ntd.get(key_st, "") or ov_provider_ntd.get(key, "")
        if ov and ov != "NONE" and "|" in ov:
            for nid_ in ov.split("|"):
                fr2 = dict(fr); fr2["_forced_ntd"] = nid_; expanded.append(fr2)
        elif ov and ov != "NONE":
            fr["_forced_ntd"] = ov; expanded.append(fr)
        elif ov == "NONE":
            fr["_forced_ntd"] = "NONE"; expanded.append(fr)
        else:
            fr["_forced_ntd"] = ""; expanded.append(fr)
    feed_records = expanded
    for fr in feed_records:
        nid, how = "", ""
        if fr["_forced_ntd"] == "NONE":
            nid, how = "", "override_no_ntd"
        elif fr["_forced_ntd"]:
            nid, how = fr["_forced_ntd"], "override"
        elif fr["source"] == "mobilitydata":
            key = ("mdb_provider", fr["agency_name_raw"])
            if False: pass
            elif fr["url"].strip().lower().rstrip("/") in atlas_url_ntd: nid, how = atlas_url_ntd[fr["url"].strip().lower().rstrip("/")], "atlas_url_match"
            elif fr["host"] in atlas_host_ntd and len(atlas_host_ntd[fr["host"]]) == 1: nid, how = next(iter(atlas_host_ntd[fr["host"]])), "atlas_host_match"
            elif fr["country"] == "US": nid, how = match_ntd_by_name(fr["agency_name_raw"], fr["state"], fr["municipality"])
        else:
            if fr["ntd_id_atlas"]: nid, how = fr["ntd_id_atlas"], "atlas_ntd_tag"
        if nid and nid not in ntd: nid, how = "", "ntd_id_not_in_bus_file:" + nid
        fr["ntd_id"] = nid; fr["ntd_match_method"] = how
        if nid:
            fr["ntd_agency"] = ntd[nid]["agency"]; fr["active_fullsize_bus"] = ntd[nid]["active_fullsize_bus"]; fr["tier"] = ntd[nid]["tier_active_fullsize_bus"]; fr["state"] = fr["state"] or ntd[nid]["state"]
        else:
            fr["ntd_agency"] = ""; fr["active_fullsize_bus"] = ""; fr["tier"] = ""
        # agency key
        canon = canon_name(fr["agency_name_raw"])
        # Canada: province is only present in the MobilityData catalog, so key Canadian agencies on name alone
        fr["agency_key"] = ("ntd:" + nid) if nid else ("name:" + fr["country"] + ":" + ((fr["state"] or "") if fr["country"] != "CA" else "") + ":" + norm_name(canon))
        match_log.append((fr["source"], fr["agency_name_raw"], fr["state"], fr["country"], nid, how, fr["agency_key"]))
    # de-duplicate non-NTD agencies across catalogs by exact URL, then by non-shared host (Canada and non-NTD US)
    url_key = {}; host_key = {}
    for fr in feed_records:
        if fr["source"] == "mobilitydata" and not fr["ntd_id"]:
            url_key.setdefault(fr["url"].strip().lower().rstrip("/"), fr["agency_key"])
            if not is_shared_host(fr["host"]): host_key.setdefault(fr["host"], fr["agency_key"])
    for fr in feed_records:
        if fr["source"] == "transitland_atlas" and not fr["ntd_id"]:
            u = fr["url"].strip().lower().rstrip("/")
            if u in url_key: fr["agency_key"] = url_key[u]; fr["ntd_match_method"] = "dedup_mdb_url"
            elif fr["host"] in host_key: fr["agency_key"] = host_key[fr["host"]]; fr["ntd_match_method"] = "dedup_mdb_host"

    with open(os.path.join(a.outdir, "gtfs_rt_feeds_classified.csv"), "w", newline="", encoding="utf-8") as fh:
        cols = ["source","feed_id","agency_name_raw","country","state","municipality","entity_type","status","is_official","url","host","vendor_publishing_layer","rule","rule_confidence","atlas_group","ntd_id","ntd_match_method","ntd_agency","active_fullsize_bus","tier","agency_key","static_reference","redirect_id","contact_email_domain","atlas_operator"]
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore"); w.writeheader()
        for fr in feed_records: w.writerow(fr)
    with open(os.path.join(review_dir, "review_match_log.tsv"), "w", encoding="utf-8") as fh:
        for x in match_log: fh.write("\t".join(str(y) for y in x) + "\n")

    # ---- agency census ----
    agencies = {}
    for fr in feed_records:
        if fr["country"] not in ("US", "CA"): continue
        k = fr["agency_key"]
        if k in ov_exclude: continue
        ag = agencies.setdefault(k, {"agency_key": k, "country": fr["country"], "state": fr["state"], "ntd_id": fr["ntd_id"], "ntd_agency": fr["ntd_agency"], "names": set(), "vendors_vp_tu": collections.Counter(), "vendors_sa": collections.Counter(), "vendors_vp_tu_active": collections.Counter(), "hosts": set(), "sources": set(), "feeds": 0, "feeds_active": 0, "rules": set(), "confs": set(), "deprecated_vendors": collections.Counter()})
        ag["names"].add(fr["agency_name_raw"]); ag["hosts"].add(fr["host"]); ag["sources"].add(fr["source"]); ag["feeds"] += 1
        ag["rules"].add(fr["rule"]); ag["confs"].add(fr["rule_confidence"])
        if not ag["state"] and fr["state"]: ag["state"] = fr["state"]
        ent = fr["entity_type"]
        is_vp_tu = ("vp" in ent) or ("tu" in ent)
        if fr["status"] == "deprecated":
            ag["deprecated_vendors"][fr["vendor_publishing_layer"]] += 1
            continue
        ag["feeds_active"] += 1
        if is_vp_tu: ag["vendors_vp_tu"][fr["vendor_publishing_layer"]] += 1
        else: ag["vendors_sa"][fr["vendor_publishing_layer"]] += 1
    rows_out = []
    for k, ag in agencies.items():
        vv = ag["vendors_vp_tu"]
        if ag["ntd_id"] and ag["ntd_id"] in ov_vendor: primary = ov_vendor[ag["ntd_id"]]; conf = "override"
        elif k in ov_vendor: primary = ov_vendor[k]; conf = "override"
        elif vv:
            # prefer attributed vendors over 'Agency-hosted / unattributed' and over aggregators when co-published
            ranked = sorted(vv.items(), key=lambda x: (x[0].startswith("Agency-hosted"), x[0].startswith("MTC 511"), -x[1], x[0]))
            primary = ranked[0][0]; conf = "feed_rule"
        elif ag["vendors_sa"]:
            primary = "(alerts-only) " + sorted(ag["vendors_sa"].items(), key=lambda x: -x[1])[0][0]; conf = "feed_rule_alerts_only"
        else:
            primary = "(deprecated-only) " + (sorted(ag["deprecated_vendors"].items(), key=lambda x: -x[1])[0][0] if ag["deprecated_vendors"] else ""); conf = "deprecated_only"
        fleet = ntd[ag["ntd_id"]]["active_fullsize_bus"] if ag["ntd_id"] else ""
        tier = ntd[ag["ntd_id"]]["tier_active_fullsize_bus"] if ag["ntd_id"] else ""
        sor = ov_sor.get(ag["ntd_id"] or "", ov_sor.get(k, ("", "", "")))
        rows_out.append({
            "agency_key": k, "country": ag["country"], "state": ag["state"], "ntd_id": ag["ntd_id"], "ntd_agency": ag["ntd_agency"],
            "names_in_catalogs": " | ".join(sorted(ag["names"]))[:300], "primary_rt_publisher": primary, "primary_attribution": conf,
            "all_vp_tu_vendors_active": "; ".join(f"{v} ({n})" for v, n in sorted(vv.items(), key=lambda x: -x[1])),
            "alerts_only_vendors_active": "; ".join(f"{v} ({n})" for v, n in sorted(ag["vendors_sa"].items(), key=lambda x: -x[1])),
            "deprecated_feed_vendors": "; ".join(f"{v} ({n})" for v, n in sorted(ag["deprecated_vendors"].items(), key=lambda x: -x[1])),
            "has_active_vp_or_tu_feed": "yes" if vv else "no", "n_feeds_total": ag["feeds"], "n_feeds_active": ag["feeds_active"],
            "hosts": " | ".join(sorted(ag["hosts"]))[:300], "catalog_sources": "+".join(sorted(ag["sources"])), "rule_confidence_set": "/".join(sorted(c for c in ag["confs"] if c)),
            "active_fullsize_bus_ntd2025": fleet, "fleet_tier": tier, "cad_avl_system_of_record": sor[0], "system_of_record_source": sor[1], "system_of_record_note": sor[2],
            "overlay_flag": "yes" if (sor[0] and primary.startswith("Swiftly") and not sor[0].lower().startswith("swiftly")) or (len([v for v in vv if not v.startswith("Agency") and not v.startswith("MTC")]) >= 2) else "",
        })
    rows_out.sort(key=lambda r: (r["country"], -(float(r["active_fullsize_bus_ntd2025"]) if r["active_fullsize_bus_ntd2025"] else -1), r["agency_key"]))
    # NTD agencies with no feed at all (whitespace)
    covered_ntd = set(r["ntd_id"] for r in rows_out if r["ntd_id"])
    for nid, r in ntd.items():
        if nid in covered_ntd: continue
        rows_out.append({"agency_key": "ntd:" + nid, "country": "US", "state": r["state"], "ntd_id": nid, "ntd_agency": r["agency"], "names_in_catalogs": "", "primary_rt_publisher": "NO PUBLIC FEED CATALOGUED", "primary_attribution": "whitespace",
                         "all_vp_tu_vendors_active": "", "alerts_only_vendors_active": "", "deprecated_feed_vendors": "", "has_active_vp_or_tu_feed": "no", "n_feeds_total": 0, "n_feeds_active": 0, "hosts": "", "catalog_sources": "", "rule_confidence_set": "",
                         "active_fullsize_bus_ntd2025": r["active_fullsize_bus"], "fleet_tier": r["tier_active_fullsize_bus"], "cad_avl_system_of_record": ov_sor.get(nid, ("", "", ""))[0], "system_of_record_source": ov_sor.get(nid, ("", "", ""))[1], "system_of_record_note": ov_sor.get(nid, ("", "", ""))[2], "overlay_flag": ""})
    with open(os.path.join(a.outdir, "gtfs_rt_agency_census.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows_out[0].keys())); w.writeheader()
        for r in rows_out: w.writerow(r)

    # ---- top-100 NTD manual-review table ----
    top = [r for r in rows_out if r["country"] == "US" and r["ntd_id"]]
    top.sort(key=lambda r: -float(r["active_fullsize_bus_ntd2025"] or 0))
    with open(os.path.join(a.outdir, "gtfs_rt_top100_ntd_review.csv"), "w", newline="", encoding="utf-8") as fh:
        cols = ["rank", "ntd_id", "ntd_agency", "state", "active_fullsize_bus_ntd2025", "fleet_tier", "primary_rt_publisher", "all_vp_tu_vendors_active", "hosts", "catalog_sources", "rule_confidence_set", "cad_avl_system_of_record", "system_of_record_source", "overlay_flag"]
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore"); w.writeheader()
        for i, r in enumerate(top[:100]):
            r2 = dict(r); r2["rank"] = i + 1; w.writerow(r2)

    # ---- vendor share tables ----
    def vendor_family(v):
        v = v or ""
        suffix = " (probable)" if "probable" in v.lower() else ""
        for key, fam in [("Swiftly","Swiftly"),("Passio","Passio"),("Avail","Avail"),("Trapeze","Trapeze/Vontas (Modaxo)"),("Modaxo TripSpark","TripSpark/Trapeze (Modaxo, probable)"),("TripSpark","TripSpark (Modaxo)"),("Clever","Clever Devices / Hitachi MMS"),("Consat","Consat Telematics"),("Systrans","Equans / Ineo Systrans"),("Connexionz","Connexionz"),("GMV","GMV Syncromatics"),("INIT","INIT"),("Strategic Mapping","Strategic Mapping"),("OneBusAway","OneBusAway / open source"),("ETA","ETA Transit"),("Peak","Peak Transit"),("TripShot","TripShot"),("Mecatran","Mecatran"),("Zenbus","Zenbus"),("Trillium","Trillium (Optibus) alerts-only"),("MTC 511","MTC 511 aggregator"),("MTA NY","MTA NY in-house"),("exo","exo in-house"),("Civilia","Civilia"),("Hub'Up","Hub'Up"),("Cubic","Cubic Umo"),("TransLoc","TransLoc"),("DoubleMap","DoubleMap"),("SimplifyTransit","SimplifyTransit"),("Agency-hosted","Agency-hosted / unattributed"),("NO PUBLIC","No public feed (whitespace)"),("(alerts-only)","Alerts-only feed"),("(deprecated-only)","Deprecated feed only")]:
            if key.lower() in v.lower(): return fam + (suffix if fam not in ("No public feed (whitespace)", "Agency-hosted / unattributed") else "")
        return v
    share_rows = []
    for country in ("US", "CA"):
        sub = [r for r in rows_out if r["country"] == country]
        tiers = ["1: 1-49", "2: 50-249", "3: 250-999", "4: 1000+", "ALL (tiers 1-4)", "memo: NTD agencies with 0 full-size buses", "memo: catalog agencies not in NTD bus file"] if country == "US" else ["ALL (no fleet universe)"]
        for tier in tiers:
            if country == "US":
                if tier == "ALL (tiers 1-4)": tsub = [r for r in sub if r["fleet_tier"] in ("1: 1-49", "2: 50-249", "3: 250-999", "4: 1000+")]
                elif tier.startswith("memo: NTD agencies with 0"): tsub = [r for r in sub if r["ntd_id"] and r["fleet_tier"] not in ("1: 1-49", "2: 50-249", "3: 250-999", "4: 1000+")]
                elif tier.startswith("memo: catalog"): tsub = [r for r in sub if not r["ntd_id"]]
                else: tsub = [r for r in sub if r["fleet_tier"] == tier]
            else:
                tsub = sub
            n_ag = len(tsub); fleet_tot = sum(float(r["active_fullsize_bus_ntd2025"] or 0) for r in tsub)
            fam = collections.defaultdict(lambda: [0, 0.0])
            for r in tsub:
                f = vendor_family(r["primary_rt_publisher"]); fam[f][0] += 1; fam[f][1] += float(r["active_fullsize_bus_ntd2025"] or 0)
            for f, (n, fl) in sorted(fam.items(), key=lambda x: -x[1][1] if country == "US" else -x[1][0]):
                share_rows.append({"country": country, "fleet_tier": tier, "vendor_family": f, "agencies": n, "agency_share_pct": round(100 * n / n_ag, 1) if n_ag else "", "active_fullsize_buses": int(fl), "fleet_share_pct": round(100 * fl / fleet_tot, 1) if fleet_tot else "", "universe_agencies": n_ag, "universe_buses": int(fleet_tot)})
    with open(os.path.join(a.outdir, "gtfs_rt_vendor_share_by_tier.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(share_rows[0].keys())); w.writeheader()
        for r in share_rows: w.writerow(r)

    # ---- migrations from git history + redirects ----
    mig = []
    hist = collections.defaultdict(list)
    with open(a.git_history, encoding="utf-8") as fh:
        rd = csv.DictReader(fh, delimiter="\t")
        for r in rd: hist[r["file"]].append(r)
    for f, evs in hist.items():
        prov = evs[0]["provider"]
        sets = sorted([e for e in evs if e["event"] == "url_set"], key=lambda e: e["date"])
        rems = [e for e in evs if e["event"] == "url_removed"]
        added = [e for e in evs if e["event"] == "file_added"]
        first_date = added[0]["date"][:10] if added else ""
        # pair removed->set in same commit with host change
        by_commit = collections.defaultdict(lambda: {"rem": [], "set": []})
        for e in sets: by_commit[e["commit"]]["set"].append(e["url"])
        for e in rems: by_commit[e["commit"]]["rem"].append(e["url"])
        for e in sets:
            c = by_commit[e["commit"]]
            for old in c["rem"]:
                oh, nh = host_of(old), host_of(e["url"])
                if oh != nh:
                    ov_, _, _, _ = classify(old); nv_, _, _, _ = classify(e["url"])
                    mig.append({"evidence": "catalog_git_url_change", "feed_file": f, "provider": prov, "date": e["date"][:10], "old_host": oh, "new_host": nh, "old_vendor": ov_, "new_vendor": nv_, "vendor_changed": "yes" if ov_ != nv_ else "no", "commit": e["commit"][:10]})
        for e in evs:
            if e["event"] == "status_set" and e["url"] == "deprecated":
                mig.append({"evidence": "catalog_git_status_deprecated", "feed_file": f, "provider": prov, "date": e["date"][:10], "old_host": "", "new_host": "", "old_vendor": "", "new_vendor": "", "vendor_changed": "", "commit": e["commit"][:10]})
        if first_date:
            curr = sets[-1]["url"] if sets else ""
            cv, _, _, _ = classify(curr)
            mig.append({"evidence": "catalog_git_feed_first_added", "feed_file": f, "provider": prov, "date": first_date, "old_host": "", "new_host": host_of(curr), "old_vendor": "", "new_vendor": cv, "vendor_changed": "", "commit": added[0]["commit"][:10]})
    # redirects (dated with the new feed's first-added commit and the old feed's deprecation commit)
    sid_added = {}; sid_deprecated = {}
    for f, evs in hist.items():
        sid = str(evs[0]["mdb_source_id"])
        for e in evs:
            if e["event"] == "file_added": sid_added[sid] = e["date"][:10]
            if e["event"] == "status_set" and e["url"] == "deprecated": sid_deprecated[sid] = e["date"][:10]
    def sid_of(mdb_id):
        m = re.search(r"(\d+)$", mdb_id or ""); return m.group(1) if m else ""
    for r in mdb_rt:
        if r["redirect.id"]:
            for rid in r["redirect.id"].split("|"):
                new = mdb_by_id.get(rid.strip())
                if not new: continue
                ov_, _, _, _ = classify(r["urls.direct_download"]); nv_, _, _, _ = classify(new["urls.direct_download"])
                d_new = sid_added.get(sid_of(rid.strip()), ""); d_old = sid_deprecated.get(sid_of(r["id"]), "")
                mig.append({"evidence": "catalog_redirect", "feed_file": r["id"] + "->" + rid.strip(), "provider": r["provider"], "date": d_new or d_old, "old_host": host_of(r["urls.direct_download"]), "new_host": host_of(new["urls.direct_download"]), "old_vendor": ov_, "new_vendor": nv_, "vendor_changed": "yes" if ov_ != nv_ else "no", "commit": ("new_feed_added:" + d_new + ";old_feed_deprecated:" + d_old)})
    with open(os.path.join(a.outdir, "gtfs_rt_feed_migrations.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["evidence","feed_file","provider","date","old_host","new_host","old_vendor","new_vendor","vendor_changed","commit"]); w.writeheader()
        for r in sorted(mig, key=lambda x: (x["provider"], x["date"])): w.writerow(r)

    # ---- summary to stdout ----
    print("MDB US/CA gtfs_rt rows:", len(mdb_rt), "| atlas gtfs-rt feed-url records (all countries):", sum(1 for fr in feed_records if fr["source"] == "transitland_atlas"),
          "| atlas unresolved country:", len(atlas_unresolved))
    for country in ("US", "CA"):
        sub = [r for r in rows_out if r["country"] == country]
        print(country, "agencies in census:", len(sub), "| with active vp/tu feed:", sum(1 for r in sub if r["has_active_vp_or_tu_feed"] == "yes"), "| NTD-matched:", sum(1 for r in sub if r["ntd_id"]))
    t14 = [r for r in rows_out if r["country"] == "US" and r["fleet_tier"] in ("1: 1-49", "2: 50-249", "3: 250-999", "4: 1000+")]
    print("US NTD agencies with >=1 active full-size bus (tiers 1-4):", len(t14), "| with any catalogued feed:", sum(1 for r in t14 if r["primary_attribution"] != "whitespace"), "| with active vp/tu feed:", sum(1 for r in t14 if r["has_active_vp_or_tu_feed"] == "yes"))
    fl = sum(float(r["active_fullsize_bus_ntd2025"] or 0) for r in t14); flc = sum(float(r["active_fullsize_bus_ntd2025"] or 0) for r in t14 if r["has_active_vp_or_tu_feed"] == "yes")
    print("  buses in tiers 1-4:", int(fl), "| buses at agencies with active vp/tu feed:", int(flc), "(%.1f%%)" % (100 * flc / fl))
    print("US NTD bus agencies (bus file):", len(ntd), "| whitespace rows (no feed catalogued, all tiers):", sum(1 for r in rows_out if r["primary_attribution"] == "whitespace"))

if __name__ == "__main__":
    main()
