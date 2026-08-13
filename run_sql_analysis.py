import sqlite3
import pandas as pd
import os

# Connect to SQLite Database
conn = sqlite3.connect('data/processed/retail_bi.db')

queries = [
    {
        'id': 'Q1',
        'domain': 'Customer Intelligence',
        'title': 'Customer Value-Engagement Segment Revenue Contribution',
        'sql': """
            WITH Overall_Revenue AS (
                SELECT SUM(purchase_amount_usd) AS grand_total_revenue FROM customer_transactions
            )
            SELECT 
                t.value_engagement_segment,
                COUNT(t.customer_id) AS customer_count,
                SUM(t.purchase_amount_usd) AS total_revenue,
                ROUND(AVG(t.purchase_amount_usd), 2) AS avg_order_value,
                ROUND(SUM(t.purchase_amount_usd) * 100.0 / r.grand_total_revenue, 2) AS revenue_share_pct,
                ROUND(SUM(CASE WHEN t.subscription_status = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(t.customer_id), 2) AS subscriber_share_pct
            FROM customer_transactions t
            CROSS JOIN Overall_Revenue r
            GROUP BY t.value_engagement_segment, r.grand_total_revenue
            ORDER BY total_revenue DESC;
        """
    },
    {
        'id': 'Q2',
        'domain': 'Customer Intelligence',
        'title': 'Demographic Revenue Drivers Across Age Group & Gender',
        'sql': """
            WITH Overall_Revenue AS (
                SELECT SUM(purchase_amount_usd) AS grand_total_revenue FROM customer_transactions
            )
            SELECT 
                t.age_group,
                t.gender,
                COUNT(t.customer_id) AS customer_count,
                SUM(t.purchase_amount_usd) AS total_revenue,
                ROUND(AVG(t.purchase_amount_usd), 2) AS avg_order_value,
                ROUND(SUM(t.purchase_amount_usd) * 100.0 / r.grand_total_revenue, 2) AS revenue_share_pct
            FROM customer_transactions t
            CROSS JOIN Overall_Revenue r
            GROUP BY t.age_group, t.gender, r.grand_total_revenue
            ORDER BY t.age_group, t.gender;
        """
    },
    {
        'id': 'Q3',
        'domain': 'Customer Intelligence',
        'title': 'Engagement Tier Volume vs Spend Analysis',
        'sql': """
            SELECT 
                engagement_tier,
                COUNT(customer_id) AS customer_count,
                SUM(purchase_amount_usd) AS total_revenue,
                ROUND(AVG(purchase_amount_usd), 2) AS avg_order_value,
                ROUND(AVG(previous_purchases), 2) AS avg_previous_purchases,
                ROUND(SUM(CASE WHEN subscription_status = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(customer_id), 2) AS subscriber_share_pct
            FROM customer_transactions
            GROUP BY engagement_tier
            ORDER BY total_revenue DESC;
        """
    },
    {
        'id': 'Q4',
        'domain': 'Customer Intelligence',
        'title': 'Subscription Status Distribution Across Customer Value Tiers',
        'sql': """
            SELECT 
                customer_value_tier,
                subscription_status,
                COUNT(customer_id) AS customer_count,
                SUM(purchase_amount_usd) AS total_revenue,
                ROUND(AVG(purchase_amount_usd), 2) AS avg_order_value
            FROM customer_transactions
            GROUP BY customer_value_tier, subscription_status
            ORDER BY customer_value_tier, subscription_status;
        """
    },
    {
        'id': 'Q5',
        'domain': 'Product Intelligence',
        'title': 'Category Commercial Performance Matrix & Revenue Ranking',
        'sql': """
            WITH Overall_Revenue AS (
                SELECT SUM(purchase_amount_usd) AS grand_total_revenue FROM customer_transactions
            )
            SELECT 
                DENSE_RANK() OVER (ORDER BY SUM(t.purchase_amount_usd) DESC) AS revenue_rank,
                t.category,
                COUNT(t.customer_id) AS transaction_volume,
                SUM(t.purchase_amount_usd) AS total_revenue,
                ROUND(SUM(t.purchase_amount_usd) * 100.0 / r.grand_total_revenue, 2) AS category_revenue_share_pct,
                ROUND(AVG(t.purchase_amount_usd), 2) AS avg_purchase_amount,
                ROUND(AVG(t.review_rating), 2) AS avg_review_rating,
                ROUND(SUM(CASE WHEN t.discount_applied = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(t.customer_id), 2) AS discount_penetration_pct
            FROM customer_transactions t
            CROSS JOIN Overall_Revenue r
            GROUP BY t.category, r.grand_total_revenue
            ORDER BY revenue_rank;
        """
    },
    {
        'id': 'Q6',
        'domain': 'Product Intelligence',
        'title': 'Product-Level Performance Ranking (Top 10 Revenue Generators)',
        'sql': """
            SELECT 
                DENSE_RANK() OVER (ORDER BY SUM(purchase_amount_usd) DESC) AS product_rank,
                category,
                item_purchased,
                COUNT(customer_id) AS transaction_count,
                SUM(purchase_amount_usd) AS total_revenue,
                ROUND(AVG(purchase_amount_usd), 2) AS avg_order_value,
                ROUND(AVG(review_rating), 2) AS avg_review_rating,
                ROUND(SUM(CASE WHEN discount_applied = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(customer_id), 2) AS discount_penetration_pct
            FROM customer_transactions
            GROUP BY category, item_purchased
            ORDER BY product_rank
            LIMIT 10;
        """
    },
    {
        'id': 'Q7',
        'domain': 'Product Intelligence',
        'title': 'Product Satisfaction Ranking (Top 5 & Bottom 5 Rated Products)',
        'sql': """
            WITH Rated_Products AS (
                SELECT 
                    category,
                    item_purchased,
                    COUNT(customer_id) AS order_count,
                    SUM(purchase_amount_usd) AS total_revenue,
                    ROUND(AVG(review_rating), 2) AS avg_rating,
                    ROW_NUMBER() OVER (ORDER BY AVG(review_rating) DESC, COUNT(customer_id) DESC) AS top_rating_rank,
                    ROW_NUMBER() OVER (ORDER BY AVG(review_rating) ASC, COUNT(customer_id) DESC) AS bottom_rating_rank
                FROM customer_transactions
                GROUP BY category, item_purchased
            )
            SELECT 
                'Top Rated' AS rating_tier,
                top_rating_rank AS rank,
                category,
                item_purchased,
                order_count,
                total_revenue,
                avg_rating
            FROM Rated_Products
            WHERE top_rating_rank <= 5
            UNION ALL
            SELECT 
                'Bottom Rated' AS rating_tier,
                bottom_rating_rank AS rank,
                category,
                item_purchased,
                order_count,
                total_revenue,
                avg_rating
            FROM Rated_Products
            WHERE bottom_rating_rank <= 5
            ORDER BY rating_tier DESC, rank ASC;
        """
    },
    {
        'id': 'Q8',
        'domain': 'Product Intelligence',
        'title': 'Product Category Revenue Distribution Across Customer Value Tiers',
        'sql': """
            SELECT 
                category,
                customer_value_tier,
                COUNT(customer_id) AS transaction_count,
                SUM(purchase_amount_usd) AS total_revenue,
                ROUND(AVG(purchase_amount_usd), 2) AS avg_order_value
            FROM customer_transactions
            GROUP BY category, customer_value_tier
            ORDER BY category, customer_value_tier;
        """
    },
    {
        'id': 'Q9',
        'domain': 'Commercial Intelligence',
        'title': 'Commercial Impact of Discounting on Transaction Order Value',
        'sql': """
            WITH Overall_Orders AS (
                SELECT COUNT(*) AS grand_total_orders FROM customer_transactions
            )
            SELECT 
                t.discount_applied,
                COUNT(t.customer_id) AS transaction_count,
                SUM(t.purchase_amount_usd) AS total_revenue,
                ROUND(AVG(t.purchase_amount_usd), 2) AS avg_order_value,
                ROUND(COUNT(t.customer_id) * 100.0 / o.grand_total_orders, 2) AS transaction_share_pct
            FROM customer_transactions t
            CROSS JOIN Overall_Orders o
            GROUP BY t.discount_applied, o.grand_total_orders;
        """
    },
    {
        'id': 'Q10',
        'domain': 'Commercial Intelligence',
        'title': 'Shipping Channel Monetization & Subscriber Share',
        'sql': """
            SELECT 
                DENSE_RANK() OVER (ORDER BY AVG(purchase_amount_usd) DESC) AS aov_rank,
                shipping_type,
                COUNT(customer_id) AS transaction_count,
                SUM(purchase_amount_usd) AS total_revenue,
                ROUND(AVG(purchase_amount_usd), 2) AS avg_purchase_amount,
                ROUND(SUM(CASE WHEN subscription_status = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(customer_id), 2) AS subscriber_share_pct
            FROM customer_transactions
            GROUP BY shipping_type
            ORDER BY aov_rank;
        """
    },
    {
        'id': 'Q11',
        'domain': 'Commercial Intelligence',
        'title': 'Payment Gateway Revenue Distribution & Average Basket Size',
        'sql': """
            WITH Overall_Revenue AS (
                SELECT SUM(purchase_amount_usd) AS grand_total_revenue FROM customer_transactions
            )
            SELECT 
                t.payment_method,
                COUNT(t.customer_id) AS transaction_count,
                SUM(t.purchase_amount_usd) AS total_revenue,
                ROUND(AVG(t.purchase_amount_usd), 2) AS avg_order_value,
                ROUND(SUM(t.purchase_amount_usd) * 100.0 / r.grand_total_revenue, 2) AS revenue_share_pct
            FROM customer_transactions t
            CROSS JOIN Overall_Revenue r
            GROUP BY t.payment_method, r.grand_total_revenue
            ORDER BY total_revenue DESC;
        """
    },
    {
        'id': 'Q12',
        'domain': 'Commercial Intelligence',
        'title': 'Seasonal Category Demand Matrix',
        'sql': """
            SELECT 
                category,
                SUM(CASE WHEN season = 'Spring' THEN purchase_amount_usd ELSE 0 END) AS spring_revenue,
                SUM(CASE WHEN season = 'Summer' THEN purchase_amount_usd ELSE 0 END) AS summer_revenue,
                SUM(CASE WHEN season = 'Fall' THEN purchase_amount_usd ELSE 0 END) AS fall_revenue,
                SUM(CASE WHEN season = 'Winter' THEN purchase_amount_usd ELSE 0 END) AS winter_revenue,
                SUM(purchase_amount_usd) AS total_annual_revenue
            FROM customer_transactions
            GROUP BY category
            ORDER BY total_annual_revenue DESC;
        """
    },
    {
        'id': 'Q13',
        'domain': 'Strategic Opportunities',
        'title': 'Subscriber Acquisition Opportunity Target List',
        'sql': """
            SELECT 
                customer_id,
                age,
                gender,
                category,
                item_purchased,
                purchase_amount_usd,
                previous_purchases,
                value_engagement_segment
            FROM customer_transactions
            WHERE subscription_status = 'No'
              AND previous_purchases > 25
              AND purchase_amount_usd > 75
            ORDER BY previous_purchases DESC, purchase_amount_usd DESC;
        """
    },
    {
        'id': 'Q14',
        'domain': 'Strategic Opportunities',
        'title': 'Category Revenue vs. Discount Penetration Multi-Dimensional Risk Matrix',
        'sql': """
            WITH CategoryMetrics AS (
                SELECT 
                    category,
                    SUM(purchase_amount_usd) AS total_revenue,
                    ROUND(SUM(CASE WHEN discount_applied = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(customer_id), 2) AS discount_penetration_pct
                FROM customer_transactions
                GROUP BY category
            )
            SELECT 
                category,
                total_revenue,
                discount_penetration_pct,
                RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank,
                RANK() OVER (ORDER BY discount_penetration_pct DESC) AS discount_rank
            FROM CategoryMetrics
            ORDER BY revenue_rank;
        """
    }
]

print("================ EXECUTING AND RECONCILING 14 CORE SQL BUSINESS ANALYSES ================\n")

results_summary = []

for q in queries:
    df = pd.read_sql_query(q['sql'], conn)
    results_summary.append({
        'id': q['id'],
        'domain': q['domain'],
        'title': q['title'],
        'rows_returned': len(df),
        'df': df
    })
    print(f"[{q['id']}] {q['domain']}: {q['title']}")
    print(f"Rows: {len(df)}")
    print(df.head(5).to_string(index=False))
    print("-" * 80 + "\n")

print("All 14 SQL Queries Executed Successfully!")
