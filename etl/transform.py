"""
etl/transform.py — Transform stage of the ETL pipeline.

Responsibilities
----------------
* Standardise column names (snake_case).
* Drop redundant ``promo_code_used`` column (100 % collinear with discount_applied).
* Harmonise ``frequency_of_purchases`` labels (e.g. Fortnightly → Bi-Weekly).
* Impute missing ``review_rating`` with category-level median.
* Engineer derived features: age_group, purchase_frequency_days,
  customer_value_tier, engagement_tier, value_engagement_segment.
* Produce separate summary DataFrames for product- and category-level outputs.

All business logic is preserved exactly as established in the Phase-1 notebook
(generate_phase1_notebook.py).  Any intentional deviation is documented with
an inline comment.
"""

from __future__ import annotations

import logging
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd

from etl import config

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Individual transform steps (reusable, independently testable)
# ---------------------------------------------------------------------------

def standardise_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Rename raw column headers to snake_case using the canonical mapping.

    Parameters
    ----------
    df : pd.DataFrame
        Raw DataFrame with original column names.

    Returns
    -------
    pd.DataFrame
        DataFrame with renamed columns.

    Raises
    ------
    ValueError
        If any expected source column is absent from *df*.
    """
    missing = [c for c in config.COLUMN_RENAME_MAP if c not in df.columns]
    if missing:
        raise ValueError(
            f"[Transform] standardise_column_names: columns not found in input: {missing}"
        )
    renamed = df.rename(columns=config.COLUMN_RENAME_MAP)
    logger.debug("[Transform] Columns standardised to snake_case.")
    return renamed


def drop_redundant_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Drop the ``promo_code_used`` column, which is 100 % collinear with
    ``discount_applied`` in this dataset.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame after column renaming.

    Returns
    -------
    pd.DataFrame
        DataFrame without ``promo_code_used``.
    """
    if "promo_code_used" in df.columns:
        df = df.drop(columns=["promo_code_used"])
        logger.debug(
            "[Transform] Dropped redundant column 'promo_code_used'."
        )
    else:
        logger.debug(
            "[Transform] 'promo_code_used' not present; nothing to drop."
        )
    return df


def harmonise_frequency_labels(df: pd.DataFrame) -> pd.DataFrame:
    """Unify semantically equivalent purchase-frequency labels.

    Transformations applied
    -----------------------
    * ``Fortnightly``    → ``Bi-Weekly``
    * ``Every 3 Months`` → ``Quarterly``

    The original raw label is preserved in a new column
    ``frequency_of_purchases_raw`` for auditability.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
    """
    df = df.copy()
    df["frequency_of_purchases_raw"] = df["frequency_of_purchases"]
    df["frequency_of_purchases"] = df["frequency_of_purchases"].map(
        config.FREQUENCY_HARMONISATION_MAP
    )
    unmapped = df["frequency_of_purchases"].isna().sum()
    if unmapped > 0:
        logger.warning(
            "[Transform] %d rows have unrecognised frequency labels after harmonisation.",
            unmapped,
        )
    logger.debug(
        "[Transform] Frequency labels harmonised. Value counts:\n%s",
        df["frequency_of_purchases"].value_counts().to_dict(),
    )
    return df


def impute_review_rating(df: pd.DataFrame) -> pd.DataFrame:
    """Impute missing ``review_rating`` values with the category-level median.

    This preserves the distribution shape within each product category
    rather than applying a global fill value.  Matches the Phase-1 notebook.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
    """
    df = df.copy()
    missing_before = int(df["review_rating"].isna().sum())
    if missing_before == 0:
        logger.debug("[Transform] No missing review_rating values found.")
        return df

    df["review_rating"] = df.groupby("category")["review_rating"].transform(
        lambda x: x.fillna(x.median())
    )
    missing_after = int(df["review_rating"].isna().sum())
    logger.info(
        "[Transform] review_rating: imputed %d missing values using category median. "
        "Remaining nulls: %d.",
        missing_before - missing_after,
        missing_after,
    )
    if missing_after > 0:
        logger.warning(
            "[Transform] %d review_rating nulls remain after imputation "
            "(category had no non-null rows).",
            missing_after,
        )
    return df


