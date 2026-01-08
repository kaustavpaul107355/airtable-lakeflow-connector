"""
Airtable Lakeflow Connector - Official Pattern with UC Connection
==================================================================

This implementation uses the official Lakeflow pattern where credentials
are automatically pulled from Unity Catalog connection.

NO explicit credentials needed:
- ❌ No spark.conf.get() for credentials
- ❌ No Databricks secrets
- ❌ No pipeline configuration for credentials
- ✅ UC connection handles everything automatically

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

2. This file MUST be in Databricks Repos for proper serialization

For local testing, use ingest_local.py instead.
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
# The connection_name references the UC connection.
# Credentials are automatically retrieved - NO explicit config needed!
#
# =============================================================================

pipeline_spec = {
    "connection_name": "airtable",      # UC connection name (credentials pulled automatically)
    
    "objects": [
        {
            "table": {
                "source_table": "Packaging Tasks",
                "destination_catalog": "main",
                "destination_schema": "default",
                "destination_table": "packaging_tasks",
            }
        },
        {
            "table": {
                "source_table": "Campaigns",
                "destination_catalog": "main",
                "destination_schema": "default",
                "destination_table": "campaigns",
            }
        },
        {
            "table": {
                "source_table": "Creative Requests",
                "destination_catalog": "main",
                "destination_schema": "default",
                "destination_table": "creative_requests",
            }
        }
    ]
}

# =============================================================================
# PIPELINE EXECUTION
# =============================================================================
# Registers connector and executes ingestion using official Lakeflow pattern
# =============================================================================

print("=" * 80)
print("🚀 Airtable Lakeflow Connector - Official Pattern")
print("=" * 80)
print(f"Source: {source_name}")
print(f"UC Connection: {pipeline_spec['connection_name']}")
print(f"Tables: {len(pipeline_spec['objects'])}")
print()
print("✅ Using UC connection - no explicit credentials needed")
print()

# Register the Airtable connector as a Spark Data Source
register_lakeflow_source = get_register_function(source_name)
register_lakeflow_source(spark)

print("✓ Connector registered")
print()

# Execute the ingestion pipeline
# This uses: spark.read.format("lakeflow_connect").option("databricks.connection", "airtable")
# Credentials are automatically retrieved from UC connection
ingest(spark, pipeline_spec)

print()
print("=" * 80)
print("✅ Ingestion pipeline completed!")
print("=" * 80)
