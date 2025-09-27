# DVProject1Team1.py 
import csv, math
from pathlib import Path
import plotly.graph_objects as go

# === your function (used for ALL factors) ===
def scale5(mean, name):
    n = name.strip().lower().replace(" ", "_")
    raw_max = 2.0 if n == "stress_level" else 30.0
    return max(0.0, min(5.0, mean * (5.0 / raw_max)))

# locate CSV
CSV = None
for p in ("StressLevelDataset.csv", "data/StressLevelDataset.csv"):
    if Path(p).exists():
        CSV = p
        break
if not CSV:
    raise SystemExit("Could not find StressLevelDataset.csv")

# read & accumulate numeric means for every header (skip a few obvious metadata cols)
SKIP = {"id","index","row","timestamp","time","date"}
with open(CSV, newline="", encoding="utf-8") as f:
    rdr = csv.DictReader(f)
    headers = [h for h in (rdr.fieldnames or []) if h and h.strip().lower() not in SKIP]
    sums = {h: 0.0 for h in headers}
    cnts = {h: 0   for h in headers}
    for row in rdr:
        for h in headers:
            v = row.get(h, "")
            try:
                x = float(v)
                if not math.isnan(x):
                    sums[h] += x
                    cnts[h] += 1
            except (TypeError, ValueError):
                pass

# build dots: x = scaled mean (0–5), y = factor
names, means5 = [], []
for h in headers:
    n = cnts[h]
    if n > 0:
        raw_mean = sums[h] / n
        names.append(h)
        means5.append(scale5(raw_mean, h))
if not names:
    raise SystemExit("No numeric columns to plot")

# plot 
fig = go.Figure(
    go.Scatter(
        x=means5, y=names, mode="markers",
        marker=dict(symbol="circle", size=12, color="#2ca02c"),
        hovertemplate="factor=%{y}<br>mean (0–5)=%{x:.2f}<extra></extra>",
        showlegend=False
    )
)

# layout
fig.update_layout(
    title="Factors Affect Student Stress",
    xaxis_title="Quantiles",
    yaxis_title="Factor",
    paper_bgcolor="white", plot_bgcolor="white",
    template=None, width=900,
    height=max(600, 28*len(names)+160),
    margin=dict(l=110, r=40, t=70, b=60),
)


fig.update_xaxes(range=[0,5], dtick=0.5, showgrid=True, zeroline=True,ticks="outside", linecolor="black", linewidth=1, mirror=True)

fig.update_yaxes(showgrid=True, zeroline=True, ticks="outside",linecolor="black", linewidth=1, mirror=True, automargin=True)

fig.write_html("scatter_plot.html", include_plotlyjs="cdn")
print("Wrote scatter_plot.html")
