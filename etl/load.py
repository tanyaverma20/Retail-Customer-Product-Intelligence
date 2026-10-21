"""
etl/load.py — Load stage of the ETL pipeline.

Responsibilities
----------------
* Persist cleaned DataFrames to CSV files in ``data/processed/``.
* Load analytical tables into the SQLite database using transactions.
* Use IF-NOT-EXISTS / REPLACE semantics to make reruns safe and idempotent.
* Never silently duplicate records; DROP + INSERT strategy is used for each
  table to prevent partial-run accumulation.
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from etl import config

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# CSV persistence helpers
# ---------------------------------------------------------------------------

def save_csv(
    df: pd.DataFrame,
    path: Path,
    description: str = "",
) -> None:
    """Write a DataFrame to CSV, creating parent directories if necessary.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to persist.
    path : Path
        Destination file path.
    description : str
        Human-readable label used in log messages.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    logger.info(
        "[Load] Saved %s → %s  (rows: %d, cols: %d)",
        description,
        path,
        df.shape[0],
        df.shape[1],
    )


def save_all_csvs(
    cleaned_df: pd.DataFrame,
    customer_intel_df: pd.DataFrame,
    product_summary: pd.DataFrame,
    category_summary: pd.DataFrame,
    processed_dir: Optional[Path] = None,
) -> Dict[str, Path]:
    """Save all four processed CSV files to ``data/processed/``.

    Parameters
    ----------
    cleaned_df : pd.DataFrame
        Master cleaned dataset.
    customer_intel_df : pd.DataFrame
        Customer-level intelligence subset.
    product_summary : pd.DataFrame
        Product-level aggregated summary.
    category_summary : pd.DataFrame
        Category-level aggregated summary.
    processed_dir : Path | None
        Override for the output directory (defaults to ``config.PROCESSED_DIR``).

    Returns
    -------
    dict[str, Path]
        Mapping of dataset name → saved file path.
    """
    base = Path(processed_dir) if processed_dir else config.PROCESSED_DIR
    base.mkdir(parents=True, exist_ok=True)

    paths: Dict[str, Path] = {
        "cleaned": base / "customer_shopping_behavior_cleaned.csv",
        "customer_intelligence": base / "customer_intelligence.csv",
        "product_intelligence": base / "product_intelligence.csv",
        "category_intelligence": base / "category_intelligence.csv",
    }

    save_csv(cleaned_df, paths["cleaned"], "cleaned dataset")
    save_csv(customer_intel_df, paths["customer_intelligence"], "customer_intelligence")
    save_csv(product_summary, paths["product_intelligence"], "product_intelligence")
    save_csv(category_summary, paths["category_intelligence"], "category_intelligence")

    return paths


# ---------------------------------------------------------------------------
# SQLite helpers
# ---------------------------------------------------------------------------

def get_connection(db_path: Path) -> sqlite3.Connection:
    """Open a SQLite connection with foreign-key enforcement enabled.

    Parameters
    ----------
    db_path : Path
        Path to the SQLite database file.

    Returns
    -------
    sqlite3.Connection
    """
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


def load_dataframe_to_sqlite(
    df: pd.DataFrame,
    table_name: str,
    conn: sqlite3.Connection,
) -> int:
    """Drop and recreate a SQLite table, then insert all rows atomically.

    Using DROP + INSERT (rather than UPSERT) is intentional: it guarantees
    row-count parity with the source DataFrame and prevents duplicate records
    across pipeline reruns.  This is safe because all tables are fully derived
    from the source CSV on every run.

    Parameters
    ----------
    df : pd.DataFrame
        Data to insert.
    table_name : str
        Target SQLite table name.
    conn : sqlite3.Connection
        Active SQLite connection.

    Returns
    -------
    int
        Number of rows inserted.
    """
    with conn:
        # Truncate existing data atomically
        conn.execute(f"DROP TABLE IF EXISTS [{table_name}]")
        # Let pandas create schema from DataFrame dtypes
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        cursor = conn.execute(f"SELECT COUNT(*) FROM [{table_name}]")
        row_count = cursor.fetchone()[0]

    logger.info(
        "[Load] SQLite table '%s' loaded — %d rows inserted.", table_name, row_count
    )
    return row_count


def load_all_to_sqlite(
    cleaned_df: pd.DataFrame,
    customer_intel_df: pd.DataFrame,
    product_summary: pd.DataFrame,
    category_summary: pd.DataFrame,
    db_path: Optional[Path] = None,
) -> Dict[str, int]:
    """Load all four analytical DataFrames into the SQLite database.

    Parameters
    ----------
    cleaned_df : pd.DataFrame
        Master transaction-level dataset → ``customer_transactions`` table.
    customer_intel_df : pd.DataFrame
        Customer intelligence subset → ``customer_intelligence`` table.
    product_summary : pd.DataFrame
        Product summary → ``product_intelligence`` table.
    category_summary : pd.DataFrame
        Category summary → ``category_intelligence`` table.
    db_path : Path | None
        Override database path (defaults to ``config.DB_PATH``).

    Returns
    -------
    dict[str, int]
        Table name → row count inserted.
    """
    target_db = Path(db_path) if db_path else config.DB_PATH

    conn = get_connection(target_db)
    logger.info("[Load] Connected to SQLite database: %s", target_db)

    row_counts: Dict[str, int] = {}
    try:
        row_counts[config.TRANSACTIONS_TABLE] = load_dataframe_to_sqlite(
            cleaned_df, config.TRANSACTIONS_TABLE, conn
        )
        row_counts[config.CUSTOMER_INTEL_TABLE] = load_dataframe_to_sqlite(
            customer_intel_df, config.CUSTOMER_INTEL_TABLE, conn
        )
        row_counts[config.PRODUCT_INTEL_TABLE] = load_dataframe_to_sqlite(
            product_summary, config.PRODUCT_INTEL_TABLE, conn
        )
        row_counts[config.CATEGORY_INTEL_TABLE] = load_dataframe_to_sqlite(
            category_summary, config.CATEGORY_INTEL_TABLE, conn
        )
    finally:
        conn.close()
        logger.info("[Load] SQLite connection closed.")

    return row_counts
