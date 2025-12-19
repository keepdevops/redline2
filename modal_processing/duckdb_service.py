#!/usr/bin/env python3
"""
Modal DuckDB Processing Service
Serverless functions for data processing, analysis, and conversions
"""

import modal
import io
import json
from typing import Dict, List, Optional, Any

# Create Modal app
app = modal.App("variosync-duckdb-processor")

# Define image with dependencies
image = modal.Image.debian_slim().pip_install(
    "duckdb>=1.4.2",
    "pandas>=2.3.3",
    "numpy>=2.3.5",
    "pyarrow>=22.0.0",
    "fastparquet>=2024.11.0",
    "polars>=1.35.2",
    "openpyxl>=3.1.5",
    "xlsxwriter>=3.2.9"
)


@app.function(image=image, timeout=600)
def process_csv(
    file_data: bytes,
    filename: str,
    operation: str = "preview",
    query: Optional[str] = None,
    limit: int = 1000
) -> Dict[str, Any]:
    """
    Process CSV/Parquet/Excel files with DuckDB

    Args:
        file_data: File content as bytes
        filename: Original filename (to detect format)
        operation: "preview", "query", "metadata", "stats"
        query: SQL query to execute (for operation="query")
        limit: Max rows to return

    Returns:
        Dict with results and metadata
    """
    import duckdb
    import pandas as pd

    try:
        # Detect file format
        file_ext = filename.lower().split('.')[-1]

        # Load data into pandas
        if file_ext == 'csv':
            df = pd.read_csv(io.BytesIO(file_data))
        elif file_ext in ['parquet', 'pq']:
            df = pd.read_parquet(io.BytesIO(file_data))
        elif file_ext in ['xlsx', 'xls']:
            df = pd.read_excel(io.BytesIO(file_data))
        else:
            return {"error": f"Unsupported file format: {file_ext}"}

        # Create DuckDB connection
        con = duckdb.connect(':memory:')
        con.register('data', df)

        result = {}

        if operation == "preview":
            # Return first N rows
            preview_df = df.head(limit)
            result = {
                "columns": list(df.columns),
                "data": preview_df.to_dict('records'),
                "total_rows": len(df),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
            }

        elif operation == "metadata":
            # Return metadata only
            result = {
                "columns": list(df.columns),
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "memory_usage_mb": df.memory_usage(deep=True).sum() / (1024 * 1024)
            }

        elif operation == "stats":
            # Return statistical summary
            stats_df = df.describe(include='all')
            result = {
                "stats": stats_df.to_dict(),
                "null_counts": df.isnull().sum().to_dict(),
                "unique_counts": df.nunique().to_dict()
            }

        elif operation == "query" and query:
            # Execute custom SQL query
            query_result = con.execute(query).fetchdf()
            result = {
                "columns": list(query_result.columns),
                "data": query_result.head(limit).to_dict('records'),
                "total_rows": len(query_result)
            }

        else:
            result = {"error": "Invalid operation or missing query"}

        con.close()
        return result

    except Exception as e:
        return {"error": str(e)}


