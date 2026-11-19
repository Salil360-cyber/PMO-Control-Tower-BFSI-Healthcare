"""Static preview of the 2-page Power BI design, from the same CSVs (numbers match SQL)."""
import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
P = pd.read_csv("01_data/projects.csv"); W = pd.read_csv("01_data/weekly_status.csv", parse_dates=["week_ending"])
R = pd.read_csv("01_data/raid_log.csv", parse_dates=["due_date"]); C = pd.read_csv("01_data/change_requests.csv")
RA = pd.read_csv("01_data/resource_allocation.csv", parse_dates=["week_ending"]); M = pd.read_csv("01_data/milestones.csv", parse_dates=["planned_date", "forecast_date"])
AS_OF = pd.Timestamp("2027-07-02")
L = W.sort_values("week_ending").groupby("project_id").tail(1).merge(P, on="project_id")
L["spi"] = L.earned_value_lakh / L.planned_value_lakh; L["cpi"] = L.earned_value_lakh / L.actual_cost_lakh
INK, MUTED, GRID, BAR, KEY, BG = "#1b1f24", "#5b6470", "#e6e8eb", "#9db4d6", "#1f4e9a", "#ffffff"
RED, AMB, GRN = "#c0392b", "#d68910", "#1e8449"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRID, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.labelcolor": MUTED, "axes.spines.top": False, "axes.spines.right": False})

def card(ax, label, value):
    ax.axis("off"); ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, color="#f3f5f8"))
    ax.text(.06, .6, value, fontsize=22, weight="bold", color=INK, transform=ax.transAxes)
    ax.text(.06, .2, label, fontsize=10, color=MUTED, transform=ax.transAxes)

def title(ax, t):
    ax.set_title(t, loc="left", color=INK, fontsize=11, weight="bold")

def page(t):
    fig = plt.figure(figsize=(16, 9), facecolor=BG)
    fig.text(.03, .955, t, fontsize=18, weight="bold", color=INK)
    fig.text(.03, .925, "PMO Control Tower · Sahyog Financial Group (fictional: bank + health insurer) · 8 projects · status date 2 Jul 2027", fontsize=10, color=MUTED)
    return fig

def ragc(v):
    return GRN if v >= .95 else (AMB if v >= .85 else RED)

# Page 1
fig = page("Portfolio health")
water = ((L.reported_rag == "Green") & (L[["spi", "cpi"]].min(axis=1) < .95)) | ((L.reported_rag == "Amber") & (L[["spi", "cpi"]].min(axis=1) < .85))
over = ((R.status == "Open") & (R.due_date < AS_OF)).sum()
for i, (l, v) in enumerate([("Projects (5 done, 3 running)", "8"), ("Budget", "₹530 lakh"), ("Watermelon projects", str(int(water.sum()))), ("Overdue RAID items", str(int(over)))]):
    card(fig.add_axes([.03 + i * .24, .76, .22, .12]), l, v)
ax = fig.add_axes([.06, .08, .38, .58])
ax.axhline(1, color=GRID); ax.axvline(1, color=GRID); ax.axhline(.85, color=GRID, ls="--"); ax.axvline(.85, color=GRID, ls="--")
for _, r in L.iterrows():
    col = ragc(min(r.spi, r.cpi)); ax.scatter(r.spi, r.cpi, s=40 + r.budget_lakh * 1.2, color=col, alpha=.85, edgecolor="white", linewidth=2, zorder=3)
    lab = {"P02": "P02, P06", "P06": ""}.get(r.project_id, r.project_id) + (" (reported " + r.reported_rag + ")" if bool(water[_]) else "")
    if lab: ax.annotate(lab, (r.spi, r.cpi), xytext=(8, 6), textcoords="offset points", fontsize=9, color=INK)
ax.set_xlim(.7, 1.08); ax.set_ylim(.75, 1.08); ax.set_xlabel("SPI (schedule): below 1 = behind"); ax.set_ylabel("CPI (cost): below 1 = over budget")
title(ax, "Where each project stands (bubble = budget, colour = EVM RAG)")
run = L[L.pct_complete < 1].copy()
appr = C[C.decision == "Approved"].groupby("project_id").cost_impact_lakh.sum()
run["revised"] = run.budget_lakh + run.project_id.map(appr).fillna(0); run["eac"] = run.budget_lakh / run.cpi
ax = fig.add_axes([.56, .48, .4, .2]); y = np.arange(len(run))
ax.barh(y + .18, run.revised, height=.34, color=BAR, label="Revised budget"); ax.barh(y - .18, run.eac, height=.34, color=RED, label="Forecast cost (EAC)")
ax.set_yticks(y, run.project_id); ax.invert_yaxis(); ax.legend(frameon=False, fontsize=9, loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2)
for i, (rv, e) in enumerate(zip(run.revised, run.eac)):
    ax.text(e, i - .18, f" {e:.1f}", va="center", fontsize=9, color=INK); ax.text(rv, i + .18, f" {rv:.1f}", va="center", fontsize=9, color=INK)
