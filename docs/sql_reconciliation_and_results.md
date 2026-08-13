# SQL Business Intelligence Reconciliation & Analytical Results Report

## 1. SQL Data Model Overview
The SQL layer is built on top of the primary analytical transaction table `customer_transactions` (populated directly from `data/processed/customer_shopping_behavior_cleaned.csv`), representing 3,900 unique customer purchase records.

### Database Tables / Views
1. `customer_transactions` (3,900 rows × 23 attributes) — Primary transaction snapshot table.
2. `customer_intelligence` (3,900 rows × 20 attributes) — Customer segmentation snapshot table.
3. `product_intelligence` (25 rows × 10 attributes) — Product performance matrix table.
4. `category_intelligence` (4 rows × 10 attributes) — Category commercial performance table.

---

## 2. Python / SQL Reconciliation Matrix (10 Points of Audit)

| # | Analytical Metric | Phase 1 Python Metric | Phase 2 SQL Query Result | Status | Reconciliation Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Total Enterprise Revenue** | **$233,081** | **$233,081** | **EXACT MATCH** | 100% agreement across all 3,900 transactions. |
| **2** | **Total Transaction Count** | **3,900 orders** | **3,900 orders** | **EXACT MATCH** | Zero missing or uncounted records. |
| **3** | **Total Unique Customers** | **3,900 customers** | **3,900 customers** | **EXACT MATCH** | 1 snapshot record per unique Customer ID. |
| **4** | **Category Count & Revenue** | **4 Categories ($233,081)** | **4 Categories ($233,081)** | **EXACT MATCH** | Clothing ($104,264), Accessories ($74,200), Footwear ($36,093), Outerwear ($18,524). |
| **5** | **Product Count & Top Item** | **25 Products (Top: Blouse)** | **25 Products (Top: Blouse)** | **EXACT MATCH** | Blouse revenue ($10,410 across 171 transactions). |
| **6** | **Segment Revenue Share** | **9 Segments ($233,081)** | **9 Segments ($233,081)** | **EXACT MATCH** | Medium Value - Medium Engagement top ($40,937 / 17.56%). |
| **7** | **Subscription Volume** | **1,053 Subscribers (27.0%)** | **1,053 Subscribers (27.0%)** | **EXACT MATCH** | Non-subscribers = 2,847 (73.0%). |
| **8** | **Discount Transaction Count** | **1,677 Discounted (43.0%)** | **1,677 Discounted (43.0%)** | **EXACT MATCH** | Full-price transactions = 2,223 (57.0%). |
| **9** | **Product Count** | **25 items** | **25 items** | **EXACT MATCH** | All items accounted for in grouping queries. |
| **10**| **Category Count** | **4 categories** | **4 categories** | **EXACT MATCH** | Zero orphan or null categories. |

---

## 3. Core Business Question Results Summary (14 Queries)

### Customer Intelligence (Q1 - Q4)
* **Q1 (Value-Engagement Segment Revenue Contribution)**: `Medium Value - Medium Engagement` ($40,937 / 17.56% share) and `High Value - Medium Engagement` ($40,346 / 17.31% share) drive the largest shares of revenue.
* **Q2 (Demographic Revenue Drivers)**: Male customers account for $157,890 (67.7% of total revenue), while Female customers account for $75,191 (32.3%). AOV is nearly identical ($59.54 Male vs. $60.25 Female).
* **Q3 (Engagement Volume vs Spend)**: Medium Engagement (16–35 previous purchases) generates $108,786 across 1,874 transactions, compared to High Engagement ($74,614 / 1,147 transactions) and Low Engagement ($49,611 / 879 transactions).
* **Q4 (Subscription Status Across Value Tiers)**: High Value non-subscribers generate $78,097 (884 customers, $88.35 AOV) vs High Value subscribers generating $28,868 (330 customers, $87.48 AOV).

### Product Intelligence (Q5 - Q8)
* **Q5 (Category Performance Matrix)**: Clothing ranks #1 ($104,264 revenue, 44.73% share, 42.08% discount rate), followed by Accessories ($74,200 / 31.83% share), Footwear ($36,093 / 15.49% share), and Outerwear ($18,524 / 7.95% share).
* **Q6 (Top 10 Products by Revenue)**: Top 3 products are Blouse ($10,410), Shirt ($10,332), and Dress ($10,320) — all in the Clothing category.
* **Q7 (Product Rating Ranking)**: Top rated item is Gloves (3.86 avg rating / 140 orders), while lowest rated item is Shirt (3.62 avg rating / 169 orders).
* **Q8 (Category Value Preference)**: Clothing is the dominant category across all spend tiers, generating $48,703 among High Value shoppers, $42,311 among Medium Value shoppers, and $13,250 among Low Value shoppers.

### Commercial Intelligence (Q9 - Q12)
* **Q9 (Discounting Commercial Impact)**: Full-price sales ($133,670 revenue, 2,223 orders) yield $60.13 AOV, while Discounted sales ($99,411 revenue, 1,677 orders) yield $59.28 AOV.
* **Q10 (Shipping Channel Monetization)**: 2-Day Shipping achieves the highest AOV ($60.73), followed by Express ($60.48), Free Shipping ($60.41), Store Pickup ($59.89), Next Day Air ($58.63), and Standard ($58.46).
* **Q11 (Payment Gateway Revenue Distribution)**: Credit Card leads revenue ($40,310 / 17.29% share), followed by PayPal ($40,109 / 17.21%), Cash ($40,002 / 17.16%), Debit Card ($38,742 / 16.62%), Venmo ($37,374 / 16.03%), and Bank Transfer ($36,544 / 15.68%).
* **Q12 (Seasonal Category Demand Matrix)**: Clothing peaks in Spring ($27,692) and Winter ($27,274). Accessories peaks in Fall ($19,874) and Summer ($19,028).

### Strategic Opportunities (Q13 - Q14)
* **Q13 (High-Value Non-Subscriber Target List)**: 431 non-subscribed customers meet the target criteria of >25 previous purchases and >$75 order spend, representing prime candidates for subscriber conversion.
* **Q14 (Category Revenue vs Discount Risk Matrix)**: Clothing ranks #1 in revenue but #4 in discount penetration (42.08%), whereas Outerwear ranks #4 in revenue but #1 in discount penetration (44.44%).