@app.function(image=image, timeout=600)
def convert_format(
    file_data: bytes,
    input_format: str,
    output_format: str,
    options: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Convert data between formats using DuckDB

    Args:
        file_data: Input file content as bytes
        input_format: Source format (csv, parquet, xlsx)
        output_format: Target format (csv, parquet, xlsx, json)
        options: Conversion options (delimiter, compression, etc.)

    Returns:
        Dict with converted file data and metadata
    """
    import duckdb
    import pandas as pd

    try:
        options = options or {}

        # Load data
        if input_format == 'csv':
            df = pd.read_csv(io.BytesIO(file_data))
        elif input_format in ['parquet', 'pq']:
            df = pd.read_parquet(io.BytesIO(file_data))
        elif input_format in ['xlsx', 'xls']:
            df = pd.read_excel(io.BytesIO(file_data))
        else:
            return {"error": f"Unsupported input format: {input_format}"}

        # Convert to output format
        output_buffer = io.BytesIO()

        if output_format == 'csv':
            df.to_csv(output_buffer, index=False, **options)
        elif output_format == 'parquet':
            df.to_parquet(output_buffer, index=False, **options)
        elif output_format == 'xlsx':
            df.to_excel(output_buffer, index=False, **options)
        elif output_format == 'json':
            output_buffer.write(df.to_json(orient='records', **options).encode())
        else:
            return {"error": f"Unsupported output format: {output_format}"}

        output_data = output_buffer.getvalue()

        return {
            "file_data": output_data,
            "size_bytes": len(output_data),
            "rows_converted": len(df),
            "columns": list(df.columns)
        }

    except Exception as e:
        return {"error": str(e)}


@app.function(image=image, timeout=300)
def generate_chart_data(
    file_data: bytes,
    filename: str,
    chart_type: str,
    x_column: str,
    y_column: Optional[str] = None,
    group_by: Optional[str] = None,
    aggregation: str = "sum"
) -> Dict[str, Any]:
    """
    Generate aggregated data for charts

    Args:
        file_data: File content as bytes
        filename: Original filename
        chart_type: "line", "bar", "scatter", "histogram"
        x_column: X-axis column
        y_column: Y-axis column
        group_by: Column to group by
        aggregation: "sum", "mean", "count", "min", "max"

    Returns:
        Aggregated data ready for charting
    """
    import duckdb
    import pandas as pd

    try:
        # Load data
        file_ext = filename.lower().split('.')[-1]
        if file_ext == 'csv':
            df = pd.read_csv(io.BytesIO(file_data))
        elif file_ext in ['parquet', 'pq']:
            df = pd.read_parquet(io.BytesIO(file_data))
        else:
            return {"error": f"Unsupported format: {file_ext}"}

        # Create DuckDB connection
        con = duckdb.connect(':memory:')
        con.register('data', df)

        # Build aggregation query
        if group_by:
            query = f"SELECT {x_column}, {aggregation}({y_column}) as value FROM data GROUP BY {x_column} ORDER BY {x_column}"
        else:
            query = f"SELECT {x_column}, {y_column} as value FROM data ORDER BY {x_column}"

        result_df = con.execute(query).fetchdf()
        con.close()

        return {
            "labels": result_df[x_column].tolist(),
            "values": result_df['value'].tolist(),
            "chart_type": chart_type,
            "total_points": len(result_df)
        }

    except Exception as e:
        return {"error": str(e)}


@app.function(image=image, timeout=300)
def run_query(
    file_data: bytes,
    filename: str,
    query: str,
    limit: int = 1000
) -> Dict[str, Any]:
    """
    Execute arbitrary SQL query on data

    Args:
        file_data: File content as bytes
        filename: Original filename
        query: SQL query to execute
        limit: Max rows to return

    Returns:
        Query results
    """
    import duckdb
    import pandas as pd

    try:
        # Load data
        file_ext = filename.lower().split('.')[-1]
        if file_ext == 'csv':
            df = pd.read_csv(io.BytesIO(file_data))
        elif file_ext in ['parquet', 'pq']:
            df = pd.read_parquet(io.BytesIO(file_data))
        elif file_ext in ['xlsx', 'xls']:
            df = pd.read_excel(io.BytesIO(file_data))
        else:
            return {"error": f"Unsupported format: {file_ext}"}

        # Execute query
        con = duckdb.connect(':memory:')
        con.register('data', df)

        result_df = con.execute(query).fetchdf()
        con.close()

        # Limit results
        limited_df = result_df.head(limit)

        return {
            "columns": list(limited_df.columns),
            "data": limited_df.to_dict('records'),
            "total_rows": len(result_df),
            "returned_rows": len(limited_df)
        }

    except Exception as e:
        return {"error": str(e)}


@app.function(image=image, timeout=120)
def get_metadata(file_data: bytes, filename: str) -> Dict[str, Any]:
    """
    Extract metadata from data file

    Args:
        file_data: File content as bytes
        filename: Original filename

    Returns:
        File metadata (columns, types, row count, etc.)
    """
    import pandas as pd

    try:
        file_ext = filename.lower().split('.')[-1]

        if file_ext == 'csv':
            df = pd.read_csv(io.BytesIO(file_data), nrows=5)
            total_rows = sum(1 for _ in io.BytesIO(file_data)) - 1  # Approximate
        elif file_ext in ['parquet', 'pq']:
            df = pd.read_parquet(io.BytesIO(file_data))
            total_rows = len(df)
        elif file_ext in ['xlsx', 'xls']:
            df = pd.read_excel(io.BytesIO(file_data), nrows=5)
            total_rows = len(pd.read_excel(io.BytesIO(file_data)))
        else:
            return {"error": f"Unsupported format: {file_ext}"}

        return {
            "filename": filename,
            "format": file_ext,
            "columns": list(df.columns),
            "total_columns": len(df.columns),
            "total_rows": total_rows,
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "sample_data": df.head(3).to_dict('records')
        }

    except Exception as e:
        return {"error": str(e)}
