#!/usr/bin/env bash
# Log per-second WiFi state during a drive-around survey to a CSV.
#
# Captures for two interfaces (built-in wlan0 and USB wlx... dongle):
#   BSSID currently associated, signal (dBm), tx bitrate (Mbit/s),
#   cumulative rx/tx byte counters, plus the current default-route
#   interface + metric so you can see which radio owned outbound traffic.
#
# Ctrl-C to stop. Output goes to $PWD/wifi_drive_<timestamp>.csv.
#
# Analyze with tools/plot_wifi_drive.py.
#
# NOTE: the USB interface name is hard-coded to `wlx90de801012a6` (the
# specific dongle used on our robot). Change USB_IF below for a different
# dongle, or set it via env: USB_IF=wlxABCDEF012345 bash wifi_drive_logger.sh

set -u
USB_IF="${USB_IF:-wlx90de801012a6}"

LOG="wifi_drive_$(date +%Y%m%d_%H%M%S).csv"
echo "ts,default_iface,default_metric,wlan0_bssid,wlan0_signal,wlan0_bitrate,wlan0_rx,wlan0_tx,wlxUSB_bssid,wlxUSB_signal,wlxUSB_bitrate,wlxUSB_rx,wlxUSB_tx" > "$LOG"
echo "Logging to $LOG  (Ctrl-C to stop)"

while sleep 1; do
  ts=$(date +%Y-%m-%dT%H:%M:%S.%3N)
  read di dm <<<"$(ip -o -4 route show default | head -1 | awk '{for(i=1;i<=NF;i++){if($i=="dev")d=$(i+1); if($i=="metric")m=$(i+1)} print d,m}')"
  read w0b w0s w0r <<<"$(iw dev wlan0 link 2>/dev/null | awk '/Connected to/{b=$3} /signal:/{s=$2} /tx bitrate:/{r=$3} END{print (b?b:"NA"),(s?s:"NA"),(r?r:"NA")}')"
  read wub wus wur <<<"$(iw dev "$USB_IF" link 2>/dev/null | awk '/Connected to/{b=$3} /signal:/{s=$2} /tx bitrate:/{r=$3} END{print (b?b:"NA"),(s?s:"NA"),(r?r:"NA")}')"
  w0rx=$(cat /sys/class/net/wlan0/statistics/rx_bytes 2>/dev/null || echo 0)
  w0tx=$(cat /sys/class/net/wlan0/statistics/tx_bytes 2>/dev/null || echo 0)
  wurx=$(cat "/sys/class/net/$USB_IF/statistics/rx_bytes" 2>/dev/null || echo 0)
  wutx=$(cat "/sys/class/net/$USB_IF/statistics/tx_bytes" 2>/dev/null || echo 0)
  echo "$ts,${di:-NA},${dm:-NA},$w0b,$w0s,$w0r,$w0rx,$w0tx,$wub,$wus,$wur,$wurx,$wutx" | tee -a "$LOG"
done
