"""
Airtable Lakeflow Connector - Databricks Deployment
====================================================

Main ingestion pipeline for Databricks deployment.
Use this file when deploying to Databricks workspace.

For local testing, use ingest_local.py instead.

Prerequisites:
1. Unity Catalog connection named 'airtable' must exist:
   CREATE CONNECTION IF NOT EXISTS airtable
   TYPE GENERIC_LAKEFLOW_CONNECT
   OPTIONS (
     sourceName 'airtable',
     bearer_token 'your_token',
     base_id 'your_base_id',
     base_url 'https://api.airtable.com/v0'
   );

2. This file should be in a Databricks Repo for proper Python path resolution

Usage:
- Upload to Databricks Repos (recommended)
- Or use Databricks UI: "+New" -> "Add or upload data" -> "Community connectors"
- Or use CLI tool: tools/community_connector
"""

from pipeline.ingestion_pipeline import ingest
from libs.common.source_loader import get_register_function

# =============================================================================
# CONNECTOR CONFIGURATION
# =============================================================================

source_name = "airtable"

# =============================================================================
# PIPELINE SPECIFICATION
# =============================================================================
# Configure your ingestion pipeline below.
#
# Required fields:
# - connection_name: Unity Catalog connection name (required)
# - default_catalog: Default catalog for tables (required)
# - default_schema: Default schema for tables (required)
# - objects: List of tables to ingest (required)
#
# Each table entry supports:
# - source_table: Table name in Airtable (required)
# - destination_catalog: Override default catalog (optional)
# - destination_schema: Override default schema (optional)
# - destination_table: Target table name (optional, defaults to source_table)
# - table_configuration: Additional options (optional)
#   - scd_type: "SCD_TYPE_1" (default), "SCD_TYPE_2", or "APPEND_ONLY"
#   - primary_keys: List of column names (optional, overrides connector default)
#
# =============================================================================

pipeline_spec = {
    "connection_name": "airtable",      # UC connection name (must match CREATE CONNECTION)
    "base_id": "appSaRcgA5UCGoRg5",     # ← UPDATE: Your Airtable base ID
    "default_catalog": "main",          # ← UPDATE: Your target catalog
    "default_schema": "default",        # ← UPDATE: Your target schema
    
    "objects": [
        {
            "table": {
                "source_table": "Packaging Tasks",        # ← Update with your table name
                "destination_table": "packaging_tasks",   # ← Optional: target table name
                # Optional table configuration:
                # "table_configuration": {
                #     "scd_type": "SCD_TYPE_2",           # Enable SCD Type 2
                #     "primary_keys": ["id"]              # Override primary keys
                # }
            }
        },
        {
            "table": {
                "source_table": "Campaigns",
                "destination_table": "campaigns",
            }
        },
        {
            "table": {
                "source_table": "Creative Requests",
                "destination_table": "creative_requests",
            }
        }
        
        # Add more tables as needed:
        # {
        #     "table": {
        #         "source_table": "Your Table Name",
        #         "destination_table": "your_table_name",
        #     }
        # }
    ]
}

# =============================================================================
# PIPELINE EXECUTION
# =============================================================================
# The code below registers the Airtable connector and executes the ingestion.
# DO NOT MODIFY unless you know what you're doing!
# =============================================================================

print("=" * 80)
print("🚀 Airtable Lakeflow Connector - Starting Ingestion")
print("=" * 80)
print(f"Source: {source_name}")
print(f"Connection: {pipeline_spec['connection_name']}")
print(f"Tables: {len(pipeline_spec['objects'])}")
print()

# Register the Airtable connector as a Spark Data Source
register_lakeflow_source = get_register_function(source_name)
register_lakeflow_source(spark)

print("✓ Connector registered")
print()

# Execute the ingestion pipeline
ingest(spark, pipeline_spec)

print()
print("=" * 80)
print("✅ Ingestion pipeline completed!")
print("=" * 80)
