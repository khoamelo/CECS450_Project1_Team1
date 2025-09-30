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
    data = []
    sums, cnts = {h: 0.0 for h in headers}, {h: 0 for h in headers}
    for row in rdr:
        # store all rows for correlation calc
        data.append(row)
        for h in headers:
            v = row.get(h, "")
            try:
                x = float(v)
                if not math.isnan(x):
                    sums[h] += x
                    cnts[h] += 1
            except (TypeError, ValueError):
                pass

# get the stress lvl column
stress_lvl_col = None
for h in headers:
    if "stress" in h.lower() and "level" in h.lower():
        stress_lvl_col = h
        break

corr = {}
if stress_lvl_col:
    # get each pair of (factor, stress level) values
    for h in headers:
        if h != stress_lvl_col:
            factor_vals, stress_vals = [], []
            for row in data:
                try:
                    factor_val = float(row.get(h, ""))
                    stress_val = float(row.get(stress_lvl_col, ""))
                    if not (math.isnan(factor_val) or math.isnan(stress_val)):
                        factor_vals.append(factor_val)
                        stress_vals.append(stress_val)
                except (TypeError, ValueError):
                    pass
            
            # pearson correlation coefficient calc
            if len(factor_vals) > 2:
                n = len(factor_vals)
                sum_x = sum(factor_vals)
                sum_y = sum(stress_vals)
                sum_x2 = sum(x**2 for x in factor_vals)
                sum_y2 = sum(y**2 for y in stress_vals)
                sum_xy = sum(x*y for x, y in zip(factor_vals, stress_vals))

                numerator = n*sum_xy-sum_x*sum_y
                denominator = math.sqrt((n*sum_x2-sum_x**2)*(n*sum_y2-sum_y**2))

                if denominator != 0:
                    corr[h] = numerator / denominator
                else:
                    corr[h] = 0.0
            else:
                corr[h] = 0.0

# build data for plotting
names, scaled_means, raw_means, corr_vals = [], [], [], []
for h in headers:
    n = cnts[h]
    if n > 0:
        raw_mean = sums[h] / n
        names.append(h)
        raw_means.append(raw_mean)
        scaled_means.append(scale5(raw_mean, h))
        corr_vals.append(corr.get(h, 0.0))
if not names:
    raise SystemExit("No numeric columns to plot")
    
#shapes + categories
def norm(s: str) -> str:
    return s.strip().lower().replace(" ", "_")

SCHOOL = {
    "teacher_student_relationship", "study_load", "academic_performance", "extracurricular_performance"
}
SOCIAL = {
    "peer_pressure", "social_support", "self_esteem", "noise_level", "bullying"
}
HEALTH = {
    "headache", "stress_level", "breathing_problem", "blood_pressure", "mental_health",
    "depression", "anxiety_level"
}
PERSONAL = {
    "future_career_concerns", "basic_needs", "living_conditions", "safety", "sleep_quality"
}


def category_of(col_name: str) -> str:
    n = norm(col_name)
    if n in SCHOOL:  return "School"
    if n in SOCIAL:  return "Social life"
    if n in HEALTH:  return "Health"
    if n in PERSONAL:return "Personal"
    return "Personal"  # default if not listed

shape_map = {
    "School": "square",
    "Social life": "circle",
    "Health": "triangle-up",
    "Personal": "diamond",
}

categories = [category_of(n) for n in names]
shapes = [shape_map.get(cat, "diamond") for cat in categories]

#size range
MIN_SIZE, MAX_SIZE = 20.0, 80.0
sizes = [MIN_SIZE + (m/5.0) * (MAX_SIZE - MIN_SIZE) for m in scaled_means]

#plot with color scale
fig = go.Figure(
    go.Scatter(
        x=scaled_means, y=names, mode="markers",
        marker=dict(
            symbol=shapes,
            size=sizes,
            color=scaled_means,             # color by scaled mean
            colorscale="Viridis",           # nice interactive colormap
            showscale=True,                 # colorbar legend
            colorbar=dict(title="Mean (0–5)")
        ),
        hovertemplate="<b>%{y}</b><br>"
                      "Scaled Mean: %{x:.2f}/5<br>"
                      "Raw Mean: %{customdata[0]:.2f}<br>"
                      "Correlation to Stress Level: %{customdata[1]:.2f}"
                      "<extra></extra>",
        customdata=list(zip(raw_means, corr_vals)),
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
    annotations=[dict(
        text="Shapes — School: ■  Social life: ●  Health: ▲  Personal: ◆",
        x=0, y=1.08, xref="paper", yref="paper", showarrow=False, xanchor="left", font=dict(size=12)
    )]
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

fig.update_annotations(yshift=-11)
fig.update_annotations(xshift=100)

# Save interactive HTML
fig.write_html("scatter_plot_interactive.html", include_plotlyjs="cdn")
print("Wrote scatter_plot_interactive.html")
fig.show()
