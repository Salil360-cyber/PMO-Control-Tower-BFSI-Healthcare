-- Run in psql from the repo root. In pgAdmin: right-click each table > Import/Export Data (Header ON, NULL strings blank).
-- Load projects first: the other tables reference it.
\copy projects FROM '01_data/projects.csv' WITH (FORMAT csv, HEADER true, NULL '')
\copy weekly_status FROM '01_data/weekly_status.csv' WITH (FORMAT csv, HEADER true, NULL '')
\copy milestones FROM '01_data/milestones.csv' WITH (FORMAT csv, HEADER true, NULL '')
\copy raid_log FROM '01_data/raid_log.csv' WITH (FORMAT csv, HEADER true, NULL '')
\copy change_requests FROM '01_data/change_requests.csv' WITH (FORMAT csv, HEADER true, NULL '')
\copy resource_allocation FROM '01_data/resource_allocation.csv' WITH (FORMAT csv, HEADER true, NULL '')
\copy sprints FROM '01_data/sprints.csv' WITH (FORMAT csv, HEADER true, NULL '')

SELECT 'projects' AS t, COUNT(*) FROM projects UNION ALL
SELECT 'weekly_status', COUNT(*) FROM weekly_status UNION ALL
SELECT 'milestones', COUNT(*) FROM milestones UNION ALL
SELECT 'raid_log', COUNT(*) FROM raid_log UNION ALL
SELECT 'change_requests', COUNT(*) FROM change_requests UNION ALL
SELECT 'resource_allocation', COUNT(*) FROM resource_allocation UNION ALL
SELECT 'sprints', COUNT(*) FROM sprints;