ax.set_xlim(0, 440); title(ax, "Running projects: forecast cost vs revised budget (₹ lakh)")
me = W.groupby(W.week_ending.dt.to_period("M")).week_ending.max()
tr = W[W.week_ending.isin(me)].groupby("week_ending").agg(pv=("planned_value_lakh", "sum"), ev=("earned_value_lakh", "sum"), ac=("actual_cost_lakh", "sum"))
ax = fig.add_axes([.56, .08, .4, .24]); x = tr.index.strftime("%b")
ax.plot(x, tr.ev / tr.pv, color=KEY, lw=2, marker="o", label="Portfolio SPI"); ax.plot(x, tr.ev / tr.ac, color=MUTED, lw=2, marker="o", label="Portfolio CPI")
ax.axhline(.95, color=GRID, ls="--"); ax.set_ylim(.7, 1.0); ax.legend(frameon=False, fontsize=9); ax.yaxis.grid(True, color=GRID)
title(ax, "Portfolio SPI and CPI at each month end")
fig.savefig("04_powerbi/screenshots/page1_portfolio_health.png", dpi=100); plt.close(fig)

# Page 2
fig = page("Delivery control: RAID, resources, milestones, changes")
o = R[R.status == "Open"].assign(overdue=lambda d: d.due_date < AS_OF).groupby("project_id").overdue.sum().reindex(P.project_id).fillna(0)
ax = fig.add_axes([.05, .55, .4, .3]); ax.bar(o.index, o.values, color=[RED if v > 0 else BAR for v in o.values], width=.6)
for i, v in enumerate(o.values): ax.text(i, v, f"{int(v)}", ha="center", va="bottom", fontsize=9)
title(ax, "Overdue open RAID items by project"); ax.yaxis.grid(True, color=GRID); ax.set_axisbelow(True)
t = RA.groupby(["person", "week_ending"]).allocated_hours.sum().unstack()
top = t[(t > 40).sum(axis=1) > 0]
ax = fig.add_axes([.55, .55, .42, .3]); im = ax.imshow(top.values, aspect="auto", cmap=matplotlib.colors.ListedColormap(["#eef2f8", "#9db4d6", "#e6a39b"]),
                                                       norm=matplotlib.colors.BoundaryNorm([0, 33, 40.5, 80], 3))
ax.set_yticks(range(len(top)), top.index); ax.set_xticks(range(0, len(top.columns), 4), [d.strftime("%d %b") for d in top.columns[::4]])
title(ax, "Over-allocated people: hours per week (red = over 40)")
sl = M.assign(slip=(M.forecast_date - M.planned_date).dt.days).groupby("project_id").slip.mean().reindex(P.project_id)
ax = fig.add_axes([.05, .08, .4, .32]); ax.bar(sl.index, sl.values, color=[RED if v > 14 else BAR for v in sl.values], width=.6)
for i, v in enumerate(sl.values): ax.text(i, max(v, 0), f"{v:.0f}", ha="center", va="bottom", fontsize=9)
title(ax, "Average milestone slip (days)"); ax.yaxis.grid(True, color=GRID); ax.set_axisbelow(True)
ca = C[C.decision == "Approved"].groupby("project_id").cost_impact_lakh.sum().reindex(P.project_id).fillna(0)
ax = fig.add_axes([.55, .08, .42, .32]); ax.bar(ca.index, ca.values, color=[KEY if v == ca.max() else BAR for v in ca.values], width=.6)
for i, v in enumerate(ca.values): ax.text(i, v, f"{v:.1f}", ha="center", va="bottom", fontsize=9)
title(ax, "Cost added by approved change requests (₹ lakh)"); ax.yaxis.grid(True, color=GRID); ax.set_axisbelow(True)
fig.savefig("04_powerbi/screenshots/page2_delivery_control.png", dpi=100); plt.close(fig)
print("ok")
