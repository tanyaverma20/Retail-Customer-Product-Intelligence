# Power BI Business Intelligence Dashboard Documentation

## 1. Dashboard Overview & Analytical Architecture

The **Retail Customer & Product Intelligence Power BI Dashboard** (`customer_behavior_dashboard.pbix`) converts raw snapshot transactions into an interactive, executive-grade business intelligence product.

### Core Analytical Objectives
* **Executive Summary**: Provide C-suite visibility into top-line revenue ($233,081), transaction volume (3,900 orders), customer acquisition (3,900 unique customers), subscriber rates (27.0%), and discount penetration (43.0%).
* **Customer Intelligence**: Analyze customer value tiers, engagement tiers, demographic drivers, and subscription rates across 9 Value-Engagement segments.
* **Product & Category Intelligence**: Evaluate category performance rankings, product revenue contribution, ratings variance, and discount dependency across 25 items.
* **Commercial Opportunities**: Identify high-value non-subscriber conversion target cohorts (431 customers), evaluate discount dependency (Full-price AOV $60.13 vs Discounted AOV $59.28), and map seasonal category demand patterns.

---

## 2. Power BI Data Model Architecture

The Power BI data model is designed around the canonical Phase 1 cleaned dataset (`customer_shopping_behavior_cleaned.csv`), supplemented by intelligence tables to prevent artificial many-to-many relationship ambiguity.

```
+-----------------------------------------------------------------------------------+
|                        customer_shopping_behavior_cleaned                         |
|-----------------------------------------------------------------------------------|
| customer_id (PK)                 | purchase_amount_usd                            |
| age                              | age_group                                      |
| gender                           | customer_value_tier                            |
| item_purchased                   | engagement_tier                                |
| category                         | value_engagement_segment                       |
| review_rating                    | purchase_frequency_days                        |
| subscription_status              | shipping_type                                  |
| discount_applied                 | payment_method                                 |
| previous_purchases               | season                                         |
+-----------------------------------------------------------------------------------+
                                     |
                +--------------------+--------------------+
                |                                         |
                v                                         v
+-------------------------------+         +-------------------------------+
|     product_intelligence      |         |     category_intelligence     |
|-------------------------------|         |-------------------------------|
| category (FK)                 |         | category (PK)                 |
| item_purchased (PK)           |         | total_revenue                 |
| total_revenue                 |         | transaction_volume            |
| transaction_count             |         | avg_purchase_amount           |
| avg_review_rating             |         | discount_penetration_pct      |
+-------------------------------+         +-------------------------------+
```

---

## 3. Core DAX Measures Taxonomy

All metrics in the dashboard are computed dynamically via explicit DAX measures. `Customer ID` is explicitly protected against non-sensical summation using `DISTINCTCOUNT(customer_id)`.

