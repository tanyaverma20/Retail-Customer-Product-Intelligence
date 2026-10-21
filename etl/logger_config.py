"""
etl/logger_config.py — Centralised logging configuration.

Call ``setup_logging()`` once at application startup to configure both a
rotating file handler (logs/etl_pipeline.log) and a console handler.
"""

from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path
from typing import Optional


def setup_logging(
    log_dir: Optional[Path] = None,
    log_level: int = logging.INFO,
    console: bool = True,
) -> logging.Logger:
    """Configure the root logger for the ETL pipeline.

    Parameters
    ----------
    log_dir : Path | None
        Directory for the rotating log file.  Defaults to ``logs/`` relative
        to the repository root.  Pass ``None`` to suppress file logging.
    log_level : int
        Logging level (e.g. ``logging.DEBUG``, ``logging.INFO``).
    console : bool
        Whether to attach a StreamHandler to stdout.

    Returns
    -------
    logging.Logger
        The root logger, now configured.
    """
    root_logger = logging.getLogger()

    # Remove any handlers added by previous calls (useful in tests)
    root_logger.handlers.clear()
    root_logger.setLevel(log_level)

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)-8s] %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    if console:
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        ch.setFormatter(fmt)
        root_logger.addHandler(ch)

    # Rotating file handler
    if log_dir is not None:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "etl_pipeline.log"
        fh = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3,
            encoding="utf-8",
        )
        fh.setLevel(log_level)
        fh.setFormatter(fmt)
        root_logger.addHandler(fh)

    return root_logger
