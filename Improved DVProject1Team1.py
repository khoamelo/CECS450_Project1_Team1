# DVProject1Team1.py 
import csv, math
from pathlib import Path
import plotly.graph_objects as go

#scaling function (used for ALL factors)
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

# read & accumulate numeric means for every header (skip metadata cols)
SKIP = {"id","index","row","timestamp","time","date"}
with open(CSV, newline="", encoding="utf-8") as f:
    rdr = csv.DictReader(f)
    headers = [h for h in (rdr.fieldnames or []) if h and h.strip().lower() not in SKIP]
    sums, cnts = {h: 0.0 for h in headers}, {h: 0 for h in headers}
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

# build data for plotting
names, scaled_means, raw_means = [], [], []
for h in headers:
    n = cnts[h]
    if n > 0:
        raw_mean = sums[h] / n
        names.append(h)
        raw_means.append(raw_mean)
        scaled_means.append(scale5(raw_mean, h))
if not names:
    raise SystemExit("No numeric columns to plot")

#plot with color scale
fig = go.Figure(
    go.Scatter(
        x=scaled_means, y=names, mode="markers",
        marker=dict(
            symbol="circle",
            size=14,
            color=scaled_means,             # color by scaled mean
            colorscale="Viridis",           # nice interactive colormap
            showscale=True,                 # colorbar legend
            colorbar=dict(title="Mean (0–5)")
        ),
        hovertemplate="<b>%{y}</b><br>"
                      "Scaled Mean: %{x:.2f}/5<br>"
                      "Raw Mean: %{customdata:.2f}<extra></extra>",
        customdata=raw_means,
        showlegend=False
    )
)

#layout enhancements
fig.update_layout(
    title="Factors Affecting Student Stress (Interactive)",
    xaxis_title="Scaled Mean (0–5)",
    yaxis_title="Factor",
    paper_bgcolor="white",
    plot_bgcolor="white",
    template="plotly_white",
    width=950,
    height=max(650, 30*len(names)+160),
    margin=dict(l=120, r=60, t=80, b=70),
)

# x-axis interactive settings
fig.update_xaxes(
    range=[0, 5],
    dtick=0.5,
    showgrid=True,
    zeroline=True,
    ticks="outside",
    linecolor="black",
    linewidth=1,
    mirror=True,
    rangeslider=dict(visible=True)  # add interactive slider
)

# y-axis formatting
fig.update_yaxes(
    showgrid=True,
    zeroline=False,
    ticks="outside",
    linecolor="black",
    linewidth=1,
    mirror=True,
    automargin=True
)

# Save interactive HTML
fig.write_html("scatter_plot_interactive.html", include_plotlyjs="cdn")
print("Wrote scatter_plot_interactive.html")
