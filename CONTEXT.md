# Repository Context: Retail Customer & Product Intelligence

This document is based on the actual repository implementation, not on generic project templates or assumptions. It reflects the files, scripts, generated data assets, SQL queries, completed Power BI artifacts, and executive deliverables present in this repository.

## 1. Repository identity and project type

This repository is an end-to-end retail customer, product, and commercial business intelligence project focused on transforming raw transactional customer data into an interactive decision-support layer.

It is an analytics and business intelligence product centered on Python, SQLite/SQL, and Power BI. It includes a fully functional, interactive Power BI dashboard (`customer_behavior_dashboard.pbix`) as its primary business user interface.

The repository is best characterized as:

- an end-to-end data preparation and feature engineering pipeline (Python)
- a relational business intelligence query engine (SQLite + ANSI/PostgreSQL SQL)
- a cross-engine metric reconciliation and data validation framework
- a completed, 4-page interactive executive Power BI dashboard (`customer_behavior_dashboard.pbix`)
- a documented executive decision-support deliverable with evidence-based commercial recommendations

From the repository architecture, it does not require a web application runtime, REST API, or deployed microservice backend. The user-facing presentation and interactive exploration layer is delivered through the native Power BI dashboard supported by executive documentation and slide deck deliverables.

## 2. Source of truth and repository evidence

The repository implements a complete, validated analytical pipeline:

1. **Raw Data Ingestion**: The raw customer transaction CSV (`customer_shopping_behavior.csv`, 3,900 rows) is ingested.
2. **Data Cleaning & Feature Engineering (Python)**: Data quality checks, median imputation, column standardization, and multi-tier customer segmentation are executed.
3. **Data Materialization**: Cleaned and segmented datasets are materialized to CSV outputs and loaded into SQLite (`retail_bi.db`).
4. **Relational BI Query Engine (SQL)**: 14 business intelligence queries are executed across customer, product, and commercial domains to uncover core transactional patterns.
5. **Reconciliation & Validation**: Results across Python, SQL, and DAX are reconciled via a 13-point audit matrix achieving 100% exact agreement ($0.00 variance).
6. **Interactive Visualization (Power BI)**: A completed 4-page interactive Power BI dashboard (`customer_behavior_dashboard.pbix`) provides dynamic visual exploration across executive, customer, product, and commercial dimensions.
7. **Business Interpretation & Commercial Recommendations**: Quantitative patterns are synthesized into actionable commercial strategies for retail leadership.

### Primary Evidence Files
- `README.md` — project overview, analytical architecture, and business context
- `run_sql_analysis.py` — SQL analysis execution engine running against SQLite
- `build_powerbi_dashboard.py` — PBIX layout manipulation and dashboard page generation script
- `customer_behavior_dashboard.pbix` — completed, 4-page interactive Power BI report
- `generate_phase1_notebook.py` — script generating the end-to-end Phase 1 cleaning, EDA, and feature engineering notebook
- `generate_phase4_assets.py` — high-resolution chart, PowerPoint, and PDF presentation generation engine
- `customer_behavior_sql_queries.sql` — comprehensive SQL business intelligence query library
- `customer_shopping_behavior.csv` — raw source transaction dataset (3,900 rows)
- `data/processed/customer_shopping_behavior_cleaned.csv` — canonical cleaned dataset
- `data/processed/customer_intelligence.csv` — customer-level segmentation and demographic dataset
- `data/processed/product_intelligence.csv` — product-level metrics and rating variance dataset (25 products)
- `data/processed/category_intelligence.csv` — category-level commercial performance dataset (4 categories)
- `data/processed/retail_bi.db` — SQLite relational database storing transactional data
- `docs/executive_business_report.md` — comprehensive executive report and strategic recommendation narrative
- `docs/power_bi_dashboard_documentation.md` — DAX taxonomy, page architecture, and KPI reconciliation matrix
- `docs/sql_reconciliation_and_results.md` — validation logs confirming cross-engine consistency
- `presentation/executive_presentation.md` — C-suite presentation narrative and deck structure

## 3. Actual repository structure

