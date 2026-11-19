-- PMO Control Tower: portfolio questions answered in SQL
-- Status date: Friday 2 July 2027 (last reporting week).
-- EVM RAG rule used by the PMO: the lower of SPI and CPI; 0.95+ Green, 0.85-0.95 Amber, below 0.85 Red.

-- Q1. What is in the portfolio?
SELECT domain, method, COUNT(*) AS projects, SUM(budget_lakh) AS budget_lakh
FROM projects
GROUP BY domain, method
ORDER BY domain, method;

-- Q2. Latest status of each project: EVM vs what the PM reported ("watermelon" check)
WITH latest AS (
    SELECT w.*, ROW_NUMBER() OVER (PARTITION BY project_id ORDER BY week_ending DESC) AS rn
    FROM weekly_status w
), evm AS (
    SELECT p.project_id, p.project_name, l.week_ending, l.pct_complete,
           ROUND(l.earned_value_lakh / NULLIF(l.planned_value_lakh, 0), 2) AS spi,
           ROUND(l.earned_value_lakh / NULLIF(l.actual_cost_lakh, 0), 2) AS cpi,
           l.reported_rag
    FROM latest l JOIN projects p ON p.project_id = l.project_id
    WHERE l.rn = 1
)
SELECT *,
       CASE WHEN LEAST(spi, cpi) >= 0.95 THEN 'Green'
            WHEN LEAST(spi, cpi) >= 0.85 THEN 'Amber' ELSE 'Red' END AS evm_rag,
       CASE WHEN reported_rag = 'Green' AND LEAST(spi, cpi) < 0.95 THEN 'Yes'
            WHEN reported_rag = 'Amber' AND LEAST(spi, cpi) < 0.85 THEN 'Yes' ELSE 'No' END AS reported_better_than_data
FROM evm
ORDER BY project_id;

-- Q3. Forecast for projects still running: cost at completion (EAC = BAC / CPI) vs the budget incl. approved changes,
--     and finish date (planned duration / SPI). VAC = revised budget - EAC; negative = overrun.
WITH latest AS (
    SELECT w.*, ROW_NUMBER() OVER (PARTITION BY project_id ORDER BY week_ending DESC) AS rn
    FROM weekly_status w
), approved AS (
    SELECT project_id, SUM(cost_impact_lakh) AS approved_cr_lakh
    FROM change_requests
    WHERE decision = 'Approved'
    GROUP BY project_id
)
SELECT p.project_id, p.project_name, p.budget_lakh,
       p.budget_lakh + COALESCE(a.approved_cr_lakh, 0) AS revised_budget_lakh,
       ROUND(l.earned_value_lakh / l.actual_cost_lakh, 2) AS cpi,
       ROUND(p.budget_lakh / (l.earned_value_lakh / l.actual_cost_lakh), 1) AS eac_lakh,
       ROUND(p.budget_lakh + COALESCE(a.approved_cr_lakh, 0) - p.budget_lakh / (l.earned_value_lakh / l.actual_cost_lakh), 1) AS vac_vs_revised_lakh,
       p.planned_end,
       p.start_date + ROUND((p.planned_end - p.start_date) / (l.earned_value_lakh / l.planned_value_lakh))::int AS forecast_end
FROM latest l
JOIN projects p ON p.project_id = l.project_id
LEFT JOIN approved a ON a.project_id = p.project_id
WHERE l.rn = 1 AND l.pct_complete < 1
ORDER BY vac_vs_revised_lakh;

-- Q4. Completed projects: finish vs plan and final cost
WITH fin AS (
    SELECT project_id, MAX(week_ending) AS finished, MAX(actual_cost_lakh) AS final_cost
    FROM weekly_status
    GROUP BY project_id
    HAVING MAX(pct_complete) >= 1
)
SELECT p.project_id, p.project_name, p.planned_end, f.finished,
       f.finished - p.planned_end AS days_late,
       p.budget_lakh, f.final_cost,
       ROUND(100.0 * (f.final_cost - p.budget_lakh) / p.budget_lakh, 1) AS cost_variance_pct
FROM fin f JOIN projects p ON p.project_id = f.project_id
ORDER BY p.project_id;

