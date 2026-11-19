"""PMO workbook: every KPI is a formula on the data sheets."""
import pandas as pd, datetime as dt
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.formatting.rule import FormulaRule, CellIsRule
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter as L

F = "Arial"
H = Font(name=F, bold=True, color="FFFFFF"); HF = PatternFill("solid", fgColor="1F3864")
N = Font(name=F); B = Font(name=F, bold=True); T = Font(name=F, bold=True, size=14); I = Font(name=F, italic=True, color="555555")
RED = PatternFill("solid", fgColor="F4CCCC"); AMB = PatternFill("solid", fgColor="FCE5CD"); GRN = PatternFill("solid", fgColor="D9EAD3")
AS_OF = dt.date(2027, 7, 2)

def hdr(ws, r, vals, c0=1):
    for i, v in enumerate(vals):
        c = ws.cell(r, c0 + i, v); c.font = H; c.fill = HF; c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

def rd(name, dates=()):
    return pd.read_csv(f"01_data/{name}.csv", parse_dates=list(dates))

def put_table(ws, df, tname, dates=(), widths=None):
    hdr(ws, 1, list(df.columns))
    for r in df.itertuples(index=False):
        ws.append([None if pd.isna(v) else (v.date() if isinstance(v, pd.Timestamp) else v) for v in r])
    n = len(df) + 1
    for c in dates:
        col = list(df.columns).index(c) + 1
        for row in ws.iter_rows(min_row=2, max_row=n, min_col=col, max_col=col):
            row[0].number_format = "dd-mmm-yy"
    ws.freeze_panes = "A2"
    for i, w in enumerate(widths or [], 1):
        ws.column_dimensions[L(i)].width = w
    return n

wb = Workbook()
ab = wb.active; ab.title = "About"
for i, (t, f) in enumerate([
    ("PMO Control Tower: Portfolio Workbook", T),
    ("Sahyog Financial Group (fictional: a bank + a health insurer) · 8 projects · weekly status 8 Jan to 2 Jul 2027 · synthetic data", N), ("", N),
    ("Sheets", B),
    ("Dashboard: one row per project at the status date: progress, SPI, CPI, EVM RAG vs reported RAG, forecast cost, RAID, CRs, milestones", N),
    ("Weekly_Status: PM updates + formula columns SPI, CPI, EVM RAG, latest-week flag", N),
    ("Milestones: slip days (forecast - planned) by formula", N),
    ("RAID_Log: score (probability x impact) and overdue flag by formula", N),
    ("Change_Requests: decisions and impact", N),
    ("Resource_Heatmap: hours per person per week (SUMIFS); red when over 40 hours", N),
    ("Projects, Resource_Data, Sprints: source data", N), ("", N),
    ("EVM terms: PV = planned value, EV = earned value (budget of work done), AC = actual cost. SPI = EV / PV, CPI = EV / AC, EAC = BAC / CPI.", N),
    ("EVM RAG rule: the lower of SPI and CPI; 0.95+ Green, 0.85 to 0.95 Amber, below 0.85 Red.", N),
    ("Watermelon = a project the PM reports better than its EVM numbers (Green outside, red inside).", N),
    ("Status date: 2 Jul 2027 (cell Dashboard!B2).", I)], 1):
    ab.cell(i, 1, t).font = f
ab.column_dimensions["A"].width = 125

# source sheets
pj = rd("projects", ["start_date", "planned_end"]); wsd = rd("weekly_status", ["week_ending"])
ms = rd("milestones", ["planned_date", "forecast_date", "actual_date"]); rl = rd("raid_log", ["raised_date", "due_date", "closed_date"])
cr = rd("change_requests", ["raised_date", "decision_date"]); ra = rd("resource_allocation", ["week_ending"]); sp = rd("sprints", ["sprint_end"])

s = wb.create_sheet("Projects"); nP = put_table(s, pj, "projects", ["start_date", "planned_end"], [8, 36, 16, 11, 10, 24, 16, 11, 11, 10, 8])
s = wb.create_sheet("Weekly_Status")
nW = put_table(s, wsd, "weekly", ["week_ending"], [8, 11, 10, 10, 10, 10, 9, 10])
hdr(s, 1, ["SPI", "CPI", "EVM RAG", "Is latest week"], 9)
for r in range(2, nW + 1):
    s.cell(r, 9, f"=IF(D{r}=0,\"\",ROUND(E{r}/D{r},2))").number_format = "0.00"
    s.cell(r, 10, f"=IF(F{r}=0,\"\",ROUND(E{r}/F{r},2))").number_format = "0.00"
    s.cell(r, 11, f'=IF(I{r}="","",IF(MIN(I{r},J{r})>=0.95,"Green",IF(MIN(I{r},J{r})>=0.85,"Amber","Red")))')
    s.cell(r, 12, f"=IF(B{r}=_xlfn.MAXIFS($B$2:$B${nW},$A$2:$A${nW},A{r}),1,0)")
