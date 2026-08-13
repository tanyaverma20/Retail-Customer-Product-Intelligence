-- ================================================================================
-- RETAIL CUSTOMER & PRODUCT INTELLIGENCE — SQL BUSINESS INTELLIGENCE ENGINE
-- Database: PostgreSQL / ANSI SQL Compatible
-- Target Schema: customer_transactions (3,900 customer transaction snapshot records)
-- Core Focus: Customer Intelligence, Product Intelligence, Commercial Intelligence, Strategic Opportunities
-- ================================================================================


-- ================================================================================
-- 1. CUSTOMER INTELLIGENCE
-- ================================================================================

-- Business Question 1: Customer Value-Engagement Segment Revenue Contribution
-- Objective: Segment customers into 9 Value-Engagement tiers (Spend x Previous Purchase Volume) and quantify revenue share.
-- Decision Relevance: Identifies core revenue-generating customer clusters to focus loyalty retention programs.
WITH Overall_Revenue AS (
    SELECT SUM(purchase_amount_usd) AS grand_total_revenue
    FROM customer_transactions
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


-- Business Question 2: Demographic Revenue Drivers Across Age Group & Gender
-- Objective: Evaluate revenue contribution, average order value, and order volume across demographic brackets.
-- Decision Relevance: Guides demographic audience targeting for marketing campaigns without assuming equal sample sizes.
WITH Overall_Revenue AS (
    SELECT SUM(purchase_amount_usd) AS grand_total_revenue
    FROM customer_transactions
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


-- Business Question 3: Historical Purchase Volume (Engagement Tier) vs Transaction Spend
-- Objective: Analyze whether higher previous purchase volume corresponds to higher single-transaction order value.
-- Decision Relevance: Evaluates whether repeat buyers spend more per transaction or simply purchase more frequently over time.
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


-- Business Question 4: Subscription Status Distribution Across Customer Value Tiers
-- Objective: Assess subscription penetration rates and order values across Low, Medium, and High transaction value tiers.
-- Decision Relevance: Tests for basket-size parity between subscribers and non-subscribers within price brackets.
SELECT 
    customer_value_tier,
    subscription_status,
    COUNT(customer_id) AS customer_count,
    SUM(purchase_amount_usd) AS total_revenue,
    ROUND(AVG(purchase_amount_usd), 2) AS avg_order_value
FROM customer_transactions
GROUP BY customer_value_tier, subscription_status
ORDER BY customer_value_tier, subscription_status;



-- ================================================================================
-- 2. PRODUCT INTELLIGENCE
-- ================================================================================

-- Business Question 5: Category Commercial Performance Matrix & Revenue Ranking
-- Objective: Rank top-level categories by revenue contribution, order volume, average rating, and discount penetration.
-- Decision Relevance: Directs core merchandising resources and inventory budgeting toward top-performing categories.
WITH Overall_Revenue AS (
    SELECT SUM(purchase_amount_usd) AS grand_total_revenue
    FROM customer_transactions
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


-- Business Question 6: Product-Level Performance Ranking (Top 10 Revenue Generators)
-- Objective: Rank all 25 items by total revenue contribution using window functions.
-- Decision Relevance: Identifies hero products driving top-line revenue versus tail products.
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


-- Business Question 7: Product Satisfaction Ranking (Top 5 & Bottom 5 Rated Products)
-- Objective: Rank products by customer review rating to identify satisfaction leaders and quality risk items.
-- Decision Relevance: Informs quality assurance audits for low-rated products and promotional spotlighting for top-rated items.
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


-- Business Question 8: Product Category Revenue Distribution Across Customer Value Tiers
-- Objective: Map category purchase distribution across Low, Medium, and High Customer Value Tiers.
-- Decision Relevance: Evaluates whether premium categories appeal disproportionately to high-value shoppers.
SELECT 
    category,
    customer_value_tier,
    COUNT(customer_id) AS transaction_count,
    SUM(purchase_amount_usd) AS total_revenue,
    ROUND(AVG(purchase_amount_usd), 2) AS avg_order_value
FROM customer_transactions
GROUP BY category, customer_value_tier
ORDER BY category, customer_value_tier;



-- ================================================================================
-- 3. COMMERCIAL INTELLIGENCE
-- ================================================================================

-- Business Question 9: Commercial Impact of Discounting on Transaction Order Value
-- Objective: Compare order volume, total revenue, and average purchase amount between discounted and full-price orders.
-- Decision Relevance: Evaluates whether discount usage expands basket size or yields lower average order values.
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


-- Business Question 10: Shipping Channel Monetization & Subscriber Share
-- Objective: Rank shipping channels by average transaction purchase amount and evaluate subscriber participation.
-- Decision Relevance: Guides shipping fee structure and express logistics prioritization.
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


-- Business Question 11: Payment Gateway Revenue Distribution & Average Basket Size
-- Objective: Quantify revenue share and average transaction spend across all 6 payment methods.
-- Decision Relevance: Informs payment gateway partnership terms and transaction processing fee negotiations.
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


-- Business Question 12: Seasonal Category Demand Matrix (Conditional Aggregation)
-- Objective: Pivot revenue by category across the 4 seasons (Spring, Summer, Fall, Winter).
-- Decision Relevance: Directs seasonal inventory replenishment and marketing promotional timing per category.
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



-- ================================================================================
-- 4. STRATEGIC OPPORTUNITIES
-- ================================================================================

-- Business Question 13: Subscriber Acquisition Opportunity Target List
-- Objective: Identify non-subscribed customers demonstrating high previous purchase volume (>25) and high transaction spend (>$75).
-- Decision Relevance: Creates a qualified target audience for subscriber conversion marketing campaigns.
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


-- Business Question 14: Category Revenue vs. Discount Penetration Multi-Dimensional Risk Matrix
-- Objective: Multi-rank product categories by top-line revenue contribution versus discount dependence.
-- Decision Relevance: Highlights categories generating high revenue but carrying potential gross margin risk due to heavy discount reliance.
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
