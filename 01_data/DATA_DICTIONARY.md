# Data dictionary

All data is **synthetic**, made by [`scripts/generate_data.py`](../scripts/generate_data.py). Sahyog Financial Group (a bank and a health insurer), its people and projects are fictional. Money is in **Rs lakh**. Weekly reporting runs from Friday 8 Jan to Friday 2 Jul 2027 (the status date).

| File | Rows | One row per |
| --- | --- | --- |
| projects.csv | 8 | project |
| weekly_status.csv | 159 | project per reporting week |
| milestones.csv | 38 | milestone |
| raid_log.csv | 63 | risk, issue, action or dependency |
| change_requests.csv | 14 | change request |
| resource_allocation.csv | 620 | person per project per week |
| sprints.csv | 33 | sprint of an Agile project |

## projects.csv
project_id · project_name · business_unit · domain (Banking / Healthcare) · method (Agile / Waterfall / Hybrid) · sponsor · project_manager · start_date · planned_end · budget_lakh (BAC, budget at completion) · vendor_led (Yes / No)

## weekly_status.csv
| Column | Meaning |
| --- | --- |
| week_ending | Friday of the reporting week |
| status_submitted | Yes if the project manager sent the weekly update |
| planned_value_lakh | PV: budgeted cost of work planned to date (cumulative) |
| earned_value_lakh | EV: budgeted cost of work actually done to date |
| actual_cost_lakh | AC: money actually spent to date |
| pct_complete | EV / budget |
| reported_rag | Red / Amber / Green the PM reported (blank when no update was sent) |

Rows stop the week a project reaches 100%.

## milestones.csv
milestone_id · project_id · milestone · planned_date · forecast_date · actual_date (if completed) · status (Completed / On track / At risk / Late)

## raid_log.csv
raid_id · project_id · type (Risk / Issue / Action / Dependency) · description · probability (1-5, risks) · impact (1-5, risks and issues) · owner · raised_date · due_date · status (Open / Closed) · closed_date

## change_requests.csv
cr_id · project_id · description · cost_impact_lakh · schedule_impact_days (negative = time saved) · raised_date · decision (Approved / Rejected / Pending) · decision_date

## resource_allocation.csv
person · role · project_id · week_ending · allocated_hours (capacity is 40 hours a week)

## sprints.csv
project_id · sprint_no · sprint_end · committed_points · completed_points (Agile projects P01, P02, P04, P06; 2-week sprints)

## Built-in story (how the generator was set up)
P07 and P08 are planned to under-perform while their PMs report a better RAG; P03 is behind and reported honestly; four people are booked across two troubled projects; PMs of troubled projects miss more weekly updates.