# ---------------------------------------------------------------------------
# Feature engineering helpers
# ---------------------------------------------------------------------------

def engineer_age_group(df: pd.DataFrame) -> pd.DataFrame:
    """Bin the ``age`` column into labelled demographic cohorts.

    Bins  : [17, 30] → 18-30 (Young Adult)
             [31, 45] → 31-45 (Adult)
             [46, 60] → 46-60 (Middle-Aged)
             [61, 70] → 61-70 (Senior)

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
        With new column ``age_group``.
    """
    df = df.copy()
    df["age_group"] = pd.cut(
        df["age"],
        bins=config.AGE_BINS,
        labels=config.AGE_LABELS,
    ).astype(str)
    logger.debug("[Transform] age_group engineered.")
    return df


def engineer_purchase_frequency_days(df: pd.DataFrame) -> pd.DataFrame:
    """Map harmonised frequency labels to numerical day intervals.

    ``Weekly`` → 7, ``Bi-Weekly`` → 14, ``Monthly`` → 30,
    ``Quarterly`` → 90, ``Annually`` → 365.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
        With new column ``purchase_frequency_days``.
    """
    df = df.copy()
    df["purchase_frequency_days"] = df["frequency_of_purchases"].map(
        config.FREQUENCY_DAYS_MAP
    )
    unmapped = df["purchase_frequency_days"].isna().sum()
    if unmapped > 0:
        logger.warning(
            "[Transform] %d rows could not be mapped to purchase_frequency_days.",
            unmapped,
        )
    logger.debug("[Transform] purchase_frequency_days engineered.")
    return df


def classify_value_tier(spend: float) -> str:
    """Return the customer value tier for a single purchase amount.

    Parameters
    ----------
    spend : float
        ``purchase_amount_usd`` for one transaction.

    Returns
    -------
    str
        ``'Low Value'``, ``'Medium Value'``, or ``'High Value'``.
    """
    if spend < config.VALUE_LOW_MAX:
        return "Low Value"
    elif spend <= config.VALUE_MEDIUM_MAX:
        return "Medium Value"
    else:
        return "High Value"


def classify_engagement_tier(purchases: int) -> str:
    """Return the engagement tier based on previous purchase volume.

    Parameters
    ----------
    purchases : int
        ``previous_purchases`` for one customer.

    Returns
    -------
    str
        ``'Low Engagement'``, ``'Medium Engagement'``, or ``'High Engagement'``.
    """
    if purchases <= config.ENGAGEMENT_LOW_MAX:
        return "Low Engagement"
    elif purchases <= config.ENGAGEMENT_MED_MAX:
        return "Medium Engagement"
    else:
        return "High Engagement"


def engineer_tiers_and_segment(df: pd.DataFrame) -> pd.DataFrame:
    """Apply value tier, engagement tier, and combined segment engineering.

    Adds columns
    ------------
    * ``customer_value_tier``
    * ``engagement_tier``
    * ``value_engagement_segment``

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
    """
    df = df.copy()
    df["customer_value_tier"] = df["purchase_amount_usd"].apply(classify_value_tier)
    df["engagement_tier"] = df["previous_purchases"].apply(classify_engagement_tier)
    df["value_engagement_segment"] = (
        df["customer_value_tier"] + " - " + df["engagement_tier"]
    )
    logger.debug(
        "[Transform] Tiers and segment engineered. Segment distribution:\n%s",
        df["value_engagement_segment"].value_counts().to_dict(),
    )
    return df


# ---------------------------------------------------------------------------
# Summary-table builders (for product_intelligence and category_intelligence)
# ---------------------------------------------------------------------------

