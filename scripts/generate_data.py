"""Synthetic PMO data for a fictional group (Sahyog Financial Group: a bank + a health insurer).
8 projects, 26 weekly reporting weeks (Fridays 8 Jan to 2 Jul 2027). All names and numbers are invented."""
import numpy as np, pandas as pd, datetime as dt

rng = np.random.default_rng(27)
W0 = dt.date(2027, 1, 8)
WEEKS = [W0 + dt.timedelta(weeks=i) for i in range(26)]
AS_OF = WEEKS[-1]

# id, name, unit, domain, method, sponsor, pm, start_week(1-based), planned_weeks, BAC (Rs lakh), vendor, true SPI, true CPI, PM-reported RAG bias
P = [
 ("P01", "Video KYC Capacity Upgrade", "Retail Banking", "Banking", "Agile", "Head of Retail Banking", "Ananya Rao", 1, 16, 45, "No", 0.96, 1.00, None),
 ("P02", "Loan Fast-Track Lane", "Retail Lending", "Banking", "Agile", "Head of Retail Lending", "Rohit Kulkarni", 1, 14, 18, "Yes", 0.91, 0.97, None),
 ("P03", "NHCX Cashless Claims Integration", "Health Insurance", "Healthcare", "Hybrid", "Head of Claims", "Meera Iyer", 3, 30, 60, "Yes", 0.87, 0.89, None),
 ("P04", "UPI AutoPay for EMI Collections", "Collections", "Banking", "Agile", "Head of Collections", "Vikram Shah", 2, 17, 30, "No", 1.02, 1.04, None),
 ("P05", "AML Alert Threshold Tuning", "Compliance", "Banking", "Waterfall", "Chief Compliance Officer", "Farah Khan", 1, 20, 25, "No", 0.97, 0.96, None),
 ("P06", "Branch MIS Automation", "Operations", "Banking", "Agile", "Head of Operations", "Ananya Rao", 4, 12, 12, "No", 1.00, 1.03, None),
 ("P07", "Hospital Network Empanelment Portal", "Health Insurance", "Healthcare", "Waterfall", "Head of Provider Network", "Sanjay Menon", 2, 28, 40, "Yes", 0.78, 0.80, "Green"),
 ("P08", "Core Banking Upgrade (Phase 1)", "Technology", "Banking", "Waterfall", "Chief Technology Officer", "Deepa Nair", 1, 40, 300, "Yes", 0.82, 0.86, "Amber"),
]
proj = pd.DataFrame([dict(project_id=p[0], project_name=p[1], business_unit=p[2], domain=p[3], method=p[4], sponsor=p[5],
                          project_manager=p[6], start_date=W0 + dt.timedelta(weeks=p[7] - 1) - dt.timedelta(days=4),
                          planned_end=W0 + dt.timedelta(weeks=p[7] - 1 + p[8] - 1), budget_lakh=p[9], vendor_led=p[10]) for p in P])

def curve(x):  # S-curve share of work done at fraction x of time
    x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)

def rag(v):
    return "Green" if v >= 0.95 else ("Amber" if v >= 0.85 else "Red")

rows = []
for (pid, name, unit, dom, meth, spn, pm, sw, pw, bac, ven, spi, cpi, bias) in P:
    ev_prev = 0; ac_prev = 0; done = False
    for k, wk in enumerate(WEEKS, 1):
        if k < sw or done:
            continue
        t = (k - sw + 1) / pw
        pv = bac * curve(t)
        ev = bac * curve(t * spi * rng.normal(1, 0.015))
        ev = float(np.clip(max(ev, ev_prev), 0, bac))
        ac = max(ac_prev, ev / (cpi * rng.normal(1, 0.02))) if ev > 0 else 0
        ev_prev, ac_prev = ev, ac
        submitted = "No" if (rng.random() < (0.12 if pid in ("P07", "P08", "P03") else 0.03)) else "Yes"
        true_rag = rag(min(ev / pv if pv else 1, ev / ac if ac else 1))
        reported = bias if (bias and k - sw > 3) else true_rag
        if bias == "Amber" and true_rag == "Green":
            reported = "Green"
        rows.append(dict(project_id=pid, week_ending=wk, status_submitted=submitted,
                         planned_value_lakh=round(pv, 2), earned_value_lakh=round(ev, 2), actual_cost_lakh=round(ac, 2),
                         pct_complete=round(ev / bac, 3), reported_rag=reported if submitted == "Yes" else ""))
        if ev >= bac - 1e-6:
            done = True
ws = pd.DataFrame(rows)

