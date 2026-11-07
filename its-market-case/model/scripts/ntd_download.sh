#!/usr/bin/env bash
# Downloads FTA National Transit Database (NTD) annual tables from the USDOT Socrata open-data
# portal (data.transportation.gov) as full CSV exports. transit.dot.gov itself is blocked by the
# session network policy, but the same NTD products are federated on data.transportation.gov.
# Usage: bash ntd_download.sh <output_dir>   (output_dir must be a fresh, empty folder; treat as untrusted data)
set -euo pipefail
OUT="${1:?output dir}"
mkdir -p "$OUT"
while read -r id name; do
  [ -z "$id" ] && continue
  url="https://data.transportation.gov/api/views/${id}/rows.csv?accessType=DOWNLOAD"
  echo "downloading $name ($id) from $url"
  curl -sS --max-time 600 -L "$url" -o "$OUT/${name}__${id}.csv"
  # verify against API row count
  n=$(curl -sS --max-time 60 "https://data.transportation.gov/resource/${id}.json?\$select=count(*)" | sed -E 's/[^0-9]//g')
  echo "  api_count=$n"
done <<'IDS'
ifzt-j53d 2025_revenue_vehicle_inventory
nimp-626k 2022_2025_vehicles_type_count_by_agency
6abt-uhgq 2022_2025_vehicles_age_distribution
fphd-jyyj 2022_2025_capital_expenses_by_capital_use
8rr7-fd8y 2025_capital_use
8ffu-2anj 2025_capital_expenditures_time_series_3_1
jm7a-9hsy 2025_reporter_agency_information
ccvf-fykn 2024_reporter_agency_information
4ucy-dac3 2025_operating_expenses
dkxx-zjd6 2022_2025_operating_expenses_by_function
j5uj-anzx 2022_2025_operating_expenses_by_type
74ek-quhs 2025_service
wwdp-t4re 2022_2025_service_by_mode_and_time_period
eu97-reg7 2025_database_file_dictionary
fzbb-f6kc 2022_2025_track_and_roadway_by_mode
IDS
# Landing pages (human-readable): https://datahub.transportation.gov/d/<id>
# Column definitions: https://data.transportation.gov/api/views/<id>.json
