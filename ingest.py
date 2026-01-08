"""
Airtable Lakeflow Connector - Official Pattern
===============================================

This uses the official Databricks Lakeflow Community Connectors pattern.

Key Points (per Expert guidance):
1. Connector implementation (sources/airtable/airtable.py) does NOT access UC
2. UC connection integration handled by framework (pipeline/ingestion_pipeline.py)
3. Spark engine automatically injects credentials from UC connection

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

2. Deploy via official Databricks Lakeflow UI tool:
   +New → Add or upload data → Community connectors
   
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
# The framework will automatically retrieve credentials from UC connection
# named 'airtable' and pass them to the connector.
# 
# NO manual UC access needed - the engine handles it!
# =============================================================================

pipeline_spec = {
    "connection_name": "airtable",  # References UC connection
    
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
# The framework handles:
# 1. Reading UC connection 'airtable'
# 2. Extracting credentials (bearer_token, base_id, base_url)
# 3. Passing credentials to connector via Python Data Source API
# 4. Creating DLT tables
# =============================================================================

print("=" * 80)
print("🚀 Airtable Lakeflow Connector - Official Pattern")
print("=" * 80)
print(f"Source: {source_name}")
print(f"UC Connection: {pipeline_spec['connection_name']}")
print(f"Tables: {len(pipeline_spec['objects'])}")
print()
print("✅ Framework will handle UC credential retrieval automatically")
print()

# Register the Airtable connector as a Spark Data Source
register_lakeflow_source = get_register_function(source_name)
register_lakeflow_source(spark)

print("✓ Connector registered")
print()

# Execute the ingestion pipeline
# This uses spark.read.format("lakeflow_connect").option("databricks.connection", "airtable")
# The Spark engine will:
# - Read UC connection "airtable"
# - Pass credentials to connector
# - No manual UC queries needed!
ingest(spark, pipeline_spec)

print()
print("=" * 80)
print("✅ Ingestion pipeline completed!")
print("=" * 80)