# milestones
MS = {
 "P01": ["Vendor slots contracted", "Scheduling module live", "Agent pool expanded", "Go-live", "Benefits review"],
 "P02": ["BRD signed off", "Checklist live", "Upload check live", "Fast-track lane live", "Go-live"],
 "P03": ["NHCX sandbox access", "Claim API build", "Insurer UAT", "Pilot with 10 hospitals", "Go-live"],
 "P04": ["NPCI mandate setup", "AutoPay journey built", "UAT", "Go-live", "Collections review"],
 "P05": ["Alert data extract", "Back-testing", "Compliance sign-off", "Thresholds live"],
 "P06": ["Data model", "Dashboard build", "Branch rollout"],
 "P07": ["Requirements signed off", "Portal build", "Document verification module", "UAT", "Go-live"],
 "P08": ["Vendor mobilised", "Data migration design", "Mock migration 1", "Mock migration 2", "SIT complete", "Cutover rehearsal"],
}
ms_rows = []
for (pid, name, unit, dom, meth, spn, pm, sw, pw, bac, ven, spi, cpi, bias) in P:
    n = len(MS[pid])
    for j, m in enumerate(MS[pid], 1):
        frac = j / n
        plan_wk = sw - 1 + round(pw * frac)
        planned = W0 + dt.timedelta(weeks=plan_wk - 1)
        slip_days = int(round((planned - (W0 - dt.timedelta(weeks=sw - 1))).days * (1 / spi - 1))) + int(rng.integers(-3, 4))
        slip_days = max(slip_days, -5)
        forecast = planned + dt.timedelta(days=slip_days)
        if forecast <= AS_OF:
            status, actual = "Completed", forecast
        else:
            status, actual = ("Late" if planned <= AS_OF else ("At risk" if slip_days > 10 else "On track")), None
        ms_rows.append(dict(milestone_id=f"{pid}-M{j}", project_id=pid, milestone=m, planned_date=planned,
                            forecast_date=forecast, actual_date=actual, status=status))
ms = pd.DataFrame(ms_rows)

# RAID
PROJ_END = {pid: d for pid, d in ws.groupby("project_id").week_ending.max().items() if ws[ws.project_id == pid].pct_complete.max() >= 1}
TPL = {
 "Risk": ["Vendor resource shortage may delay build", "Key SME may be unavailable during UAT", "Regulatory change may alter scope",
          "Data quality issues may delay testing", "Integration with legacy system may take longer than planned", "Budget may run out before go-live"],
 "Issue": ["Test environment unavailable for 5 days", "Vendor deliverable rejected in review", "Requirement gap found in UAT",
           "API access delayed by partner", "Key resource on unplanned leave"],
 "Action": ["Confirm UAT dates with business", "Send revised plan to sponsor", "Book steering committee slot", "Update RAID owners",
            "Chase vendor for revised timeline"],
 "Dependency": ["Needs security sign-off before go-live", "Needs data feed from core banking", "Needs NPCI / NHCX onboarding approval"],
}
OWN = ["Project manager", "Business analyst", "Vendor lead", "IT lead", "Business SME", "Compliance"]
weight = {"P01": 5, "P02": 6, "P03": 12, "P04": 5, "P05": 5, "P06": 3, "P07": 11, "P08": 16}
raid = []; rid = 0
for pid, nitems in weight.items():
    sw = [p for p in P if p[0] == pid][0][7]
    for _ in range(nitems):
        rid += 1
        typ = rng.choice(["Risk", "Issue", "Action", "Dependency"], p=[.4, .25, .25, .1])
        raised = W0 + dt.timedelta(days=int(rng.integers((sw - 1) * 7, 170)))
        due = raised + dt.timedelta(days=int(rng.integers(7, 35)))
        bad = pid in ("P03", "P07", "P08")
        finished = PROJ_END.get(pid)
        closed = (rng.random() < (0.45 if bad else 0.85) and due < AS_OF + dt.timedelta(days=10)) or (finished is not None)
        if finished is not None and raised > finished:
            raised = finished - dt.timedelta(days=int(rng.integers(10, 40))); due = raised + dt.timedelta(days=int(rng.integers(7, 21)))
        closed_on = max(raised, min(due + dt.timedelta(days=int(rng.integers(-5, 15 if bad else 6))), AS_OF)) if closed else None
        prob = int(rng.integers(2, 6)) if typ == "Risk" else None
        imp = int(rng.integers(2, 6)) if typ in ("Risk", "Issue") else None
        raid.append(dict(raid_id=f"RAID-{rid:03d}", project_id=pid, type=typ, description=str(rng.choice(TPL[typ])),
                         probability=prob, impact=imp, owner=str(rng.choice(OWN)), raised_date=raised, due_date=due,
                         status="Closed" if closed else "Open", closed_date=closed_on))
raid = pd.DataFrame(raid)
for c in ["probability", "impact"]:
    raid[c] = raid[c].astype("Int64")

# change requests
CR = [("P01", "Add Hindi and Marathi video agent languages", 3.0, 7, "Approved"),
      ("P02", "Move DSA portal upload check after go-live", 0.0, -4, "Approved"),
      ("P02", "Add co-applicant documents to checklist", 1.5, 6, "Rejected"),
      ("P03", "Support 3 more TPAs in phase 1", 8.0, 21, "Approved"),
      ("P03", "Add pre-authorisation status tracker for hospitals", 4.0, 14, "Pending"),
      ("P04", "Add e-mandate for credit cards", 5.0, 18, "Rejected"),
      ("P05", "Include trade-based rules in tuning", 3.5, 15, "Approved"),
      ("P06", "Add NPA view to branch dashboard", 1.0, 5, "Approved"),
      ("P07", "Add bulk upload for hospital documents", 4.5, 20, "Approved"),
      ("P07", "Integrate with state health scheme registry", 9.0, 35, "Pending"),
      ("P08", "Extra mock migration cycle", 12.0, 28, "Approved"),
      ("P08", "Additional vendor team for data cleansing", 15.0, 0, "Approved"),
      ("P08", "Move loan module to phase 2", -40.0, -30, "Pending"),
      ("P08", "Upgrade reporting layer in phase 1", 18.0, 25, "Rejected")]
