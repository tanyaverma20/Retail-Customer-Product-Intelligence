"""
Phase 4 Asset Generator
Retail Customer & Product Intelligence
Author: Tanya Verma

Generates:
1. High-resolution chart graphics in assets/phase4_charts/
2. 12-slide executive presentation in presentation/retail_customer_product_intelligence.pptx
3. Publication-grade PDF report in docs/executive_business_report.pdf
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "customer_shopping_behavior_cleaned.csv")
CHARTS_DIR = os.path.join(BASE_DIR, "assets", "phase4_charts")
PPTX_PATH = os.path.join(BASE_DIR, "presentation", "retail_customer_product_intelligence.pptx")
PDF_PATH = os.path.join(BASE_DIR, "docs", "executive_business_report.pdf")

os.makedirs(CHARTS_DIR, exist_ok=True)
os.makedirs(os.path.dirname(PPTX_PATH), exist_ok=True)
os.makedirs(os.path.dirname(PDF_PATH), exist_ok=True)

# Set matplotlib style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']

# Corporate Palette
COLOR_NAVY = '#1E293B'
COLOR_SLATE = '#475569'
COLOR_TEAL = '#0EA5E9'
COLOR_LIGHT_BG = '#F8FAFC'
COLOR_ACCENT = '#38BDF8'
COLOR_CORAL = '#E11D48'
COLOR_GREEN = '#10B981'
COLOR_AMBER = '#F59E0B'
COLOR_CARD_BORDER = '#E2E8F0'

def load_data():
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        return df
    else:
        raise FileNotFoundError(f"Data file not found at {DATA_PATH}")

def generate_charts(df):
    print("Generating high-resolution charts for Phase 4...")
    
    # 1. Category Revenue Chart
    cat_df = df.groupby('category')['purchase_amount_usd'].sum().reset_index()
    cat_df = cat_df.sort_values(by='purchase_amount_usd', ascending=False)
    
    fig, ax = plt.subplots(figsize=(7, 4.2), dpi=300)
    bars = ax.bar(cat_df['category'], cat_df['purchase_amount_usd'], color=['#0EA5E9', '#0284C7', '#38BDF8', '#7DD3FC'], width=0.55)
    ax.set_title('Recorded Revenue by Product Category ($USD)', fontsize=13, fontweight='bold', color=COLOR_NAVY, pad=15)
    ax.set_ylabel('Recorded Revenue ($)', fontsize=10, color=COLOR_SLATE)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)
    
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'${height:,.0f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9.5, fontweight='bold', color=COLOR_NAVY)
    
    ax.set_ylim(0, 120000)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "category_revenue.png"), bbox_inches='tight')
    plt.close()

    # 2. Value-Engagement Segment Revenue Chart
    seg_df = df.groupby('value_engagement_segment')['purchase_amount_usd'].sum().reset_index()
    seg_df = seg_df.sort_values(by='purchase_amount_usd', ascending=True)
    
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=300)
    bars = ax.barh(seg_df['value_engagement_segment'], seg_df['purchase_amount_usd'], color='#0EA5E9', height=0.6)
    ax.set_title('Recorded Revenue by Value-Engagement Segment ($USD)', fontsize=13, fontweight='bold', color=COLOR_NAVY, pad=15)
    ax.set_xlabel('Recorded Revenue ($)', fontsize=10, color=COLOR_SLATE)
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)
    
    for bar in bars:
        width = bar.get_width()
        ax.annotate(f'${width:,.0f}',
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0), textcoords="offset points",
                    ha='left', va='center', fontsize=8.5, fontweight='bold', color=COLOR_NAVY)
        
    ax.set_xlim(0, 48000)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "segment_revenue.png"), bbox_inches='tight')
    plt.close()

    # 3. Subscription Status Donut
    sub_df = df['subscription_status'].value_counts()
    
    fig, ax = plt.subplots(figsize=(5, 4.2), dpi=300)
    colors_pie = ['#CBD5E1', '#0EA5E9']
    wedges, texts, autotexts = ax.pie(sub_df, labels=['Non-Subscribers\n(2,847)', 'Subscribers\n(1,053)'], 
                                      autopct='%1.1f%%', startangle=140, colors=colors_pie,
                                      pctdistance=0.75, textprops=dict(color=COLOR_NAVY, fontsize=9.5, fontweight='bold'))
    centre_circle = plt.Circle((0,0), 0.55, fc='white')
    fig.gca().add_artist(centre_circle)
    ax.set_title('Subscription Adoption Share', fontsize=13, fontweight='bold', color=COLOR_NAVY, pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "subscription_status.png"), bbox_inches='tight')
    plt.close()

    # 4. Full-Price vs Discounted AOV Comparison
    disc_aov = df.groupby('discount_applied')['purchase_amount_usd'].mean().reset_index()
    
    fig, ax = plt.subplots(figsize=(6, 4.2), dpi=300)
    bars = ax.bar(['Full-Price Orders\n($133,670 / 2,223 orders)', 'Discounted Orders\n($99,411 / 1,677 orders)'], 
                  disc_aov['purchase_amount_usd'], color=['#0284C7', '#F59E0B'], width=0.45)
    ax.set_title('Average Order Value (AOV) by Discount Application', fontsize=12, fontweight='bold', color=COLOR_NAVY, pad=15)
    ax.set_ylabel('Average Order Value ($)', fontsize=10, color=COLOR_SLATE)
    ax.set_ylim(0, 75)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)
    
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'${height:.2f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4), textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, fontweight='bold', color=COLOR_NAVY)
        
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "discount_aov.png"), bbox_inches='tight')
    plt.close()

    # 5. Top 10 Products by Revenue
    top_p = df.groupby(['item_purchased', 'category'])['purchase_amount_usd'].sum().reset_index()
    top_p = top_p.sort_values(by='purchase_amount_usd', ascending=True).tail(10)
    
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=300)
    bars = ax.barh(top_p['item_purchased'], top_p['purchase_amount_usd'], color='#0284C7', height=0.6)
    ax.set_title('Top 10 Products by Recorded Revenue ($USD)', fontsize=13, fontweight='bold', color=COLOR_NAVY, pad=15)
    ax.set_xlabel('Recorded Revenue ($)', fontsize=10, color=COLOR_SLATE)
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)
    
    for bar in bars:
        width = bar.get_width()
        ax.annotate(f'${width:,.0f}',
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0), textcoords="offset points",
                    ha='left', va='center', fontsize=8.5, fontweight='bold', color=COLOR_NAVY)
        
    ax.set_xlim(0, 12000)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "top_products.png"), bbox_inches='tight')
    plt.close()

    # 6. Product Revenue vs Review Rating Scatter/Bubble
    p_agg = df.groupby('item_purchased').agg({
        'purchase_amount_usd': 'sum',
        'review_rating': 'mean',
        'customer_id': 'count'
    }).reset_index()
    
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    scatter = ax.scatter(p_agg['review_rating'], p_agg['purchase_amount_usd'], 
                         s=p_agg['customer_id']*1.8, color='#0EA5E9', alpha=0.7, edgecolors=COLOR_NAVY, linewidth=1)
    
    ax.set_title('Product Recorded Revenue vs. Average Review Rating', fontsize=12, fontweight='bold', color=COLOR_NAVY, pad=15)
    ax.set_xlabel('Average Review Rating (out of 5.0)', fontsize=10, color=COLOR_SLATE)
    ax.set_ylabel('Recorded Revenue ($)', fontsize=10, color=COLOR_SLATE)
    ax.grid(True, linestyle='--', alpha=0.5)
    
    # Highlight specific items
    shirt = p_agg[p_agg['item_purchased']=='Shirt'].iloc[0]
    blouse = p_agg[p_agg['item_purchased']=='Blouse'].iloc[0]
    gloves = p_agg[p_agg['item_purchased']=='Gloves'].iloc[0]
    
    ax.annotate(f"Shirt ($10.3K, {shirt['review_rating']:.2f})", xy=(shirt['review_rating'], shirt['purchase_amount_usd']),
                xytext=(-60, -25), textcoords='offset points',
                arrowprops=dict(arrowstyle='->', color=COLOR_CORAL, lw=1.2),
                fontsize=8.5, fontweight='bold', color=COLOR_CORAL)
                
    ax.annotate(f"Blouse ($10.4K, {blouse['review_rating']:.2f})", xy=(blouse['review_rating'], blouse['purchase_amount_usd']),
                xytext=(10, 10), textcoords='offset points',
                arrowprops=dict(arrowstyle='->', color=COLOR_NAVY, lw=1.2),
                fontsize=8.5, fontweight='bold', color=COLOR_NAVY)

    ax.annotate(f"Gloves ($9.3K, {gloves['review_rating']:.2f})", xy=(gloves['review_rating'], gloves['purchase_amount_usd']),
                xytext=(10, -15), textcoords='offset points',
                arrowprops=dict(arrowstyle='->', color=COLOR_GREEN, lw=1.2),
                fontsize=8.5, fontweight='bold', color=COLOR_GREEN)

    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "rating_vs_revenue.png"), bbox_inches='tight')
    plt.close()
    
    print("Charts generated successfully!")

# ----------------------------------------------------
# PPTX Generator
# ----------------------------------------------------

def add_header(slide, title_text, category_text="RETAIL CUSTOMER & PRODUCT INTELLIGENCE"):
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.8))
    tf = title_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p_cat = tf.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.size = Pt(9)
    p_cat.font.bold = True
    p_cat.font.color.rgb = RGBColor(14, 165, 233) # Teal
    
    p_title = tf.add_paragraph()
    p_title.text = title_text
    p_title.font.size = Pt(20)
    p_title.font.bold = True
    p_title.font.color.rgb = RGBColor(30, 41, 59) # Navy

def add_footer(slide, current_page, total_pages=12):
    footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.0), Inches(11.7), Inches(0.3))
    tf = footer_box.text_frame
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = f"Tanya Verma  |  Retail Customer & Product Intelligence Case Study  |  Slide {current_page} of {total_pages}"
    p.font.size = Pt(8.5)
    p.font.color.rgb = RGBColor(148, 163, 184)

def add_kpi_card(slide, left, top, width, height, value_text, label_text, sub_text=None, border_color=RGBColor(14, 165, 233)):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(248, 250, 252)
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1.5)
    
    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Inches(0.15)
    tf.margin_right = Inches(0.15)
    
    p_val = tf.paragraphs[0]
    p_val.text = value_text
    p_val.font.size = Pt(22)
    p_val.font.bold = True
    p_val.font.color.rgb = RGBColor(30, 41, 59)
    p_val.alignment = PP_ALIGN.CENTER
    
    p_lbl = tf.add_paragraph()
    p_lbl.text = label_text
    p_lbl.font.size = Pt(10)
    p_lbl.font.bold = True
    p_lbl.font.color.rgb = RGBColor(71, 85, 105)
    p_lbl.alignment = PP_ALIGN.CENTER
    
    if sub_text:
        p_sub = tf.add_paragraph()
        p_sub.text = sub_text
        p_sub.font.size = Pt(8.5)
        p_sub.font.color.rgb = RGBColor(148, 163, 184)
        p_sub.alignment = PP_ALIGN.CENTER

def build_pptx():
    print("Building 12-slide PowerPoint presentation...")
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]
    
    # ----------------------------------------------------
    # SLIDE 1: Title
    # ----------------------------------------------------
    slide1 = prs.slides.add_slide(blank_layout)
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = RGBColor(30, 41, 59) # Dark Navy
    bg1.line.fill.background()
    
    tbox1 = slide1.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(11.333), Inches(3.5))
    tf1 = tbox1.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "RETAIL CUSTOMER & PRODUCT INTELLIGENCE"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)
    
    p2 = tf1.add_paragraph()
    p2.text = "Customer, Product & Commercial Analytics Case Study"
    p2.font.size = Pt(18)
    p2.font.color.rgb = RGBColor(56, 189, 248) # Cyan accent
    
    p3 = tf1.add_paragraph()
    p3.text = "\nAuthor: Tanya Verma  |  GitHub: tanyaverma20/Retail-Customer-Product-Intelligence\nReconciliation: 100% Exact Agreement (13/13 Enterprise KPI Checks Reconciled)"
    p3.font.size = Pt(12)
    p3.font.color.rgb = RGBColor(203, 213, 225)
    
    # ----------------------------------------------------
    # SLIDE 2: Executive Summary
    # ----------------------------------------------------
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "Executive Summary: Top-Line Metrics & Key Findings")
    add_footer(slide2, 2)
    
    # KPI Cards (5)
    kpis = [
        ("3,900", "Unique Customers", "100% Snapshot Grain"),
        ("$233,081", "Recorded Revenue", "$59.76 Enterprise AOV"),
        ("25", "Retail Products", "4 Product Categories"),
        ("27.0%", "Subscriber Rate", "1,053 Active Subscribers"),
        ("43.0%", "Discount Penetration", "1,677 Discounted Orders")
    ]
    card_w = Inches(2.2)
    card_h = Inches(1.3)
    start_x = Inches(0.8)
    spacing = Inches(0.18)
    
    for idx, (val, lbl, sub) in enumerate(kpis):
        x = start_x + idx * (card_w + spacing)
        add_kpi_card(slide2, x, Inches(1.4), card_w, card_h, val, lbl, sub)
        
    # Takeaways Box
    shape_t = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(3.0), Inches(11.7), Inches(3.8))
    shape_t.fill.solid()
    shape_t.fill.fore_color.rgb = RGBColor(248, 250, 252)
    shape_t.line.color.rgb = RGBColor(226, 232, 240)
    
    tf_t = shape_t.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = Inches(0.3)
    tf_t.margin_top = Inches(0.3)
    
    pt = tf_t.paragraphs[0]
    pt.text = "CORE STRATEGIC TAKEAWAYS"
    pt.font.size = Pt(13)
    pt.font.bold = True
    pt.font.color.rgb = RGBColor(14, 165, 233)
    
    bullets = [
        "1. Heavy Revenue Concentration: Clothing ($104,264) and Accessories ($74,200) account for $178,464 or 76.56% of total recorded revenue.",
        "2. High-Value Non-Subscriber Opportunity: 431 high-value non-subscriber customers (>25 purchases, >$75 spend) identified as a prime potential subscription-targeting cohort.",
        "3. Promotional Mix & AOV Parity: 43.0% discount penetration. Full-price orders average $60.13 vs. $59.28 for discounted orders (an observed association in the snapshot dataset).",
        "4. Product Satisfaction Friction: Top revenue products show rating variance (Shirt $10,332 sales / 3.62 rating; Blouse $10,410 / 3.68 rating), signaling items requiring quality investigation."
    ]
    for b in bullets:
        pb = tf_t.add_paragraph()
        pb.text = b
        pb.font.size = Pt(11)
        pb.font.color.rgb = RGBColor(51, 65, 85)
        pb.space_before = Pt(8)

    # ----------------------------------------------------
    # SLIDE 3: Business Problem & Objectives
    # ----------------------------------------------------
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "Business Problem & Analytical Objectives")
    add_footer(slide3, 3)
    
    # Left narrative card
    s_left = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.4), Inches(4.2), Inches(5.4))
    s_left.fill.solid()
    s_left.fill.fore_color.rgb = RGBColor(30, 41, 59)
    s_left.line.fill.background()
    
    tf_l = s_left.text_frame
    tf_l.word_wrap = True
    tf_l.margin_left = tf_l.margin_top = Inches(0.3)
    
    p = tf_l.paragraphs[0]
    p.text = "THE ANALYTICAL OBJECTIVE"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = RGBColor(56, 189, 248)
    
    p_desc = tf_l.add_paragraph()
    p_desc.text = "\nConvert raw retail transaction records into evidence-based executive decision support.\n\nManagement requires visibility into customer value, engagement, subscription adoption, product concentration, and discount mechanics to prioritize strategic growth initiatives."
    p_desc.font.size = Pt(11)
    p_desc.font.color.rgb = RGBColor(241, 245, 249)
    
    # Right 5 Business Questions
    questions = [
        ("1. Customer Segmentation", "Who are the highest-value customers, and how does spending vary across value and engagement tiers?"),
        ("2. Category Priorities", "Which categories and products drive the vast majority of recorded enterprise revenue?"),
        ("3. Subscription Expansion", "Where are the strongest observable subscription targeting opportunities across customer cohorts?"),
        ("4. Promotional Review", "Where is discounting concentrated, and how does discount application associate with order values?"),
        ("5. Action Prioritization", "Which strategic initiatives should management prioritize for maximum commercial impact?")
    ]
    
    start_y = Inches(1.4)
    q_h = Inches(0.95)
    for idx, (q_title, q_body) in enumerate(questions):
        y = start_y + idx * (q_h + Inches(0.16))
        sq = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.2), y, Inches(7.3), q_h)
        sq.fill.solid()
        sq.fill.fore_color.rgb = RGBColor(248, 250, 252)
        sq.line.color.rgb = RGBColor(226, 232, 240)
        
        tf_q = sq.text_frame
        tf_q.word_wrap = True
        tf_q.margin_left = Inches(0.2)
        tf_q.margin_top = Inches(0.12)
        
        pq1 = tf_q.paragraphs[0]
        pq1.text = q_title
        pq1.font.size = Pt(11)
        pq1.font.bold = True
        pq1.font.color.rgb = RGBColor(14, 165, 233)
        
        pq2 = tf_q.add_paragraph()
        pq2.text = q_body
        pq2.font.size = Pt(9.5)
        pq2.font.color.rgb = RGBColor(51, 65, 85)

    # ----------------------------------------------------
    # SLIDE 4: Analytical Architecture
    # ----------------------------------------------------
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "End-to-End Analytical Architecture & Data Pipeline")
    add_footer(slide4, 4)
    
    arch_steps = [
        ("Python Analytics", "Data Cleaning & EDA", "Feature engineering, value/engagement tiers, schema validation.", RGBColor(14, 165, 233)),
        ("SQL BI Engine", "Relational Analytics", "SQLite DB, 14 analytical queries, multi-table joins.", RGBColor(2, 132, 199)),
        ("Power BI Dashboard", "Dynamic DAX Suite", "15 DAX measures, 4 pages, 21 visuals, 11 interactive slicers.", RGBColor(56, 189, 248)),
        ("Decision Support", "Strategic Frameworks", "Evidence tables, 5 recommendations, decision governance.", RGBColor(16, 185, 129))
    ]
    
    card_w4 = Inches(2.7)
    card_h4 = Inches(3.8)
    for idx, (title, sub, body, col) in enumerate(arch_steps):
        x = Inches(0.8) + idx * (card_w4 + Inches(0.3))
        sa = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.5), card_w4, card_h4)
        sa.fill.solid()
        sa.fill.fore_color.rgb = RGBColor(248, 250, 252)
        sa.line.color.rgb = col
        sa.line.width = Pt(2)
        
        tfa = sa.text_frame
        tfa.word_wrap = True
        tfa.margin_left = Inches(0.2)
        tfa.margin_top = Inches(0.2)
        
        p1 = tfa.paragraphs[0]
        p1.text = f"LAYER {idx+1}"
        p1.font.size = Pt(9)
        p1.font.bold = True
        p1.font.color.rgb = col
        
        p2 = tfa.add_paragraph()
        p2.text = title
        p2.font.size = Pt(14)
        p2.font.bold = True
        p2.font.color.rgb = RGBColor(30, 41, 59)
        
        p3 = tfa.add_paragraph()
        p3.text = sub
        p3.font.size = Pt(10)
        p3.font.bold = True
        p3.font.color.rgb = RGBColor(71, 85, 105)
        
        p4 = tfa.add_paragraph()
        p4.text = f"\n{body}"
        p4.font.size = Pt(9.5)
        p4.font.color.rgb = RGBColor(100, 116, 139)

    # Bottom Trust Box
    s_trust = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.5), Inches(11.7), Inches(1.3))
    s_trust.fill.solid()
    s_trust.fill.fore_color.rgb = RGBColor(30, 41, 59)
    s_trust.line.fill.background()
    
    tft = s_trust.text_frame
    tft.word_wrap = True
    tft.margin_left = Inches(0.3)
    tft.margin_top = Inches(0.2)
    
    pt1 = tft.paragraphs[0]
    pt1.text = "100% EXACT DATA RECONCILIATION PASSED (13/13 ENTERPRISE CHECKS)"
    pt1.font.size = Pt(11)
    pt1.font.bold = True
    pt1.font.color.rgb = RGBColor(56, 189, 248)
    
    pt2 = tft.add_paragraph()
    pt2.text = "Zero discrepancy across Python, SQL, and Power BI DAX calculations ($233,081 recorded revenue, 3,900 unique customers, $104,264 Clothing revenue, 1,053 subscribers, 1,677 discounted orders)."
    pt2.font.size = Pt(9.5)
    pt2.font.color.rgb = RGBColor(241, 245, 249)

    # ----------------------------------------------------
    # SLIDE 5: Customer Intelligence
    # ----------------------------------------------------
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "Customer Intelligence & Value Segmentation Matrix")
    add_footer(slide5, 5)
    
    # Left Chart Image
    chart5_path = os.path.join(CHARTS_DIR, "segment_revenue.png")
    if os.path.exists(chart5_path):
        slide5.shapes.add_picture(chart5_path, Inches(0.8), Inches(1.4), width=Inches(6.2))
        
    # Right Callout Card for 431 Cohort
    s_c5 = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.2), Inches(1.4), Inches(5.3), Inches(5.4))
    s_c5.fill.solid()
    s_c5.fill.fore_color.rgb = RGBColor(248, 250, 252)
    s_c5.line.color.rgb = RGBColor(14, 165, 233)
    s_c5.line.width = Pt(2)
    
    tfc5 = s_c5.text_frame
    tfc5.word_wrap = True
    tfc5.margin_left = tfc5.margin_top = Inches(0.3)
    
    pc1 = tfc5.paragraphs[0]
    pc1.text = "KEY CUSTOMER COHORT FOCUS"
    pc1.font.size = Pt(11)
    pc1.font.bold = True
    pc1.font.color.rgb = RGBColor(14, 165, 233)
    
    pc2 = tfc5.add_paragraph()
    pc2.text = "431 High-Value Non-Subscribers"
    pc2.font.size = Pt(18)
    pc2.font.bold = True
    pc2.font.color.rgb = RGBColor(30, 41, 59)
    
    pc3 = tfc5.add_paragraph()
    pc3.text = "\nDefined as: Potential Subscription-Targeting Cohort\n\n" \
               "• Targeting Criteria: >25 previous purchases & >$75 current spend.\n" \
               "• Strategic Context: Represents highly engaged, high-spending shoppers currently purchasing outside the subscription program.\n" \
               "• Demographic Insight: Male revenue ($157,890 / 67.7%) vs. Female ($75,191 / 32.3%), with near-identical order value parity ($59.54 Male AOV vs. $60.25 Female AOV)."
    pc3.font.size = Pt(10)
    pc3.font.color.rgb = RGBColor(51, 65, 85)

    # ----------------------------------------------------
    # SLIDE 6: Product & Category Intelligence
    # ----------------------------------------------------
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "Product & Category Revenue Concentration")
    add_footer(slide6, 6)
    
    # Left Chart Image
    chart6_path = os.path.join(CHARTS_DIR, "category_revenue.png")
    if os.path.exists(chart6_path):
        slide6.shapes.add_picture(chart6_path, Inches(0.8), Inches(1.4), width=Inches(5.8))
        
    # Right Revenue Concentration Card
    s_c6 = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.4))
    s_c6.fill.solid()
    s_c6.fill.fore_color.rgb = RGBColor(248, 250, 252)
    s_c6.line.color.rgb = RGBColor(226, 232, 240)
    
    tfc6 = s_c6.text_frame
    tfc6.word_wrap = True
    tfc6.margin_left = tfc6.margin_top = Inches(0.3)
    
    p1 = tfc6.paragraphs[0]
    p1.text = "CATEGORY REVENUE CONCENTRATION"
    p1.font.size = Pt(11)
    p1.font.bold = True
    p1.font.color.rgb = RGBColor(14, 165, 233)
    
    p2 = tfc6.add_paragraph()
    p2.text = "76.56% of Recorded Revenue"
    p2.font.size = Pt(20)
    p2.font.bold = True
    p2.font.color.rgb = RGBColor(30, 41, 59)
    
    p3 = tfc6.add_paragraph()
    p3.text = "\nClothing ($104,264) + Accessories ($74,200) = $178,464\n\n" \
               "• Clothing: $104,264 (44.73% share | 1,737 orders | $60.03 AOV)\n" \
               "• Accessories: $74,200 (31.83% share | 1,240 orders | $59.84 AOV)\n" \
               "• Footwear: $36,093 (15.49% share | 599 orders | $60.26 AOV)\n" \
               "• Outerwear: $18,524 (7.95% share | 324 orders | $57.17 AOV)\n\n" \
               "Strategic Note: Interpreted strictly as revenue concentration, not profitability."
    p3.font.size = Pt(10)
    p3.font.color.rgb = RGBColor(51, 65, 85)

    # ----------------------------------------------------
    # SLIDE 7: Promotional Intelligence
    # ----------------------------------------------------
    slide7 = prs.slides.add_slide(blank_layout)
    add_header(slide7, "Promotional Mix & Observed Basket-Value Association")
    add_footer(slide7, 7)
    
    chart7_path = os.path.join(CHARTS_DIR, "discount_aov.png")
    if os.path.exists(chart7_path):
        slide7.shapes.add_picture(chart7_path, Inches(0.8), Inches(1.4), width=Inches(5.5))
        
    s_c7 = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.5), Inches(1.4), Inches(6.0), Inches(5.4))
    s_c7.fill.solid()
    s_c7.fill.fore_color.rgb = RGBColor(248, 250, 252)
    s_c7.line.color.rgb = RGBColor(245, 158, 11) # Amber border
    s_c7.line.width = Pt(1.5)
    
    tfc7 = s_c7.text_frame
    tfc7.word_wrap = True
    tfc7.margin_left = tfc7.margin_top = Inches(0.3)
    
    p1 = tfc7.paragraphs[0]
    p1.text = "PROMOTIONAL PENETRATION AUDIT"
    p1.font.size = Pt(11)
    p1.font.bold = True
    p1.font.color.rgb = RGBColor(245, 158, 11)
    
    p2 = tfc7.add_paragraph()
    p2.text = "43.0% Discount Penetration"
    p2.font.size = Pt(20)
    p2.font.bold = True
    p2.font.color.rgb = RGBColor(30, 41, 59)
    
    p3 = tfc7.add_paragraph()
    p3.text = "\n• Discounted Volume: 1,677 transactions ($99,411 recorded revenue).\n" \
               "• Full-Price Volume: 2,223 transactions ($133,670 recorded revenue).\n" \
               "• AOV Variance: Full-price order average is $60.13 vs. $59.28 for discounted orders (-$0.85 variance).\n\n" \
               "Analytical Rigor Rule: This represents an observed association in the available snapshot dataset — not a causal claim that discounts cause lower order values.\n\n" \
               "Management Implications: Flat promotional discounting does not correlate with expanded cart sizes, suggesting a shift toward spend-threshold promotional incentives."
    p3.font.size = Pt(10)
    p3.font.color.rgb = RGBColor(51, 65, 85)

    # ----------------------------------------------------
    # SLIDE 8: Product Quality Signals
    # ----------------------------------------------------
    slide8 = prs.slides.add_slide(blank_layout)
    add_header(slide8, "Product Quality Signals & Satisfaction Friction")
    add_footer(slide8, 8)
    
    chart8_path = os.path.join(CHARTS_DIR, "rating_vs_revenue.png")
    if os.path.exists(chart8_path):
        slide8.shapes.add_picture(chart8_path, Inches(0.8), Inches(1.4), width=Inches(6.2))
        
    s_c8 = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.2), Inches(1.4), Inches(5.3), Inches(5.4))
    s_c8.fill.solid()
    s_c8.fill.fore_color.rgb = RGBColor(248, 250, 252)
    s_c8.line.color.rgb = RGBColor(225, 29, 72) # Coral border
    s_c8.line.width = Pt(1.5)
    
    tfc8 = s_c8.text_frame
    tfc8.word_wrap = True
    tfc8.margin_left = tfc8.margin_top = Inches(0.3)
    
    p1 = tfc8.paragraphs[0]
    p1.text = "PRODUCTS REQUIRING QUALITY INVESTIGATION"
    p1.font.size = Pt(10)
    p1.font.bold = True
    p1.font.color.rgb = RGBColor(225, 29, 72)
    
    p2 = tfc8.add_paragraph()
    p2.text = "Satisfaction Friction on Top Sellers"
    p2.font.size = Pt(16)
    p2.font.bold = True
    p2.font.color.rgb = RGBColor(30, 41, 59)
    
    p3 = tfc8.add_paragraph()
    p3.text = "\n• Shirt ($10,332 Revenue | Rank #2): Lowest review rating in the entire 25-product catalog at 3.62 / 5.00.\n" \
               "• Blouse ($10,410 Revenue | Rank #1): Top revenue driver records a 3.68 / 5.00 average rating.\n" \
               "• Benchmark Items: Top-rated product is Gloves (3.86 / 5.00 rating | $9,276 revenue).\n\n" \
               "Actionable Framework: Top-selling products exhibiting lower ratings indicate quality friction (fabric durability, sizing accuracy, stitching) requiring immediate vendor audit."
    p3.font.size = Pt(9.5)
    p3.font.color.rgb = RGBColor(51, 65, 85)

    # ----------------------------------------------------
    # SLIDE 9: Commercial Opportunities
    # ----------------------------------------------------
    slide9 = prs.slides.add_slide(blank_layout)
    add_header(slide9, "Commercial Opportunities & Decision Modules")
    add_footer(slide9, 9)
    
    opps = [
        ("Subscription Conversion", "431 high-value non-subscriber cohort (>25 purchases, >$75 spend).", "Test targeted subscription onboarding offers and preview incentives.", RGBColor(14, 165, 233)),
        ("Category Prioritization", "76.56% of recorded revenue concentrated in Clothing & Accessories.", "Focus inventory depth and supplier negotiations on top 2 categories.", RGBColor(2, 132, 199)),
        ("Promotional Governance", "43% discount rate; Full-price AOV $60.13 vs Discounted $59.28.", "Shift to minimum spend threshold promotions (e.g., $15 off >$80).", RGBColor(245, 158, 11)),
        ("Product Quality Control", "Shirt ($10.3K sales, 3.62 rating) & Blouse ($10.4K, 3.68 rating) friction.", "Initiate vendor inspections, fabric checks, and sizing review.", RGBColor(225, 29, 72))
    ]
    
    w9 = Inches(5.7)
    h9 = Inches(2.5)
    coords = [(Inches(0.8), Inches(1.5)), (Inches(6.8), Inches(1.5)), (Inches(0.8), Inches(4.3)), (Inches(6.8), Inches(4.3))]
    
    for idx, (title, ev, act, col) in enumerate(opps):
        x, y = coords[idx]
        so = slide9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w9, h9)
        so.fill.solid()
        so.fill.fore_color.rgb = RGBColor(248, 250, 252)
        so.line.color.rgb = col
        so.line.width = Pt(1.5)
        
        tfo = so.text_frame
        tfo.word_wrap = True
        tfo.margin_left = Inches(0.2)
        tfo.margin_top = Inches(0.15)
        
        p1 = tfo.paragraphs[0]
        p1.text = f"OPPORTUNITY {idx+1}: {title.upper()}"
        p1.font.size = Pt(11)
        p1.font.bold = True
        p1.font.color.rgb = col
        
        p2 = tfo.add_paragraph()
        p2.text = f"Empirical Evidence: {ev}"
        p2.font.size = Pt(9.5)
        p2.font.bold = True
        p2.font.color.rgb = RGBColor(30, 41, 59)
        
        p3 = tfo.add_paragraph()
        p3.text = f"Recommended Action: {act}"
        p3.font.size = Pt(9.5)
        p3.font.color.rgb = RGBColor(71, 85, 105)

    # ----------------------------------------------------
    # SLIDE 10: Strategic Recommendations
    # ----------------------------------------------------
    slide10 = prs.slides.add_slide(blank_layout)
    add_header(slide10, "Strategic Recommendations for Executive Management")
    add_footer(slide10, 10)
    
    recs = [
        ("1. Target Subscription Conversion", "Execute targeted subscription onboarding pilots tailored to the 431 high-value non-subscriber cohort."),
        ("2. Prioritize Core Merchandising", "Focus inventory depth and supplier negotiation resources on Clothing and Accessories (76.56% revenue share)."),
        ("3. Restructure Promotional Incentives", "Transition from flat order discounts to spend-threshold rules to incentivize larger basket sizes."),
        ("4. Audit High-Volume Product Quality", "Initiate vendor inspections and quality audits on top-selling items receiving review ratings below 3.70."),
        ("5. Upgrade Data & Analytics Infrastructure", "Deploy timestamped transactional logging to enable future cohort retention, repeat purchase velocity, and true CLV analysis.")
    ]
    
    r_y = Inches(1.5)
    r_h = Inches(0.95)
    for idx, (title, body) in enumerate(recs):
        y = r_y + idx * (r_h + Inches(0.12))
        sr = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), y, Inches(11.7), r_h)
        sr.fill.solid()
        sr.fill.fore_color.rgb = RGBColor(248, 250, 252)
        sr.line.color.rgb = RGBColor(14, 165, 233)
        
        tfr = sr.text_frame
        tfr.word_wrap = True
        tfr.margin_left = Inches(0.25)
        tfr.margin_top = Inches(0.12)
        
        pr1 = tfr.paragraphs[0]
        pr1.text = title
        pr1.font.size = Pt(11)
        pr1.font.bold = True
        pr1.font.color.rgb = RGBColor(14, 165, 233)
        
        pr2 = tfr.add_paragraph()
        pr2.text = body
        pr2.font.size = Pt(10)
        pr2.font.color.rgb = RGBColor(51, 65, 85)

    # ----------------------------------------------------
    # SLIDE 11: Data Reconciliation & Trust
    # ----------------------------------------------------
    slide11 = prs.slides.add_slide(blank_layout)
    add_header(slide11, "Data Reconciliation & Enterprise Analytical Trust")
    add_footer(slide11, 11)
    
    # Reconciliation Table
    rows, cols = 8, 4
    table_shape = slide11.shapes.add_table(rows, cols, Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.2))
    table = table_shape.table
    
    headers = ["Analytical Metric Dimension", "Phase 1 Python", "Phase 2 SQL Result", "Phase 3 Power BI DAX"]
    data_rows = [
        ["Total Recorded Revenue", "$233,081", "$233,081", "$233,081"],
        ["Transaction Volume", "3,900 orders", "3,900 orders", "3,900 orders"],
        ["Unique Customers", "3,900 customers", "3,900 customers", "3,900 customers"],
        ["Clothing Category Revenue", "$104,264", "$104,264", "$104,264"],
        ["Accessories Category Revenue", "$74,200", "$74,200", "$74,200"],
        ["Active Subscriber Count", "1,053 subscribers", "1,053 subscribers", "1,053 subscribers"],
        ["Target Non-Subscriber Cohort", "431 customers", "431 customers", "431 customers"]
    ]
    
    for c_idx, h_text in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.text = h_text
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(30, 41, 59)
        p = cell.text_frame.paragraphs[0]
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)
        
    for r_idx, r_data in enumerate(data_rows):
        for c_idx, val_text in enumerate(r_data):
            cell = table.cell(r_idx + 1, c_idx)
            cell.text = val_text
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(248, 250, 252) if r_idx % 2 == 0 else RGBColor(255, 255, 255)
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(9.5)
            p.font.color.rgb = RGBColor(51, 65, 85)

    # ----------------------------------------------------
    # SLIDE 12: Executive Conclusion
    # ----------------------------------------------------
    slide12 = prs.slides.add_slide(blank_layout)
    bg12 = slide12.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg12.fill.solid()
    bg12.fill.fore_color.rgb = RGBColor(30, 41, 59)
    bg12.line.fill.background()
    
    tbox12 = slide12.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.333), Inches(4.5))
    tf12 = tbox12.text_frame
    tf12.word_wrap = True
    
    p = tf12.paragraphs[0]
    p.text = "FROM CUSTOMER DATA TO COMMERCIAL DECISIONS"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)
    
    p2 = tf12.add_paragraph()
    p2.text = "\nCustomer Intelligence + Product Intelligence + Business Intelligence = Executive Decision Support"
    p2.font.size = Pt(16)
    p2.font.color.rgb = RGBColor(56, 189, 248)
    
    p3 = tf12.add_paragraph()
    p3.text = "\n\n• Verified Baseline: 3,900 customers | $233,081 recorded revenue | 100% data reconciliation.\n" \
               "• Priority Action 1: Target conversion campaign for the 431 high-value non-subscriber cohort.\n" \
               "• Priority Action 2: Protect core merchandising in Clothing & Accessories (76.56% recorded revenue).\n" \
               "• Priority Action 3: Restructure promotional discounting to spend-threshold rules.\n" \
               "• Author: Tanya Verma  |  GitHub: tanyaverma20/Retail-Customer-Product-Intelligence"
    p3.font.size = Pt(12)
    p3.font.color.rgb = RGBColor(203, 213, 225)

    prs.save(PPTX_PATH)
    print(f"Presentation saved successfully to {PPTX_PATH}!")

# ----------------------------------------------------
# PDF Generator
# ----------------------------------------------------

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (on pages 2+)
        if self._pageNumber > 1:
            self.drawString(54, 750, "Retail Customer & Product Intelligence — Executive Business Report")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
        # Footer (all pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 32, page_text)
        self.drawString(54, 32, "Author: Tanya Verma | Retail Customer & Product Intelligence Case Study")
        self.restoreState()

def build_pdf():
    print("Building publication-grade PDF report...")
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=6
    )
    
    meta_style = ParagraphStyle(
        'MetaText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#475569'),
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor('#0EA5E9'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'ReportBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#334155'),
        leftIndent=12,
        spaceAfter=4
    )

    tbl_cell_header = ParagraphStyle(
        'TblCellHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=0
    )

    tbl_cell_body = ParagraphStyle(
        'TblCellBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#334155'),
        alignment=0
    )

    story = []
    
    # Title & Metadata
    story.append(Paragraph("Retail Customer & Product Intelligence", title_style))
    story.append(Paragraph("<b>Executive Business Consulting Report</b> &nbsp;|&nbsp; Author: Tanya Verma &nbsp;|&nbsp; GitHub: tanyaverma20/Retail-Customer-Product-Intelligence<br/><b>Reconciliation Status</b>: 13/13 Enterprise KPI Checks Reconciled (100% Exact Agreement)", meta_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0EA5E9'), spaceAfter=12))

    # Reads Markdown content and parses it into story elements cleanly
    md_file = os.path.join(BASE_DIR, "docs", "executive_business_report.md")
    if os.path.exists(md_file):
        with open(md_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        in_table = False
        table_data = []
        
        for line in lines:
            line_str = line.strip()
            
            # Skip Title / Meta rendered above
            if line_str.startswith("# Retail Customer & Product Intelligence") or line_str.startswith("**Author**"):
                continue
                
            if line_str.startswith("|"):
                in_table = True
                # Parse markdown table row
                cells = [c.strip() for c in line_str.split("|")[1:-1]]
                if len(cells) > 0 and not all(c.startswith(":") or c.startswith("-") for c in cells):
                    table_data.append(cells)
                continue
            else:
                if in_table and len(table_data) > 0:
                    # Render table
                    formatted_table = []
                    for r_idx, row in enumerate(table_data):
                        formatted_row = []
                        for c_idx, cell in enumerate(row):
                            style_use = tbl_cell_header if r_idx == 0 else tbl_cell_body
                            # Clean markdown formatting bold
                            cell_clean = cell.replace("**", "<b>", 1).replace("**", "</b>", 1) if "**" in cell else cell
                            formatted_row.append(Paragraph(cell_clean, style_use))
                        formatted_table.append(formatted_row)
                    
                    col_count = len(table_data[0])
                    col_width = 504.0 / col_count
                    
                    t = Table(formatted_table, colWidths=[col_width]*col_count)
                    t_style = [
                        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
                        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                        ('VALIGN', (0,0), (-1,-1), 'TOP'),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                        ('TOPPADDING', (0,0), (-1,-1), 5),
                        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                    ]
                    for r in range(1, len(table_data)):
                        if r % 2 == 0:
                            t_style.append(('BACKGROUND', (0, r), (-1, r), colors.HexColor('#F8FAFC')))
                    t.setStyle(TableStyle(t_style))
                    story.append(Spacer(1, 4))
                    story.append(t)
                    story.append(Spacer(1, 8))
                    table_data = []
                    in_table = False
                    
            if line_str.startswith("## "):
                story.append(Paragraph(line_str.replace("## ", ""), h1_style))
            elif line_str.startswith("### "):
                story.append(Paragraph(line_str.replace("### ", ""), h2_style))
            elif line_str.startswith("* ") or line_str.startswith("- "):
                text_clean = line_str[2:].replace("**", "<b>", 1).replace("**", "</b>", 1)
                story.append(Paragraph(f"• {text_clean}", bullet_style))
            elif line_str.startswith("1. ") or line_str.startswith("2. ") or line_str.startswith("3. ") or line_str.startswith("4. ") or line_str.startswith("5. "):
                text_clean = line_str.replace("**", "<b>", 1).replace("**", "</b>", 1)
                story.append(Paragraph(text_clean, bullet_style))
            elif len(line_str) > 0 and not line_str.startswith("---"):
                text_clean = line_str.replace("**", "<b>").replace("**", "</b>")
                story.append(Paragraph(text_clean, body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF report saved successfully to {PDF_PATH}!")

if __name__ == "__main__":
    df = load_data()
    generate_charts(df)
    build_pptx()
    build_pdf()
    print("All Phase 4 assets successfully generated!")
