"""
Lakeflow Connect Interface

This is the base interface that all Lakeflow community connectors must implement.
It provides a standardized way to:
- List available tables
- Get table schemas
- Read table metadata (primary keys, cursor fields, ingestion types)
- Read table data with incremental support
"""

from typing import Iterator
from pyspark.sql.types import StructType


class LakeflowConnect:
    """
    Base interface for Lakeflow community connectors.
    
    All connectors must implement these methods to work with the
    Lakeflow ingestion pipeline and Spark Data Source API.
    """
    
    def __init__(self, options: dict[str, str]) -> None:
        """
        Initialize the connector with configuration options.
        
        Args:
            options: Dictionary containing connection parameters.
                    Common keys include:
                    - 'token': Authentication token/API key
                    - 'connection_name': Unity Catalog connection name
                    - Other source-specific configuration
        
        Raises:
            ValueError: If required options are missing
            ConnectionError: If connection cannot be established
        """
        raise NotImplementedError("Subclasses must implement __init__")
    
    def list_tables(self) -> list[str]:
        """
        List all available tables in the source system.
        
        Returns:
            List of table names as strings
            
        Raises:
            ConnectionError: If unable to fetch table list
        """
        raise NotImplementedError("Subclasses must implement list_tables")
    
    def get_table_schema(self, table_name: str, table_options: dict[str, str]) -> StructType:
        """
        Get the Spark schema for a specific table.
        
        Args:
            table_name: Name of the table
            table_options: Additional table-specific options
        
        Returns:
            PySpark StructType representing the table schema
            
        Raises:
            ValueError: If table doesn't exist
            ConnectionError: If unable to fetch schema
        """
        raise NotImplementedError("Subclasses must implement get_table_schema")
    
    def read_table_metadata(self, table_name: str, table_options: dict[str, str]) -> dict:
        """
        Get metadata about how to ingest this table.
        
        Args:
            table_name: Name of the table
            table_options: Additional table-specific options
        
        Returns:
            Dictionary containing:
            - 'primary_keys': list[str] - Column names that form the primary key
            - 'cursor_field': str - Column to use for incremental reads (optional)
            - 'ingestion_type': str - One of 'snapshot', 'cdc', 'append'
        
        Raises:
            ValueError: If table doesn't exist
        """
        raise NotImplementedError("Subclasses must implement read_table_metadata")
    
    def read_table(
        self, 
        table_name: str, 
        start_offset: dict, 
        table_options: dict[str, str]
    ) -> tuple[Iterator[dict], dict]:
        """
        Read data from a table, optionally starting from an offset.
        
        Args:
            table_name: Name of the table to read
            start_offset: Dictionary containing the starting position for incremental reads.
                         Empty dict {} means read from beginning.
                         Example: {'last_modified': '2025-01-01T00:00:00Z'}
            table_options: Additional table-specific options
        
        Returns:
            Tuple of (records_iterator, next_offset):
            - records_iterator: Iterator yielding records as dictionaries
            - next_offset: Dictionary to use for the next incremental read
        
        Raises:
            ValueError: If table doesn't exist
            ConnectionError: If unable to read data
        """
        raise NotImplementedError("Subclasses must implement read_table")