cr = []
for i, (pid, d, cost, days, dec) in enumerate(CR, 1):
    raised = W0 + dt.timedelta(days=int(rng.integers(20, 150)))
    cr.append(dict(cr_id=f"CR-{i:02d}", project_id=pid, description=d, cost_impact_lakh=cost, schedule_impact_days=days,
                   raised_date=raised, decision=dec,
                   decision_date=(raised + dt.timedelta(days=int(rng.integers(5, 21)))) if dec != "Pending" else None))
cr = pd.DataFrame(cr)

# resources (hours per week; capacity 40)
PEOPLE = [("Ananya Rao", "Project manager"), ("Rohit Kulkarni", "Project manager"), ("Meera Iyer", "Project manager"),
          ("Vikram Shah", "Project manager"), ("Farah Khan", "Project manager"), ("Sanjay Menon", "Project manager"),
          ("Deepa Nair", "Project manager"), ("Kavya Joshi", "Business analyst"), ("Arjun Patil", "Business analyst"),
          ("Nisha Verma", "Business analyst"), ("Imran Sheikh", "Developer"), ("Pooja Desai", "Developer"),
          ("Rahul Gupta", "Developer"), ("Sneha Pillai", "QA analyst"), ("Aditya Bose", "QA analyst"),
          ("Tanvi Mehta", "Data analyst"), ("Karan Malhotra", "Data analyst"), ("Ritu Sharma", "Change manager")]
ASSIGN = {  # person: [(project, base hours)]
 "Ananya Rao": [("P01", 22), ("P06", 14)], "Rohit Kulkarni": [("P02", 32)], "Meera Iyer": [("P03", 36)],
 "Vikram Shah": [("P04", 32)], "Farah Khan": [("P05", 30)], "Sanjay Menon": [("P07", 34)], "Deepa Nair": [("P08", 36)],
 "Kavya Joshi": [("P02", 20), ("P03", 26)], "Arjun Patil": [("P07", 24), ("P08", 20)], "Nisha Verma": [("P01", 18), ("P04", 18)],
 "Imran Sheikh": [("P03", 30), ("P07", 18)], "Pooja Desai": [("P04", 28), ("P06", 8)], "Rahul Gupta": [("P08", 36)],
 "Sneha Pillai": [("P01", 14), ("P02", 12), ("P05", 10)], "Aditya Bose": [("P07", 20), ("P08", 24)],
 "Tanvi Mehta": [("P05", 22), ("P06", 14)], "Karan Malhotra": [("P08", 32)], "Ritu Sharma": [("P01", 12), ("P03", 12), ("P07", 12)]}
active = {p[0]: (p[7], p[7] + p[8] - 1) for p in P}
fin = ws.groupby("project_id").week_ending.max().to_dict()
res = []
for person, role in PEOPLE:
    for k, wk in enumerate(WEEKS, 1):
        for pid, h in ASSIGN[person]:
            s, e = active[pid]
            if k < s or wk > fin[pid]:
                continue
            res.append(dict(person=person, role=role, project_id=pid, week_ending=wk,
                            allocated_hours=int(max(4, round(h * rng.normal(1, .04))))))
res = pd.DataFrame(res)

# sprints for Agile projects (2-week sprints)
sp = []
for (pid, name, unit, dom, meth, spn, pm, sw, pw, bac, ven, spi, cpi, bias) in P:
    if meth != "Agile":
        continue
    nsprints = int(np.ceil((fin[pid] - (W0 + dt.timedelta(weeks=sw - 1))).days / 14)) + 1
    base = {"P01": 30, "P02": 22, "P04": 28, "P06": 18}[pid]
    for s in range(1, nsprints + 1):
        committed = int(round(base * rng.normal(1, .06)))
        completed = int(min(committed, round(committed * spi * rng.normal(1, .07))))
        sp.append(dict(project_id=pid, sprint_no=s, sprint_end=W0 + dt.timedelta(weeks=sw - 1 + 2 * s - 1),
                       committed_points=committed, completed_points=completed))
sp = pd.DataFrame(sp)

for df, f in [(proj, "projects"), (ws, "weekly_status"), (ms, "milestones"), (raid, "raid_log"), (cr, "change_requests"),
              (res, "resource_allocation"), (sp, "sprints")]:
    df.to_csv(f"01_data/{f}.csv", index=False)
print({f: len(d) for d, f in [(proj, "projects"), (ws, "weekly_status"), (ms, "milestones"), (raid, "raid"), (cr, "cr"), (res, "res"), (sp, "sprints")]})
