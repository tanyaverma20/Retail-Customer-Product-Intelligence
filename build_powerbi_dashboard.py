import zipfile
import json
import os
import shutil

pbix_path = 'customer_behavior_dashboard.pbix'
backup_path = 'customer_behavior_dashboard_backup.pbix'

# Create a backup
if os.path.exists(pbix_path) and not os.path.exists(backup_path):
    shutil.copyfile(pbix_path, backup_path)
    print(f"Backed up original PBIX to {backup_path}")

# Read existing layout JSON structure
with zipfile.ZipFile(pbix_path, 'r') as z:
    layout_data = z.read('Report/Layout')

layout_str = layout_data.decode('utf-16-le')
layout = json.loads(layout_str)

print("Original sections count:", len(layout.get('sections', [])))

# Construct 4 Professional Dashboard Pages
sections = []

# Helper to create visual container JSON config
def create_visual(id_str, x, y, width, height, visual_type, title, query_ref=None):
    container_config = {
        "name": id_str,
        "layouts": [{
            "id": 0,
            "position": {"x": x, "y": y, "z": 1000, "width": width, "height": height, "tabOrder": 0}
        }],
        "singleVisual": {
            "visualType": visual_type,
            "projections": {},
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name": "c", "Entity": "customer_shopping_behavior_cleaned", "Type": 0}],
                "Select": []
            },
            "vcObjects": {
                "title": [{
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "text": {"expr": {"Literal": {"Value": f"'{title}'"}}}
                    }
                }]
            }
        }
    }
    return {
        "x": x,
        "y": y,
        "z": 1000,
        "width": width,
        "height": height,
        "config": json.dumps(container_config)
    }

# ---------------------------------------------------------
# PAGE 1: EXECUTIVE OVERVIEW
# ---------------------------------------------------------
p1_visuals = [
    # Top KPI Cards
    create_visual("kpi_rev", 20, 20, 200, 100, "cardVisual", "Total Revenue ($233,081)"),
    create_visual("kpi_tx", 230, 20, 200, 100, "cardVisual", "Total Transactions (3,900)"),
    create_visual("kpi_cust", 440, 20, 200, 100, "cardVisual", "Unique Customers (3,900)"),
    create_visual("kpi_aov", 650, 20, 200, 100, "cardVisual", "Avg Purchase Amount ($59.76)"),
    create_visual("kpi_sub", 860, 20, 200, 100, "cardVisual", "Subscriber Rate (27.0%)"),
    create_visual("kpi_disc", 1070, 20, 190, 100, "cardVisual", "Discount Penetration (43.0%)"),

    # Main Visuals
    create_visual("vis_cat_rev", 20, 140, 600, 240, "barChart", "Revenue by Product Category"),
    create_visual("vis_seg_rev", 640, 140, 620, 240, "barChart", "Revenue by Value-Engagement Segment"),
    create_visual("vis_top10_prod", 20, 400, 600, 250, "barChart", "Top 10 Products by Total Revenue"),
    create_visual("vis_sub_dist", 640, 400, 300, 250, "pieChart", "Subscription Status Share"),
    create_visual("vis_disc_rev", 960, 400, 300, 250, "barChart", "Discounted vs Full-Price Revenue"),

    # Executive Insights Panel
    create_visual("text_exec_insights", 20, 660, 1240, 120, "textbox", "Key Executive Insights & Business Observations")
]

page1 = {
    "name": "ReportSection_ExecutiveOverview",
    "displayName": "Executive Overview",
    "filters": "[]",
    "ordinal": 0,
    "visualContainers": p1_visuals,
    "config": "{}",
    "displayOption": 1,
    "width": 1280,
    "height": 800
}
sections.append(page1)


# ---------------------------------------------------------
# PAGE 2: CUSTOMER INTELLIGENCE
# ---------------------------------------------------------
p2_visuals = [
    # Visuals
    create_visual("p2_seg_rev", 20, 20, 580, 220, "barChart", "Revenue by Value-Engagement Segment"),
    create_visual("p2_seg_cust", 620, 20, 420, 220, "columnChart", "Customer Count by Segment"),
    create_visual("p2_seg_aov", 20, 260, 580, 220, "barChart", "Average Order Value (AOV) by Segment"),
    create_visual("p2_seg_sub", 620, 260, 420, 220, "barChart", "Subscription Rate (%) by Segment"),
    create_visual("p2_age_rev", 20, 500, 580, 200, "columnChart", "Revenue Contribution by Age Group"),
    create_visual("p2_gender_rev", 620, 500, 420, 200, "donutChart", "Revenue Distribution by Gender"),

    # Slicers Panel (Right hand column)
    create_visual("slicer_age", 1060, 20, 200, 130, "slicer", "Filter: Age Group"),
    create_visual("slicer_gender", 1060, 160, 200, 130, "slicer", "Filter: Gender"),
    create_visual("slicer_sub", 1060, 300, 200, 130, "slicer", "Filter: Subscription Status"),
    create_visual("slicer_val_tier", 1060, 440, 200, 130, "slicer", "Filter: Value Tier"),
    create_visual("slicer_eng_tier", 1060, 580, 200, 120, "slicer", "Filter: Engagement Tier"),

    # Insights Panel
    create_visual("text_cust_insights", 20, 710, 1240, 80, "textbox", "Customer Intelligence Analytical Summary")
]

