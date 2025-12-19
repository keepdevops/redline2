#!/usr/bin/env python3
"""
Modal Client for VarioSync
Calls Modal serverless functions for DuckDB data processing
"""

import os
import logging
from typing import Dict, List, Optional, Any
import modal

logger = logging.getLogger(__name__)

# Modal app reference
MODAL_APP_NAME = "variosync-duckdb-processor"


class ModalClient:
    """Client for calling Modal DuckDB processing functions"""

    def __init__(self):
        """Initialize Modal client"""
        try:
            # Get Modal function references
            self.app = modal.Func.lookup(MODAL_APP_NAME, "process_csv")
            logger.info("Modal client initialized successfully")
        except Exception as e:
            logger.warning(f"Modal client initialization failed: {str(e)}")
            self.app = None

    def _is_available(self) -> bool:
        """Check if Modal is available"""
        return self.app is not None

    def process_csv(
        self,
        file_data: bytes,
        filename: str,
        operation: str = "preview",
        query: Optional[str] = None,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """
        Process CSV/Parquet/Excel files

        Args:
            file_data: File content as bytes
            filename: Original filename
            operation: "preview", "query", "metadata", "stats"
            query: SQL query (for operation="query")
            limit: Max rows to return

        Returns:
            Processing results
        """
        if not self._is_available():
            return {"error": "Modal processing not available"}

        try:
            func = modal.Func.lookup(MODAL_APP_NAME, "process_csv")
            result = func.remote(
                file_data=file_data,
                filename=filename,
                operation=operation,
                query=query,
                limit=limit
            )
            return result
        except Exception as e:
            logger.error(f"Modal process_csv error: {str(e)}")
            return {"error": str(e)}

    def convert_format(
        self,
        file_data: bytes,
        input_format: str,
        output_format: str,
        options: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Convert data between formats

        Args:
            file_data: Input file bytes
            input_format: Source format (csv, parquet, xlsx)
            output_format: Target format (csv, parquet, xlsx, json)
            options: Conversion options

        Returns:
            Converted file data and metadata
        """
        if not self._is_available():
            return {"error": "Modal processing not available"}

        try:
            func = modal.Func.lookup(MODAL_APP_NAME, "convert_format")
            result = func.remote(
                file_data=file_data,
                input_format=input_format,
                output_format=output_format,
                options=options or {}
            )
            return result
        except Exception as e:
            logger.error(f"Modal convert_format error: {str(e)}")
            return {"error": str(e)}

    def generate_chart_data(
        self,
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
            file_data: File content
            filename: Original filename
            chart_type: "line", "bar", "scatter", "histogram"
            x_column: X-axis column
            y_column: Y-axis column
            group_by: Group by column
            aggregation: "sum", "mean", "count", "min", "max"

        Returns:
            Chart data ready for visualization
        """
        if not self._is_available():
            return {"error": "Modal processing not available"}

        try:
            func = modal.Func.lookup(MODAL_APP_NAME, "generate_chart_data")
            result = func.remote(
                file_data=file_data,
                filename=filename,
                chart_type=chart_type,
                x_column=x_column,
                y_column=y_column,
                group_by=group_by,
                aggregation=aggregation
            )
            return result
        except Exception as e:
            logger.error(f"Modal generate_chart_data error: {str(e)}")
            return {"error": str(e)}

    def run_query(
        self,
        file_data: bytes,
        filename: str,
        query: str,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """
        Execute SQL query on data

        Args:
            file_data: File content
            filename: Original filename
            query: SQL query to execute
            limit: Max rows to return

        Returns:
            Query results
        """
        if not self._is_available():
            return {"error": "Modal processing not available"}

        try:
            func = modal.Func.lookup(MODAL_APP_NAME, "run_query")
            result = func.remote(
                file_data=file_data,
                filename=filename,
                query=query,
                limit=limit
            )
            return result
        except Exception as e:
            logger.error(f"Modal run_query error: {str(e)}")
            return {"error": str(e)}

    def get_metadata(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Extract metadata from file

        Args:
            file_data: File content
            filename: Original filename

        Returns:
            File metadata
        """
        if not self._is_available():
            return {"error": "Modal processing not available"}

        try:
            func = modal.Func.lookup(MODAL_APP_NAME, "get_metadata")
            result = func.remote(file_data=file_data, filename=filename)
            return result
        except Exception as e:
            logger.error(f"Modal get_metadata error: {str(e)}")
            return {"error": str(e)}


# Global Modal client instance
modal_client = ModalClient()
