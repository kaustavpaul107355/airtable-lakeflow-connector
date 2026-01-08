# pylint: disable=no-member
from typing import List
from pyspark import pipelines as sdp
from pyspark.sql.functions import col
from libs.spec_parser import SpecParser


def _create_cdc_table(
    spark,
    connection_name: str,
    source_table: str,
    destination_table: str,
    primary_keys: List[str],
    sequence_by: str,
    scd_type: str,
    view_name: str,
    table_config: dict[str, str],
) -> None:
    """Create CDC table using streaming and apply_changes"""

    @sdp.view(name=view_name)
    def v():
        return (
            spark.readStream.format("lakeflow_connect")
            .option("databricks.connection", connection_name)
            .option("tableName", source_table)
            .options(**table_config)
            .load()
        )

    sdp.create_streaming_table(name=destination_table)
    sdp.apply_changes(
        target=destination_table,
        source=view_name,
        keys=primary_keys,
        sequence_by=col(sequence_by),
        stored_as_scd_type=scd_type,
    )


def _create_snapshot_table(
    spark,
    connection_name: str,
    source_table: str,
    destination_table: str,
    primary_keys: List[str],
    scd_type: str,
    view_name: str,
    table_config: dict[str, str],
) -> None:
    """Create snapshot table using apply_changes_from_snapshot"""

    @sdp.view(name=view_name)
    def snapshot_view():
        return (
            spark.read.format("lakeflow_connect")
            .option("databricks.connection", connection_name)
            .option("tableName", source_table)
            .options(**table_config)
            .load()
        )

    sdp.create_streaming_table(name=destination_table)
    sdp.apply_changes_from_snapshot(
        target=destination_table,
        source=view_name,
        keys=primary_keys,
        stored_as_scd_type=scd_type,
    )


def _create_append_table(
    spark,
    connection_name: str,
    source_table: str,
    destination_table: str,
    view_name: str,
    table_config: dict[str, str],
) -> None:
    """Create append-only table using append_flow"""

    sdp.create_streaming_table(name=destination_table)

    @sdp.append_flow(name=view_name, target=destination_table)
    def af():
        return (
            spark.readStream.format("lakeflow_connect")
            .option("databricks.connection", connection_name)
            .option("tableName", source_table)
            .options(**table_config)
            .load()
        )


def _get_table_metadata(spark, connection_name: str, table_list: list[str]) -> dict:
    """Get metadata for all tables in the pipeline"""
    metadata = {}
    
    # Try to read metadata from the connector via the metadata table
    try:
        metadata_df = (
            spark.read.format("lakeflow_connect")
            .option("databricks.connection", connection_name)
            .option("tableName", "_lakeflow_metadata")  # Query metadata table
            .load()
        )
        
        # Filter for requested tables
        metadata_df = metadata_df.filter(col("tableName").isin(table_list))
        
        for row in metadata_df.collect():
            table_metadata = {
                "primary_keys": row["primary_keys"] if row["primary_keys"] else [],
                "cursor_field": row["cursor_field"] if row["cursor_field"] else None,
                "ingestion_type": row["ingestion_type"] if row["ingestion_type"] else "snapshot",
            }

            metadata[row["tableName"]] = table_metadata
    except Exception:
        # Metadata query failed - use defaults
        # All tables will default to snapshot ingestion with no primary keys
        # These can be overridden in the pipeline spec
        pass
    
    # Fill in default metadata for tables that don't have it
    for table in table_list:
        if table not in metadata:
            metadata[table] = {
                "primary_keys": [],
                "cursor_field": None,
                "ingestion_type": "snapshot",  # Default to snapshot ingestion
            }
    
    return metadata


def ingest(spark, pipeline_spec: dict) -> None:
    """Ingest a list of tables using DLT/SDP decorators"""

    # parse the pipeline spec
    spec = SpecParser(pipeline_spec)
    connection_name = spec.connection_name()
    table_list = spec.get_table_list()

    metadata = _get_table_metadata(spark, connection_name, table_list)

    def _ingest_table(table: str) -> None:
        """Helper function to ingest a single table"""
        primary_keys = metadata[table].get("primary_keys")
        cursor_field = metadata[table].get("cursor_field")
        ingestion_type = metadata[table].get("ingestion_type", "cdc")
        view_name = table + "_staging"
        table_config = spec.get_table_configuration(table)
        destination_table = spec.get_full_destination_table_name(table)

        # Override parameters with spec values if available
        primary_keys = spec.get_primary_keys(table) or primary_keys
        sequence_by = spec.get_sequence_by(table) or cursor_field
        scd_type_raw = spec.get_scd_type(table)
        if scd_type_raw == "APPEND_ONLY":
            ingestion_type = "append"
        scd_type = "2" if scd_type_raw == "SCD_TYPE_2" else "1"

        if ingestion_type == "cdc":
            _create_cdc_table(
                spark,
                connection_name,
                table,
                destination_table,
                primary_keys,
                sequence_by,
                scd_type,
                view_name,
                table_config,
            )
        elif ingestion_type == "snapshot":
            _create_snapshot_table(
                spark,
                connection_name,
                table,
                destination_table,
                primary_keys,
                scd_type,
                view_name,
                table_config,
            )
        elif ingestion_type == "append":
            _create_append_table(
                spark,
                connection_name,
                table,
                destination_table,
                view_name,
                table_config,
            )

    for table in table_list:
        _ingest_table(table)
