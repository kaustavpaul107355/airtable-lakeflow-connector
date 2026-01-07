"""
Lakeflow Python Data Source

This module implements a Spark Python Data Source that wraps the LakeflowConnect interface.
It allows any connector implementing LakeflowConnect to be used as a Spark data source.
"""

from pyspark.sql.datasource import (
    DataSource,
    SimpleDataSourceStreamReader,
    DataSourceReader,
)
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    ArrayType,
)

# Metadata table name
METADATA_TABLE = "_lakeflow_metadata"
TABLE_NAME = "tableName"
TABLE_NAME_LIST = "tableNameList"


class LakeflowStreamReader(SimpleDataSourceStreamReader):
    """Stream reader for Lakeflow connectors"""
    
    def __init__(self, options, schema, lakeflow_connect):
        self.options = options
        self.schema = schema
        self.lakeflow_connect = lakeflow_connect
        self.current_offset = {}
    
    def initialOffset(self):
        """Return initial offset for streaming"""
        return {}
    
    def read(self, start_offset):
        """Read data from start_offset"""
        table = self.options[TABLE_NAME]
        records_iter, next_offset = self.lakeflow_connect.read_table(
            table,
            start_offset or {},
            self.options
        )
        self.current_offset = next_offset
        return list(records_iter)
    
    def latestOffset(self):
        """Return latest offset after read"""
        return self.current_offset
    
    def commit(self, end_offset):
        """Commit the offset"""
        pass


class LakeflowBatchReader(DataSourceReader):
    """Batch reader for Lakeflow connectors"""
    
    def __init__(self, options, schema, lakeflow_connect):
        self.options = options
        self.schema = schema
        self.lakeflow_connect = lakeflow_connect
    
    def read(self, partition):
        """Read data for this partition"""
        table = self.options[TABLE_NAME]
        
        # For metadata table, return table list with metadata
        if table == METADATA_TABLE:
            tables = self.lakeflow_connect.list_tables()
            for table_name in tables:
                metadata = self.lakeflow_connect.read_table_metadata(table_name, self.options)
                yield (
                    table_name,
                    metadata.get("primary_keys", []),
                    metadata.get("cursor_field"),
                    metadata.get("ingestion_type", "snapshot"),
                )
        else:
            # For regular tables, read data
            start_offset = {}
            records_iter, _ = self.lakeflow_connect.read_table(
                table,
                start_offset,
                self.options
            )
            for record in records_iter:
                yield tuple(record.get(field.name) for field in self.schema.fields)


class LakeflowSource(DataSource):
    """
    Spark Data Source for Lakeflow Community Connectors.
    
    This data source wraps a specific connector class and handles UC connection resolution.
    """
    
    # Class variable to store the connector class
    _connector_class = None
    
    def __init__(self, options):
        self.options = options
        
        if self._connector_class is None:
            raise ValueError(
                "No connector class registered. "
                "Call LakeflowSource.register(spark, source_name, connector_class) first."
            )
        
        # Initialize the connector with options
        # When .option("databricks.connection", "name") is used,
        # Spark automatically resolves the UC connection and passes its options here
        self.lakeflow_connect = self._connector_class(options)
    
    @classmethod
    def name(cls):
        """Name of this data source"""
        return "lakeflow_connect"
    
    @classmethod
    def register(cls, spark, source_name: str, connector_class):
        """
        Register a connector class as a Spark Data Source.
        
        Args:
            spark: SparkSession
            source_name: Name of the source (e.g., "airtable")
            connector_class: The connector class (must implement LakeflowConnect interface)
        
        Example:
            from sources.airtable.airtable import AirtableLakeflowConnector
            from pipeline.lakeflow_python_source import LakeflowSource
            
            LakeflowSource.register(
                spark, 
                source_name="airtable", 
                connector_class=AirtableLakeflowConnector
            )
        """
        cls._connector_class = connector_class
        spark.dataSource.register(cls)
        print(f"✅ Registered '{source_name}' connector as 'lakeflow_connect' data source")
    
    def schema(self):
        """Return the schema for the requested table"""
        table = self.options[TABLE_NAME]
        
        if table == METADATA_TABLE:
            # Schema for metadata table
            return StructType([
                StructField("tableName", StringType(), False),
                StructField("primary_keys", ArrayType(StringType()), True),
                StructField("cursor_field", StringType(), True),
                StructField("ingestion_type", StringType(), True),
            ])
        else:
            # Schema for data table
            return self.lakeflow_connect.get_table_schema(table, self.options)
    
    def reader(self, schema: StructType):
        """Return a batch reader"""
        return LakeflowBatchReader(self.options, schema, self.lakeflow_connect)
    
    def simpleStreamReader(self, schema: StructType):
        """Return a streaming reader"""
        return LakeflowStreamReader(self.options, schema, self.lakeflow_connect)

