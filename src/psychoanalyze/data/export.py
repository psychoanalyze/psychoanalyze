"""Export utilities for psychophysics data.

This module provides functions for exporting trial, points, and block data
to various file formats including CSV (zipped), JSON, Parquet, and DuckDB.
"""

import io
import tempfile
import zipfile
from pathlib import Path

import polars as pl


def to_csv_zip(
    trials: pl.DataFrame,
    points: pl.DataFrame | None = None,
    blocks: pl.DataFrame | None = None,
) -> bytes:
    """Export data to a ZIP archive containing CSV files.

    Creates a ZIP archive with separate CSV files for each data level:
    - trials.csv: Trial-level data (always included)
    - points.csv: Point-level aggregated data (if provided)
    - blocks.csv: Block-level summary data (if provided)

    Args:
        trials: Trial-level DataFrame with Intensity, Result, Block columns
        points: Optional point-level DataFrame with Hit Rate, n trials columns
        blocks: Optional block-level DataFrame with fitted parameters

    Returns:
        Bytes of the ZIP archive

    Example:
        >>> zip_bytes = to_csv_zip(trials_df, points_df, blocks_df)
        >>> with open("data.zip", "wb") as f:
        ...     f.write(zip_bytes)
    """
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(
        zip_buffer,
        mode="a",
        compression=zipfile.ZIP_DEFLATED,
        allowZip64=False,
    ) as zip_file:
        # Always include trials
        csv_buffer = io.StringIO()
        trials.write_csv(csv_buffer)
        zip_file.writestr("trials.csv", csv_buffer.getvalue())

        # Include points if provided
        if points is not None:
            csv_buffer = io.StringIO()
            points.write_csv(csv_buffer)
            zip_file.writestr("points.csv", csv_buffer.getvalue())

        # Include blocks if provided
        if blocks is not None:
            csv_buffer = io.StringIO()
            blocks.write_csv(csv_buffer)
            zip_file.writestr("blocks.csv", csv_buffer.getvalue())

    zip_buffer.seek(0)
    return zip_buffer.read()


def to_json(df: pl.DataFrame) -> bytes:
    """Export DataFrame to JSON bytes.

    Uses pandas JSON serialization for compatibility with common tools.

    Args:
        df: DataFrame to export

    Returns:
        UTF-8 encoded JSON bytes

    Example:
        >>> json_bytes = to_json(points_df)
        >>> data = json.loads(json_bytes.decode("utf-8"))
    """
    return df.to_pandas().to_json().encode("utf-8")


def to_parquet(df: pl.DataFrame) -> bytes:
    """Export DataFrame to Parquet bytes.

    Parquet is a columnar format that provides efficient compression
    and is well-suited for large datasets.

    Args:
        df: DataFrame to export

    Returns:
        Parquet file bytes

    Example:
        >>> parquet_bytes = to_parquet(trials_df)
        >>> with open("trials.parquet", "wb") as f:
        ...     f.write(parquet_bytes)
    """
    buffer = io.BytesIO()
    df.write_parquet(buffer)
    buffer.seek(0)
    return buffer.read()


def to_duckdb(
    trials: pl.DataFrame,
    points: pl.DataFrame | None = None,
    blocks: pl.DataFrame | None = None,
    db_name: str = "psychoanalyze",
) -> bytes:
    """Export data to a DuckDB database file.

    Creates a DuckDB database with tables for each data level:
    - trials: Trial-level data (always included)
    - points: Point-level aggregated data (if provided)
    - blocks: Block-level summary data (if provided)

    Args:
        trials: Trial-level DataFrame
        points: Optional point-level DataFrame
        blocks: Optional block-level DataFrame
        db_name: Name for the database (not used in output, for documentation)

    Returns:
        Bytes of the DuckDB database file

    Example:
        >>> db_bytes = to_duckdb(trials_df, points_df, blocks_df)
        >>> with open("data.duckdb", "wb") as f:
        ...     f.write(db_bytes)
    """
    import duckdb

    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / f"{db_name}.duckdb"
        connection = duckdb.connect(str(db_path))

        # Register and create trials table
        connection.register("trials_df", trials.to_pandas())
        connection.execute("CREATE TABLE trials AS SELECT * FROM trials_df")

        # Register and create points table if provided
        if points is not None:
            connection.register("points_df", points.to_pandas())
            connection.execute("CREATE TABLE points AS SELECT * FROM points_df")

        # Register and create blocks table if provided
        if blocks is not None:
            connection.register("blocks_df", blocks.to_pandas())
            connection.execute("CREATE TABLE blocks AS SELECT * FROM blocks_df")

        connection.close()
        return db_path.read_bytes()


def write_csv_zip(
    path: str | Path,
    trials: pl.DataFrame,
    points: pl.DataFrame | None = None,
    blocks: pl.DataFrame | None = None,
) -> None:
    """Write data to a ZIP file containing CSVs.

    Args:
        path: Output file path
        trials: Trial-level DataFrame
        points: Optional point-level DataFrame
        blocks: Optional block-level DataFrame
    """
    Path(path).write_bytes(to_csv_zip(trials, points, blocks))


def write_parquet(path: str | Path, df: pl.DataFrame) -> None:
    """Write DataFrame to a Parquet file.

    Args:
        path: Output file path
        df: DataFrame to write
    """
    Path(path).write_bytes(to_parquet(df))


def write_duckdb(
    path: str | Path,
    trials: pl.DataFrame,
    points: pl.DataFrame | None = None,
    blocks: pl.DataFrame | None = None,
) -> None:
    """Write data to a DuckDB database file.

    Args:
        path: Output file path
        trials: Trial-level DataFrame
        points: Optional point-level DataFrame
        blocks: Optional block-level DataFrame
    """
    Path(path).write_bytes(to_duckdb(trials, points, blocks))