for col, w in zip("IJKL", [7, 7, 10, 9]):
    s.column_dimensions[col].width = w
W = lambda c: f"Weekly_Status!${c}$2:${c}${nW}"

s = wb.create_sheet("Milestones"); nM = put_table(s, ms, "ms", ["planned_date", "forecast_date", "actual_date"], [9, 6, 32, 11, 11, 11, 10])
hdr(s, 1, ["Slip days"], 8)
for r in range(2, nM + 1):
    s.cell(r, 8, f"=E{r}-D{r}")
M = lambda c: f"Milestones!${c}$2:${c}${nM}"

s = wb.create_sheet("RAID_Log"); nR = put_table(s, rl, "raid", ["raised_date", "due_date", "closed_date"], [10, 6, 11, 50, 7, 7, 16, 11, 11, 8, 11])
hdr(s, 1, ["Score", "Overdue"], 12)
for r in range(2, nR + 1):
    s.cell(r, 12, f'=IF(E{r}="","",E{r}*F{r})')
    s.cell(r, 13, f'=IF(AND(J{r}="Open",I{r}<Dashboard!$B$2),"Yes","No")')
R = lambda c: f"RAID_Log!${c}$2:${c}${nR}"

s = wb.create_sheet("Change_Requests"); nC = put_table(s, cr, "cr", ["raised_date", "decision_date"], [7, 6, 44, 10, 10, 11, 10, 11])
C = lambda c: f"Change_Requests!${c}$2:${c}${nC}"

s = wb.create_sheet("Resource_Data"); nRA = put_table(s, ra, "res", ["week_ending"], [16, 18, 8, 11, 10])
RA = lambda c: f"Resource_Data!${c}$2:${c}${nRA}"
s = wb.create_sheet("Sprints"); put_table(s, sp, "sp", ["sprint_end"], [8, 8, 11, 10, 10])

# Dashboard
d = wb.create_sheet("Dashboard", 1)
d["A1"] = "Portfolio dashboard"; d["A1"].font = T
d["A2"] = "Status date"; d["A2"].font = B
d["B2"] = AS_OF; d["B2"].number_format = "dd-mmm-yyyy"; d["B2"].font = Font(name=F, color="0000FF")
heads = ["Project", "Name", "Budget (Rs lakh)", "% complete", "PV", "EV", "AC", "SPI", "CPI", "EVM RAG", "Reported RAG",
         "Watermelon?", "Approved CRs (Rs lakh)", "Revised budget", "EAC = BAC/CPI", "VAC vs revised", "Open RAID", "Overdue RAID",
         "Milestones late / at risk", "Missing updates"]
hdr(d, 4, heads)
P_ = lambda c: f"Projects!${c}$2:${c}${nP}"
for k in range(8):
    r = 5 + k; pid = f"P0{k+1}"
    d.cell(r, 1, pid)
    d.cell(r, 2, f"=INDEX({P_('B')},MATCH(A{r},{P_('A')},0))")
    d.cell(r, 3, f"=INDEX({P_('J')},MATCH(A{r},{P_('A')},0))")
    for col, src in ((4, "G"), (5, "D"), (6, "E"), (7, "F")):
        d.cell(r, col, f"=SUMIFS({W(src)},{W('A')},$A{r},{W('L')},1)")
    d.cell(r, 4).number_format = "0%"
    for col in (5, 6, 7):
        d.cell(r, col).number_format = "0.0"
    d.cell(r, 8, f"=ROUND(F{r}/E{r},2)").number_format = "0.00"
    d.cell(r, 9, f"=ROUND(F{r}/G{r},2)").number_format = "0.00"
    d.cell(r, 10, f'=IF(MIN(H{r},I{r})>=0.95,"Green",IF(MIN(H{r},I{r})>=0.85,"Amber","Red"))')
    d.cell(r, 11, f"=INDEX({W('H')},MATCH(1,INDEX(({W('A')}=A{r})*({W('L')}=1),0),0))")
    d.cell(r, 12, f'=IF(OR(AND(K{r}="Green",J{r}<>"Green"),AND(K{r}="Amber",J{r}="Red")),"Yes","No")')
    d.cell(r, 13, f'=SUMIFS({C("D")},{C("B")},A{r},{C("G")},"Approved")').number_format = "0.0"
    d.cell(r, 14, f"=C{r}+M{r}").number_format = "0.0"
    d.cell(r, 15, f'=IF(D{r}>=1,G{r},ROUND(C{r}*G{r}/F{r},1))').number_format = "0.0"
    d.cell(r, 16, f"=ROUND(N{r}-O{r},1)").number_format = "0.0;[Red]-0.0"
    d.cell(r, 17, f'=COUNTIFS({R("B")},A{r},{R("J")},"Open")')
    d.cell(r, 18, f'=COUNTIFS({R("B")},A{r},{R("M")},"Yes")')
    d.cell(r, 19, f'=COUNTIFS({M("B")},A{r},{M("G")},"Late")+COUNTIFS({M("B")},A{r},{M("G")},"At risk")')
    d.cell(r, 20, f'=COUNTIFS({W("A")},A{r},{W("C")},"No")')
    for c in range(1, 21):
        if d.cell(r, c).font != B:
            d.cell(r, c).font = N
