# 03_sql

PostgreSQL 16 (pgAdmin 4 or psql).

| File | What it does |
| --- | --- |
| [`01_schema.sql`](01_schema.sql) | 7 tables with primary and foreign keys |
| [`02_load.sql`](02_load.sql) | Loads the 7 CSVs (projects first) and counts rows |
| [`03_analysis.sql`](03_analysis.sql) | 12 PMO questions: portfolio mix, EVM vs reported RAG (watermelons), EAC and forecast finish, completed-project variance, missing updates, milestone slip, RAID hygiene, top risks, change-request impact, over-allocation, sprint say-do ratio, monthly portfolio SPI / CPI |
| [`results.md`](results.md) | Output of every query |

SQL used: CTEs, `ROW_NUMBER() OVER (PARTITION BY …)` for the latest week, `LEAST`, `CASE WHEN`, `LEFT JOIN`, `COALESCE`, `NULLIF`, `HAVING`, date arithmetic, `DATE_TRUNC`, `TO_CHAR`.
