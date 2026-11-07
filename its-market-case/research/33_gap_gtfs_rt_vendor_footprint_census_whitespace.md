# 33. Gap fill: GTFS-Realtime vendor-footprint census and whitespace (US + Canada real-time/AVL layer)

**Task:** `gtfs_rt_vendor_footprint_census_whitespace` — quantify vendor footprint and whitespace for the real-time/AVL publishing layer across US and Canadian transit agencies by classifying every public GTFS-Realtime (GTFS-RT) feed URL by vendor signature, deduplicating to one record per agency, joining to the NTD 2025 bus-fleet universe (file 16 / `ntd_2025_bus_fleet_by_agency.csv`) and dating feed migrations from the MobilityData catalog's git history.

**Date of research:** 2026-11-07. **Research conditions:** the shared WebSearch budget was already exhausted when this agent started (every search returned the budget notice), and the session's WebFetch cannot resolve vendor domains (goswift.ly, passiotech.com, availtec.com, transitapp.com, connexionz.com, etatransit.com, gmvsyncromatics.com all ENOTFOUND). Everything below therefore rests on (a) two downloaded feed catalogues and their git history, (b) primary pages fetched with `curl` through the session proxy (systrans.com, bctransit.com, mta.maryland.gov, communitytransit.org, transitapp.com/partners, goswift.ly/about, hitachimms.com, passiotech.com, availtec.com, tripspark.com), (c) RDAP registry records for the hosting domains, and (d) the award evidence already compiled in files 12, 31 and 35. All downloaded data were treated as untrusted input and parsed only with `python3 -I`.

**The single most important caveat, repeated on every table:** *feed hosting attributes the real-time PUBLISHING layer, not necessarily the CAD/AVL contract.* A SaaS overlay (Swiftly, a regional aggregator, an open-source OneBusAway server) can publish GTFS-RT on top of a Clever/INIT/Trapeze system of record, and large agencies often publish in-house. Section 8 separates the two layers wherever the system of record is evidenced.

---

## 1. Key takeaways

1. **Coverage of the census.** The MobilityData catalogue (feeds_v2.csv, 2026-11-07) holds **1,095 US/CA gtfs_rt rows from 359 providers**; the transit.land atlas (commit df1e677, 2026-11-05) adds 873 gtfs-rt feed records worldwide and, crucially, `us_ntd_id` tags on 1,187 operator records plus a 1,216-row NTD crosswalk. Union of the two, deduplicated: **491 US agencies and 57 Canadian agencies with an active vehicle-position or trip-update feed.** Against the NTD universe of **977 US agencies with at least one active full-size bus (65,239 buses)**, **361 agencies (37%) have any catalogued public real-time feed and 358 (36.6%) an active VP/TU feed; those agencies operate 51,080 buses (78.3% of the fleet).** Only 16 of the 361 were found in MobilityData alone; 145 were found only in transit.land, so a single-catalogue census would understate coverage by roughly 40%.

2. **Whitespace is large by agency count and concentrated in the small tier, but not trivial in fleet terms.** **616 of 977 NTD bus agencies (63.1%), operating 13,870 full-size buses (21.3%), have no public real-time feed in either catalogue.** By tier: 1–49 buses: 574 of 772 agencies (74.4%) and 6,085 of 10,541 buses (57.7%); 50–249: 36 of 149 (24.2%) and 3,385 of 15,142 buses (22.4%); 250–999: 5 of 46 (10.9%) and 1,858 buses (9.1%); 1,000+: 1 of 10 (NJ Transit, 2,542 buses, whose Clever system feeds a registration-only developer portal rather than an open feed). The 42 whitespace agencies in tiers 2–4 (7,785 buses) are listed in Section 6; several have a known CAD/AVL vendor but no open feed (NJ Transit/Clever, New Orleans RTA/Clever, DART/INIT), i.e. whitespace in *open data* is not the same as whitespace in *CAD/AVL*.

3. **Measured publishing-layer shares (US, tiers 1–4, primary publisher per agency; shares of the 977-agency / 65,239-bus universe):** agency in-house or unattributed hosts 23 agencies / 12,370 buses (19.0%); **Swiftly 40 agencies / 7,817 buses (12.0%)** plus 2 probable (S3 bucket pattern: King County Metro, Community Transit; 1,540 buses, 2.4%); MTA New York in-house 3 / 5,995 (9.2%); **Clever Devices BusTime 26 / 4,747 (7.3%)**; **Avail 68 agencies / 4,332 buses (7.0% of agencies, 6.6% of buses)**; **Trapeze/Vontas TransitMaster 16 / 3,243 (5.0%) plus 13 probable / 1,625 (2.5%)**; MTC 511 aggregator 13 / 1,783; GMV Syncromatics 9 confirmed + 33 probable / 2,371 (3.6%); Mecatran 7 / 1,082 (Valley Metro regional, San Diego MTS); OneBusAway open source 4 / 1,015; Passio 44 agencies / 789 buses; Equans/Ineo Systrans 15 / 711; Connexionz 19 / 702; INIT-pattern 3 / 549; ETA 10 / 338; TripSpark 2, TripShot 4, Peak 3, Strategic Mapping 1, TransLoc 1. Expressed as a share of the *catalogued* fleet (51,369 buses at agencies with any feed) Swiftly publishes for 15.2% (+3.0% probable), Clever BusTime 9.2%, Avail 8.4%, Trapeze/Vontas 6.3% (+3.2%), GMV 2.7% (+1.9%).