tr = 13
d.cell(tr, 1, "Portfolio").font = B
for col in (3, 5, 6, 7, 13, 14, 15, 16, 17, 18, 19, 20):
    c = d.cell(tr, col, f"=SUM({L(col)}5:{L(col)}12)"); c.font = B; c.number_format = d.cell(5, col).number_format
d.cell(tr, 12, '=COUNTIF(L5:L12,"Yes")').font = B
d.cell(tr + 1, 1, "EAC for finished projects = their final actual cost. Watermelon count in L13.").font = I
rag_rng = "J5:K12"
d.conditional_formatting.add(rag_rng, CellIsRule(operator="equal", formula=['"Red"'], fill=RED))
d.conditional_formatting.add(rag_rng, CellIsRule(operator="equal", formula=['"Amber"'], fill=AMB))
d.conditional_formatting.add(rag_rng, CellIsRule(operator="equal", formula=['"Green"'], fill=GRN))
d.conditional_formatting.add("L5:L12", CellIsRule(operator="equal", formula=['"Yes"'], fill=RED))
widths = [8, 34, 9, 9, 8, 8, 8, 7, 7, 9, 9, 10, 10, 9, 9, 9, 7, 8, 10, 9]
for i, w in enumerate(widths, 1):
    d.column_dimensions[L(i)].width = w
d.row_dimensions[4].height = 45
d.freeze_panes = "C5"

# Resource heatmap
hm = wb.create_sheet("Resource_Heatmap", 2)
hm["A1"] = "Hours per person per week (capacity 40)"; hm["A1"].font = T
people = list(dict.fromkeys(ra.person))
weeks = sorted(ra.week_ending.dt.date.unique())
hdr(hm, 3, ["Person", "Role"])
for j, wk in enumerate(weeks):
    c = hm.cell(3, 3 + j, wk); c.number_format = "dd-mmm"; c.font = H; c.fill = HF
    c.alignment = Alignment(text_rotation=90, horizontal="center")
    hm.column_dimensions[L(3 + j)].width = 4.5
hdr(hm, 3, ["Weeks over 40h"], 3 + len(weeks))
for i, pname in enumerate(people):
    r = 4 + i
    hm.cell(r, 1, pname).font = N
    hm.cell(r, 2, f"=INDEX({RA('B')},MATCH(A{r},{RA('A')},0))").font = N
    for j in range(len(weeks)):
        col = L(3 + j)
        c = hm.cell(r, 3 + j, f"=SUMIFS({RA('E')},{RA('A')},$A{r},{RA('D')},{col}$3)"); c.font = N
        c.number_format = "0;-0;"
    last = L(2 + len(weeks))
    hm.cell(r, 3 + len(weeks), f'=COUNTIF(C{r}:{last}{r},">40")').font = B
rng = f"C4:{L(2 + len(weeks))}{3 + len(people)}"
hm.conditional_formatting.add(rng, CellIsRule(operator="greaterThan", formula=["40"], fill=RED))
hm.conditional_formatting.add(rng, CellIsRule(operator="between", formula=["33", "40"], fill=AMB))
hm.column_dimensions["A"].width = 16; hm.column_dimensions["B"].width = 16
hm.row_dimensions[3].height = 45
hm.cell(5 + len(people), 1, "Red = over 40 hours; amber = 33 to 40 hours (near capacity).").font = I
hm.freeze_panes = "C4"
wb.save("02_excel/PMO_Control_Tower.xlsx"); print("saved")
