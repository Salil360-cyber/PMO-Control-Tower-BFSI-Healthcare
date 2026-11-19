# Power BI build: model and DAX

## Load and model
Get Data > Text/CSV for all 7 files (names = file names). Dates as Date, money as Decimal.
Relationships (Model view): `projects[project_id]` 1 → * every other table's `project_id`. Add a `Date` table if you want month slicers.

## Calculated column on weekly_status
```
Is Latest = 
VAR maxWeek = CALCULATE(MAX(weekly_status[week_ending]), ALLEXCEPT(weekly_status, weekly_status[project_id]))
RETURN IF(weekly_status[week_ending] = maxWeek, 1, 0)
```

## Measures
```
PV = CALCULATE(SUM(weekly_status[planned_value_lakh]), weekly_status[Is Latest] = 1)
EV = CALCULATE(SUM(weekly_status[earned_value_lakh]), weekly_status[Is Latest] = 1)
AC = CALCULATE(SUM(weekly_status[actual_cost_lakh]), weekly_status[Is Latest] = 1)
SPI = DIVIDE([EV], [PV])
CPI = DIVIDE([EV], [AC])
Budget = SUM(projects[budget_lakh])
Approved CR = CALCULATE(SUM(change_requests[cost_impact_lakh]), change_requests[decision] = "Approved")
Revised Budget = [Budget] + [Approved CR]
EAC = SUMX(projects, VAR e = [EV] VAR a = [AC] VAR done = e >= projects[budget_lakh] RETURN IF(done, a, DIVIDE(projects[budget_lakh] * a, e)))
VAC = [Revised Budget] - [EAC]
EVM RAG = VAR m = MIN([SPI], [CPI]) RETURN IF(m >= 0.95, "Green", IF(m >= 0.85, "Amber", "Red"))
Reported RAG = CALCULATE(MAX(weekly_status[reported_rag]), weekly_status[Is Latest] = 1)
Watermelon = IF(([Reported RAG] = "Green" && [EVM RAG] <> "Green") || ([Reported RAG] = "Amber" && [EVM RAG] = "Red"), 1, 0)
Watermelons = SUMX(VALUES(projects[project_id]), [Watermelon])
Overdue RAID = CALCULATE(COUNTROWS(raid_log), raid_log[status] = "Open", raid_log[due_date] < DATE(2027, 7, 2))
Missing Updates = CALCULATE(COUNTROWS(weekly_status), weekly_status[status_submitted] = "No")
Say-Do % = DIVIDE(SUM(sprints[completed_points]), SUM(sprints[committed_points]))
```

## Expected values
| Measure | Value |
| --- | --- |
| Budget | 530 |
| Revised Budget | 577 |
| EAC (portfolio) | 603.0 |
| Watermelons | 2 (P07, P08) |
| Overdue RAID | 21 |
| Missing Updates | 10 |
| P08 SPI / CPI | 0.76 / 0.85 |
