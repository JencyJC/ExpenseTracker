import pandas as pd
import mysql.connector
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')


# Load environment variables from .env file
load_dotenv()


# MySQL connection details from .env
db_config = {
    'host': os.getenv("DB_HOST"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'database': os.getenv("DB_NAME"),
    'autocommit': True
}


# Connect to MySQL
conn = mysql.connector.connect(**db_config)


# Read Excel files
df_income = pd.read_excel("Income.xlsx", engine='openpyxl')
df_expenses = pd.read_excel("Expenses.xlsx", engine='openpyxl')
df_savings = pd.read_excel("Savings.xlsx", engine='openpyxl')


# Step 2: Insert data into existing MySQL tables
cursor = conn.cursor()


# Insert Income
for _, row in df_income.iterrows():
    cursor.execute("""
        INSERT INTO income (date, source, amount,income_type)
        VALUES (%s, %s, %s, %s)
    """, (row['date'], row['source'], row['amount'],row['income_type']))


# Insert Expenses
for _, row in df_expenses.iterrows():
    cursor.execute("""
        INSERT INTO expenses (date, category, description, amount)
        VALUES (%s, %s, %s, %s)
    """, (row['date'], row['category'], row['description'], row['amount']))


# Insert Savings
for _, row in df_savings.iterrows():
    cursor.execute("""
        INSERT INTO savings (date, goal_name, goal_amount, saved_amount)
        VALUES (%s, %s, %s, %s)
    """, (row['date'], row['goal_name'], row['goal_amount'], row['saved_amount']))

conn.commit()


# Step 3: Monthly Income , Expense & Savings Summary
print("\n📊 Monthly Income & Expense Summary:")

summary_query = """
SELECT 
    Month,
    SUM(Total_Income) AS Total_Income,
    SUM(Total_Expense) AS Total_Expense,
    SUM(Total_Income) - SUM(Total_Expense) AS Net_Savings
FROM (
    -- Monthly Income
    SELECT 
        DATE_FORMAT(date, '%Y-%m') AS Month,
        SUM(amount) AS Total_Income,
        0 AS Total_Expense
    FROM income
    WHERE MONTH(date) IN (1, 2, 3)
    GROUP BY DATE_FORMAT(date, '%Y-%m')

    UNION ALL

    -- Monthly Expenses
    SELECT 
        DATE_FORMAT(date, '%Y-%m') AS Month,
        0 AS Total_Income,
        SUM(amount) AS Total_Expense
    FROM expenses
    GROUP BY DATE_FORMAT(date, '%Y-%m')
) AS combined
GROUP BY Month
ORDER BY Month;
"""

summary = pd.read_sql(summary_query, conn)
print(summary)

#grouped bar chart
summary.plot(x='Month', y=['Total_Income', 'Total_Expense', 'Net_Savings'], kind='bar', figsize=(10,6))
plt.title('Monthly Income, Expense & Net Savings')
plt.ylabel('Amount (₹)')
plt.xlabel('Month')
plt.xticks(rotation=45)
plt.grid(axis='y')
plt.tight_layout()
plt.show()



# Step 4: Category-Wise Expense
print("\n📂 Category-Wise Expense:")

category_query = """
SELECT category, SUM(amount) AS total_spent
FROM expenses
GROUP BY category
ORDER BY total_spent DESC;
"""
category_expenses = pd.read_sql(category_query, conn)
print(category_expenses)

#pie chart
category_expenses.set_index('category')['total_spent'].plot(kind='pie', autopct='%1.1f%%', figsize=(8,8))
plt.title('Category-Wise Expense Distribution')
plt.ylabel('')
plt.tight_layout()
plt.show()



# Step 5: Overspending Alerts
print("\n🚨 Overspending Alerts:")

limits = {
    "Grocery": 3000,
    "Medical": 3000,
    "Rent": 10000,
    "Dining": 1000,
    "Utilities": 1500,
    "Education": 2000,
    "Services": 2000,
    "Fitness": 3000,
    "Transport": 5000,
    "Subscriptions": 1500,
    "Shopping": 2000
}

# Fetch monthly totals per category
query = """
    SELECT category, DATE_FORMAT(date, '%b') AS month, SUM(amount) AS total 
    FROM expenses 
    GROUP BY category, month
    ORDER BY FIELD(month, 'Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'), category;
"""

df = pd.read_sql(query, conn)

if df.empty:
    print("No expenses recorded.")
else:
    for month in df['month'].unique():
        print(f"\n📅 {month}:")
        monthly_data = df[df['month'] == month]
        for _, row in monthly_data.iterrows():
            category = row['category']
            total = row['total']
            limit = limits.get(category)
            
            if limit is not None:
                status = "✅ Within Limit" if total <= limit else "⚠️ Overspending"
                print(f"- {category}: ₹{total} (Limit: ₹{limit}) → {status}")
            else:
                print(f"- {category}: ₹{total} (No limit set)")


# Clean and pivot the data
df_sorted = df.sort_values(by='month', key=lambda x: pd.to_datetime(x, format='%b'))
pivot_df = df_sorted.pivot(index='category', columns='month', values='total').fillna(0)

months = pivot_df.columns.tolist()
categories = pivot_df.index.tolist()

# Create subplots
fig, axes = plt.subplots(nrows=1, ncols=len(months), figsize=(16, 6), sharey=True)

for i, month in enumerate(months):
    axes[i].barh(categories, pivot_df[month], color='teal')
    axes[i].set_title(month)
    axes[i].set_xlabel("₹ Amount")
    if i == 0:
        axes[i].set_ylabel("Category")
    axes[i].invert_yaxis()
    axes[i].grid(axis='x', linestyle='--', alpha=0.7)

fig.suptitle("Monthly Expenses by Category", fontsize=16)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()




# Step 6: Savings Progress
print("\n💰 Savings Goals Progress:")

savings = pd.read_sql("SELECT * FROM savings", conn)
savings["Progress (%)"] = round((savings["saved_amount"] / savings["goal_amount"]) * 100, 2)
print(savings[["goal_name", "goal_amount", "saved_amount", "Progress (%)"]])

# Plot savings progress with horizontal bar chart
savings.sort_values("Progress (%)", inplace=True)
plt.figure(figsize=(10,6))
plt.barh(savings["goal_name"], savings["Progress (%)"], color='green')
plt.xlabel("Progress (%)")
plt.title("Savings Goals Progress")
plt.grid(axis='x')
plt.tight_layout()
plt.show()


cursor.close()
conn.close()