-- Q5. Data quality: weekly updates the PMs did not send
SELECT p.project_id, p.project_manager,
       COUNT(*) AS weeks_reported_on,
       SUM(CASE WHEN w.status_submitted = 'No' THEN 1 ELSE 0 END) AS updates_missing,
       ROUND(100.0 * SUM(CASE WHEN w.status_submitted = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS submission_rate_pct
FROM weekly_status w JOIN projects p ON p.project_id = w.project_id
GROUP BY p.project_id, p.project_manager
ORDER BY updates_missing DESC, p.project_id;

-- Q6. Milestones: hit, slipping and late
SELECT project_id,
       COUNT(*) AS milestones,
       SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) AS completed,
       SUM(CASE WHEN status = 'Completed' AND actual_date <= planned_date THEN 1 ELSE 0 END) AS completed_on_time,
       SUM(CASE WHEN status IN ('Late', 'At risk') THEN 1 ELSE 0 END) AS late_or_at_risk,
       ROUND(AVG(forecast_date - planned_date), 1) AS avg_slip_days
FROM milestones
GROUP BY project_id
ORDER BY avg_slip_days DESC;

-- Q7. RAID hygiene: open and overdue items by project
SELECT project_id,
       COUNT(*) AS items,
       SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) AS open_items,
       SUM(CASE WHEN status = 'Open' AND due_date < DATE '2027-07-02' THEN 1 ELSE 0 END) AS overdue,
       ROUND(AVG(CASE WHEN status = 'Open' AND due_date < DATE '2027-07-02'
                      THEN DATE '2027-07-02' - due_date END), 0) AS avg_days_overdue
FROM raid_log
GROUP BY project_id
ORDER BY overdue DESC, project_id;

-- Q8. Top open risks by score (probability x impact)
SELECT raid_id, project_id, description, probability, impact,
       probability * impact AS score, owner, due_date
FROM raid_log
WHERE type = 'Risk' AND status = 'Open'
ORDER BY score DESC, due_date
LIMIT 8;

-- Q9. Change requests: what approved changes added
SELECT p.project_id, p.project_name, p.budget_lakh,
       COUNT(c.cr_id) AS change_requests,
       SUM(CASE WHEN c.decision = 'Approved' THEN c.cost_impact_lakh ELSE 0 END) AS approved_cost_lakh,
       SUM(CASE WHEN c.decision = 'Approved' THEN c.schedule_impact_days ELSE 0 END) AS approved_days,
       SUM(CASE WHEN c.decision = 'Pending' THEN 1 ELSE 0 END) AS pending,
       ROUND(100.0 * SUM(CASE WHEN c.decision = 'Approved' THEN c.cost_impact_lakh ELSE 0 END) / p.budget_lakh, 1) AS budget_increase_pct
FROM projects p LEFT JOIN change_requests c ON c.project_id = p.project_id
GROUP BY p.project_id, p.project_name, p.budget_lakh
ORDER BY approved_cost_lakh DESC;

-- Q10. Who is over-allocated? (capacity 40 hours a week)
WITH weekly AS (
    SELECT person, role, week_ending, SUM(allocated_hours) AS hours, COUNT(DISTINCT project_id) AS projects
    FROM resource_allocation
    GROUP BY person, role, week_ending
)
SELECT person, role,
       SUM(CASE WHEN hours > 40 THEN 1 ELSE 0 END) AS weeks_over_40h,
       MAX(hours) AS peak_hours,
       MAX(projects) AS max_projects_in_a_week
FROM weekly
GROUP BY person, role
HAVING SUM(CASE WHEN hours > 40 THEN 1 ELSE 0 END) > 0
ORDER BY weeks_over_40h DESC;

-- Q11. Agile delivery: say-do ratio and velocity
SELECT project_id,
       COUNT(*) AS sprints,
       ROUND(AVG(completed_points), 1) AS avg_velocity,
       ROUND(100.0 * SUM(completed_points) / SUM(committed_points), 1) AS say_do_pct
FROM sprints
GROUP BY project_id
ORDER BY project_id;

-- Q12. Portfolio trend: month-end SPI and CPI of all running work
WITH month_end AS (
    SELECT DATE_TRUNC('month', week_ending) AS month, MAX(week_ending) AS last_week
    FROM weekly_status
    GROUP BY 1
)
SELECT TO_CHAR(m.month, 'Mon YYYY') AS month,
       ROUND(SUM(w.earned_value_lakh) / SUM(w.planned_value_lakh), 2) AS portfolio_spi,
       ROUND(SUM(w.earned_value_lakh) / SUM(w.actual_cost_lakh), 2) AS portfolio_cpi,
       COUNT(*) AS projects_reporting
FROM month_end m JOIN weekly_status w ON w.week_ending = m.last_week
GROUP BY m.month
ORDER BY m.month;
