"""
Airtable Lakeflow Connector

Implements the LakeflowConnect interface for Airtable data sources.
Supports:
- Table discovery
- Schema inference from Airtable field types
- Incremental syncs based on createdTime or Last Modified fields
- Full-refresh snapshots
"""

import requests
import time
from datetime import datetime
from typing import Iterator
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType,
    BooleanType,
    ArrayType,
    TimestampType,
)

from ..interface.lakeflow_connect import LakeflowConnect


class AirtableLakeflowConnector(LakeflowConnect):
    """
    Lakeflow connector for Airtable.
    
    Configuration options:
    - token or bearer_token: Airtable Personal Access Token (required)
      Note: UC connections use 'bearer_token', direct usage uses 'token'
    - base_id: Airtable base ID (required)
    - batch_size: Number of records per API request (default: 100)
    - max_retries: Maximum number of retry attempts (default: 3)
    - timeout: Request timeout in seconds (default: 30)
    """
    
    def __init__(self, options: dict[str, str]) -> None:
        """
        Initialize Airtable connector.
        
        Args:
            options: Must contain 'token' (or 'bearer_token') and 'base_id'
        """
        # Extract required options
        # Support both 'token' and 'bearer_token' for UC connection compatibility
        token = options.get("token") or options.get("bearer_token")
        if not token:
            raise ValueError("Airtable connector requires 'token' or 'bearer_token' in options")
        
        self.base_id = options.get("base_id")
        if not self.base_id:
            raise ValueError("Airtable connector requires 'base_id' in options")
        
        # Optional configuration
        self.batch_size = int(options.get("batch_size", 100))
        self.max_retries = int(options.get("max_retries", 3))
        self.timeout = int(options.get("timeout", 30))
        
        # Base URL - configurable for UC connections or custom endpoints
        self.base_url = options.get("base_url", "https://api.airtable.com")
        
        # Initialize HTTP session
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        })
    
    def list_tables(self) -> list[str]:
        """
        List all tables in the Airtable base.
        
        Returns:
            List of table names
        """
        url = f"{self.base_url}/v0/meta/bases/{self.base_id}/tables"
        
        for attempt in range(self.max_retries):
            try:
                response = self._session.get(url, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                return [table["name"] for table in data.get("tables", [])]
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise ConnectionError(f"Failed to list tables: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def get_table_schema(self, table_name: str, table_options: dict[str, str]) -> StructType:
        """
        Get Spark schema for an Airtable table.
        
        Args:
            table_name: Name of the Airtable table
            table_options: Additional options (unused for Airtable)
        
        Returns:
            StructType representing the table schema
        """
        url = f"{self.base_url}/v0/meta/bases/{self.base_id}/tables"
        
        for attempt in range(self.max_retries):
            try:
                response = self._session.get(url, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                
                # Find the table
                table = next(
                    (t for t in data.get("tables", []) if t["name"] == table_name),
                    None
                )
                if not table:
                    raise ValueError(f"Table '{table_name}' not found in base '{self.base_id}'")
                
                # Build schema
                fields = [
                    StructField("id", StringType(), False),
                    StructField("createdTime", StringType(), True),
                ]
                
                # Map Airtable field types to Spark types
                for field in table.get("fields", []):
                    field_type = field.get("type", "singleLineText")
                    spark_type = self._map_airtable_type_to_spark(field_type)
                    # Sanitize field name for Delta Lake compatibility
                    sanitized_name = self._sanitize_column_name(field["name"])
                    fields.append(StructField(sanitized_name, spark_type, True))
                
                return StructType(fields)
                
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise ConnectionError(f"Failed to get schema for table '{table_name}': {e}")
                time.sleep(2 ** attempt)
    
    def read_table_metadata(self, table_name: str, table_options: dict[str, str]) -> dict:
        """
        Get metadata for table ingestion.
        
        Args:
            table_name: Name of the Airtable table
            table_options: Additional options (unused for Airtable)
        
        Returns:
            Metadata dict with primary_keys, cursor_field, ingestion_type
        """
        return {
            "primary_keys": ["id"],  # Airtable always uses 'id' as primary key
            "cursor_field": "createdTime",  # Use createdTime for incremental reads
            "ingestion_type": "snapshot",  # Default to snapshot (full refresh)
        }
    
    def read_table(
        self,
        table_name: str,
        start_offset: dict,
        table_options: dict[str, str]
    ) -> tuple[Iterator[dict], dict]:
        """
        Read data from an Airtable table.
        
        Args:
            table_name: Name of the table to read
            start_offset: Starting position for incremental reads
                         e.g., {'createdTime': '2025-01-01T00:00:00.000Z'}
            table_options: Additional options (e.g., filter formulas)
        
        Returns:
            (records_iterator, next_offset)
        """
        url = f"{self.base_url}/v0/{self.base_id}/{table_name}"
        params = {"pageSize": self.batch_size}
        
        # Add filter if starting from offset
        if start_offset and "createdTime" in start_offset:
            # Airtable filterByFormula: {createdTime} > 'timestamp'
            filter_formula = f"{{createdTime}} > '{start_offset['createdTime']}'"
            params["filterByFormula"] = filter_formula
        
        # Add custom filter from table_options if provided
        if table_options.get("filter_formula"):
            custom_filter = table_options["filter_formula"]
            if "filterByFormula" in params:
                # Combine filters with AND
                params["filterByFormula"] = f"AND({params['filterByFormula']}, {custom_filter})"
            else:
                params["filterByFormula"] = custom_filter
        
        def record_generator():
            """Generator that yields records"""
            offset = None
            latest_created_time = start_offset.get("createdTime") if start_offset else None
            
            while True:
                current_params = params.copy()
                if offset:
                    current_params["offset"] = offset
                
                for attempt in range(self.max_retries):
                    try:
                        response = self._session.get(url, params=current_params, timeout=self.timeout)
                        response.raise_for_status()
                        data = response.json()
                        break
                    except requests.exceptions.RequestException as e:
                        if attempt == self.max_retries - 1:
                            raise ConnectionError(f"Failed to read table '{table_name}': {e}")
                        time.sleep(2 ** attempt)
                
                records = data.get("records", [])
                if not records:
                    break
                
                for record in records:
                    fields = record.get("fields", {})
                    
                    # Convert integers to floats and sanitize column names
                    normalized_fields = {}
                    for key, value in fields.items():
                        # Sanitize the key (column name)
                        sanitized_key = self._sanitize_column_name(key)
                        
                        # Convert int to float for DoubleType compatibility
                        if isinstance(value, int) and not isinstance(value, bool):
                            normalized_fields[sanitized_key] = float(value)
                        else:
                            normalized_fields[sanitized_key] = value
                    
                    record_dict = {
                        "id": record["id"],
                        "createdTime": record.get("createdTime"),
                        **normalized_fields
                    }
                    
                    # Track latest timestamp
                    if record_dict.get("createdTime"):
                        if not latest_created_time or record_dict["createdTime"] > latest_created_time:
                            latest_created_time = record_dict["createdTime"]
                    
                    yield record_dict
                
                # Check for next page
                offset = data.get("offset")
                if not offset:
                    break
            
            # Return next offset for incremental reads
            nonlocal next_offset_holder
            next_offset_holder = {
                "createdTime": latest_created_time
            } if latest_created_time else {}
        
        # Holder for next offset (generator needs to populate this)
        next_offset_holder = {}
        
        return record_generator(), next_offset_holder
    
    def _sanitize_column_name(self, col_name: str) -> str:
        """
        Sanitize column name for Delta Lake compatibility.
        
        Delta Lake doesn't allow spaces and special characters like (), $, #, etc.
        
        Args:
            col_name: Original column name from Airtable
        
        Returns:
            Sanitized column name
        """
        # Replace common special characters
        sanitized = col_name.replace(" ", "_")
        sanitized = sanitized.replace("(", "")
        sanitized = sanitized.replace(")", "")
        sanitized = sanitized.replace("$", "dollar")
        sanitized = sanitized.replace("#", "num")
        sanitized = sanitized.replace(",", "")
        sanitized = sanitized.replace(";", "")
        sanitized = sanitized.replace("{", "")
        sanitized = sanitized.replace("}", "")
        sanitized = sanitized.replace("\n", "")
        sanitized = sanitized.replace("\t", "")
        sanitized = sanitized.replace("=", "")
        # Remove any remaining special characters
        sanitized = "".join(c if c.isalnum() or c == "_" else "_" for c in sanitized)
        # Ensure it doesn't start with a number
        if sanitized and sanitized[0].isdigit():
            sanitized = "col_" + sanitized
        return sanitized.lower()
    
    def _map_airtable_type_to_spark(self, airtable_type: str) -> type:
        """
        Map Airtable field type to Spark type.
        
        Args:
            airtable_type: Airtable field type string
        
        Returns:
            Spark type class
        """
        type_mapping = {
            "number": DoubleType(),
            "checkbox": BooleanType(),
            "multipleSelects": ArrayType(StringType()),
            "multipleRecordLinks": ArrayType(StringType()),
            "multipleAttachments": ArrayType(StringType()),
            "date": StringType(),  # Keep as string for now
            "dateTime": StringType(),  # Keep as string for now
            # Default to StringType for all other types
        }
        return type_mapping.get(airtable_type, StringType())

