"""
etl/extract.py — Extract stage of the ETL pipeline.

Responsibilities
----------------
* Load source CSV file from disk.
* Validate file availability and that all required columns are present.
* Return a raw DataFrame; no transformations are applied here.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

import pandas as pd

from etl.config import RAW_REQUIRED_COLUMNS

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract(
    source_path: Path,
    required_columns: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Load and minimally validate the raw CSV source file.

    Parameters
    ----------
    source_path : Path
        Absolute path to the raw CSV file.
    required_columns : list[str] | None
        Columns that must exist.  Defaults to ``RAW_REQUIRED_COLUMNS``.

    Returns
    -------
    pd.DataFrame
        Raw, unmodified DataFrame as read from the CSV.

    Raises
    ------
    FileNotFoundError
        If ``source_path`` does not exist.
    ValueError
        If one or more required columns are missing from the file.
    """
    if required_columns is None:
        required_columns = RAW_REQUIRED_COLUMNS

    # ---- File availability check ------------------------------------------
    source_path = Path(source_path)
    if not source_path.exists():
        raise FileNotFoundError(
            f"[Extract] Source file not found: {source_path}"
        )

    logger.info("[Extract] Loading raw CSV from: %s", source_path)
    raw_df = pd.read_csv(source_path)
    logger.info(
        "[Extract] Raw dataset loaded — rows: %d, columns: %d",
        raw_df.shape[0],
        raw_df.shape[1],
    )

    # ---- Required-column presence check -----------------------------------
    missing_cols = [c for c in required_columns if c not in raw_df.columns]
    if missing_cols:
        raise ValueError(
            f"[Extract] Required columns missing from source file: {missing_cols}"
        )

    logger.info("[Extract] All %d required columns present.", len(required_columns))
    return raw_df


def get_raw_row_count(source_path: Path) -> int:
    """Return the number of data rows in the raw CSV (excluding header).

    Parameters
    ----------
    source_path : Path
        Path to the raw CSV file.

    Returns
    -------
    int
        Row count (header excluded).
    """
    source_path = Path(source_path)
    if not source_path.exists():
        raise FileNotFoundError(f"[Extract] File not found: {source_path}")
    df = pd.read_csv(source_path)
    return len(df)