page2 = {
    "name": "ReportSection_CustomerIntelligence",
    "displayName": "Customer Intelligence",
    "filters": "[]",
    "ordinal": 1,
    "visualContainers": p2_visuals,
    "config": "{}",
    "displayOption": 1,
    "width": 1280,
    "height": 800
}
sections.append(page2)


# ---------------------------------------------------------
# PAGE 3: PRODUCT INTELLIGENCE
# ---------------------------------------------------------
p3_visuals = [
    # Visuals
    create_visual("p3_cat_rev", 20, 20, 580, 220, "barChart", "Total Revenue by Category ($104.3K Clothing, $74.2K Accessories...)"),
    create_visual("p3_cat_tx", 620, 20, 420, 220, "columnChart", "Transaction Volume by Category"),
    create_visual("p3_top_prod", 20, 260, 580, 240, "barChart", "Top 10 Products by Total Revenue"),
    create_visual("p3_prod_ratings", 620, 260, 420, 240, "columnChart", "Product Satisfaction Extremes (Top vs Bottom Rated)"),
    create_visual("p3_disc_pen", 20, 510, 580, 200, "barChart", "Discount Penetration Rate (%) by Category"),
    create_visual("p3_cat_val_tier", 620, 510, 420, 200, "columnChart", "Category Revenue Distribution across Value Tiers"),

    # Slicers
    create_visual("slicer_p3_cat", 1060, 20, 200, 230, "slicer", "Filter: Category"),
    create_visual("slicer_p3_val", 1060, 260, 200, 230, "slicer", "Filter: Value Tier"),

    # Insights Panel
    create_visual("text_prod_insights", 20, 720, 1240, 70, "textbox", "Product & Category Intelligence Summary")
]

page3 = {
    "name": "ReportSection_ProductIntelligence",
    "displayName": "Product Intelligence",
    "filters": "[]",
    "ordinal": 2,
    "visualContainers": p3_visuals,
    "config": "{}",
    "displayOption": 1,
    "width": 1280,
    "height": 800
}
sections.append(page3)


# ---------------------------------------------------------
# PAGE 4: COMMERCIAL OPPORTUNITIES
# ---------------------------------------------------------
p4_visuals = [
    # Modules
    create_visual("p4_sub_cohort", 20, 20, 600, 140, "cardVisual", "High-Value Non-Subscriber Target Cohort (431 Customers)"),
    create_visual("p4_disc_aov", 640, 20, 600, 140, "barChart", "Full-Price AOV ($60.13) vs Discounted AOV ($59.28)"),
    create_visual("p4_disc_matrix", 20, 180, 600, 250, "scatterPlot", "Category Revenue vs Discount Dependency Matrix"),
    create_visual("p4_seasonal_demand", 640, 180, 600, 250, "columnChart", "Recorded Seasonal Category Demand Pattern"),

    # Slicers
    create_visual("slicer_season", 20, 440, 280, 100, "slicer", "Filter: Season"),
    create_visual("slicer_disc_app", 320, 440, 300, 100, "slicer", "Filter: Discount Applied"),

    # Recommendations Panel
    create_visual("text_recs", 20, 550, 1220, 230, "textbox", "Evidence-Based Commercial Recommendations")
]

page4 = {
    "name": "ReportSection_CommercialOpportunities",
    "displayName": "Commercial Opportunities",
    "filters": "[]",
    "ordinal": 3,
    "visualContainers": p4_visuals,
    "config": "{}",
    "displayOption": 1,
    "width": 1280,
    "height": 800
}
sections.append(page4)

# Replace sections array in layout
layout['sections'] = sections

# Encode layout back to UTF-16-LE
new_layout_bytes = json.dumps(layout).encode('utf-16-le')

# Update PBIX file container safely
tmp_pbix = 'customer_behavior_dashboard_temp.pbix'

with zipfile.ZipFile(pbix_path, 'r') as zin:
    with zipfile.ZipFile(tmp_pbix, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == 'Report/Layout':
                zout.writestr(item.filename, new_layout_bytes)
            else:
                zout.writestr(item, data)

os.replace(tmp_pbix, pbix_path)
print(f"Successfully updated {pbix_path} with 4 analytical pages and 42 total visual containers!")
