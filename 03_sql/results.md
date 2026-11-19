# SQL results

Run on PostgreSQL 16. Status date: 2 July 2027.

## Q1. What is in the portfolio?

```
   domain   |  method   | projects | budget_lakh 
------------+-----------+----------+-------------
 Banking    | Agile     |        4 |      105.00
 Banking    | Waterfall |        2 |      325.00
 Healthcare | Hybrid    |        1 |       60.00
 Healthcare | Waterfall |        1 |       40.00
(4 rows)
```

## Q2. Latest status of each project: EVM vs what the PM reported ("watermelon" check)

```
 project_id |            project_name             | week_ending | pct_complete | spi  | cpi  | reported_rag | evm_rag | reported_better_than_data 
------------+-------------------------------------+-------------+--------------+------+------+--------------+---------+---------------------------
 P01        | Video KYC Capacity Upgrade          | 2027-04-30  |        1.000 | 1.00 | 1.01 | Green        | Green   | No
 P02        | Loan Fast-Track Lane                | 2027-04-16  |        1.000 | 1.00 | 0.97 | Green        | Green   | No
 P03        | NHCX Cashless Claims Integration    | 2027-07-02  |        0.791 | 0.88 | 0.89 | Amber        | Amber   | No
 P04        | UPI AutoPay for EMI Collections     | 2027-05-07  |        1.000 | 1.00 | 1.01 | Green        | Green   | No
 P05        | AML Alert Threshold Tuning          | 2027-06-04  |        1.000 | 1.00 | 0.95 | Green        | Green   | No
 P06        | Branch MIS Automation               | 2027-04-23  |        1.000 | 1.00 | 0.97 | Green        | Green   | No
 P07        | Hospital Network Empanelment Portal | 2027-07-02  |        0.808 | 0.83 | 0.81 | Green        | Red     | Yes
 P08        | Core Banking Upgrade (Phase 1)      | 2027-07-02  |        0.547 | 0.76 | 0.85 | Amber        | Red     | Yes
(8 rows)
```

## Q3. Forecast for projects still running: cost at completion (EAC = BAC / CPI) vs the budget incl. approved changes,

```
 project_id |            project_name             | budget_lakh | revised_budget_lakh | cpi  | eac_lakh | vac_vs_revised_lakh | planned_end | forecast_end 
------------+-------------------------------------+-------------+---------------------+------+----------+---------------------+-------------+--------------
 P08        | Core Banking Upgrade (Phase 1)      |      300.00 |              327.00 | 0.85 |    354.6 |               -27.6 | 2027-10-08  | 2028-01-03
 P07        | Hospital Network Empanelment Portal |       40.00 |               44.50 | 0.81 |     49.2 |                -4.7 | 2027-07-23  | 2027-08-30
 P03        | NHCX Cashless Claims Integration    |       60.00 |               68.00 | 0.89 |     67.8 |                 0.2 | 2027-08-13  | 2027-09-09
(3 rows)
```

## Q4. Completed projects: finish vs plan and final cost

```
 project_id |          project_name           | planned_end |  finished  | days_late | budget_lakh | final_cost | cost_variance_pct 
------------+---------------------------------+-------------+------------+-----------+-------------+------------+-------------------
 P01        | Video KYC Capacity Upgrade      | 2027-04-23  | 2027-04-30 |         7 |       45.00 |      44.38 |              -1.4
 P02        | Loan Fast-Track Lane            | 2027-04-09  | 2027-04-16 |         7 |       18.00 |      18.57 |               3.2
 P04        | UPI AutoPay for EMI Collections | 2027-05-07  | 2027-05-07 |         0 |       30.00 |      29.81 |              -0.6
 P05        | AML Alert Threshold Tuning      | 2027-05-21  | 2027-06-04 |        14 |       25.00 |      26.20 |               4.8
 P06        | Branch MIS Automation           | 2027-04-16  | 2027-04-23 |         7 |       12.00 |      12.40 |               3.3
(5 rows)
```

## Q5. Data quality: weekly updates the PMs did not send

```
 project_id | project_manager | weeks_reported_on | updates_missing | submission_rate_pct 
------------+-----------------+-------------------+-----------------+---------------------
 P03        | Meera Iyer      |                24 |               3 |                87.5
 P07        | Sanjay Menon    |                25 |               3 |                88.0
 P08        | Deepa Nair      |                26 |               3 |                88.5
 P01        | Ananya Rao      |                17 |               1 |                94.1
 P02        | Rohit Kulkarni  |                15 |               0 |               100.0
 P04        | Vikram Shah     |                17 |               0 |               100.0
 P05        | Farah Khan      |                22 |               0 |               100.0
 P06        | Ananya Rao      |                13 |               0 |               100.0
(8 rows)
```

## Q6. Milestones: hit, slipping and late

