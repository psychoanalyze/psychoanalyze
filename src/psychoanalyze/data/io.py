"""I/O utilities for loading psychophysics data from various file formats.

This module provides functions for reading trial data from different file formats
including CSV, Parquet, and ZIP archives. These are particularly useful for
loading data from file uploads or batch processing pipelines.
"""

import io
import zipfile
from pathlib import Path

import polars as pl


def read_from_bytes(
    contents: bytes,
    filename: str,
    csv_entry: str = "trials.csv",
) -> pl.DataFrame:
    """Read trial data from bytes based on filename extension.

    Supports multiple file formats:
    - CSV (.csv): Plain CSV files
    - Parquet (.parquet, .pq): Apache Parquet files
    - ZIP (.zip): ZIP archives containing a CSV file

    Args:
        contents: Raw bytes of the file
        filename: Original filename (used for format detection)
        csv_entry: Name of CSV file to extract from ZIP archives

    Returns:
        DataFrame with trial data

    Raises:
        FileNotFoundError: If ZIP archive doesn't contain the expected CSV file
        ValueError: If file format cannot be determined

    Example:
        >>> with open("trials.csv", "rb") as f:
        ...     contents = f.read()
        >>> df = read_from_bytes(contents, "trials.csv")
        >>> df.columns
        ['Block', 'Intensity', 'Result']
    """
    filename_lower = filename.lower()

    if filename_lower.endswith(".zip") or "zip" in filename_lower:
        return _read_from_zip(contents, csv_entry)
    if filename_lower.endswith(".parquet") or filename_lower.endswith(".pq"):
        return _read_from_parquet(contents)
    if filename_lower.endswith(".csv"):
        return _read_from_csv(contents)

    # Try CSV as fallback
    return _read_from_csv(contents)


def _read_from_csv(contents: bytes) -> pl.DataFrame:
    """Read trial data from CSV bytes."""
    return pl.read_csv(io.BytesIO(contents))


def _read_from_parquet(contents: bytes) -> pl.DataFrame:
    """Read trial data from Parquet bytes."""
    return pl.read_parquet(io.BytesIO(contents))


def _read_from_zip(contents: bytes, csv_entry: str = "trials.csv") -> pl.DataFrame:
    """Read trial data from a ZIP archive containing a CSV file.

    Args:
        contents: Raw bytes of the ZIP file
        csv_entry: Name of the CSV file to extract from the archive

    Returns:
        DataFrame with trial data

    Raises:
        FileNotFoundError: If the CSV file is not found in the archive
    """
    with zipfile.ZipFile(io.BytesIO(contents)) as z:
        if csv_entry not in z.namelist():
            # Try to find any CSV file
            csv_files = [n for n in z.namelist() if n.endswith(".csv")]
            if not csv_files:
                msg = f"No CSV file found in ZIP archive. Expected '{csv_entry}'"
                raise FileNotFoundError(msg)
            csv_entry = csv_files[0]
        return pl.read_csv(z.open(csv_entry))


def read_file(path: str | Path) -> pl.DataFrame:
    """Read trial data from a file path.

    Supports the same formats as read_from_bytes():
    - CSV (.csv)
    - Parquet (.parquet, .pq)
    - ZIP (.zip)

    Args:
        path: Path to the file

    Returns:
        DataFrame with trial data

    Example:
        >>> df = read_file("data/trials.csv")
        >>> df = read_file("data/experiment.parquet")
    """
    path = Path(path)
    contents = path.read_bytes()
    return read_from_bytes(contents, path.name)