def build_product_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate transaction-level data to product (category × item) grain.

    Returns the same columns produced by the Phase-1 notebook's
    ``product_summary`` DataFrame, preserving existing export logic.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned, feature-engineered DataFrame.

    Returns
    -------
    pd.DataFrame
        Product-level summary (25 rows for the production dataset).
    """
    product_summary = (
        df.groupby(["category", "item_purchased"])
        .agg(
            transaction_count=("customer_id", "count"),
            total_revenue=("purchase_amount_usd", "sum"),
            avg_purchase_amount=("purchase_amount_usd", "mean"),
            avg_review_rating=("review_rating", "mean"),
            discounted_count=("discount_applied", lambda x: (x == "Yes").sum()),
            subscriber_count=("subscription_status", lambda x: (x == "Yes").sum()),
        )
        .reset_index()
    )
    product_summary["discount_penetration_pct"] = (
        product_summary["discounted_count"] / product_summary["transaction_count"]
    ) * 100
    product_summary["subscriber_share_pct"] = (
        product_summary["subscriber_count"] / product_summary["transaction_count"]
    ) * 100
    logger.debug(
        "[Transform] Product summary built: %d products.", len(product_summary)
    )
    return product_summary


def build_category_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate transaction-level data to category grain.

    Returns the same columns produced by the Phase-1 notebook's
    ``category_summary`` DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned, feature-engineered DataFrame.

    Returns
    -------
    pd.DataFrame
        Category-level summary (4 rows for the production dataset).
    """
    total_revenue = df["purchase_amount_usd"].sum()
    category_summary = (
        df.groupby("category")
        .agg(
            transaction_volume=("customer_id", "count"),
            total_revenue=("purchase_amount_usd", "sum"),
            avg_purchase_amount=("purchase_amount_usd", "mean"),
            avg_review_rating=("review_rating", "mean"),
            discounted_transactions=("discount_applied", lambda x: (x == "Yes").sum()),
            subscriber_transactions=("subscription_status", lambda x: (x == "Yes").sum()),
        )
        .reset_index()
    )
    category_summary["revenue_share_pct"] = (
        category_summary["total_revenue"] / total_revenue
    ) * 100
    category_summary["discount_penetration_pct"] = (
        category_summary["discounted_transactions"]
        / category_summary["transaction_volume"]
    ) * 100
    category_summary["subscriber_share_pct"] = (
        category_summary["subscriber_transactions"]
        / category_summary["transaction_volume"]
    ) * 100
    logger.debug(
        "[Transform] Category summary built: %d categories.", len(category_summary)
    )
    return category_summary


# ---------------------------------------------------------------------------
# Master transform entry point
# ---------------------------------------------------------------------------

def transform(raw_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Execute all transformation and feature-engineering steps in order.

    Parameters
    ----------
    raw_df : pd.DataFrame
        Raw DataFrame returned by the Extract stage.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
        1. ``cleaned_df``        — fully cleaned & feature-enriched transaction dataset.
        2. ``product_summary``   — product-level aggregated summary.
        3. ``category_summary``  — category-level aggregated summary.
    """
    logger.info("[Transform] Starting transformation pipeline.")

    df = raw_df.copy()
    input_rows = len(df)

    # Step 1 — rename columns
    df = standardise_column_names(df)

    # Step 2 — drop redundant column
    df = drop_redundant_columns(df)

    # Step 3 — harmonise frequency labels
    df = harmonise_frequency_labels(df)

    # Step 4 — impute missing review ratings
    df = impute_review_rating(df)

    # Step 5 — feature engineering
    df = engineer_age_group(df)
    df = engineer_purchase_frequency_days(df)
    df = engineer_tiers_and_segment(df)

    output_rows = len(df)
    logger.info(
        "[Transform] Transformation complete. Input rows: %d → Output rows: %d.",
        input_rows,
        output_rows,
    )

    # Build summary tables from the cleaned dataset
    product_summary = build_product_summary(df)
    category_summary = build_category_summary(df)

    return df, product_summary, category_summary