```
 project_id | milestones | completed | completed_on_time | late_or_at_risk | avg_slip_days 
------------+------------+-----------+-------------------+-----------------+---------------
 P07        |          5 |         3 |                 0 |               2 |          35.4
 P08        |          6 |         3 |                 0 |               3 |          33.2
 P03        |          5 |         3 |                 0 |               2 |          22.4
 P02        |          5 |         5 |                 1 |               0 |           4.6
 P01        |          5 |         5 |                 1 |               0 |           3.6
 P05        |          4 |         4 |                 0 |               0 |           2.5
 P06        |          3 |         3 |                 1 |               0 |           0.7
 P04        |          5 |         5 |                 4 |               0 |          -2.0
(8 rows)
```

## Q7. RAID hygiene: open and overdue items by project

```
 project_id | items | open_items | overdue | avg_days_overdue 
------------+-------+------------+---------+------------------
 P08        |    16 |         10 |      10 |               51
 P03        |    12 |          7 |       6 |               71
 P07        |    11 |          6 |       5 |               61
 P01        |     5 |          0 |       0 |                 
 P02        |     6 |          0 |       0 |                 
 P04        |     5 |          0 |       0 |                 
 P05        |     5 |          0 |       0 |                 
 P06        |     3 |          0 |       0 |                 
(8 rows)
```

## Q8. Top open risks by score (probability x impact)

```
 raid_id  | project_id |                         description                         | probability | impact | score |      owner       |  due_date  
----------+------------+-------------------------------------------------------------+-------------+--------+-------+------------------+------------
 RAID-048 | P08        | Integration with legacy system may take longer than planned |           4 |      5 |    20 | Business analyst | 2027-03-03
 RAID-041 | P07        | Budget may run out before go-live                           |           5 |      3 |    15 | Project manager  | 2027-04-14
 RAID-057 | P08        | Regulatory change may alter scope                           |           3 |      4 |    12 | Project manager  | 2027-06-01
 RAID-056 | P08        | Vendor resource shortage may delay build                    |           2 |      4 |     8 | IT lead          | 2027-06-18
 RAID-054 | P08        | Vendor resource shortage may delay build                    |           2 |      3 |     6 | Business SME     | 2027-04-20
 RAID-042 | P07        | Budget may run out before go-live                           |           2 |      2 |     4 | Project manager  | 2027-05-27
(6 rows)
```

## Q9. Change requests: what approved changes added

```
 project_id |            project_name             | budget_lakh | change_requests | approved_cost_lakh | approved_days | pending | budget_increase_pct 
------------+-------------------------------------+-------------+-----------------+--------------------+---------------+---------+---------------------
 P08        | Core Banking Upgrade (Phase 1)      |      300.00 |               4 |              27.00 |            28 |       1 |                 9.0
 P03        | NHCX Cashless Claims Integration    |       60.00 |               2 |               8.00 |            21 |       1 |                13.3
 P07        | Hospital Network Empanelment Portal |       40.00 |               2 |               4.50 |            20 |       1 |                11.3
 P05        | AML Alert Threshold Tuning          |       25.00 |               1 |               3.50 |            15 |       0 |                14.0
 P01        | Video KYC Capacity Upgrade          |       45.00 |               1 |               3.00 |             7 |       0 |                 6.7
 P06        | Branch MIS Automation               |       12.00 |               1 |               1.00 |             5 |       0 |                 8.3
 P04        | UPI AutoPay for EMI Collections     |       30.00 |               1 |                  0 |             0 |       0 |                 0.0
 P02        | Loan Fast-Track Lane                |       18.00 |               2 |               0.00 |            -4 |       0 |                 0.0
(8 rows)
```

## Q10. Who is over-allocated? (capacity 40 hours a week)

```
    person    |       role       | weeks_over_40h | peak_hours | max_projects_in_a_week 
--------------+------------------+----------------+------------+------------------------
 Aditya Bose  | QA analyst       |             25 |         47 |                      2
 Arjun Patil  | Business analyst |             25 |         47 |                      2
 Imran Sheikh | Developer        |             24 |         51 |                      2
 Kavya Joshi  | Business analyst |             13 |         48 |                      2
(4 rows)
```

## Q11. Agile delivery: say-do ratio and velocity

```
 project_id | sprints | avg_velocity | say_do_pct 
------------+---------+--------------+------------
 P01        |       9 |         29.1 |       96.7
 P02        |       8 |         19.8 |       89.3
 P04        |       9 |         27.6 |       97.6
 P06        |       7 |         16.9 |       95.2
(4 rows)
```

## Q12. Portfolio trend: month-end SPI and CPI of all running work

```
  month   | portfolio_spi | portfolio_cpi | projects_reporting 
----------+---------------+---------------+--------------------
 Jan 2027 |          0.82 |          0.95 |                  8
 Feb 2027 |          0.84 |          0.95 |                  8
 Mar 2027 |          0.84 |          0.95 |                  8
 Apr 2027 |          0.82 |          0.92 |                  6
 May 2027 |          0.78 |          0.87 |                  4
 Jun 2027 |          0.76 |          0.85 |                  3
 Jul 2027 |          0.79 |          0.85 |                  3
(7 rows)
```
