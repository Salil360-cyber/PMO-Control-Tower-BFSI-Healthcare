# Build guide

Build it yourself and check your numbers against the **expected** values.

## Part A: Excel (start from the 7 CSVs in `01_data`)

1. New workbook → save as `PMO_Control_Tower.xlsx`. For each CSV: Data > From Text/CSV > Load To > Table in a new sheet. Name the sheets Projects, Weekly_Status, Milestones, RAID_Log, Change_Requests, Resource_Data, Sprints.
2. **Weekly_Status: add 4 columns** (I to L):
   - SPI `=IF(D2=0,"",ROUND(E2/D2,2))` · CPI `=IF(F2=0,"",ROUND(E2/F2,2))`
   - EVM RAG `=IF(I2="","",IF(MIN(I2,J2)>=0.95,"Green",IF(MIN(I2,J2)>=0.85,"Amber","Red")))`
   - Is latest `=IF(B2=MAXIFS($B:$B,$A:$A,A2),1,0)` → 1 on each project's last week.
3. **Dashboard sheet:** B2 = status date `02-Jul-2027`. Row 4 headers, A5:A12 = P01 … P08. For each row:
   - Name `=INDEX(Projects!B:B,MATCH(A5,Projects!A:A,0))`, Budget the same with column J
   - PV / EV / AC `=SUMIFS(Weekly_Status!D:D,Weekly_Status!A:A,A5,Weekly_Status!L:L,1)` (E and F for EV and AC)
   - SPI `=ROUND(EV/PV,2)`, CPI `=ROUND(EV/AC,2)`, EVM RAG with the same nested IF
   - Reported RAG `=INDEX(Weekly_Status!H:H,MATCH(1,INDEX((Weekly_Status!A:A=A5)*(Weekly_Status!L:L=1),0),0))`
   - Watermelon `=IF(OR(AND(K5="Green",J5<>"Green"),AND(K5="Amber",J5="Red")),"Yes","No")`
   - Approved CRs `=SUMIFS(Change_Requests!D:D,Change_Requests!B:B,A5,Change_Requests!G:G,"Approved")`, Revised budget = Budget + CRs
   - EAC `=IF(%complete>=1,AC,ROUND(Budget*AC/EV,1))`, VAC = Revised − EAC
   - Open / overdue RAID with `COUNTIFS`; late milestones with `COUNTIFS` on status "Late" + "At risk"; missing updates `COUNTIFS(...,"No")`
   - Home > Conditional Formatting > Highlight Cells > Equal To "Red" / "Amber" / "Green" on the RAG columns.
4. **Resource_Heatmap:** names down column A, week dates across row 3, each cell `=SUMIFS(Resource_Data!E:E,Resource_Data!A:A,$A4,Resource_Data!D:D,C$3)`. Conditional formatting: greater than 40 → red, between 33 and 40 → amber. Last column `=COUNTIF(C4:AB4,">40")`.

**Expected:** P07 SPI 0.83 CPI 0.81 Red (reported Green) · P08 0.76 / 0.85 Red (reported Amber) · portfolio EAC 603.0 vs revised 577 · overdue RAID 21 · watermelons 2 · Aditya Bose and Arjun Patil 25 weeks over 40 h.

## Part B: SQL (pgAdmin)

1. Create database `pmo` → run `03_sql/01_schema.sql`.
2. Import the CSVs (right-click table > Import/Export Data, Header ON) **projects first**, then the rest.
3. Expected counts: 8 · 159 · 38 · 63 · 14 · 620 · 33.
4. Run the 12 queries one by one; compare with `results.md`. Q2 (ROW_NUMBER for the latest week) and Q3 (EAC) are the ones to explain in interviews.

## Part C: Power BI

Follow [`04_powerbi/DAX_measures.md`](04_powerbi/DAX_measures.md). Page 1: 4 cards, scatter (X = SPI, Y = CPI, size = Budget, legend = EVM RAG, details = project_id), clustered bar (Revised Budget vs EAC for running projects), line (month vs SPI and CPI). Page 2: bar of Overdue RAID by project, matrix heatmap (person × week, values = hours, conditional formatting > 40 red), bar of milestone slip, bar of Approved CR by project.

## Part D: practise the story

Read `05_pm_docs/02_portfolio_status_report.md` and `03_steering_committee_pack.md` aloud. In an interview: "I found two watermelon projects by comparing reported RAG with earned value, forecast a Rs 26 lakh overrun, and gave the steering committee three options for the worst project."