```dax
// 1. Total Revenue
Total Revenue = 
SUM(customer_shopping_behavior_cleaned[purchase_amount_usd])

// 2. Total Transactions
Total Transactions = 
COUNT(customer_shopping_behavior_cleaned[customer_id])

// 3. Unique Customers
Unique Customers = 
DISTINCTCOUNT(customer_shopping_behavior_cleaned[customer_id])

// 4. Average Purchase Amount (AOV)
Average Purchase Amount = 
AVERAGE(customer_shopping_behavior_cleaned[purchase_amount_usd])

// 5. Subscriber Count
Subscriber Count = 
CALCULATE(
    COUNT(customer_shopping_behavior_cleaned[customer_id]),
    customer_shopping_behavior_cleaned[subscription_status] = "Yes"
)

// 6. Subscriber Rate (%)
Subscriber Rate = 
DIVIDE([Subscriber Count], [Total Transactions], 0)

// 7. Discounted Transaction Count
Discounted Transaction Count = 
CALCULATE(
    COUNT(customer_shopping_behavior_cleaned[customer_id]),
    customer_shopping_behavior_cleaned[discount_applied] = "Yes"
)

// 8. Discount Penetration Rate (%)
Discount Penetration Rate = 
DIVIDE([Discounted Transaction Count], [Total Transactions], 0)

// 9. Revenue Share (%)
Revenue Share = 
DIVIDE(
    [Total Revenue],
    CALCULATE([Total Revenue], ALL(customer_shopping_behavior_cleaned)),
    0
)

// 10. Average Review Rating
Average Review Rating = 
AVERAGE(customer_shopping_behavior_cleaned[review_rating])

// 11. Total Previous Purchases Volume
Previous Purchases Volume = 
SUM(customer_shopping_behavior_cleaned[previous_purchases])

// 12. Average Previous Purchases
Average Previous Purchases = 
AVERAGE(customer_shopping_behavior_cleaned[previous_purchases])

// 13. High-Value Non-Subscriber Target Cohort Count
High-Value Non-Subscriber Opportunity Cohort = 
CALCULATE(
    COUNT(customer_shopping_behavior_cleaned[customer_id]),
    customer_shopping_behavior_cleaned[subscription_status] = "No",
    customer_shopping_behavior_cleaned[previous_purchases] > 25,
    customer_shopping_behavior_cleaned[purchase_amount_usd] > 75
)

// 14. Full-Price Average Order Value (AOV)
Full Price AOV = 
CALCULATE(
    AVERAGE(customer_shopping_behavior_cleaned[purchase_amount_usd]),
    customer_shopping_behavior_cleaned[discount_applied] = "No"
)

// 15. Discounted Average Order Value (AOV)
Discounted AOV = 
CALCULATE(
    AVERAGE(customer_shopping_behavior_cleaned[purchase_amount_usd]),
    customer_shopping_behavior_cleaned[discount_applied] = "Yes"
)
```

---

## 4. Multi-Page Dashboard Architecture

### Page 1: Executive Overview
* **Business Question**: *"How is the retail business performing, and where are the major customer/product opportunities?"*
* **KPI Cards (6)**: Total Revenue ($233,081), Total Transactions (3,900), Unique Customers (3,900), Avg Purchase Amount ($59.76), Subscriber Rate (27.0%), Discount Penetration (43.0%).
* **Visuals (5)**:
  1. `Revenue by Product Category` (Clustered Bar: Clothing $104.3K, Accessories $74.2K, Footwear $36.1K, Outerwear $18.5K).
  2. `Revenue by Value-Engagement Segment` (Clustered Bar across 9 segments).
  3. `Top 10 Products by Total Revenue` (Horizontal Bar: Blouse $10.4K to Shorts $9.4K).
  4. `Subscription Status Share` (Donut Chart: 1,053 Subscribed / 2,847 Non-Subscribed).
  5. `Discounted vs Full-Price Revenue` (Column Chart: $133.7K Full Price / $99.4K Discounted).
* **Key Executive Insights Panel**: Concise observations summarizing category concentration (76.56% in Clothing + Accessories) and value segment contributions (45.89% in High Value tiers).

### Page 2: Customer Intelligence
* **Business Question**: *"Which customer groups contribute the most recorded value, and how does customer behavior differ across segments?"*
* **Visuals (6)**:
  1. `Revenue by Value-Engagement Segment` (Bar Chart).
  2. `Customer Count by Value-Engagement Segment` (Column Chart).
  3. `Average Order Value (AOV) by Segment` (Bar Chart).
  4. `Subscription Rate (%) by Segment` (Bar Chart).
  5. `Revenue Contribution by Age Group` (Column Chart: 18-30, 31-45, 46-60, 61-70).
  6. `Revenue Distribution by Gender` (Donut Chart: Male 67.7% / Female 32.3%).
* **Interactive Slicers (5)**: `Age Group`, `Gender`, `Subscription Status`, `Customer Value Tier`, `Engagement Tier`.
* **Analytical Insights Panel**: Clarifies demographic volume representation vs AOV parity ($59.54 Male vs $60.25 Female).

### Page 3: Product Intelligence
* **Business Question**: *"Which products and categories drive recorded retail performance?"*
* **Visuals (6)**:
  1. `Total Revenue by Category` (Bar Chart).
  2. `Transaction Volume by Category` (Column Chart).
  3. `Top 10 Products by Total Revenue` (Horizontal Bar Chart).
  4. `Product Satisfaction Extremes` (Grouped Bar Chart: Top rated Gloves 3.86 vs Lowest rated Shirt 3.62).
  5. `Discount Penetration Rate (%) by Category` (Bar Chart).
  6. `Category Revenue Distribution across Value Tiers` (Stacked Column Chart).
