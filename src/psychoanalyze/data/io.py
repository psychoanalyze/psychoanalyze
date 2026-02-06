import io
import tempfile
import zipfile
from pathlib import Path

import polars as pl


def read_from_bytes(
    contents: bytes,
    filename: str,
    csv_entry: str = "trials.csv",
) -> pl.DataFrame:

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
    return pl.read_csv(io.BytesIO(contents))


def _read_from_parquet(contents: bytes) -> pl.DataFrame:
    return pl.read_parquet(io.BytesIO(contents))


def _read_from_zip(contents: bytes, csv_entry: str = "trials.csv") -> pl.DataFrame:
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
    path = Path(path)
    contents = path.read_bytes()
    return read_from_bytes(contents, path.name)


def to_csv_zip(
    trials: pl.DataFrame,
    points: pl.DataFrame | None = None,
    blocks: pl.DataFrame | None = None,
) -> bytes:

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

    return df.to_pandas().to_json().encode("utf-8")


def to_parquet(df: pl.DataFrame) -> bytes:

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

    Path(path).write_bytes(to_csv_zip(trials, points, blocks))


def write_parquet(path: str | Path, df: pl.DataFrame) -> None:

    Path(path).write_bytes(to_parquet(df))


def write_duckdb(
    path: str | Path,
    trials: pl.DataFrame,
    points: pl.DataFrame | None = None,
    blocks: pl.DataFrame | None = None,
) -> None:

    Path(path).write_bytes(to_duckdb(trials, points, blocks))
