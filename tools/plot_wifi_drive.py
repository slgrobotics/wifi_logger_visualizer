#!/usr/bin/env python3
"""Plot wlxUSB signal over time, colored by AP (BSSID).
Interactive window — run from a session that can display X (PuTTY+X or NoMachine).
Always writes a PNG next to the CSV.

Usage:  python3 plot_wifi_drive.py [csv_path] [--map ap_map.yaml]

AP names come from a sidecar YAML (see tools/ap_map.example.yaml).
Lookup order for the map file:
  1. --map <path> on the command line
  2. $AP_MAP environment variable
  3. ap_map.yaml in the same directory as the CSV
  4. ~/ap_map.yaml
If none is found, BSSIDs render as raw MACs.
"""
import sys, os, csv, argparse
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

try:
    import yaml
except ImportError:
    yaml = None


def load_ap_map(csv_path, explicit):
    candidates = []
    if explicit:
        candidates.append(explicit)
    env = os.environ.get("AP_MAP")
    if env:
        candidates.append(env)
    candidates.append(os.path.join(os.path.dirname(os.path.abspath(csv_path)),
                                   "ap_map.yaml"))
    candidates.append(os.path.expanduser("~/ap_map.yaml"))
    for p in candidates:
        if p and os.path.isfile(p):
            if yaml is None:
                sys.stderr.write(
                    f"AP map found at {p} but PyYAML not installed; "
                    "legend will show raw BSSIDs.\n")
                return {}, None
            with open(p) as f:
                data = yaml.safe_load(f) or {}
            m = data.get("aps", {}) if isinstance(data, dict) else {}
            return {k.lower(): v for k, v in m.items()}, p
    return {}, None


ap = argparse.ArgumentParser()
ap.add_argument("csv", help="wifi_drive_*.csv produced by wifi_drive_logger.sh")
ap.add_argument("--map", dest="mapfile", default=None,
                help="AP map YAML (default: auto-discover)")
args = ap.parse_args()
CSV = args.csv

AP_NAME, map_src = load_ap_map(CSV, args.mapfile)
if map_src:
    print(f"AP map:  {map_src}  ({len(AP_NAME)} entries)")
else:
    print("AP map:  (none found — legend will show raw BSSIDs)")

def ap_label(bssid):
    return AP_NAME.get(bssid.lower(), bssid)


ts, sig, bss = [], [], []
with open(CSV) as f:
    for r in csv.DictReader(f):
        b = r["wlxUSB_bssid"]
        s = r["wlxUSB_signal"]
        if b in ("", "NA") or s in ("", "NA"):
            continue
        ts.append(datetime.fromisoformat(r["ts"]))
        sig.append(int(s))
        bss.append(b)

bssids = sorted(set(bss))
cmap = plt.get_cmap("tab10")
color = {b: cmap(i % 10) for i, b in enumerate(bssids)}

fig, ax = plt.subplots(figsize=(14, 5))
for b in bssids:
    xs = [t for t, bb in zip(ts, bss) if bb == b]
    ys = [s for s, bb in zip(sig, bss) if bb == b]
    ax.scatter(xs, ys, s=14, color=color[b],
               label=f"{ap_label(b)}  {b}")

ax.axhline(-70, color="gray", ls="--", lw=0.5, label="-70 dBm")
ax.axhline(-80, color="red",  ls="--", lw=0.5, label="-80 dBm")
ax.set_ylabel("Signal (dBm)")
ax.set_xlabel("Time")
ax.set_title(f"wlxUSB signal — {os.path.basename(CSV)}")
ax.grid(True, alpha=0.3)
ax.legend(loc="lower left", fontsize=9)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right")
plt.tight_layout()

out = os.path.splitext(CSV)[0] + "_signal.png"
plt.savefig(out, dpi=120)
print(f"Saved: {out}")
plt.show()
