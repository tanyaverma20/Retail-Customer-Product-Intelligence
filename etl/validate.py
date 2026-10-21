"""
etl/validate.py — Data-quality validation for the ETL pipeline.

Validation is split into two severity levels:
* ``ERROR``   — blocking; the pipeline should not proceed.
* ``WARNING`` — non-blocking; the pipeline can continue but the issue is recorded.

Each check returns a :class:`ValidationResult` carrying the severity, rule ID,
a human-readable message, and (optionally) the number of offending rows.

The public ``validate_raw``, ``validate_cleaned``, and ``validate_database``
functions collect all results and return them as a list so callers can decide
how to surface them.
"""

from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

import pandas as pd

from etl import config

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result model
# ---------------------------------------------------------------------------

@dataclass
class ValidationResult:
    """Represents a single validation outcome."""

    rule_id: str
    severity: str          # "ERROR" or "WARNING"
    message: str
    offending_count: int = 0
    passed: bool = True


def _error(rule_id: str, message: str, count: int = 0) -> ValidationResult:
    logger.error("[Validate] %s — %s (offending rows: %d)", rule_id, message, count)
    return ValidationResult(rule_id=rule_id, severity="ERROR", message=message,
                             offending_count=count, passed=False)


def _warning(rule_id: str, message: str, count: int = 0) -> ValidationResult:
    logger.warning("[Validate] %s — %s (offending rows: %d)", rule_id, message, count)
    return ValidationResult(rule_id=rule_id, severity="WARNING", message=message,
                             offending_count=count, passed=False)


def _ok(rule_id: str, message: str) -> ValidationResult:
    logger.debug("[Validate] %s — PASSED: %s", rule_id, message)
    return ValidationResult(rule_id=rule_id, severity="OK", message=message,
                             offending_count=0, passed=True)


# ---------------------------------------------------------------------------
# Raw-DataFrame checks
# ---------------------------------------------------------------------------

