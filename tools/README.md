# tools/

Ad-hoc drive-around WiFi survey tools. Standalone from the ROS package —
just a bash logger and a Python plotter. Useful for characterizing WiFi
coverage in a home/office mesh before bringing up the ROS logger node.

## `wifi_drive_logger.sh`

Per-second CSV logger. Captures BSSID / signal / bitrate / rx+tx byte
counters for the built-in `wlan0` and one USB dongle (default
`wlx90de801012a6`; override with `USB_IF=...`). Also records which
interface currently owns the default route and its metric.

```bash
cd ~/wifi_logs                       # or wherever you want the CSV
bash /path/to/tools/wifi_drive_logger.sh
# ...drive the robot around...
# Ctrl-C when done
```

Output file: `wifi_drive_<timestamp>.csv` in the current directory.

Columns: `ts, default_iface, default_metric, wlan0_bssid, wlan0_signal,
wlan0_bitrate, wlan0_rx, wlan0_tx, wlxUSB_bssid, wlxUSB_signal,
wlxUSB_bitrate, wlxUSB_rx, wlxUSB_tx`. Unavailable fields are `NA`.

## `plot_wifi_drive.py`

Plots the USB dongle's signal over time, colored by BSSID. Writes a PNG
next to the CSV and opens an interactive window if `$DISPLAY` is set.

```bash
python3 /path/to/tools/plot_wifi_drive.py ~/wifi_logs/wifi_drive_20260711_075912.csv
```

Headless (no X):

```bash
MPLBACKEND=Agg python3 /path/to/tools/plot_wifi_drive.py <csv>
```

Requires `python3-matplotlib`. `python3-yaml` is optional but recommended
so the legend can show friendly AP names.

### AP name mapping (sidecar YAML)

To show room names in the legend instead of raw BSSIDs, create an
`ap_map.yaml` (see `ap_map.example.yaml` for the format).

Lookup order:

1. `--map <path>` on the command line
2. `$AP_MAP` environment variable
3. `ap_map.yaml` next to the CSV
4. `~/ap_map.yaml`

Missing entries fall back to the raw BSSID — the plot still renders.