```
Retail-Customer-Product-Intelligence/
├── assets/
│   ├── eda_plots/
│   └── phase4_charts/
├── data/
│   └── processed/
│       ├── category_intelligence.csv
│       ├── customer_intelligence.csv
│       ├── customer_shopping_behavior_cleaned.csv
│       ├── product_intelligence.csv
│       └── retail_bi.db
├── docs/
│   ├── executive_business_report.md
│   ├── power_bi_dashboard_documentation.md
│   └── sql_reconciliation_and_results.md
├── presentation/
│   └── executive_presentation.md
├── build_powerbi_dashboard.py
├── customer_behavior_dashboard.pbix
├── customer_behavior_sql_queries.sql
├── customer_shopping_behavior.csv
├── Customer_Shopping_Behavior_Analysis.ipynb
├── generate_phase1_notebook.py
├── generate_phase4_assets.py
├── run_sql_analysis.py
├── README.md
├── CONTEXT.md
└── LICENSE
```

## 4. Business problem and analytical framing

The repository addresses commercial challenges common in omnichannel and retail organizations:

- **Customer Value & Engagement**: Identifying revenue concentration across customer cohorts and evaluating the relationship between purchase frequency and basket size.
- **Subscription Program Adoption**: Measuring baseline subscription rates and pinpointing high-value non-subscribers for targeted conversion campaigns.
- **Category & Product Merchandising**: Evaluating top-line revenue concentration across categories and identifying operational quality risks in high-volume SKUs.
- **Promotional Mix Evaluation**: Measuring discount penetration across categories and evaluating basket size parity between discounted and full-price orders.
- **Seasonal Demand Patterns**: Capturing category-specific demand fluctuations across seasons to optimize inventory procurement and promotional timing.

## 5. Data model and dataset characteristics

The underlying data is a retail customer shopping snapshot dataset consisting of:

- **Total records**: 3,900
- **Unique customers**: 3,900 (one transaction record per customer ID; snapshot granularity with recorded historical purchase count)
- **Product categories**: 4 (`Clothing`, `Accessories`, `Footwear`, `Outerwear`)
- **Distinct products analyzed**: 25
- **Total recorded revenue**: $233,081
- **Domain**: Retail customer behavior, merchandising, and commercial intelligence
- **Time context**: Seasonal indicators are present (`Spring`, `Summer`, `Fall`, `Winter`), but no arbitrary date/timestamp series exists.

### Primary Fields in the Cleaned Dataset
- `customer_id` (Primary Key)
- `age`
- `gender`
- `item_purchased`
- `category`
- `purchase_amount_usd`
- `location`
- `size`
- `color`
- `season`
- `review_rating` (median imputed by category)
- `subscription_status` (`Yes` / `No`)
- `shipping_type`
- `discount_applied` (`Yes` / `No`)
- `previous_purchases` (recorded historical purchase count)
- `payment_method`
- `frequency_of_purchases` (standardized frequency label)
- `frequency_of_purchases_raw` (original raw survey label)
- `age_group` (engineered demographic cohort)
- `purchase_frequency_days` (numerical mapping of frequency)
- `customer_value_tier` (spend-based tier)
- `engagement_tier` (historical loyalty tier)
- `value_engagement_segment` (synthesized 3x3 matrix segment)

## 6. Python data cleaning & feature engineering layer

The Python data layer (`generate_phase1_notebook.py` and canonical processing scripts) handles data hygiene and creates the analytical dimensions:

### Cleaning Actions
- **Standardization**: Converted all column names to standard `snake_case`.
- **Missing Value Imputation**: Imputed missing `review_rating` values using category-specific medians (e.g., Clothing: 3.7, Accessories: 3.8, Footwear: 3.7, Outerwear: 3.65).
- **Redundancy Elimination**: Dropped `promo_code_used` because it was 100% collinear with `discount_applied`.
- **Label Harmonization**: Unified frequency labels (e.g., `Fortnightly` → `Bi-Weekly`, `Every 3 Months` → `Quarterly`).

### Engineered Features
- **Age Group**:
  - `18-30 (Young Adult)`
  - `31-45 (Adult)`
  - `46-60 (Middle-Aged)`
  - `61-70 (Senior)`
- **Purchase Frequency Days**:
  - `Weekly` = 7 days
  - `Bi-Weekly` = 14 days
  - `Monthly` = 30 days
  - `Quarterly` = 90 days
  - `Annually` = 365 days
- **Customer Value Tier**:
  - `Low Value`: Spend < $40
  - `Medium Value`: Spend $40 to $75
  - `High Value`: Spend > $75
- **Engagement Tier**:
  - `Low Engagement`: Previous purchases ≤ 15
  - `Medium Engagement`: Previous purchases 16 to 35
  - `High Engagement`: Previous purchases > 35
