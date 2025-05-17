-- CREATE DATABASE finance_tracker;

USE finance_tracker;

-- CREATE TABLE income (
--     income_id INTEGER PRIMARY KEY AUTO_INCREMENT,
--     date DATE,
--     source TEXT,
--     amount FLOAT,
--     income_type TEXT
-- );

-- If table records already exists, to start fresh, truncate table and set suto increment to 1
-- TRUNCATE TABLE income;
-- ALTER TABLE income AUTO_INCREMENT = 1;

-- CREATE TABLE expenses (
--     expense_id INTEGER PRIMARY KEY AUTO_INCREMENT,
--     date DATE,
--     category TEXT,
--     description TEXT,
--     amount FLOAT
-- );

-- If table records already exists, to start fresh, truncate table and set suto increment to 1
-- TRUNCATE TABLE expenses;
-- ALTER TABLE expenses AUTO_INCREMENT = 1; 

-- CREATE TABLE savings (
--     saving_id INTEGER PRIMARY KEY AUTO_INCREMENT,
--     date DATE,
--     goal_name TEXT,
--     goal_amount FLOAT,
--     saved_amount FLOAT
-- );


-- DELETE FROM savings;
-- DELETE FROM expenses;
-- DELETE FROM income;

-- DROP TABLE income;
-- DROP TABLE savings;
-- DROP TABLE expenses;

SELECT * FROM savings;
SELECT * FROM expenses;
SELECT * FROM income;

-- If table records already exists, to start fresh, truncate table and set suto increment to 1
-- TRUNCATE TABLE savings;
-- ALTER TABLE savings AUTO_INCREMENT = 1;

-- To check if data exists in April month
-- SELECT category, amount, date FROM expenses WHERE DATE_FORMAT(date, '%Y-%m') = '2025-03';

-- Analysis

-- Monthly Income vs Expense Summary
SELECT DATE_FORMAT(date, '%Y-%m') AS Month, SUM(amount) FROM income GROUP BY Month;
SELECT DATE_FORMAT(date, '%Y-%m') AS Month, SUM(amount) FROM expenses GROUP BY Month;


-- Income Type Breakdown (Passive vs Active)
SELECT income_type, SUM(amount) AS total_income
FROM income
GROUP BY income_type;


-- Average Monthly Spending by Category
SELECT category, ROUND(AVG(monthly_amount), 2) AS avg_monthly_spending
FROM (
    SELECT category, DATE_FORMAT(date, '%Y-%m') AS month, SUM(amount) AS monthly_amount
    FROM expenses
    GROUP BY category, month
) AS sub
GROUP BY category;


-- Top N Expenses by Category or Overall
SELECT category, description, amount, date 
FROM expenses 
ORDER BY amount DESC 
LIMIT 5;


-- Monthly Income vs Expenses with Net Savings
SELECT 
    m.Month,
    IFNULL(i.total_income, 0) AS total_income,
    IFNULL(e.total_expense, 0) AS total_expense,
    (IFNULL(i.total_income, 0) - IFNULL(e.total_expense, 0)) AS net_savings
FROM (
    SELECT DISTINCT DATE_FORMAT(date, '%Y-%m') AS Month FROM income
    UNION 
    SELECT DISTINCT DATE_FORMAT(date, '%Y-%m') FROM expenses
) m
LEFT JOIN (
    SELECT DATE_FORMAT(date, '%Y-%m') AS Month, SUM(amount) AS total_income
    FROM income
    GROUP BY Month
) i ON m.Month = i.Month
LEFT JOIN (
    SELECT DATE_FORMAT(date, '%Y-%m') AS Month, SUM(amount) AS total_expense
    FROM expenses
    GROUP BY Month
) e ON m.Month = e.Month
ORDER BY m.Month;


-- Category-Wise Expense Breakdown
SELECT 
    category,
    SUM(amount) AS total_spent,
    ROUND(SUM(amount) * 100 / (SELECT SUM(amount) FROM expenses), 2) AS percentage
FROM expenses
GROUP BY category
ORDER BY total_spent DESC;


-- Savings Goal Progress Status
SELECT 
    date,
    goal_name,
    goal_amount,
    saved_amount,
    ROUND((saved_amount / goal_amount) * 100, 2) AS progress_pct,
    CASE 
        WHEN saved_amount >= goal_amount THEN 'Achieved'
        ELSE 'In Progress'
    END AS status
FROM savings;






