-- PMO Control Tower: PostgreSQL schema
DROP TABLE IF EXISTS sprints, resource_allocation, change_requests, raid_log, milestones, weekly_status, projects;

CREATE TABLE projects (
    project_id      VARCHAR(4) PRIMARY KEY,
    project_name    VARCHAR(60),
    business_unit   VARCHAR(30),
    domain          VARCHAR(12),       -- Banking / Healthcare
    method          VARCHAR(10),       -- Agile / Waterfall / Hybrid
    sponsor         VARCHAR(40),
    project_manager VARCHAR(30),
    start_date      DATE,
    planned_end     DATE,
    budget_lakh     NUMERIC(8,2),      -- BAC: budget at completion, Rs lakh
    vendor_led      VARCHAR(3)
);

CREATE TABLE weekly_status (
    project_id          VARCHAR(4) REFERENCES projects(project_id),
    week_ending         DATE,
    status_submitted    VARCHAR(3),    -- did the PM send the weekly update?
    planned_value_lakh  NUMERIC(8,2),  -- PV, cumulative
    earned_value_lakh   NUMERIC(8,2),  -- EV, cumulative
    actual_cost_lakh    NUMERIC(8,2),  -- AC, cumulative
    pct_complete        NUMERIC(5,3),
    reported_rag        VARCHAR(5),    -- RAG the PM reported (blank if no update)
    PRIMARY KEY (project_id, week_ending)
);

CREATE TABLE milestones (
    milestone_id  VARCHAR(8) PRIMARY KEY,
    project_id    VARCHAR(4) REFERENCES projects(project_id),
    milestone     VARCHAR(50),
    planned_date  DATE,
    forecast_date DATE,
    actual_date   DATE,
    status        VARCHAR(10)          -- Completed / On track / At risk / Late
);

CREATE TABLE raid_log (
    raid_id     VARCHAR(8) PRIMARY KEY,
    project_id  VARCHAR(4) REFERENCES projects(project_id),
    type        VARCHAR(10),           -- Risk / Assumption / Issue / Action / Dependency
    description VARCHAR(80),
    probability SMALLINT,              -- 1-5, risks only
    impact      SMALLINT,              -- 1-5, risks and issues
    owner       VARCHAR(20),
    raised_date DATE,
    due_date    DATE,
    status      VARCHAR(6),
    closed_date DATE
);

CREATE TABLE change_requests (
    cr_id                VARCHAR(6) PRIMARY KEY,
    project_id           VARCHAR(4) REFERENCES projects(project_id),
    description          VARCHAR(60),
    cost_impact_lakh     NUMERIC(7,2),
    schedule_impact_days SMALLINT,
    raised_date          DATE,
    decision             VARCHAR(8),   -- Approved / Rejected / Pending
    decision_date        DATE
);

CREATE TABLE resource_allocation (
    person          VARCHAR(20),
    role            VARCHAR(20),
    project_id      VARCHAR(4) REFERENCES projects(project_id),
    week_ending     DATE,
    allocated_hours SMALLINT
);

CREATE TABLE sprints (
    project_id       VARCHAR(4) REFERENCES projects(project_id),
    sprint_no        SMALLINT,
    sprint_end       DATE,
    committed_points SMALLINT,
    completed_points SMALLINT
);