def validate_raw(df: pd.DataFrame) -> List[ValidationResult]:
    """Run data-quality checks on the raw (pre-transform) DataFrame.

    Rules checked
    -------------
    R01 — Required columns present.
    R02 — No completely empty DataFrame.
    R03 — ``Customer ID`` uniqueness.
    R04 — Numeric range: ``Age`` in [18, 70].
    R05 — Numeric range: ``Purchase Amount (USD)`` in [1, 10 000].
    R06 — Numeric range: ``Previous Purchases`` ≥ 0.
    R07 — ``Review Rating`` in [1, 5] (NaN allowed — imputed downstream).
    R08 — ``Category`` within expected set.
    R09 — ``Gender`` within expected set.
    R10 — ``Subscription Status`` within expected set.
    R11 — ``Discount Applied`` within expected set.
    R12 — ``Season`` within expected set.

    Parameters
    ----------
    df : pd.DataFrame
        Raw DataFrame from the Extract stage.

    Returns
    -------
    list[ValidationResult]
    """
    results: List[ValidationResult] = []

    # R01 — required columns
    missing_cols = [c for c in config.RAW_REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        results.append(_error("R01", f"Missing required columns: {missing_cols}"))
    else:
        results.append(_ok("R01", "All required columns present."))

    # R02 — non-empty
    if len(df) == 0:
        results.append(_error("R02", "DataFrame is empty."))
        return results  # further checks are meaningless on empty df
    results.append(_ok("R02", f"Dataset has {len(df):,} rows."))

    # R03 — Customer ID uniqueness
    dupes = int(df["Customer ID"].duplicated().sum())
    if dupes > 0:
        results.append(_error("R03", f"Duplicate Customer IDs found: {dupes}.", dupes))
    else:
        results.append(_ok("R03", "Customer IDs are unique."))

    # R04 — Age range
    age_bad = int(((df["Age"] < config.AGE_MIN) | (df["Age"] > config.AGE_MAX)).sum())
    if age_bad > 0:
        results.append(_warning("R04", f"{age_bad} Age values outside [{config.AGE_MIN}, {config.AGE_MAX}].", age_bad))
    else:
        results.append(_ok("R04", "All Age values within expected range."))

    # R05 — Purchase amount range
    pa_col = "Purchase Amount (USD)"
    pa_bad = int(((df[pa_col] < config.PURCHASE_MIN) | (df[pa_col] > config.PURCHASE_MAX)).sum())
    if pa_bad > 0:
        results.append(_warning("R05", f"{pa_bad} purchase amounts outside [{config.PURCHASE_MIN}, {config.PURCHASE_MAX}].", pa_bad))
    else:
        results.append(_ok("R05", "All purchase amounts within expected range."))

    # R06 — Previous Purchases ≥ 0
    pp_bad = int((df["Previous Purchases"] < config.PREV_PURCHASES_MIN).sum())
    if pp_bad > 0:
        results.append(_warning("R06", f"{pp_bad} Previous Purchases values < 0.", pp_bad))
    else:
        results.append(_ok("R06", "All Previous Purchases values ≥ 0."))

    # R07 — Review Rating range (NaN allowed)
    rr_non_null = df["Review Rating"].dropna()
    rr_bad = int(((rr_non_null < config.RATING_MIN) | (rr_non_null > config.RATING_MAX)).sum())
    rr_null = int(df["Review Rating"].isna().sum())
    if rr_bad > 0:
        results.append(_warning("R07", f"{rr_bad} Review Rating values outside [1, 5].", rr_bad))
    else:
        results.append(_ok("R07", f"All non-null Review Ratings within [1,5]. ({rr_null} nulls will be imputed.)"))

    # R08 — Category values
    invalid_cats = df[~df["Category"].isin(config.VALID_CATEGORIES)]["Category"].unique().tolist()
    if invalid_cats:
        cnt = int((~df["Category"].isin(config.VALID_CATEGORIES)).sum())
        results.append(_warning("R08", f"Unexpected Category values: {invalid_cats}. Count: {cnt}.", cnt))
    else:
        results.append(_ok("R08", "All Category values are valid."))

    # R09 — Gender values
    invalid_genders = df[~df["Gender"].isin(config.VALID_GENDERS)]["Gender"].unique().tolist()
    if invalid_genders:
        cnt = int((~df["Gender"].isin(config.VALID_GENDERS)).sum())
        results.append(_warning("R09", f"Unexpected Gender values: {invalid_genders}.", cnt))
    else:
        results.append(_ok("R09", "All Gender values are valid."))

    # R10 — Subscription Status
    invalid_sub = df[~df["Subscription Status"].isin(config.VALID_SUBSCRIPTION_STATUSES)]["Subscription Status"].unique().tolist()
    if invalid_sub:
        cnt = int((~df["Subscription Status"].isin(config.VALID_SUBSCRIPTION_STATUSES)).sum())
        results.append(_warning("R10", f"Unexpected Subscription Status values: {invalid_sub}.", cnt))
    else:
        results.append(_ok("R10", "All Subscription Status values are valid."))

    # R11 — Discount Applied
    invalid_disc = df[~df["Discount Applied"].isin(config.VALID_DISCOUNT_VALUES)]["Discount Applied"].unique().tolist()
    if invalid_disc:
        cnt = int((~df["Discount Applied"].isin(config.VALID_DISCOUNT_VALUES)).sum())
        results.append(_warning("R11", f"Unexpected Discount Applied values: {invalid_disc}.", cnt))
    else:
        results.append(_ok("R11", "All Discount Applied values are valid."))

    # R12 — Season
    invalid_seasons = df[~df["Season"].isin(config.VALID_SEASONS)]["Season"].unique().tolist()
    if invalid_seasons:
        cnt = int((~df["Season"].isin(config.VALID_SEASONS)).sum())
        results.append(_warning("R12", f"Unexpected Season values: {invalid_seasons}.", cnt))
    else:
        results.append(_ok("R12", "All Season values are valid."))

    return results


# ---------------------------------------------------------------------------
# Cleaned-DataFrame checks
# ---------------------------------------------------------------------------

def validate_cleaned(
    raw_df: pd.DataFrame,
    cleaned_df: pd.DataFrame,
) -> List[ValidationResult]:
    """Run data-quality checks on the cleaned & feature-engineered DataFrame.

    Rules checked
    -------------
    C01 — Row count is preserved (no accidental drops during transform).
    C02 — No null review_rating values remain.
    C03 — All frequency_of_purchases values are harmonised.
    C04 — customer_value_tier contains only expected values.
    C05 — engagement_tier contains only expected values.
    C06 — value_engagement_segment is not null.
    C07 — age_group is not null.
    C08 — purchase_frequency_days is not null.
    C09 — promo_code_used has been dropped.
    C10 — customer_id uniqueness preserved.

    Parameters
    ----------
    raw_df : pd.DataFrame
        Original raw DataFrame (for row-count comparison).
    cleaned_df : pd.DataFrame
        Cleaned/transformed DataFrame.

    Returns
    -------
    list[ValidationResult]
    """
    results: List[ValidationResult] = []

    # C01 — row count preserved
    if len(cleaned_df) != len(raw_df):
        results.append(_error(
            "C01",
            f"Row count changed during transform: raw={len(raw_df)}, cleaned={len(cleaned_df)}.",
            abs(len(raw_df) - len(cleaned_df)),
        ))
    else:
        results.append(_ok("C01", f"Row count preserved: {len(cleaned_df):,} rows."))

    # C02 — no null review_rating
    null_rr = int(cleaned_df["review_rating"].isna().sum())
    if null_rr > 0:
        results.append(_error("C02", f"{null_rr} null review_rating values remain after imputation.", null_rr))
    else:
        results.append(_ok("C02", "No null review_rating values."))

    # C03 — harmonised frequency values
    invalid_freq = cleaned_df[~cleaned_df["frequency_of_purchases"].isin(config.VALID_FREQUENCIES)]
    if len(invalid_freq) > 0:
        results.append(_warning(
            "C03",
            f"{len(invalid_freq)} rows have unrecognised frequency_of_purchases values: "
            f"{invalid_freq['frequency_of_purchases'].unique().tolist()}.",
            len(invalid_freq),
        ))
    else:
        results.append(_ok("C03", "All frequency_of_purchases values are harmonised."))

    # C04 — customer_value_tier
    valid_vt = {"Low Value", "Medium Value", "High Value"}
    invalid_vt = cleaned_df[~cleaned_df["customer_value_tier"].isin(valid_vt)]
    if len(invalid_vt) > 0:
        results.append(_error("C04", f"{len(invalid_vt)} invalid customer_value_tier values.", len(invalid_vt)))
    else:
        results.append(_ok("C04", "All customer_value_tier values valid."))

    # C05 — engagement_tier
    valid_et = {"Low Engagement", "Medium Engagement", "High Engagement"}
    invalid_et = cleaned_df[~cleaned_df["engagement_tier"].isin(valid_et)]
    if len(invalid_et) > 0:
        results.append(_error("C05", f"{len(invalid_et)} invalid engagement_tier values.", len(invalid_et)))
    else:
        results.append(_ok("C05", "All engagement_tier values valid."))

    # C06 — value_engagement_segment not null
    null_seg = int(cleaned_df["value_engagement_segment"].isna().sum())
    if null_seg > 0:
        results.append(_error("C06", f"{null_seg} null value_engagement_segment values.", null_seg))
    else:
        results.append(_ok("C06", "No null value_engagement_segment values."))

    # C07 — age_group not null
    null_ag = int(cleaned_df["age_group"].isna().sum()) if "age_group" in cleaned_df.columns else 0
    if null_ag > 0:
        results.append(_warning("C07", f"{null_ag} null age_group values.", null_ag))
    else:
        results.append(_ok("C07", "No null age_group values."))

    # C08 — purchase_frequency_days not null
    null_pfd = int(cleaned_df["purchase_frequency_days"].isna().sum())
    if null_pfd > 0:
        results.append(_warning("C08", f"{null_pfd} null purchase_frequency_days values.", null_pfd))
    else:
        results.append(_ok("C08", "No null purchase_frequency_days values."))

    # C09 — promo_code_used dropped
    if "promo_code_used" in cleaned_df.columns:
        results.append(_error("C09", "Redundant column 'promo_code_used' was NOT dropped."))
    else:
        results.append(_ok("C09", "'promo_code_used' correctly dropped."))

    # C10 — customer_id uniqueness
    dupes = int(cleaned_df["customer_id"].duplicated().sum())
    if dupes > 0:
        results.append(_error("C10", f"{dupes} duplicate customer_id values in cleaned dataset.", dupes))
    else:
        results.append(_ok("C10", "customer_id uniqueness preserved."))

    return results


# ---------------------------------------------------------------------------
# SQLite integrity checks
# ---------------------------------------------------------------------------

def validate_database(db_path: Path, expected_transaction_rows: int) -> List[ValidationResult]:
    """Verify SQLite table existence, schema columns, and row-count parity.

    Rules checked
    -------------
    D01 — All four tables exist.
    D02 — customer_transactions row count matches expected_transaction_rows.
    D03 — customer_transactions contains required analytical columns.
    D04 — No duplicate customer_id in customer_transactions.

    Parameters
    ----------
    db_path : Path
        Path to the SQLite database file.
    expected_transaction_rows : int
        Expected row count for ``customer_transactions``.

    Returns
    -------
    list[ValidationResult]
    """
    results: List[ValidationResult] = []

    if not Path(db_path).exists():
        results.append(_error("D01", f"SQLite database not found at: {db_path}"))
        return results

    conn = sqlite3.connect(str(db_path))
    try:
        # D01 — table existence
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = {row[0] for row in cursor.fetchall()}
        required_tables = {
            config.TRANSACTIONS_TABLE,
            config.CUSTOMER_INTEL_TABLE,
            config.PRODUCT_INTEL_TABLE,
            config.CATEGORY_INTEL_TABLE,
        }
        missing_tables = required_tables - existing_tables
        if missing_tables:
            results.append(_error("D01", f"Missing tables in database: {missing_tables}"))
        else:
            results.append(_ok("D01", f"All {len(required_tables)} expected tables exist."))

        if config.TRANSACTIONS_TABLE not in existing_tables:
            # Cannot run further checks without the main table
            return results

        # D02 — row count
        actual_rows = conn.execute(
            f"SELECT COUNT(*) FROM [{config.TRANSACTIONS_TABLE}]"
        ).fetchone()[0]
        if actual_rows != expected_transaction_rows:
            results.append(_error(
                "D02",
                f"customer_transactions row count mismatch: "
                f"expected {expected_transaction_rows}, found {actual_rows}.",
                abs(actual_rows - expected_transaction_rows),
            ))
        else:
            results.append(_ok("D02", f"customer_transactions has correct row count: {actual_rows:,}."))

        # D03 — required columns in customer_transactions
        cursor = conn.execute(f"PRAGMA table_info([{config.TRANSACTIONS_TABLE}])")
        existing_cols = {row[1] for row in cursor.fetchall()}
        required_cols = {
            "customer_id", "age", "gender", "purchase_amount_usd", "category",
            "item_purchased", "subscription_status", "discount_applied",
            "previous_purchases", "customer_value_tier", "engagement_tier",
            "value_engagement_segment",
        }
        missing_cols = required_cols - existing_cols
        if missing_cols:
            results.append(_error("D03", f"Missing columns in customer_transactions: {missing_cols}"))
        else:
            results.append(_ok("D03", "All required analytical columns present in customer_transactions."))

        # D04 — duplicate customer_id
        dup_count = conn.execute(
            f"SELECT COUNT(*) - COUNT(DISTINCT customer_id) FROM [{config.TRANSACTIONS_TABLE}]"
        ).fetchone()[0]
        if dup_count > 0:
            results.append(_error("D04", f"{dup_count} duplicate customer_id values in customer_transactions.", dup_count))
        else:
            results.append(_ok("D04", "No duplicate customer_id in customer_transactions."))

    finally:
        conn.close()

    return results


# ---------------------------------------------------------------------------
# Python vs SQL KPI reconciliation check
# ---------------------------------------------------------------------------

def reconcile_kpis(
    cleaned_df: pd.DataFrame,
    db_path: Path,
) -> List[ValidationResult]:
    """Cross-validate key KPIs between Python (pandas) and SQLite.

    KPIs reconciled
    ---------------
    KR01 — Total revenue.
    KR02 — Total transaction count.
    KR03 — Subscriber count.
    KR04 — Discounted order count.
    KR05 — Clothing category revenue.
    KR06 — High-value non-subscriber cohort count (>25 purchases, >$75, no subscription).

    Tolerance: exact integer match for counts; ≤ $0.01 tolerance for currency
    aggregates (floating-point rounding).

    Parameters
    ----------
    cleaned_df : pd.DataFrame
        In-memory cleaned DataFrame.
    db_path : Path
        Path to the SQLite database.

    Returns
    -------
    list[ValidationResult]
    """
    results: List[ValidationResult] = []

    if not Path(db_path).exists():
        results.append(_error("KR00", f"SQLite database not found for reconciliation: {db_path}"))
        return results

    conn = sqlite3.connect(str(db_path))
    TOLERANCE = 0.01  # acceptable float rounding gap

    try:
        def _sql_scalar(query: str):
            return conn.execute(query).fetchone()[0]

        # KR01 — Total revenue
        py_total_rev = float(cleaned_df["purchase_amount_usd"].sum())
        sql_total_rev = float(_sql_scalar(f"SELECT SUM(purchase_amount_usd) FROM [{config.TRANSACTIONS_TABLE}]") or 0)
        if abs(py_total_rev - sql_total_rev) > TOLERANCE:
            results.append(_error("KR01", f"Total revenue mismatch: Python={py_total_rev:.2f}, SQL={sql_total_rev:.2f}"))
        else:
            results.append(_ok("KR01", f"Total revenue reconciled: ${py_total_rev:,.2f}"))

        # KR02 — Transaction count
        py_count = len(cleaned_df)
        sql_count = int(_sql_scalar(f"SELECT COUNT(*) FROM [{config.TRANSACTIONS_TABLE}]"))
        if py_count != sql_count:
            results.append(_error("KR02", f"Transaction count mismatch: Python={py_count}, SQL={sql_count}"))
        else:
            results.append(_ok("KR02", f"Transaction count reconciled: {py_count:,}"))

        # KR03 — Subscriber count
        py_subs = int((cleaned_df["subscription_status"] == "Yes").sum())
        sql_subs = int(_sql_scalar(
            f"SELECT COUNT(*) FROM [{config.TRANSACTIONS_TABLE}] WHERE subscription_status = 'Yes'"
        ))
        if py_subs != sql_subs:
            results.append(_error("KR03", f"Subscriber count mismatch: Python={py_subs}, SQL={sql_subs}"))
        else:
            results.append(_ok("KR03", f"Subscriber count reconciled: {py_subs:,}"))

        # KR04 — Discounted order count
        py_disc = int((cleaned_df["discount_applied"] == "Yes").sum())
        sql_disc = int(_sql_scalar(
            f"SELECT COUNT(*) FROM [{config.TRANSACTIONS_TABLE}] WHERE discount_applied = 'Yes'"
        ))
        if py_disc != sql_disc:
            results.append(_error("KR04", f"Discounted orders mismatch: Python={py_disc}, SQL={sql_disc}"))
        else:
            results.append(_ok("KR04", f"Discounted orders reconciled: {py_disc:,}"))

        # KR05 — Clothing revenue
        py_cloth = float(cleaned_df[cleaned_df["category"] == "Clothing"]["purchase_amount_usd"].sum())
        sql_cloth = float(_sql_scalar(
            f"SELECT SUM(purchase_amount_usd) FROM [{config.TRANSACTIONS_TABLE}] WHERE category = 'Clothing'"
        ) or 0)
        if abs(py_cloth - sql_cloth) > TOLERANCE:
            results.append(_error("KR05", f"Clothing revenue mismatch: Python=${py_cloth:,.2f}, SQL=${sql_cloth:,.2f}"))
        else:
            results.append(_ok("KR05", f"Clothing revenue reconciled: ${py_cloth:,.2f}"))

        # KR06 — High-value non-subscriber cohort (Q13 criteria)
        py_cohort = int(
            ((cleaned_df["subscription_status"] == "No") &
             (cleaned_df["previous_purchases"] > 25) &
             (cleaned_df["purchase_amount_usd"] > 75)).sum()
        )
        sql_cohort = int(_sql_scalar(
            f"SELECT COUNT(*) FROM [{config.TRANSACTIONS_TABLE}] "
            f"WHERE subscription_status = 'No' AND previous_purchases > 25 AND purchase_amount_usd > 75"
        ))
        if py_cohort != sql_cohort:
            results.append(_error("KR06", f"High-value non-subscriber cohort mismatch: Python={py_cohort}, SQL={sql_cohort}"))
        else:
            results.append(_ok("KR06", f"High-value non-subscriber cohort reconciled: {py_cohort:,}"))

    finally:
        conn.close()

    return results


# ---------------------------------------------------------------------------
# Aggregated report helper
# ---------------------------------------------------------------------------

def summarise_results(results: List[ValidationResult]) -> Tuple[int, int, int]:
    """Count passed, warning, and error results.

    Parameters
    ----------
    results : list[ValidationResult]

    Returns
    -------
    tuple[int, int, int]
        (passed, warnings, errors)
    """
    passed = sum(1 for r in results if r.severity == "OK")
    warnings = sum(1 for r in results if r.severity == "WARNING")
    errors = sum(1 for r in results if r.severity == "ERROR")
    return passed, warnings, errors


def has_blocking_errors(results: List[ValidationResult]) -> bool:
    """Return True if any result has severity == 'ERROR'."""
    return any(r.severity == "ERROR" for r in results)