4. **The tiers tell different stories.** In the 1,000+ tier the publishing layer is in-house at 7 of 10 agencies (CTA, SEPTA, WMATA, MBTA, Houston METRO, NYCT, MTA Bus) and Swiftly at LA Metro (plus probably King County Metro) — the CAD/AVL vendors behind those feeds are Clever (CTA, WMATA, NJ Transit, NYCT onboard, LA Metro from 2025), INIT (Houston 2003, King County ~2016) and unknown for SEPTA/MBTA. In the 250–999 tier Swiftly is the single largest attributed publisher (8 agencies, 4,064 buses, 19.9% of the tier's fleet, plus Community Transit probable), ahead of Clever BusTime (5 / 2,348) and Trapeze/Vontas (5 confirmed + 3 probable / 3,018). **In the 50–249 tier — the mid-market a new entrant would target — Avail is the leading publisher (32 of 149 agencies, 21.5%; 3,067 buses, 20.3%), followed by Clever BusTime (19 / 2,321), Swiftly (11 / 1,378), Trapeze/Vontas (8+6 / 1,667) and GMV (2+7 / 640), with 36 agencies (3,385 buses) still without any feed.** In the 1–49 tier the attributed publishers are the SaaS/light-ITS vendors — Avail 35, Passio 41, GMV 30, Swiftly 20, Connexionz 15, Equans 11, ETA 8 — and 574 agencies have nothing.

5. **Canada (57 agencies catalogued; no fleet universe available in this project):** **Consat Telematics hosts 22 agencies (38.6%) plus 2 probable** — BC Transit's NextRide (one contract covering 35 sub-systems, consolidated here to one agency) and the 14 small Ontario municipalities procured through Metrolinx's Transit Procurement Initiative, plus Saguenay, Sudbury, North Bay, Medicine Hat, Ontario Northland, Bow Valley; agency-hosted 8 (Calgary, TransLink, STM, OC Transpo, Grand River, Transcollines, Regina alerts, REM alerts); Trapeze/Vontas 3 confirmed (Edmonton, Guelph, Saskatoon on Trapeze cloud) + 6 probable (Halifax, London, MiWay, Barrie, Burlington, Hamilton); Zenbus 6 (small Québec systems); exo's Chrono platform 3 (exo, RTL Longueuil, STS Sherbrooke); INIT-pattern 2 (York Region, Durham Region); Hub'Up 2; Equans 1 (Brampton, on bt-cadavl.com — consistent with its 2023 Equans award); Civilia 1; Clever 1 (TTC VISION). Winnipeg, Laval, RTC Québec, STO Gatineau, Lévis, Trois-Rivières, Windsor, Oakville, Niagara, Red Deer, Lethbridge, Moncton, Saint John and St. John's have static GTFS in the atlas but no GTFS-RT record (not individually verified).

6. **Two first-pass attributions were wrong and are corrected here.** (a) `bct.tmix.se` is **not Trapeze**: "Tmix" is the product namespace of **Consat Telematics** (Swedish .se host; BC Transit's own NextRide page names Consat as the contracted AVL supplier; the same host family serves Metrolinx TPI municipalities, Saguenay, Fredericton, Sudbury and Bow Valley; Calgary's January-2025 CAD/AVL award also went to Consat, file 31). (b) `*.cadavl.com` and the `ProfilGtfsRt2_0RSProducer-*` path are **Equans/Ineo Systrans NAVINEO**: systrans.com carries a Green Bay Metro testimonial, Marin's feed moved to `gtfsrt.marintransit.cadavl.com` on 2026-03-11 after its January-2025 Systrans award, and Brampton (Equans, 2023) publishes from `bt-cadavl.com`. The transit.land atlas lists 15 US agencies on cadavl.com (Rock Region Metro, Corpus Christi, Collier, Greenlink, Williamsburg, GATRA, Worcester, Lowell, Portland ME, Green Bay, Jackson WY, Kanawha Valley, Memphis MATA, Park City, Rochester MN) plus Rogue Valley and Marin — Systrans' North-American footprint is therefore ~17 agencies, a material fact for the competitive section (systrans.com claims 250+ agencies and 60,000+ vehicles in 12 countries).

7. **Overlay-on-legacy is measurable, not anecdotal.** 49 US tier-1–4 agencies (9,856 buses) have a Swiftly VP/TU feed. Where the CAD/AVL system of record is evidenced in files 12/31/35 or by a co-published vendor feed, Swiftly sits on top of: Clever (LA Metro, Miami-Dade, SMART Detroit; AC Transit, County Connection and MARTA by contract), INIT (NCTD; King County and Community Transit probable; Suffolk County co-published), Vontas/Trapeze (GCRTA — both feeds live; CapMetro alerts), Avail (Pioneer Valley and GoDurham co-published; IndyGo by contract), GMV→Equans (Marin), GMV (Merrimack Valley), Equans (Williamsburg), Connexionz (Corvallis), Passio (Frederick County) and OneBusAway servers (HART Tampa, Alexandria DASH, Denton DCTA). **At least 26 agencies therefore pay Swiftly for a layer they could in principle get from the CAD/AVL incumbent — this is the SaaS-entry wedge in the investment thesis, and it is visible in the data.**

8. **Switching is visible and dated.** From the catalogue's redirect field and git history (916 commits, 2021-07 to 2026-10): BC Transit moved 7 systems from Strategic Mapping to Consat (16–23 Apr 2025); TARC from a TransitMaster-pattern host to Avail (4 Jun 2025, matching its 2023 Avail onboard-ITS award); Marin from GMV to Swiftly + Equans (11 Mar 2026); Madison Metro from TransitMaster-pattern to Clever BusTime (29 Aug 2024, catalogue note "New AVL feed redirect"); CTtransit from an S3 bucket to Trapeze cloud (31 Mar 2025); Via Mobility (27 Mar 2025) and Cascades East (7 Apr 2025) from Swiftly to Passio; SEPTA from Swiftly to in-house (18 Feb 2026); SMART rail from Swiftly to 511 (29 Jun 2026); Intercity Transit from Puget Sound OneBusAway to Avail and King County Metro from OneBusAway to its S3 bucket (14 Nov 2022); Arlington Transit from Connexionz to Clever-pattern (7 Nov 2023); MVgo from GMV to TripShot (11 Oct 2024); Everett Transit from OneBusAway to Strategic Mapping (18 Feb 2026). That is ~15 agency-level publishing-layer switches in ~4 years among ~420 catalogued agencies — roughly 1% of agencies per year, with Swiftly both gaining (RTC Southern Nevada, Marin) and losing (Via, Cascades East, SEPTA, SMART) — low churn consistent with the 15–20-year CAD/AVL tenure found in file 35, and a reminder that a Swiftly overlay can be displaced by a cheaper bundled publisher (Passio) or by in-house publishing.

9. **Catalogue growth is itself a market signal.** Feeds first added to the MobilityData catalogue: 432 in 2022 (seed), 6 in 2023, 31 in 2024, 157 in 2025, 118 in 2026 (to 27 Oct). The 2023–2026 additions by publisher: Consat 96 (BC Transit + TPI), agency-hosted 33, exo 33, **Passio 27, Swiftly 24, Avail 18, Clever 12, Trapeze/Vontas 10**, 511 8, Equans 7, Peak 6, TripShot 6, GMV 9, INIT-pattern 4, Connexionz 4, ETA 3 — i.e. the small-agency SaaS vendors (Passio, Swiftly, Avail) account for most new US open-data publishing.

10. **Reconciliation with vendor claims.** Vendor-claimed counts (Swiftly 200+ agencies worldwide; Passio 250+ clients; Hitachi MMS/Clever 300+ customers; TripSpark 450+ agencies served; Systrans 250+ agencies; Transit app 220+ agency partners) are 2–5x the public-feed footprint measured here (Swiftly 62 MobilityData providers / 40–49 NTD bus agencies; Passio 22 / 44; Clever 20 / 26; Avail 62 / 68; TripSpark 2 confirmed). The gap is explained by (i) customers that do not publish open feeds (universities, hospitals, private shuttles — 76 catalogued US publishers are not NTD bus agencies, 20 of them Passio and 18 Swiftly), (ii) products other than the GTFS-RT publisher (APC, scheduling, analytics, paratransit), (iii) non-US customers, and (iv) vendor counting of sub-systems. The census is a floor on footprint, not a ceiling.

---

## 2. Findings table

| # | Claim | Value | Unit | Year | Geography | Segment | Source name | URL | Confidence | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | MobilityData catalogue: gtfs_rt rows for US+CA | 1,095 rows / 359 providers (810 US, 285 CA); entity types tu 383, vp 382, sa 316, tu+vp 12, sa+tu+vp 2; status active 974, deprecated 120, development 1 | count | 2026-11-07 | US+CA | Roadway (all modes incl. rail feeds) | MobilityData feeds_v2.csv | https://files.mobilitydatabase.org/feeds_v2.csv | high | downloaded 05:06 UTC; 6,687 rows total |
| 2 | transit.land atlas: gtfs-rt feeds and NTD tags | 873 gtfs-rt feed records (all countries); 1,187 operator records with `us_ntd_id`; 1,216-row NTD crosswalk | count | 2026-11-05 (commit df1e677) | global | — | transitland-atlas GitHub | https://github.com/transitland/transitland-atlas | high | feeds/ and crosswalks/ snapshot in data/mobilitydata/transitland_atlas_20261107/ |
| 3 | NTD universe used for shares | 977 agencies with >=1 active full-size bus; 65,239 buses (tier 1: 772/10,541; tier 2: 149/15,142; tier 3: 46/20,411; tier 4: 10/19,145) | count | RY2025 | US | Roadway bus | file 16 / ntd_2025_bus_fleet_by_agency.csv (FTA NTD via data.transportation.gov) | https://data.transportation.gov/api/views/ifzt-j53d/rows.csv?accessType=DOWNLOAD | high | same universe as file 16 |
| 4 | US agencies with a public RT feed | 361 of 977 (37.0%) any feed; 358 (36.6%) active VP/TU feed; buses at agencies with active VP/TU: 51,080 (78.3%) | count/% | 2026 | US | Roadway bus | this census (gtfs_rt_agency_census.csv) | data/gtfs_rt_agency_census.csv | high (coverage) | union of both catalogues after dedup |
| 5 | Whitespace: NTD bus agencies with no public RT feed | 616 agencies (63.1%); 13,870 buses (21.3%) | count/% | 2026 | US | Roadway bus | this census | data/gtfs_rt_vendor_share_by_tier.csv | high | tier 1: 574 / 6,085; tier 2: 36 / 3,385; tier 3: 5 / 1,858; tier 4: 1 / 2,542 |
| 6 | Swiftly publishing share (US tiers 1-4, primary publisher) | 40 agencies (4.1%), 7,817 buses (12.0%); +2 probable S3-pattern (1,540 buses) | count/% | 2026 | US | RT publishing layer | this census | data/gtfs_rt_vendor_share_by_tier.csv | high (host) / low (S3 pattern) | 49 agencies / 9,856 buses have any Swiftly VP/TU feed incl. co-publication |
| 7 | Clever Devices BusTime publishing share | 26 agencies (2.7%), 4,747 buses (7.3%) | count/% | 2026 | US | RT publishing layer | this census | same | high (bustime/truetime hosts) / medium (path pattern) | excludes agencies whose Clever system feeds an in-house API (CTA, WMATA, NJT) |
| 8 | Avail publishing share | 68 agencies (7.0%), 4,332 buses (6.6%); tier 2: 32 of 149 agencies (21.5%), 3,067 buses (20.3%) | count/% | 2026 | US | RT publishing layer | this census | same | high | InfoPoint/myStop signature; PennDOT FRITS statewide contract explains the Pennsylvania cluster |
| 9 | Trapeze/Vontas TransitMaster publishing share | 16 agencies / 3,243 buses (5.0%) confirmed (TMGTFSRealTimeWebService, trpcloud/vontascloud); +13 / 1,625 (2.5%) probable directory naming | count/% | 2026 | US | RT publishing layer | this census | same | high / medium | naming heuristic corroborated by Saskatoon publishing the same feed on sasktrpcloud.com |
| 10 | GMV Syncromatics publishing share | 9 confirmed / 961 buses + 33 probable / 1,410 buses (3.6% combined) | count/% | 2026 | US | RT publishing layer | this census | same | high / medium | '/gtfs-rt/vehiclepositions' path on agency domains; transit.land groups these agency domains under syncromatics.com |
| 11 | Passio publishing share | 44 agencies (4.5%), 789 buses (1.2%); 41 of them in tier 1 | count/% | 2026 | US | RT publishing layer | this census | same | high | plus 20 non-NTD publishers (universities etc.) |
| 12 | Equans/Ineo Systrans (NAVINEO) footprint | 15 NTD agencies / 711 buses; 17 US+CA agencies incl. Marin, Brampton | count | 2026 | US+CA | RT publishing layer | this census; systrans.com; transit.land cadavl.com record | https://systrans.com/ ; https://www.tam-america.com/article/marin-transit-selects-equans-ineo-systrans-to-upgrade-cad-avl-on-buses | medium-high | cadavl.com domain registered 2021-11-26 (RDAP); Green Bay testimonial on systrans.com |
| 13 | Systrans vendor claims | 250+ public transit agencies, 12 countries, 60,000+ buses/LRVs/trains equipped | count | 2025 | global | CAD/AVL | systrans.com home page | https://systrans.com/ | medium (vendor) | fetched by curl |
| 14 | Consat Telematics footprint (Canada) | 22 agencies (+2 probable) of 57 catalogued Canadian agencies (38.6%) | count/% | 2026 | CA | RT publishing layer | this census; bctransit.com/nextride | https://www.bctransit.com/nextride/ | high | BC Transit NextRide = Consat per BC Transit page; Metrolinx TPI municipalities on metrolinx.tmix.se |
| 15 | Canada publishing-layer split | Consat 22+2; agency-hosted 8; Trapeze/Vontas 3+6; Zenbus 6; exo Chrono 3; INIT-pattern 2; Hub'Up 2; Equans 1; Civilia 1; Clever 1 (TTC) | count | 2026 | CA | RT publishing layer | this census | data/gtfs_rt_agency_census.csv | medium-high | no Canadian fleet universe available; CUTA total 16,145 buses (file 05) |
| 16 | In-house / unattributed publishing | 23 agencies / 12,370 buses (19.0%); 5 of the 10 1,000+ agencies; 60 distinct unattributed hosts | count/% | 2026 | US | RT publishing layer | this census | same | high (counts) | system of record known for CTA, WMATA, TriMet, RTD, Metro Transit MN, OCTA, Houston (Section 8) |
| 17 | MTA New York in-house | NYCT + MTA Bus: 5,979 buses (31.2% of the 1,000+ tier) published via api-endpoint.mta.info / OneBusAway-NYC server; Clever onboard | count | 2026 | US | RT publishing layer | transit.land mta.info record; file 12 | https://github.com/transitland/transitland-atlas | high | |
| 18 | Mid-market (tier 2) publisher ranking | Avail 32; Clever 19; Swiftly 11; Trapeze/Vontas 8+6; GMV 2+7; 511 5; Connexionz 4; Equans 4; agency 3; Passio 3; OBA 2; INIT 2; Mecatran 2; ETA 2; TripSpark 1; whitespace 36 | agencies | 2026 | US | RT publishing layer | this census | data/gtfs_rt_vendor_share_by_tier.csv | high | 149 agencies, 15,142 buses |
| 19 | Small tier (tier 1) publisher ranking | whitespace 574; Passio 41; Avail 35; GMV 25+5; Swiftly 20; Connexionz 15; Equans 11; ETA 8; 511 6; Trapeze 3+4; TripShot 4; Peak 3; Mecatran 3; Clever 2 | agencies | 2026 | US | RT publishing layer | this census | same | high | 772 agencies, 10,541 buses |
| 20 | Overlay cases (Swiftly feed/contract on a non-Swiftly system of record) | >=26 agencies incl. LA Metro (Clever), Miami-Dade (Clever), SMART Detroit (Clever), AC Transit (Clever, contract), County Connection (Clever, contract), MARTA (Clever/Trapeze, contract), NCTD (INIT), King County (INIT, probable), Community Transit (INIT, probable), Suffolk (INIT), GCRTA (Vontas), CapMetro (Vontas, alerts), IndyGo (Avail, contract), PVTA (Avail), GoDurham (Avail), Marin (GMV->Equans), MVRTA (GMV), Williamsburg (Equans), Corvallis (Connexionz), Frederick (Passio), HART/DASH/DCTA (OneBusAway) | count | 2026 | US | RT overlay | this census + files 12/31/35 | data/gtfs_rt_agency_census.csv (overlay_flag) | medium-high | see Section 8 |
| 21 | Dated publishing-layer switches | 15 agency-level vendor changes 2022-11 to 2026-10 (BC Transit x7 to Consat Apr-2025; TARC to Avail Jun-2025; Marin to Swiftly+Equans Mar-2026; Madison to Clever Aug-2024; CTtransit to Trapeze cloud Mar-2025; Via and Cascades East to Passio Mar/Apr-2025; SEPTA to in-house Feb-2026; SMART to 511 Jun-2026; Intercity Transit to Avail and KCM to S3 Nov-2022; Arlington to Clever Nov-2023; MVgo to TripShot Oct-2024; Everett to Strategic Mapping Feb-2026) | events | 2022-2026 | US+CA | RT publishing layer | MobilityData catalog git history + redirect field | https://github.com/MobilityData/mobility-database-catalogs | high (dates = catalogue commit dates, which lag the real switch) | data/gtfs_rt_feed_migrations.csv |
| 22 | Catalogue growth by year (US/CA RT feeds first added) | 2022: 432; 2023: 6; 2024: 31; 2025: 157; 2026 (to Oct): 118 | feeds | 2022-2026 | US+CA | — | catalog git history | same | high | 2022 = catalogue seeding, not adoption |
| 23 | New feeds 2023-2026 by publisher | Consat 96; agency 33; exo 33; Passio 27; Swiftly 24; Avail 18; Clever 12; Trapeze/Vontas 10; GMV 9; 511 8; Equans 7; Peak 6; TripShot 6 | feeds | 2023-2026 | US+CA | — | catalog git history | same | high | |
| 24 | Feed deprecations | 2024: 6; 2025: 33; 2026: 58 (of which Strategic Mapping 21, exo 36 re-platforming, Trapeze 12+6, Swiftly 11+6 S3-pattern, GMV-pattern 6, OneBusAway 5) | feeds | 2024-2026 | US+CA | — | catalog git history | same | high | deprecation = catalogue curation, not always a vendor switch |
| 25 | MobilityData 'is_official' flag | True 339, False 20, blank 736 of 1,095 rows; vendor-hosted Avail (115 blank / 8 True) and Swiftly (104 blank / 11 True) feeds are mostly unflagged, Consat/BC Transit (64 True) and exo (24 True) flagged | count | 2026 | US+CA | — | feeds_v2.csv | https://files.mobilitydatabase.org/feeds_v2.csv | high | bias note, Section 11 |
| 26 | Swiftly vendor claim | "Trusted by 200+ transit agencies worldwide"; 14k+ transit staff users; 99.9% uptime | count | 2026 | global | RT SaaS | goswift.ly/about | https://www.goswift.ly/about | medium (vendor) | curl; customers page 404 |
| 27 | Hitachi MMS (Clever) vendor claim | "Over 300 customers around the world"; largest US agency 6,000+ vehicles to 30-vehicle systems; 600+ employees, 12 locations | count | 2026 | global | CAD/AVL | hitachimms.com/about-us | https://www.hitachimms.com/about-us/ | medium (vendor) | |
| 28 | Passio vendor claim | "over 250 clients"; part of Transit Technologies family (Ecolane, CTS/TripMaster, etc.) | count | 2026 | US | RT/CAD SaaS | passiotech.com/about-us | https://passiotech.com/about-us/ | medium (vendor) | |
| 29 | TripSpark vendor claim | "450+ agencies served"; Streets CAD/AVL; MyRide PIS; focus on small-to-medium agencies | count | 2026 | NA | CAD/AVL + PIS | tripspark.com | https://www.tripspark.com/ | medium (vendor) | only 2 NTD agencies publish from tripsparkhost.com; 'MyRide' hosts (Barrie, BFT, Shore) classified probable Modaxo |
| 30 | Avail positioning | target market "transit operators with medium-sized fleets"; founded 1999 | — | 2026 | US | CAD/AVL | availtec.com/about | https://availtec.com/about/ | high | consistent with tier-2 leadership measured here |
| 31 | Transit app partner footprint | "220+ transit agency partners"; 9M monthly users; "1 in 5 US and Canadian riders"; partner cities listed incl. Salt Lake City, Toronto, Baltimore, Vancouver, Philadelphia, Ottawa, Las Vegas, Connecticut, Orange County, Niagara, San Jose, Miami, Columbus, Minneapolis, Kansas City, Dayton, Santa Monica, Boston, Calgary, Cincinnati, Cleveland, Oakland, San Antonio, Chicago, St Louis, Monterey, Saguenay | count | 2026 | US+CA | Rider app / PIS | transitapp.com/partners | https://transitapp.com/partners | medium (vendor) | Transit does not host agency GTFS-RT; it consumes it (no hosting signature) |
| 32 | MTA Maryland publishes RT via Swiftly API | GTFS-RT trip updates and vehicle positions for Local Bus, Light Rail, Metro and Commuter Bus "available via Swiftly APIs, which require access keys" | — | 2026 | US-MD | RT publishing | mta.maryland.gov developer resources | https://www.mta.maryland.gov/developer-resources | high | confirms Swiftly as publisher for 976 buses |
| 33 | Community Transit RT feeds on S3 bucket | s3.amazonaws.com/commtrans-realtime-prod/{tripupdates,vehiclepositions,alerts}.pb | — | 2026 | US-WA | RT publishing | communitytransit.org/open-data | https://www.communitytransit.org/open-data | high (URL) / low (Swiftly attribution of the bucket pattern) | INIT CAD/AVL since 2008 (file 12) |
| 34 | Hosting-domain registry facts | cadavl.com registered 2021-11-26 (Amazon Registrar); rideralerts.com 2015-03-26; availtec.com 1999-04-28; vontascloud.com 2022-08-12; ctttrpcloud.com 2022-08-11; sorttrpcloud.com 2020-06-19; glphtrpcloud.com 2022-03-29; tripsparkhost.com 2016-03-22; etaspot.net 2010-06-06; goswift.ly registrant Swiftly, Inc. (2016-01-06); passio3.com 2011-08-16 | date | 2026 | — | — | rdap.org | https://rdap.org/domain/cadavl.com | high | Trapeze cloud hosts appear 2020-2022, i.e. the incumbents' SaaS re-hosting wave |
| 35 | Catalogue error flagged | MobilityData redirect of Broward's deprecated bctmyride-buspas.com feed points to a University of Minnesota Peak Transit feed (mdb-3527) | — | 2026 | US | — | feeds_v2.csv | https://files.mobilitydatabase.org/feeds_v2.csv | high | excluded from the migration narrative |

---

## 3. Vendor signature dictionary (how each feed URL was classified)

Rules are applied in order; first match wins. "Corroboration" is the independent evidence that the signature belongs to the vendor.

| Rule | Signature (host / path) | Vendor (publishing layer) | Confidence | Corroboration |
|---|---|---|---|---|
| swiftly_host | `api.goswift.ly/real-time/<agency>/gtfs-rt-*` | Swiftly | high | registrant Swiftly, Inc. (RDAP); MTA Maryland developer page |
| passio_host | `passio3.com/<agency>/passioTransit/gtfs/realtime/*` | Passio Technologies | high | vendor domain |
| avail_host / avail_infopoint_path | `*.rideralerts.com`, `*.availtec.com`, `*.myavail.cloud`; `/InfoPoint/GTFS-Realtime.ashx`, `/myStop/`, `/TripPlanner/GTFS-Realtime.ashx` | Avail Technologies | high | vendor domains; InfoPoint/myStop are Avail product names (availtec.com) |
| trapeze_tm_cloud_host / trapeze_tm_path | `*trpcloud.com`, `*vontascloud.com`, `tmweb.*`; `/TMGTFSRealTimeWebService/`, `/realtimefeed/` | Trapeze / Vontas (TransitMaster) | high | "TM" = TransitMaster; SORTA, GCRTA, CapMetro, Metro Transit MN, Nashville and Edmonton all documented TransitMaster users (files 12/35) publish on these hosts |
| tm_dir_naming | `/Alert/Alerts.pb`, `/TripUpdate/TripUpdates.pb`, `/Vehicle/VehiclePositions.pb` on agency hosts | Trapeze / Vontas (probable) | medium | Saskatoon publishes the identical feed on `saskprdtmgtfs.sasktrpcloud.com`; TARC's old feed used it before moving to Avail |
| consat_tmix_host / consat_vehicleupdates_naming | `*.tmix.se`; `/gtfs-realtime/vehicleupdates.pb` | Consat Telematics | high / low | BC Transit NextRide page names Consat; "Tmix.Cap.TdExport.WebApi" static paths; Calgary 2025 award to Consat (file 31) |
| systrans_cadavl_host / systrans_profil_path | `*.cadavl.com`, `*bt-cadavl.com`; `/ProfilGtfsRt2_0RSProducer-<agency>/` | Equans / Ineo Systrans (NAVINEO) | high / medium | Green Bay testimonial on systrans.com; Marin and Brampton awards (files 12/35) match their cadavl hosts |
| connexionz_host / connexionz_rtt_path | `*.connexionz.net`; `/rtt/public/utility/gtfsrealtime.aspx/` | Connexionz | high | vendor domain |
| gmv_host / gmv_gtfs_rt_path | `*.syncromatics.com`, `*.gmv.com`; `/gtfs-rt/{alerts,tripupdates,vehiclepositions}` on agency domains | GMV Syncromatics | high / medium | mysmartbus.com contact support@gmvsync.com; transit.land files these agency domains under syncromatics.com.dmfr.json; LADOT (GMV incumbent) matches |
| clever_bustime_host / clever_bustime_path | `bustime.*`, `truetime.*`, `cleverapi.*`; `/gtfsrt/{alerts,trips,vehicles}` | Clever Devices BusTime / Hitachi MMS | high / medium | BusTime and TrueTime are Clever products; Kitsap (Clever 2023), SacRT, Santa Monica (Clever 2021), TTC (Clever VISION), Pittsburgh match |
| init_path | `/gtfsrealtime/{TripUpdates,VehiclePositions}` (capitalised, no extension) | INIT (probable) | medium | Suffolk County Transit awarded INIT (Mass Transit release); CDTA, YRT, DRT, C-TRAN, GRT share the pattern |
| tripspark_host / gtfs_underscore_naming | `*.tripsparkhost.com`; `GTFS_{ServiceAlerts,TripUpdates,VehiclePositions}.pb` | TripSpark (Modaxo) / Modaxo probable | high / low | 'MyRide' is TripSpark's PIS brand; Hamilton (Vontas 2024) also uses the naming, so attributed to Modaxo group, not to a brand |
| mapstrat_host | `*.mapstrat.com` | Strategic Mapping Inc. | high | vendor domain (registered 2006) |
| eta_host / peak_host / tripshot_host / mecatran_host / zenbus_host / civilia_host / hubup_host / ridesystems / transloc / doublemap / cubic_umo | vendor domains | respective vendor | high | vendor domains |
| oba_host / oba_path | `*onebusaway.org`, `*obaweb.org`, `*obanyc.com`, `transitime.org`; `-for-agency/` | OneBusAway / TheTransitClock (open source) | high / medium | open-source server; hosting agency varies (Sound Transit regional, Alexandria DASH, HART Tampa, MTA NYC) |
| swiftly_s3_pattern | `s3.amazonaws.com/<agency>-{realtime,alerts}-prod/` | Swiftly (probable) | low | King County Metro, Community Transit, LA Metro alerts, former CTtransit share the naming; not confirmed by any page |
| mtc511_aggregator / mta_inhouse / exo_chrono | `api.511.org`, `api-endpoint.mta.info`, `exo.chrono-saeiv.com` | regional/agency platforms | high | the underlying CAD/AVL vendor differs per member agency |
| none | anything else (60 hosts) | Agency-hosted / unattributed | n/a | system of record added manually where evidenced (Section 8) |

Feed-level confidence mix (active VP/TU records, US+CA, both catalogues): high 1,425; medium 231; low 62; unattributed 150. Agency-level primary attribution: US tiers 1–4 high 267, medium 62, low 10, unattributed 19; Canada high 37, medium 6, low 5, unattributed 6.

---

## 4. US vendor share by fleet tier (primary real-time publisher per agency)

Universe: NTD RY2025 agencies with >=1 active full-size bus (file 16 tier definition A). Shares are of the whole tier, so "No public feed" is the whitespace row. "(probable)" rows are pattern-based attributions kept separate from host-confirmed ones. Full table: `data/gtfs_rt_vendor_share_by_tier.csv`.

**Tier 4 (1,000+ buses; 10 agencies, 19,145 buses)**

| Publisher | Agencies | % | Buses | % |
|---|---|---|---|---|
| Agency in-house / unattributed (CTA, SEPTA, WMATA, MBTA, Houston METRO) | 5 | 50.0 | 7,341 | 38.3 |
| MTA New York in-house (NYCT, MTA Bus) | 2 | 20.0 | 5,979 | 31.2 |
| No public feed (NJ Transit) | 1 | 10.0 | 2,542 | 13.3 |
| Swiftly (LA Metro) | 1 | 10.0 | 1,999 | 10.4 |
| Swiftly (probable, King County Metro S3) | 1 | 10.0 | 1,284 | 6.7 |

**Tier 3 (250–999; 46 agencies, 20,411 buses)**

| Publisher | Agencies | % | Buses | % |
|---|---|---|---|---|
| Agency in-house / unattributed (RTD, TriMet, Metro Transit MN, UTA, OCTA, St Louis Metro, RIPTA, CapMetro portal, MTA MD part) | 9 | 19.6 | 4,509 | 22.1 |
| Swiftly (MTA Maryland, Miami-Dade, Honolulu, RTC S. Nevada, VTA, NCTD, GCRTA, SMART Detroit) | 8 | 17.4 | 4,064 | 19.9 |
| Clever Devices BusTime (Pittsburgh, AC Transit API, Milwaukee, Fairfax, DDOT) | 5 | 10.9 | 2,348 | 11.5 |
| Trapeze/Vontas TransitMaster (Pace, MARTA legacy, SORTA, COTA, CTtransit) | 5 | 10.9 | 2,027 | 9.9 |
| No public feed (DART, Montgomery County, Centro, HRT, NFTA) | 5 | 10.9 | 1,858 | 9.1 |
| MTC 511 aggregator (SF Muni, SamTrans) | 2 | 4.3 | 1,190 | 5.8 |
| Trapeze/Vontas (probable naming: VIA, CATS, Nassau NICE alerts excluded) | 3 | 6.5 | 991 | 4.9 |
| Mecatran (Phoenix, Valley Metro RPTA) | 2 | 4.3 | 844 | 4.1 |
| GMV Syncromatics (Westchester; LADOT probable) | 2+1 | 6.5 | 1,043 | 5.1 |
| OneBusAway (San Diego MTS) | 1 | 2.2 | 603 | 3.0 |
| Avail (Foothill) | 1 | 2.2 | 357 | 1.7 |
| INIT probable (CDTA) | 1 | 2.2 | 321 | 1.6 |
| Swiftly probable (Community Transit S3) | 1 | 2.2 | 256 | 1.3 |

**Tier 2 (50–249; 149 agencies, 15,142 buses)**

| Publisher | Agencies | % | Buses | % |
|---|---|---|---|---|
| No public feed | 36 | 24.2 | 3,385 | 22.4 |
| Avail | 32 | 21.5 | 3,067 | 20.3 |
| Clever Devices BusTime | 19 | 12.8 | 2,321 | 15.3 |
| Swiftly | 11 | 7.4 | 1,378 | 9.1 |
| Trapeze/Vontas TransitMaster (+probable) | 8 (+6) | 5.4 (+4.0) | 1,120 (+547) | 7.4 (+3.6) |
| GMV Syncromatics (+probable) | 2 (+7) | 1.3 (+4.7) | 142 (+498) | 0.9 (+3.3) |
| MTC 511 aggregator | 5 | 3.4 | 428 | 2.8 |
| Agency in-house / unattributed | 3 | 2.0 | 422 | 2.8 |
| OneBusAway | 2 | 1.3 | 385 | 2.5 |
| Connexionz | 4 | 2.7 | 353 | 2.3 |
| Equans / Ineo Systrans | 4 | 2.7 | 286 | 1.9 |
| INIT probable | 2 | 1.3 | 228 | 1.5 |
| Mecatran | 2 | 1.3 | 207 | 1.4 |
| Passio | 3 | 2.0 | 168 | 1.1 |
| ETA Transit | 2 | 1.3 | 125 | 0.8 |
| TripSpark | 1 | 0.7 | 82 | 0.5 |

**Tier 1 (1–49; 772 agencies, 10,541 buses)**

| Publisher | Agencies | % | Buses | % |
|---|---|---|---|---|
| No public feed | 574 | 74.4 | 6,085 | 57.7 |
| Avail | 35 | 4.5 | 908 | 8.6 |
| Passio | 41 | 5.3 | 621 | 5.9 |
| GMV Syncromatics (+probable) | 5 (+25) | 0.6 (+3.2) | 122 (+566) | 1.2 (+5.4) |
| Equans / Ineo Systrans | 11 | 1.4 | 425 | 4.0 |
| Swiftly | 20 | 2.6 | 376 | 3.6 |
| Connexionz | 15 | 1.9 | 349 | 3.3 |
| ETA Transit | 8 | 1.0 | 213 | 2.0 |
| MTC 511 aggregator | 6 | 0.8 | 165 | 1.6 |
| Trapeze/Vontas (+probable) | 3 (+4) | 0.4 (+0.5) | 96 (+87) | 0.9 (+0.8) |
| Agency in-house / unattributed | 6 | 0.8 | 98 | 0.9 |
| TripShot | 4 | 0.5 | 89 | 0.8 |
| Clever Devices BusTime | 2 | 0.3 | 78 | 0.7 |
| Peak Transit | 3 | 0.4 | 59 | 0.6 |
| TripSpark / Strategic Mapping / Mecatran / OneBusAway / TransLoc / Trillium alerts-only | 1 / 1 / 3 / 1 / 1 / 2 | — | 45 / 43 / 31 / 27 / 26 / 16 | — |

**All tiers (977 agencies, 65,239 buses)** — see Key takeaway 3. Memo: of the 1,667 NTD agencies with zero full-size buses (demand-response, vanpool, cutaway-only), 59 publish a VP/TU feed (Passio 15, Swiftly 14+1, 511 5, agency 5, Avail 4, GMV 3, Connexionz 2, Cubic Umo 2, TripShot 2, others); of the 76 catalogued US publishers that are not NTD bus agencies (universities, hospitals, NPS, TMAs), Passio hosts 20, Swiftly 18, Avail 7, TripShot 6, agency 6, GMV 5.

---

## 5. Canada (57 agencies catalogued, 55 with active VP/TU)

| Publisher | Agencies | Agencies (examples) |
|---|---|---|
| Consat Telematics (tmix.se) | 22 (+2 probable: Kingston, Thunder Bay) | BC Transit (35 sub-systems, one NextRide contract), Belleville, Cornwall, Lindsay, Milton, Orangeville, Orillia, Owen Sound, Sarnia, Sault Ste. Marie, Simcoe LINX, Stratford, St. Thomas, Temiskaming, Timmins (Metrolinx TPI), Saguenay, Sudbury, North Bay, Medicine Hat, Ontario Northland, Bow Valley |
| Agency in-house / unattributed | 8 | Calgary (Consat system of record from 2025), TransLink (Clever 2016), STM, OC Transpo, Grand River (formerly INIT-pattern), Transcollines, Regina (alerts), REM (alerts) |
| Trapeze/Vontas TransitMaster (+probable naming) | 3 (+6) | Edmonton, Guelph (glphtrpcloud), Saskatoon (sasktrpcloud); probable: Halifax, London, MiWay, Barrie, Burlington, Hamilton (Vontas award 2024) |
| Zenbus | 6 | Mont-Tremblant, L'Inter des Laurentides, MRC de Montcalm, Saint-Jean-sur-Richelieu, Pierre-De Saurel, L'autobus de ville |
| exo Chrono platform | 3 | exo (12 sectors consolidated), RTL Longueuil, STS Sherbrooke |
| INIT (probable path pattern) | 2 | York Region Transit, Durham Region Transit |
| Hub'Up | 2 | MRC du Haut-Saint-Laurent, Saint-Hyacinthe |
| Equans / Ineo Systrans | 1 | Brampton (bt-cadavl.com; Equans award 2023) |
| Civilia | 1 | Wood Buffalo |
| Clever Devices BusTime | 1 | TTC (VISION, Clever 2016) |
| Not catalogued (static GTFS only) | — | Winnipeg, STL Laval, RTC Québec, STO Gatineau, Lévis, Trois-Rivières, Windsor, Oakville, Niagara, Red Deer, Lethbridge, Moncton, Saint John, St. John's (not individually verified) |

No Canadian bus-fleet universe exists in this project (CUTA Fact Book blocked, file 04/05; CUTA total 16,145 buses per file 05), so Canadian shares are by agency count only. GO Transit (Metrolinx) itself has no GTFS-RT record in either catalogue; its municipal TPI partners do (on Consat).

---

## 6. Whitespace: NTD bus agencies with no public real-time feed

Tiers 2–4: 42 agencies, 7,785 buses. The largest, with the CAD/AVL vendor where evidenced:

| NTD ID | Agency | State | Buses | Tier | Known CAD/AVL system of record (source) |
|---|---|---|---|---|---|
| 20080 | New Jersey Transit | NJ | 2,542 | 1000+ | Clever Devices 2011/2013, sole-source refresh 2026 (file 35 A16); developer portal requires registration |
| 60056 | Dallas Area Rapid Transit | TX | 586 | 250-999 | INIT (Metro Magazine "DART selects INIT/Kinkisharyo to expand ITS", cited in file 12) |
| 30051 | Montgomery County Ride On | MD | 400 | 250-999 | n/e; rideonrealtime.net real-time site exists, no GTFS-RT catalogued |
| 20018 | CNY Centro | NY | 328 | 250-999 | n/e |
| 30083 | Hampton Roads Transit | VA | 272 | 250-999 | n/e |
| 20004 | NFTA Metro Buffalo | NY | 272 | 250-999 | n/e |
| 40027 | PSTA Pinellas | FL | 232 | 50-249 | n/e |
| 20126 | Shortline (private NJ carrier) | NJ | 172 | 50-249 | n/a (private contract carrier) |
| 30070 | PRTC OmniRide | VA | 157 | 50-249 | n/e |
| 90029 | Omnitrans | CA | 156 | 50-249 | n/e |
| 60006 | El Paso Sun Metro | TX | 152 | 50-249 | n/e (a 'El Paso Transportation Authority' Peak Transit feed in MobilityData could not be tied to Sun Metro) |
| 80289 | Roaring Fork TA | CO | 143 | 50-249 | n/e |
| 60007 | Trinity Metro Fort Worth | TX | 138 | 50-249 | n/e (GTFS page lists static GTFS and GBFS only) |
| 60032 | New Orleans RTA | LA | 138 | 50-249 | Clever Devices (FY2025 CAD/AVL maintenance contract, file 12) |
| 20122 | Academy Lines (private) | NJ | 126 | 50-249 | n/a |
| 40086 | Metropolitan Bus Authority PR | PR | 116 | 50-249 | n/e |
| 70002 | Metro Omaha | NE | 103 | 50-249 | n/e |
| 40030 | Gainesville RTS | FL | 102 | 50-249 | n/e |
| 50040 | Ann Arbor TheRide | MI | 97 | 50-249 | n/e |
| 60278 | Texas A&M | TX | 90 | 50-249 | n/e (university) |
| 20177 | Adirondack Trailways (private) | NY | 86 | 50-249 | n/a |
| 30081 | Loudoun County | VA | 79 | 50-249 | n/e |
| 70041 | CyRide Ames | IA | 79 | 50-249 | n/e |
| 20128 | Suburban Transit (private) | NJ | 78 | 50-249 | n/a |
| 50154 | Metropolitan Council (MN) | MN | 74 | 50-249 | covered operationally by Metro Transit's Vontas system and feed |
| 40042 | BJCTA Birmingham | AL | 74 | 50-249 | n/e |
| 90148 | Victor Valley TA | CA | 73 | 50-249 | n/e |
| 10006 | SRTA Southeastern MA | MA | 69 | 50-249 | n/e |
| 90035 | Gold Coast Transit | CA | 69 | 50-249 | n/e |
| 90001 | RTC Washoe | NV | 68 | 50-249 | n/e |
| 80005 | Mountain Metro Colorado Springs | CO | 67 | 50-249 | n/e |
| 50057 | MetroLINK Rock Island | IL | 67 | 50-249 | n/e |
| 40036 | StarMetro Tallahassee | FL | 66 | 50-249 | n/e |
| 40001 | CARTA Chattanooga | TN | 65 | 50-249 | n/e |
| 70035 | Johnson County KS | KS | 64 | 50-249 | n/e |
| 40028 | LeeTran | FL | 60 | 50-249 | n/e |
| 60009 | El Metro Laredo | TX | 57 | 50-249 | n/e |
| 10050 | Greater Bridgeport Transit | CT | 56 | 50-249 | n/e |
| 20149 | Rockland Coaches (private) | NJ | 56 | 50-249 | n/a |
| 40141 | COMET Columbia SC | SC | 53 | 50-249 | n/e |
| 80011 | Transfort Fort Collins | CO | 52 | 50-249 | n/e |
| 20217 | Hampton Jitney (private) | NY | 51 | 50-249 | n/a |

Six of the 42 are private contract carriers reporting to NTD (Shortline, Academy, Adirondack, Suburban, Rockland, Hampton Jitney); netting those out, **36 public mid/large agencies with 7,145 buses have no open real-time feed**, of which three have a documented CAD/AVL incumbent (NJ Transit, DART, NORTA). Tier 1 whitespace (574 agencies, 6,085 buses) is dominated by rural and small-urban operators (median agency 8 buses) — the addressable segment for low-touch SaaS (Passio/Swiftly/ETA price points of USD 0.2–2k per vehicle-year, file 12).

---

## 7. Top-100 NTD agencies: manual review summary (publishing layer vs system of record)

Full table with hosts, sources and confidence: `data/gtfs_rt_top100_ntd_review.csv`. Condensed view (buses = NTD 2025 active full-size):

| # | Agency | Buses | Publishing layer (feed signature) | CAD/AVL system of record (evidence) |
|---|---|---|---|---|
| 1 | MTA NYCT | 4,583 | MTA in-house (OneBusAway-NYC / camsys) | Clever onboard (Bus Time); Cubic onboard hardware 2013 (file 12) |
| 2 | NJ Transit | 2,542 | none open | Clever 2011/13; refresh 2026 |
| 3 | CTA | 2,012 | in-house (transitdata.transitchicago.com) | Clever ~2007; sole-source 2024-31 |
| 4 | LA Metro | 1,999 | Swiftly | Clever ATMS II (2025) over Conduent ATMS I |
| 5 | MTA Bus | 1,396 | MTA in-house | Clever onboard |
| 6 | SEPTA | 1,358 | in-house (www3.septa.org; Swiftly deprecated Feb-2026) | n/e (CARD replacement in procurement, file 35) |
| 7 | WMATA | 1,349 | in-house API | Clever (2023-26 ITS contract) |
| 8 | MBTA | 1,317 | in-house (cdn.mbta.com) | n/e (Swiftly RTPI contract, value n/d, file 35) |
| 9 | Houston METRO | 1,305 | in-house (api.ridemetro.org) | INIT 2003 (current status not verified) |
| 10 | King County Metro | 1,284 | S3 bucket (Swiftly probable) | INIT ~2016 |
| 11 | MTA Maryland | 976 | Swiftly (confirmed by agency page) | n/e |
| 12 | Denver RTD | 968 | in-house | INIT 2011 |
| 13 | SF Muni | 861 | MTC 511 | n/e |
| 14 | Miami-Dade | 791 | Swiftly | Clever 2013-2030 |
| 15 | Pittsburgh PRT | 698 | Clever TrueTime | Clever (product) |
| 16 | TriMet | 668 | in-house | INIT 2009 |
| 17 | Metro Transit MN | 650 | in-house | Vontas OnRoute/TransitMaster 2002-2031 |
| 18 | Pace | 646 | Trapeze TransitMaster (tmweb) | Trapeze (feed) |
| 19 | AC Transit | 630 | Clever-pattern API + 511 (+Swiftly by contract) | Clever 2015-2030 |
| 20 | San Diego MTS | 603 | OneBusAway + Mecatran | n/e |
| 21 | DART | 586 | none open | INIT (Metro Magazine) |
| 22 | MARTA | 535 | Trapeze TransitMaster (legacy feed) (+Swiftly by contract) | Clever 2023 award (migration pending) |
| 23 | Phoenix | 513 | Mecatran (Valley Metro regional) | Clever regional 2016 |
| 24 | UTA | 492 | in-house (apps.rideuta.com) | n/e |
| 25 | Honolulu TheBus | 485 | Swiftly | n/e |
| 26 | RTC S. Nevada | 452 | Swiftly (since catalogue seed 2022) | n/e |
| 27 | CapMetro | 449 | Texas open-data portal (+Swiftly alerts) | Vontas 2025 |
| 28 | VTA | 448 | Swiftly + 511 | n/e |
| 29 | OCTA | 446 | in-house | Conduent OrbCAD 2011 |
| 30 | VIA San Antonio | 445 | TransitMaster naming (probable) | — |
| 31 | Montgomery Ride On | 400 | none open | n/e |
| 32 | Milwaukee MCTS | 384 | Clever BusTime pattern | replacement 2021-23 (vendor n/d; pattern says Clever) |
| 33 | Broward | 373 | in-house (ISR) + GMV-pattern trolley | ISR 2014-2027 |
| 34 | Foothill | 357 | Avail cloud | Avail 2015 |
| 35 | LADOT | 346 | GMV pattern | GMV (renewal to 2030) |
| 36 | Fairfax Connector | 344 | Clever BusTime pattern | — |
| 37 | Valley Metro RPTA | 331 | Mecatran | Clever regional 2016 |
| 38 | SamTrans | 329 | MTC 511 | n/e |
| 39 | Centro | 328 | none open | n/e |
| 40 | Westchester Bee-Line | 324 | GMV (westchester.gmv.com) | GMV (feed) |
| 41 | NCTD | 324 | Swiftly | INIT (file 35 G04/B02) |
| 42 | CDTA | 321 | INIT pattern | INIT (probable) |
| 43 | GCRTA | 316 | Vontas cloud + Swiftly (both live) | Vontas ~2004-2028 |
| 44 | St Louis Metro | 311 | in-house | n/e |
| 45 | SORTA | 306 | Trapeze cloud (sorttrpcloud) | Vontas to 2027 |
| 46 | LYNX | 292 | GTFS_ naming (Modaxo probable) | — |
| 47 | DDOT Detroit | 292 | Clever BusTime pattern (myddotbus.com) | — |
| 48 | COTA | 281 | Vontas cloud | Vontas (feed) |
| 49 | NICE Bus | 273 | alerts only | — |
| 50 | SMART Detroit | 272 | Swiftly | Clever 2013 (IVN5 2023) |
| 51-52 | HRT, NFTA | 272 each | none open | n/e |
| 53 | CTtransit Hartford (+ New Haven, Stamford, Waterbury, New Britain) | 259 (+259) | Trapeze cloud (ctttrpcloud; S3 bucket before Mar-2025) | Trapeze (feed) |
| 54 | Community Transit | 256 | S3 bucket (Swiftly probable) | INIT 2008 |
| 55 | CATS Charlotte | 254 | TransitMaster naming (probable) | — |
| 56 | RIPTA | 252 | in-house | n/e |
| 57 | SacRT | 247 | Clever BusTime | Clever (extended to rail, file 08) |
| 58 | Delaware DTC | 244 | Swiftly | n/e |
| 59 | Sound Transit | 238 | Puget Sound OneBusAway | Clever BOT 2024 (Stride) |
| 60 | IndyGo | 235 | Avail InfoPoint pattern (+Swiftly by contract) | Avail (feed); Swiftly 2019- |

Rows 61–100 (see CSV) are dominated by Avail (TARC, PVTA, Palm Tran, The Rapid, Akron, MVTA, Votran, LANTA, rabbittransit, Intercity Transit), Clever BusTime (Madison, Santa Monica, JTA, Dayton, GRTC, Kitsap, Raleigh, Riverside, Santa Cruz, Santa Barbara, ATL Xpress), Trapeze/Vontas (Long Beach, Nashville, Tucson, Fresno, LTD, Spokane, CATA Lansing), Swiftly (KCATA, Albuquerque, HART, Prince George's, San Joaquin, DASH), Equans (Memphis MATA, Corpus Christi), GMV (Knoxville, Winston-Salem, Chapel Hill), Connexionz (Flint, Santa Clarita), and the whitespace agencies listed in Section 6.

---

## 8. Overlay-on-legacy: SaaS publisher on top of a CAD/AVL system of record

| Agency (buses) | Real-time publisher(s) in catalogues | CAD/AVL system of record | Evidence | Pattern |
|---|---|---|---|---|
| LA Metro (1,999) | Swiftly | Clever ATMS II (2025 award) over Conduent/Orbital ATMS I | legistar matter; Swiftly USD 169/vehicle predictions contract (file 12) | overlay kept through CAD/AVL replacement |
| King County Metro (1,284) | S3 bucket (Swiftly-pattern, probable) | INIT ~2016 | initse.com Seattle project page | probable overlay |
| MTA Maryland (976) | Swiftly (agency page) | n/e | mta.maryland.gov | overlay on unknown SoR |
| Miami-Dade (791) | Swiftly | Clever 2013-2030 | Miami-Dade BCC item 2025 | overlay |
| VTA (448) / SF Bay region | Swiftly + 511 | n/e | — | overlay + aggregator |
| NCTD (324) | Swiftly | INIT (mode-specific onboard) | NCTD agreement (file 35 B02, G04) | overlay |
| GCRTA (316) | Vontas cloud AND Swiftly | Vontas OnRoute | GCRTA presentation 2023 | dual publication |
| SMART Detroit (272) | Swiftly | Clever 2013 (IVN5 refresh 2023) | SMART board book Jan-2023 | overlay |
| Community Transit (256) | S3 bucket (Swiftly-pattern, probable) | INIT 2008 | Metro Magazine 2008 | probable overlay |
| CapMetro (449) | Texas open-data portal + Swiftly alerts | Vontas 2025 | Pavilion contract record | partial overlay |
| AC Transit (630) | agency Clever-pattern API + 511; Swiftly analytics via NASPO/Carahsoft | Clever 2015-2030 | AC Transit staff reports (file 35 A13/B03) | contract overlay, publisher stays Clever/agency |
| County Connection (125) | 511; Swiftly 5 modules | Clever IVN II since 2002 | CCCTA board items 2024-25 | contract overlay |
| MARTA (535) | Trapeze TransitMaster legacy feed; Swiftly single-source 2024 | Clever 2023 award | MARTA minutes 2023/2024 | overlay across a vendor transition |
| IndyGo (235) | Avail InfoPoint pattern | Avail (feed); Swiftly RT data/TSP SaaS since 2019 (USD 1.32m/3 yrs) | IndyGo board book Oct-2025 | contract overlay |
| Suffolk County (117) | INIT-pattern + Swiftly | INIT | Mass Transit release | dual publication |
| Pioneer Valley (186) | Avail + Swiftly | Avail (feed) | — | dual publication |
| GoDurham (63) | Avail + Swiftly | Avail (feed) | — | dual publication |
| Marin (55) | Swiftly + Equans cadavl + 511 | Equans NAVINEO 2025 (GMV 2009-2025) | TAM-America; catalogue redirect dated 2026-03-11 | overlay survived GMV->Equans switch |
| Merrimack Valley (68) | Swiftly + GMV | GMV (feed) | — | dual publication |
| Williamsburg WATA (30) | Swiftly + Equans | Equans (feed) | — | dual publication |
| Corvallis (19) | Connexionz + Swiftly | Connexionz (feed) | — | dual publication |
| Frederick County (19) | Passio + Swiftly | Passio (feed) | — | dual publication |
| HART Tampa (132), Alexandria DASH (113), Denton DCTA (27) | Swiftly + OneBusAway/TheTransitClock | n/e | — | SaaS replacing or duplicating an open-source server |
| MBTA (1,317) | in-house feed | n/e; Swiftly RTPI contract (value n/d) | file 35 | contract overlay, in-house publisher |
| SEPTA (1,358) | in-house since Feb-2026 (Swiftly feeds deprecated) | n/e | catalogue git | overlay displaced by in-house publishing |

Reading: Swiftly's installed base at NTD bus agencies is 49 agencies / 9,856 buses when co-publication is counted; at least 15 of them (c. 7,800 buses) sit on a documented Clever, INIT, Vontas, Avail, GMV or Equans system of record, and another ~10 small agencies co-publish with the CAD/AVL vendor's own feed. The overlay is bought by large and mid agencies alike (LA Metro and Miami-Dade down to Corvallis and Frederick), and it persists through CAD/AVL replacements (LA Metro, Marin, MARTA) — which supports the thesis that the real-time/data layer is procured separately from, and on a shorter cycle than, the 15–20-year CAD/AVL contract (file 35). The counter-evidence is also present: SEPTA, Via Mobility, Cascades East, SMART rail and (probably) CTtransit dropped Swiftly for in-house, Passio, 511 or Trapeze-cloud publishing between 2025 and 2026.

---

## 9. Time dimension: migrations and churn from the catalogue's history

Method: for every US/CA realtime JSON in the MobilityData GitHub catalogue, `git log --no-renames -p` on the stable `*-<mdb_source_id>.json` pathspec yields the commit date when the feed entered the catalogue, when its `direct_download` changed and when its status was set to deprecated; the catalogue's `redirect.id` field links deprecated feeds to their successors. (A first pass with `--follow` produced spurious cross-agency "migrations" because git's rename detection links small, similar JSON files; it was discarded.) Dates are catalogue-commit dates and lag the operational switch by weeks to months.

| Date (catalogue) | Agency | From host (publisher) | To host (publisher) | Corroboration |
|---|---|---|---|---|
| 2022-05-26 (seed) | RTC Southern Nevada | rtcws.rtcsnv.com (agency) | api.goswift.ly (Swiftly) | — |
| 2022-05-26 (seed) | MARTA | onebusaway.gatech.edu (OBA, Georgia Tech) | gtfs-rt.itsmarta.com (Trapeze TM) | — |
| 2022-05-26 (seed) | Arlington ART | realtime.commuterpage.com (Connexionz) | realtime.arlingtontransit.com (Clever pattern); URL change committed 2023-11-07 | — |
| 2022-05-26 (seed) | Edmonton ETS | data.edmonton.ca (portal) | gtfs.edmonton.ca (Trapeze TM) | — |
| 2022-11-14 | Intercity Transit (Olympia) | api.pugetsound.onebusaway.org | its.rideralerts.com (Avail) | — |
| 2022-11-14 | King County Metro | api.pugetsound.onebusaway.org | s3 kcm-alerts-realtime-prod (Swiftly-pattern) | INIT system of record |
| 2024-08-29 | Madison Metro | transitdata.cityofmadison.com (TM naming) | metromap.cityofmadison.com (Clever BusTime pattern) | catalogue comment "New AVL feed redirect" |
| 2024-10-11 | MVgo (Mountain View TMA) | ridemvgo.org (GMV pattern) | mtma.tripshot.com (TripShot) | — |
| 2025-03-27 | Via Mobility (Boulder) | api.goswift.ly (Swiftly) | passio3.com (Passio) | — |
| 2025-03-31 | CTtransit | s3 cttransit-realtime-prod (Swiftly-pattern) | cttprdtmgtfs.ctttrpcloud.com (Trapeze cloud) | ctttrpcloud.com registered 2022-08-11 |
| 2025-04-07 | Cascades East Transit | Trillium alerts + Swiftly | passio3.com (Passio) | — |
| 2025-04-16 to 04-23 | BC Transit (Nanaimo, Comox, Kamloops, Kelowna, Squamish, Victoria, Whistler) | *.mapstrat.com (Strategic Mapping) | bct.tmix.se (Consat NextRide) | BC Transit NextRide page |
| 2025-06-04 | TARC Louisville | gtfsrealtime.ridetarc.org (TM naming) | tarc.rideralerts.com (Avail) | Avail onboard ITS award 2023 (file 12) |
| 2026-02-18 | Everett Transit | api.pugetsound.onebusaway.org | everett.mapstrat.com (Strategic Mapping) | — |
| 2026-02-18 | SEPTA | api.goswift.ly (Swiftly) | www3.septa.org (in-house) | — |
| 2026-03-11 | Marin Transit | marintransit.net (GMV pattern) | api.goswift.ly (Swiftly) + gtfsrt.marintransit.cadavl.com (Equans) | Systrans award Jan-2025, go-live Jul-2025 (file 35 A08) |
| 2026-05-19 | Lane Transit District | feed.ltd.org (agency path) | feed.ltd.org/TMGTFSRealTimeWebService (Trapeze TM) | — |
| 2026-06-29 | SMART (Sonoma-Marin rail) | api.goswift.ly (Swiftly) | api.511.org (MTC aggregator) | — |
| 2026-10-13 | Broward | bctmyride-buspas.com (deprecated) | redirect points to a University of Minnesota Peak Transit feed | catalogue error, excluded |

Net by vendor (2022-11 to 2026-10): Consat +7 systems (one contract); Avail +2 (Intercity Transit, TARC); Clever-pattern +2 (Arlington, Madison); Passio +2 (Via, Cascades East); Trapeze cloud +2 (CTtransit, LTD); Equans +1 (Marin); Strategic Mapping +1/−7; TripShot +1; Swiftly +2 (RTC SNV at seed, Marin) / −4 (Via, Cascades East, SEPTA, SMART) and probably −1 (CTtransit S3). Interpretation: the open-data publishing layer churns at about 1% of catalogued agencies per year; the two directions of churn are (i) incumbents re-hosting to their own clouds (Trapeze trpcloud/vontascloud, Avail myavail.cloud, Equans cadavl.com — all domains registered 2020–2022) and (ii) small agencies moving between SaaS publishers on price (Swiftly→Passio). Nothing in the history shows a large agency moving its publishing layer *from* a CAD/AVL incumbent's feed *to* Swiftly after 2022 except Marin (which did it alongside a CAD/AVL replacement).

---

## 10. Method and known biases (read before quoting any share)

1. **Publishing layer ≠ contract.** Every share above attributes the host that serves the public GTFS-RT feed. For in-house publishers (23 US agencies, 19% of the fleet) the CAD/AVL vendor is only known where files 12/31/35 documented it; for Swiftly-published agencies the system of record is documented for ~15 of 49. Do not read "Swiftly 12% of buses" as CAD/AVL share; read it as "Swiftly is the public real-time publisher for 12% of the US full-size bus fleet (Clever BusTime 7.3%, Avail 6.6%, Trapeze/Vontas 5.0% + 2.5%)".
2. **Official vs unofficial feeds.** MobilityData's `is_official` flag is set on only 339 of 1,095 rows; vendor-hosted feeds are mostly unflagged, so the flag cannot be used to filter. Both catalogues are community-curated: a feed's presence proves an agency publishes, its absence does not prove it does not (NJ Transit, DART and Ride On have real-time data behind registration or proprietary APIs). Whitespace figures are therefore upper bounds on "no real-time data" and exact figures for "no open GTFS-RT feed catalogued in MobilityData or transit.land".
3. **Catalogue coverage differs sharply.** 145 of the 361 covered NTD agencies (13,075 buses) were found only in transit.land, 16 only in MobilityData, 200 in both. The MobilityData catalogue misses several large publishers (CTA, Houston METRO, Pace, UTA, Pittsburgh, Westchester, DDOT, IndyGo, Santa Monica, JTA, Tucson, GRTC, Memphis, Delaware DTC, Honolulu). Any census from one catalogue alone is biased against in-house and incumbent-hosted feeds and toward SaaS vendors that register feeds for their customers.
4. **Multi-vendor stacks.** 30+ agencies publish two or more feeds from different vendors (Swiftly + Avail/GMV/Equans/Connexionz/Passio/OneBusAway; Vontas + Swiftly at GCRTA; Trapeze legacy + Swiftly contract at MARTA). The "primary publisher" rule prefers an attributed vendor over an agency host or aggregator and then the vendor with more feed records; the full vendor list per agency is kept in `all_vp_tu_vendors_active`. Shares by primary publisher therefore slightly understate Swiftly (which is often the second feed) and overstate the incumbent feed.
5. **Pattern-based rules.** 231 medium- and 62 low-confidence feed records rest on path-naming heuristics (TransitMaster directory naming, GMV `/gtfs-rt/` paths, INIT `/gtfsrealtime/TripUpdates`, `GTFS_*.pb` Modaxo naming, S3 `-realtime-prod` buckets). Each is corroborated by at least one documented customer, but individual agencies can be wrong; the share tables keep "(probable)" rows separate so the reader can drop them.
6. **Aggregators and regional feeds.** MTC 511 (13 Bay Area agencies), Valley Metro (Phoenix, RPTA, Tempe, Scottsdale, Glendale), CTtransit statewide (six NTD IDs), Puget Sound OneBusAway and the MTA all publish one feed for several NTD reporters; these were fanned out to every member NTD ID so that coverage is not understated, but the underlying CAD/AVL vendors are mixed.
7. **NTD join.** 1,051 atlas records carried NTD IDs directly; MobilityData providers were joined by exact URL match to atlas records, by non-shared host, by name+state token matching (threshold 0.55 with city bonus) and finally by a 105-row manual override table (`data/mobilitydata/gtfs_rt_census_overrides.csv`) that also removes ferries, rail-only operators, national-park and campus shuttles. The top-120 NTD agencies were reviewed by hand (Section 7); below rank 120 residual mismatches are possible but affect few buses.
8. **Sub-systems.** BC Transit (35 catalogued sub-systems), exo (12 sectors) and MTA Maryland (4 modes) were consolidated to one agency each; the Metrolinx TPI municipalities were kept as separate agencies because they are separate operators with one shared procurement. Vendor "agency counts" in press releases usually count sub-systems, which inflates them relative to this census.
9. **Canada.** No fleet universe; agency counts only; several mid-size agencies publish no GTFS-RT (Winnipeg, Laval, RTC Québec, STO) and were not individually verified.
10. **Dates.** Migration dates are catalogue commit dates (MobilityData's curators typically update within weeks of a public change, but the 2022-05-26 seed date hides earlier switches).

---

## 11. Files produced (all reproducible)

- Script: `/home/user/Project-2-/its-market-case/model/scripts/gtfs_rt_vendor_census.py` — run as
  `python3 -I model/scripts/gtfs_rt_vendor_census.py --mdb data/mobilitydata/catalog_20261107/feeds_v2.csv --atlas-dir data/mobilitydata/transitland_atlas_20261107/feeds --atlas-xw data/mobilitydata/transitland_atlas_20261107/crosswalks --ntd data/ntd_2025_bus_fleet_by_agency.csv --git-history data/mobilitydata/catalog_20261107/mdb_catalog_git_history_us_ca_rt.tsv --overrides data/mobilitydata/gtfs_rt_census_overrides.csv --outdir data` (from `/home/user/Project-2-/its-market-case`).
- Inputs (untrusted snapshots): `data/mobilitydata/catalog_20261107/feeds_v2.csv` (MobilityData, 2026-11-07); `data/mobilitydata/catalog_20261107/mdb_catalog_git_history_us_ca_rt.tsv` (extracted from the catalogue repo at commit 12587fb, 2026-10-27); `data/mobilitydata/transitland_atlas_20261107/{feeds,crosswalks}` (transitland-atlas commit df1e677, 2026-11-05); `data/mobilitydata/gtfs_rt_census_overrides.csv` (manual review table with sources).
- Outputs: `data/gtfs_rt_feeds_classified.csv` (one row per feed URL x operator, 1,095 MobilityData + 3,192 atlas records, vendor, rule, confidence, NTD match); `data/gtfs_rt_agency_census.csv` (one row per agency incl. all 2,644 NTD bus-file agencies, publisher, all vendors, hosts, fleet, tier, system of record, overlay flag); `data/gtfs_rt_vendor_share_by_tier.csv` (US by tier and Canada); `data/gtfs_rt_top100_ntd_review.csv`; `data/gtfs_rt_feed_migrations.csv` (744 first-added, 97 deprecation, 9 URL-change and 117 redirect events with dates).

---

## 12. Gaps

1. Web search was unavailable for the whole run, so vendor customer lists (Swiftly, Passio, Avail, Clever, Vontas, GMV, ETA, Connexionz, TransLoc, Optibus) could not be cross-checked beyond the counts on their home/about pages; customer-page URLs returned 404 or are JavaScript-rendered.
2. The S3 `-realtime-prod` bucket pattern (King County Metro, Community Transit, LA Metro alerts, former CTtransit) is attributed to Swiftly on naming only; a single agency page naming the publisher would upgrade 1,540 buses from "probable" to confirmed.
3. CAD/AVL system of record remains unevidenced for SEPTA, MBTA, UTA, RTD (INIT 2011, current status), St Louis, RIPTA, OCTA (OrbCAD current), Honolulu, RTC Southern Nevada, VTA, KCATA, MTA Maryland, Delaware DTC, HART, DDOT and most tier-2 agencies; the awards sweep in files 12/31/35 covered ~60 agencies.
4. Canada lacks a fleet universe; a CUTA Fact Book extract would allow fleet-weighted shares (file 04/05 gap).
5. Whitespace agencies were not individually checked for proprietary real-time APIs (NJ Transit, DART, Ride On, Winnipeg are known to have them); the whitespace is strictly "no open GTFS-RT in the two catalogues".
6. The MobilityData catalogue's history starts 2021-07 and most US/CA feeds were seeded on 2022-05-26, so switches before mid-2022 are invisible.

---

## 13. Source list (opened and read in this run unless marked)

- MobilityData feeds catalogue CSV: https://files.mobilitydatabase.org/feeds_v2.csv (downloaded 2026-11-07)
- MobilityData catalogue repository (git history, redirects, statuses): https://github.com/MobilityData/mobility-database-catalogs (cloned; HEAD 12587fb 2026-10-27)
- transit.land atlas (DMFR feed records, `us_ntd_id` tags, NTD crosswalk, NTD GTFS weblinks readme): https://github.com/transitland/transitland-atlas (cloned; HEAD df1e677 2026-11-05)
- FTA NTD RY2025 revenue vehicle inventory via data.transportation.gov (through file 16 outputs): https://data.transportation.gov/api/views/ifzt-j53d/rows.csv?accessType=DOWNLOAD
- Systrans (Equans) home page — NAVINEO, 250+ agencies, Green Bay and Lynchburg testimonials: https://systrans.com/
- BC Transit NextRide page (Consat contract): https://www.bctransit.com/nextride/
- MTA Maryland developer resources (Swiftly API): https://www.mta.maryland.gov/developer-resources
- Community Transit open data (S3 GTFS-RT URLs): https://www.communitytransit.org/open-data
- Transit app partners page (220+ agencies, city list): https://transitapp.com/partners
- Swiftly about page (200+ agencies): https://www.goswift.ly/about
- Hitachi Mobility Multimodal Solutions about page (300+ customers): https://www.hitachimms.com/about-us/
- Passio about page (250+ clients): https://passiotech.com/about-us/
- Avail about page (medium-sized fleets): https://availtec.com/about/
- TripSpark home page (450+ agencies, MyRide, Streets): https://www.tripspark.com/
- Optibus customers page (opened; no customer list rendered): https://optibus.com/customers/
- Consat home/digital-solutions pages (opened; no customer list): https://www.consat.com/ ; https://www.consat.com/en/digital-solutions/ ; Consat newsroom https://www.mynewsdesk.com/consat (opened; JS-rendered)
- RDAP registry records: https://rdap.org/domain/cadavl.com and the other hosting domains listed in finding 34
- Montgomery County Ride On Real Time page: https://www.montgomerycountymd.gov/DOT-Transit/RideOnRealTime.html
- Trinity Metro GTFS page: https://ridetrinitymetro.org/gtfs/
- Award and contract sources reused from files 12, 31 and 35 (cited per row in `data/mobilitydata/gtfs_rt_census_overrides.csv`), including: LA Metro legistar; MARTA board minutes 2023/2024; Kitsap Resolution 23-23; CapMetro/Pavilion contract record; Santa Monica LegiFile; TAM-America Marin article; Sound Transit Motion M2026-27; Broward legistar 18073; Miami-Dade matter 251682; AC Transit legistar attachment; CTA document 9620; WMATA CY2023 awards; NJ.com via Yahoo; GCRTA 2023 presentation; TAM-America SORTA article; Mass Transit GMV/LADOT; Akron METRO board packet; NCTD agreement; County Connection board items; Metro Magazine (INIT TriMet 2009, INIT Community Transit 2008, INIT Houston 2003, INIT Denver RTD 2011, DART selects INIT, Clever NJ Transit 2011); Milwaukee County legistar; WeGo board book Dec-2025; Phoenix legistar matter 9629; LA County BOS supdoc 95050 (Foothill/Avail); OCTA legistar 7840; SMART board book Jan-2023; Met Council 2026-41; NORTA legistar; TARC Resolution 2023-11; IndyGo board book Oct-2025; Avail PennDOT FRITS release; initse.com Seattle project page; Mass Transit Suffolk/INIT release; Systrans/Metrolinx release; Vontas/Hamilton release; TTC board report Feb-2016.
- Sibling research files used: 08 (vendor landscape), 12 (contract benchmarks), 16 (NTD pull), 31 (board award sweep), 32 (statutory registry incl. Consat Telematics revenue), 35 (award dataset).
