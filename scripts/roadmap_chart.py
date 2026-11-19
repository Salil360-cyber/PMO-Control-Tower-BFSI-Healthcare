"""Portfolio roadmap: planned dates vs actual finish (done) or EVM forecast finish (running)."""
import pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt, matplotlib.dates as mdates
P = pd.read_csv("01_data/projects.csv", parse_dates=["start_date", "planned_end"])
W = pd.read_csv("01_data/weekly_status.csv", parse_dates=["week_ending"])
AS_OF = pd.Timestamp("2027-07-02")
last = W.sort_values("week_ending").groupby("project_id").tail(1).set_index("project_id")
rows = []
for _, p in P.iterrows():
    l = last.loc[p.project_id]
    if l.pct_complete >= 1:
        end, kind = l.week_ending, "Finished"
    else:  # same rule as SQL Q3: planned duration / SPI
        spi = l.earned_value_lakh / l.planned_value_lakh
        end, kind = p.start_date + pd.Timedelta(days=round((p.planned_end - p.start_date).days / spi)), "Forecast (EVM)"
    rows.append((p.project_id, p.project_name, p.start_date, p.planned_end, end, kind))
INK, MUTED, GRID, PLAN, DONE, LATE = "#1b1f24", "#5b6470", "#e6e8eb", "#c9d6ea", "#1f4e9a", "#c0392b"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": GRID,
                     "xtick.color": MUTED, "ytick.color": INK})
fig, ax = plt.subplots(figsize=(14, 6.2))
for i, (pid, name, s, pe, e, kind) in enumerate(rows):
    y = len(rows) - 1 - i
    ax.barh(y + .17, (pe - s).days, left=s, height=.3, color=PLAN, label="Planned" if i == 0 else None)
    col = DONE if kind == "Finished" else LATE
    ax.barh(y - .17, (e - s).days, left=s, height=.3, color=col)
    late = (e - pe).days
    txt = f"{e:%d %b %Y}" + (f"  (+{late} days)" if late > 0 else "  (on time)")
    ax.text(e + pd.Timedelta(days=3), y - .17, txt, va="center", fontsize=9, color=col)
ax.set_yticks(range(len(rows)), [f"{r[0]}  {r[1]}" for r in rows][::-1])
ax.axvline(AS_OF, color=INK, lw=1, ls="--"); ax.text(AS_OF, len(rows) - .35, " status date 2 Jul 2027", fontsize=9, color=INK)
ax.xaxis.set_major_locator(mdates.MonthLocator()); ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
ax.set_xlim(pd.Timestamp("2026-12-25"), pd.Timestamp("2028-04-30")); ax.xaxis.grid(True, color=GRID); ax.set_axisbelow(True)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=PLAN, label="Planned"), Patch(color=DONE, label="Actual (finished)"), Patch(color=LATE, label="Forecast (running, EVM)")],
          frameon=False, loc="upper right", fontsize=9)
ax.set_title("Portfolio roadmap: plan vs actual / forecast finish", loc="left", fontsize=13, weight="bold", color=INK)
fig.tight_layout(); fig.savefig("04_powerbi/screenshots/portfolio_roadmap.png", dpi=110)
for r in rows: print(r[0], r[3].date(), r[4].date(), r[5])