- **Value-Engagement Segment**:
  - Synthesized 3x3 matrix combining Value Tier and Engagement Tier (9 discrete segments, e.g., `High Value - High Engagement`, `Medium Value - Low Engagement`).

## 7. Descriptive analysis vs. customer intelligence

The project maintains a clear distinction across its analytical tiers:

1. **Descriptive Statistics**: Top-line aggregations, demographic distributions (67.7% male / 32.3% female revenue split; $59.54 vs $60.25 AOV parity), rating spreads, and payment/shipping frequencies.
2. **Customer Intelligence**: Multi-dimensional behavioral analysis combining spend tiers with historical engagement, evaluating subscription rates across cohorts, and mapping high-value customer clusters.
3. **Product & Category Intelligence**: SKU revenue rankings (Blouse #1 with $10,410 across 171 orders; Shirt #2 with $10,332), category concentration (76.56% in Clothing + Accessories), and satisfaction rating variances.

## 8. Relational BI query engine (SQLite + SQL)

The SQL layer (`customer_behavior_sql_queries.sql` executed via `run_sql_analysis.py` against `data/processed/retail_bi.db`) acts as the structured business analytics engine. 

**Important Architectural Role**: SQL produces the quantitative business analysis and pattern extractions; it does **not** generate subjective recommendations on its own. Analysts and business stakeholders interpret the SQL query results into actionable commercial recommendations.

The 14 SQL business intelligence queries cover four core domains:

### Customer Intelligence
- `Q1`: Customer Value-Engagement Segment Revenue Contribution
- `Q2`: Demographic Revenue Drivers Across Age Group & Gender
- `Q3`: Engagement Tier Volume vs Spend Analysis
- `Q4`: Subscription Status Distribution Across Customer Value Tiers

### Product Intelligence
- `Q5`: Category Commercial Performance Matrix & Revenue Ranking
- `Q6`: Top 10 Revenue-Generating Products
- `Q7`: Product Satisfaction Extremes (Top 5 vs Bottom 5 Rated SKUs)
- `Q8`: Category Revenue Distribution Across Customer Value Tiers

### Commercial Intelligence
- `Q9`: Promotional Impact on Order Value (Full-Price vs Discounted AOV)
- `Q10`: Shipping Channel Monetization and Subscriber Adoption
- `Q11`: Payment Method Revenue Contribution & Basket Sizes
- `Q12`: Seasonal Category Demand Pattern Matrix

### Strategic Opportunity Cohorts
- `Q13`: High-Value Non-Subscriber Target Cohort (431 Customers)
- `Q14`: Value-Oriented Merchandising Opportunities

## 9. Cross-engine validation & reconciliation

To guarantee 100% data fidelity, every key enterprise KPI was audited across Python (Pandas), SQLite (SQL), and Power BI (DAX). All 13 core audit checks achieved **exact 100% agreement with $0.00 variance**:

| # | KPI Dimension | Python Baseline | SQL Engine | Power BI DAX | Audit Status |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **1** | Total Recorded Revenue | $233,081 | $233,081 | $233,081 | **EXACT MATCH** |
| **2** | Transaction Volume | 3,900 orders | 3,900 orders | 3,900 orders | **EXACT MATCH** |
| **3** | Unique Customer Count | 3,900 customers | 3,900 customers | 3,900 customers | **EXACT MATCH** |
| **4** | Clothing Category Revenue | $104,264 | $104,264 | $104,264 | **EXACT MATCH** |
| **5** | Accessories Category Revenue | $74,200 | $74,200 | $74,200 | **EXACT MATCH** |
| **6** | Footwear Category Revenue | $36,093 | $36,093 | $36,093 | **EXACT MATCH** |
| **7** | Outerwear Category Revenue | $18,524 | $18,524 | $18,524 | **EXACT MATCH** |
| **8** | Subscriber Volume | 1,053 | 1,053 | 1,053 | **EXACT MATCH** |
| **9** | Non-Subscriber Volume | 2,847 | 2,847 | 2,847 | **EXACT MATCH** |
| **10** | Discounted Orders | 1,677 | 1,677 | 1,677 | **EXACT MATCH** |
| **11** | Full-Price Orders | 2,223 | 2,223 | 2,223 | **EXACT MATCH** |
| **12** | Top Product Revenue (Blouse) | $10,410 | $10,410 | $10,410 | **EXACT MATCH** |
| **13** | Target Non-Subscriber Cohort | 431 | 431 | 431 | **EXACT MATCH** |

## 10. Completed Power BI interactive dashboard

The final Power BI dashboard is completed, fully configured, and saved as `customer_behavior_dashboard.pbix`. It provides an executive-grade interactive analytical interface organized across 4 dedicated pages:

### Page 1 — Executive Overview
- **Core KPI Cards**:
  - `Total Revenue`: $233,081
  - `Total Transactions`: 3,900
  - `Unique Customers`: 3,900
  - `Average Purchase Amount`: $59.76
  - `Subscriber Rate`: 27.0%
  - `Discount Penetration`: 43.0%
- **Analytical Visuals**:
  - `Revenue by Product Category` (Clustered Bar Chart: Clothing $104.3K, Accessories $74.2K, Footwear $36.1K, Outerwear $18.5K)
  - `Top 10 Products by Total Revenue` (Horizontal Bar Chart: Blouse $10.4K to Shorts $9.4K)
  - `Revenue by Value-Engagement Segment` (Clustered Bar Chart across all 9 segments)
  - `Subscription Status Share` (Donut Chart: 1,053 Subscribed / 2,847 Non-Subscribed)
  - `Discounted vs Full-Price Revenue` (Column Chart: $133.7K Full-Price / $99.4K Discounted)
- **Executive Insights Panel**: High-level synthesis of category concentration (76.56% in top 2 categories) and value tier distribution.

### Page 2 — Customer Intelligence
- **Analytical Visuals**:
  - `Revenue by Value-Engagement Segment` (Bar Chart)
  - `Customer Count by Segment` (Column Chart)
  - `AOV by Segment` (Bar Chart)
  - `Subscription Rate by Segment` (Bar Chart)
  - `Revenue Contribution by Age Group` (Column Chart)
  - `Revenue Distribution by Gender` (Donut Chart: 67.7% Male / 32.3% Female)
- **Interactive Slicers**:
  - `Age Group`
  - `Gender`
  - `Subscription Status`
  - `Customer Value Tier`
  - `Engagement Tier`
- **Analytical Summary Panel**: Highlights demographic volume representation vs. basket size parity ($59.54 Male vs. $60.25 Female).

### Page 3 — Product Intelligence
- **Analytical Visuals**:
  - `Total Revenue by Category` (Bar Chart)
  - `Transaction Volume by Category` (Column Chart)
  - `Top 10 Products by Total Revenue` (Horizontal Bar Chart)
  - `Product Satisfaction / Highest-Rated Product Analysis` (Grouped Column Chart: Top-rated Gloves 3.86 vs Lowest-rated Shirt 3.62)
  - `Discount Penetration Rate by Category` (Bar Chart)
  - `Category Revenue Distribution across Value Tiers` (Stacked Column Chart)
- **Interactive Slicers**:
  - `Category`
  - `Customer Value Tier`
- **Product Insights Panel**: Highlights catalog ratings variance and high-volume SKU satisfaction risks.

### Page 4 — Commercial Opportunities
- **Target Cohort KPI Card**:
  - `High-Value Non-Subscriber Target Cohort`: **431 Customers**
- **Analytical Visuals**:
  - `Full-Price AOV vs Discounted AOV` (Comparison Bar Chart: $60.13 Full-Price vs $59.28 Discounted)
  - `Category Revenue vs Discount Dependency Comparison` (Scatter/Matrix Chart)
  - `Seasonal Category Demand Pattern` (Grouped Column Chart showing Spring/Winter Clothing peaks and Fall/Summer Accessories peaks)
- **Interactive Slicers**:
  - `Season`
  - `Discount Applied`
- **Evidence-Based Commercial Recommendations Panel**: Narrative panel detailing the 5 core strategic recommendations.

---

### Key DAX Cohort Definition
The **431 High-Value Non-Subscriber Target Cohort** is calculated strictly using the project's canonical DAX measure:

```dax
High-Value Non-Subscriber Opportunity Cohort = 
CALCULATE(
    COUNT(customer_shopping_behavior_cleaned[customer_id]),
    customer_shopping_behavior_cleaned[subscription_status] = "No",
    customer_shopping_behavior_cleaned[previous_purchases] > 25,
    customer_shopping_behavior_cleaned[purchase_amount_usd] > 75
)
```

This criteria filters for proven repeat shoppers (`previous_purchases > 25`) with above-average current transaction spend (`purchase_amount_usd > 75`) who have not yet enrolled in the subscription program (`subscription_status = "No"`).

## 11. Final evidence-based commercial recommendations

Based on the quantitative patterns uncovered across Python, SQL, and Power BI layers, 5 strategic business recommendations were formulated:

1. **Target the 431 High-Value Non-Subscriber Customers for Subscription Conversion**: Deploy personalized onboarding campaigns offering exclusive benefits or loyalty tiers to convert these 431 proven repeat, high-spend shoppers into recurring subscribers.
2. **Review Outerwear's Discount Dependency**: Outerwear exhibits high discount penetration relative to its modest top-line contribution ($18,524; 7.95% share). Re-evaluate discounting depth to protect margin and prevent customer price conditioning.
3. **Prioritize Clothing and Accessories in Merchandising**: Together, Clothing ($104,264) and Accessories ($74,200) generate **76.56% ($178,464)** of total recorded revenue. Core merchandising, inventory allocation, and marketing budget should align with these two dominant categories.
4. **Review Lower-Rated Products with High Revenue Contribution**: Investigate customer feedback and return drivers for high-volume revenue generators that exhibit lower satisfaction ratings, specifically the **Shirt (3.62 rating, $10,332 revenue)** and **Blouse (3.68 rating, $10,410 revenue)**.
5. **Align Seasonal Inventory and Marketing with Recorded Demand Patterns**: Capitalize on observed seasonal category demand—specifically Clothing peaks in Spring and Winter, and Accessories strength in Fall and Summer—to optimize promotional calendars and procurement lead times.

## 12. Asset generation & presentation deliverables

In addition to the `.pbix` dashboard, `generate_phase4_assets.py` generates presentation deliverables:
- High-resolution analytical charts in `assets/phase4_charts/`
- 16:9 executive presentation slide deck in `presentation/`
- Formal business intelligence report in `docs/`

## 13. Technology stack

- **Languages & Libraries**: Python 3.13, Pandas, NumPy, Matplotlib, Seaborn, SQLite3
- **Query & Modeling Languages**: ANSI / PostgreSQL SQL, Power BI DAX
- **Business Intelligence**: Power BI Desktop, Microsoft Tabular Model, PBIX
- **Document & Presentation Engines**: Jupyter Notebook, python-pptx, reportlab, Markdown

### Explicitly Not Present / Out of Scope
- Web application frameworks (React, Angular, Vue, Next.js)
- Backend web API services (FastAPI, Flask, Django, Express)
- Cloud infrastructure / Kubernetes / Terraform
- Predictive ML / LLM serving pipelines (the project is strictly business intelligence and diagnostic analytics)

## 14. Project completion status

- **Analytical Pipeline**: Completed and verified.
- **SQL BI Engine**: Completed and reconciled.
- **Power BI Dashboard**: Completed with 4 interactive pages, formatted visuals, explicit DAX measures, interactive slicers, and executive insight panels.
- **PBIX File**: Completed, fully configured, and saved as `customer_behavior_dashboard.pbix`.
- **Readiness**: The project is 100% complete and ready for live demonstration, portfolio display, and interview presentation.

## 15. FINAL INTERVIEW-READY PROJECT FLOW

```
Raw Retail Data (3,900 Records)
  │
  ▼
Python Data Cleaning & Feature Engineering
(Imputation, Schema Standardization, Age/Value/Engagement Tiers)
  │
  ▼
Descriptive Analysis / Customer & Product Intelligence
(Top-Line Aggregations, Demographic Baselines, Rating Variances)
  │
  ▼
SQLite + SQL Business Analysis
(14 Relational BI Queries Extracting Transactional Patterns)
  │
  ▼
Reconciliation / Validation
(13/13 KPI Audit Matrix with 100% Exact Agreement & $0.00 Variance)
  │
  ▼
Power BI Interactive Dashboard
(4 Pages: Executive Overview, Customer Intel, Product Intel, Commercial Opps)
  │
  ▼
Business Insights
(Revenue Concentration, AOV Parity, Discount Dependency, Quality Signals)
  │
  ▼
Commercial Recommendations
(Target 431 Non-Subscribers, Review Outerwear Discounts, Focus on Top 2 Categories, Audit Shirt/Blouse Quality, Seasonal Inventory Alignment)
```
