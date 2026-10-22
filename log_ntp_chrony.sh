#!/usr/bin/env bash
set -euo pipefail

OUTDIR="${1:-./ntp_logs}"
INTERVAL="${2:-1}"

mkdir -p "$OUTDIR"

RUN_TS=$(date +"%Y%m%d_%H%M%S")

TRACK_CSV="$OUTDIR/chrony_tracking_${RUN_TS}.csv"
SOURCES_CSV="$OUTDIR/chrony_sources_${RUN_TS}.csv"
SOURCESTATS_CSV="$OUTDIR/chrony_sourcestats_${RUN_TS}.csv"

echo "unix_time,ref_id,stratum,ref_time_utc,system_time_offset_s,last_offset_s,rms_offset_s,frequency_ppm,residual_freq_ppm,skew_ppm,root_delay_s,root_dispersion_s,update_interval_s,leap_status" > "$TRACK_CSV"
echo "unix_time,mode,state,name,source_ip,stratum,poll,reachability,last_rx_s,last_sample" > "$SOURCES_CSV"
echo "unix_time,name,np,nr,span_s,frequency_ppm,freq_skew_ppm,offset_s,std_dev_s" > "$SOURCESTATS_CSV"

echo "Logging to:"
echo "  $TRACK_CSV"
echo "  $SOURCES_CSV"
echo "  $SOURCESTATS_CSV"

while true; do
    TS=$(date +%s.%N)

    chronyc -c tracking    | awk -F, -v ts="$TS" '{print ts "," $0}' >> "$TRACK_CSV" || true
    chronyc -c sources     | awk -F, -v ts="$TS" '{print ts "," $0}' >> "$SOURCES_CSV" || true
    chronyc -c sourcestats | awk -F, -v ts="$TS" '{print ts "," $0}' >> "$SOURCESTATS_CSV" || true

    sleep "$INTERVAL"
done
