# 02_excel

`PMO_Control_Tower.xlsx`: every KPI is a formula on the data sheets, so changing the data updates the dashboard.

| Sheet | What it shows | Excel used |
| --- | --- | --- |
| Dashboard | One row per project at the status date: % complete, PV, EV, AC, SPI, CPI, EVM RAG vs reported RAG, watermelon flag, approved CRs, revised budget, EAC, VAC, open and overdue RAID, late milestones, missing updates | `SUMIFS`, `INDEX`/`MATCH` (incl. a two-condition match), `COUNTIFS`, nested `IF`, conditional formatting |
| Resource_Heatmap | Hours per person per week; red over 40 h, amber 33-40 h | `SUMIFS`, `COUNTIF`, conditional formatting |
| Weekly_Status | PM updates + SPI, CPI, EVM RAG and a latest-week flag | `MAXIFS`, `ROUND`, `IF` |
| Milestones | Slip days | date arithmetic |
| RAID_Log | Score and overdue flag | `IF`, `AND` |
| Change_Requests, Projects, Resource_Data, Sprints | Source data | |

Key results (match `03_sql/results.md`): **2 watermelon projects** (P07 reported Green, P08 reported Amber; both Red on EVM), portfolio forecast **Rs 603.0 lakh vs Rs 577 lakh revised budget**, **21 overdue RAID items**, **4 people over 40 h** in 13-25 weeks each.