* **Interactive Slicers (2)**: `Category`, `Customer Value Tier`.
* **Custom Tooltips**: Configured across product visuals to display Revenue, Revenue Share %, Transaction Count, AOV, Avg Rating, and Discount Penetration %.

### Page 4: Commercial Opportunities
* **Business Question**: *"Where are the strongest observable commercial opportunities in the current dataset?"*
* **Modules & Visuals (4)**:
  1. `Subscriber Target Cohort KPI Card`: Highlights **431 high-value, highly engaged non-subscribed customers**.
  2. `Discount Dependency Comparison`: Bar Chart comparing Full-Price AOV ($60.13) vs Discounted AOV ($59.28).
  3. `Category Discount Dependency Matrix`: Scatter Plot comparing Revenue Rank vs Discount Penetration Rank.
  4. `Recorded Seasonal Category Demand Pattern`: Grouped Column Chart illustrating Spring/Winter Clothing peaks and Fall/Summer Accessories peaks.
* **Interactive Slicers (2)**: `Season`, `Discount Applied`.
* **Evidence-Based Recommendations Panel**: 5 conservative recommendations covering subscription targeting, discount review, category merchandising priorities, product quality audits, and seasonal timing.

---

## 5. Baseline KPI Reconciliation Matrix

| KPI Dimension | Phase 1 Python Baseline | Phase 2 SQL Baseline | Phase 3 Power BI Measure Result | Variance | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Total Revenue** | **$233,081** | **$233,081** | **$233,081** | **$0.00** | **EXACT MATCH** |
| **Total Transactions** | **3,900** | **3,900** | **3,900** | **0** | **EXACT MATCH** |
| **Unique Customer Count** | **3,900** | **3,900** | **3,900** | **0** | **EXACT MATCH** |
| **Subscribers Count** | **1,053** | **1,053** | **1,053** | **0** | **EXACT MATCH** |
| **Subscriber Rate (%)** | **27.0%** | **27.0%** | **27.0%** | **0.0%** | **EXACT MATCH** |
| **Discounted Orders** | **1,677** | **1,677** | **1,677** | **0** | **EXACT MATCH** |
| **Discount Penetration (%)**| **43.0%** | **43.0%** | **43.0%** | **0.0%** | **EXACT MATCH** |
| **Clothing Revenue** | **$104,264** | **$104,264** | **$104,264** | **$0.00** | **EXACT MATCH** |
| **Accessories Revenue** | **$74,200** | **$74,200** | **$74,200** | **$0.00** | **EXACT MATCH** |
| **Footwear Revenue** | **$36,093** | **$36,093** | **$36,093** | **$0.00** | **EXACT MATCH** |
| **Outerwear Revenue** | **$18,524** | **$18,524** | **$18,524** | **$0.00** | **EXACT MATCH** |
| **Top Product (Blouse)** | **$10,410** | **$10,410** | **$10,410** | **$0.00** | **EXACT MATCH** |
| **Target Non-Subscribers** | **431** | **431** | **431** | **0** | **EXACT MATCH** |

---

## 6. Actual Final Metrics for Portfolio Documentation

* **DAX Measures Created**: 15 explicit measures
* **Dashboard Pages**: 4 interactive pages
* **Analytical Visuals**: 21 visual charts/cards across 4 pages
* **Interactive Slicers**: 11 slicers across pages
* **Insight Cards**: 4 strategic observation panels
* **KPI Reconciliations**: 13/13 exact match (100% agreement)

---

## 7. Power BI Quality Check & Dataset Limitations

1. **Summation Check**: `Customer ID` is nowhere summed in the report.
2. **Unsupported Claims Omitted**: Terms like "churn", "retention rate", "RFM", "CLV", "gross margin", "margin leakage", "profitability", and "market basket analysis" are strictly omitted.
3. **Approved Terminology Applied**: "Discount dependency", "discount penetration", "customer engagement opportunity", "category expansion opportunity", and "recorded seasonal pattern" are consistently enforced.
