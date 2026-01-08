"""
Airtable Lakeflow Connector - Simplified DLT Pattern (No Serialization)
========================================================================

This implementation bypasses Python Data Source serialization by calling
the connector directly in @dlt.table functions.

Approach:
- Connector runs on DRIVER only (no worker serialization)
- Only simple data (records) distributed to workers
- No ModuleNotFoundError issues

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

Note: The original serialization-based approach is preserved in 
      ingest_with_serialization.py for reference.
"""

import dlt
from sources.airtable.airtable import AirtableLakeflowConnector
from libs.spec_parser import sanitize_table_name

# =============================================================================
# CONFIGURATION - Get credentials from Unity Catalog connection  
# =============================================================================

print("=" * 80)
print("🚀 Airtable Lakeflow Connector - Simplified Pattern")
print("=" * 80)

# DLT pipelines can access UC connections via spark.conf IF configured properly
# You MUST add this to your DLT pipeline configuration (JSON/YAML):
#
# "configuration": {
#   "connection.airtable.bearer_token": "{{secrets/your-scope/airtable-token}}",
#   "connection.airtable.base_id": "<your-airtable-base-id>",
#   "connection.airtable.base_url": "https://api.airtable.com/v0"
# }
#
# OR use Databricks secrets to avoid hardcoding

try:
    bearer_token = spark.conf.get("connection.airtable.bearer_token")
    base_id = spark.conf.get("connection.airtable.base_id")
    base_url = spark.conf.get("connection.airtable.base_url", "https://api.airtable.com/v0")
    
    print(f"✅ Base ID: {base_id[:10]}...")
    print(f"✅ Base URL: {base_url}")
    print("✅ Credentials loaded successfully")
    print()
    
except Exception as e:
    print()
    print("=" * 80)
    print("❌ ERROR: Cannot access UC connection credentials")
    print("=" * 80)
    print(f"Error: {e}")
    print()
    print("🔧 FIX: Add this to your DLT Pipeline Configuration:")
    print()
    print('In DLT UI → Settings → Advanced → Configuration, add:')
    print()
    print('  Key: connection.airtable.bearer_token')
    print('  Value: {{secrets/your-scope/your-token-key}}')
    print()
    print('  Key: connection.airtable.base_id')  
    print('  Value: appSaRcgA5UCGoRg5')
    print()
    print('  Key: connection.airtable.base_url')
    print('  Value: https://api.airtable.com/v0')
    print()
    print("📖 OR see docs/DEPLOYMENT.md for detailed instructions")
    print("=" * 80)
    print()
    raise RuntimeError("UC connection not configured. See error message above for fix.")

# =============================================================================
# CREATE CONNECTOR INSTANCE (runs on driver only)
# =============================================================================

connector = AirtableLakeflowConnector({
    "bearer_token": bearer_token,
    "base_id": base_id,
    "base_url": base_url,
    "batch_size": 100,
    "max_retries": 3,
    "timeout": 30
})

print("✓ Connector initialized")
print()

# =============================================================================
# TABLE DEFINITIONS
# =============================================================================
# Define each table as a @dlt.table function.
# The connector fetches data on the driver, then Spark distributes it.
# =============================================================================

@dlt.table(
    name="packaging_tasks",
    comment="Packaging Tasks from Airtable",
    table_properties={
        "quality": "silver",
        "pipelines.autoOptimize.zOrderCols": "id"
    }
)
def packaging_tasks():
    """
    Ingest Packaging Tasks table from Airtable.
    """
    source_table = "Packaging Tasks"
    
    print(f"📊 Fetching data from Airtable table: {source_table}")
    
    # Get schema first
    schema = connector.get_table_schema(source_table, {})
    
    # Fetch data (generator returns records)
    records_iter, next_offset = connector.read_table(
        table_name=source_table,
        start_offset={},  # Full refresh - could use for incremental later
        table_options={}
    )
    
    # Convert generator to list (materializes all records on driver)
    records = list(records_iter)
    
    print(f"   ✅ Fetched {len(records)} records from {source_table}")
    
    # Create DataFrame from simple data (no complex objects to serialize)
    # Spark only distributes the simple record data, not the connector code
    return spark.createDataFrame(records, schema)


@dlt.table(
    name="campaigns",
    comment="Campaigns from Airtable",
    table_properties={
        "quality": "silver",
        "pipelines.autoOptimize.zOrderCols": "id"
    }
)
def campaigns():
    """
    Ingest Campaigns table from Airtable.
    """
    source_table = "Campaigns"
    
    print(f"📊 Fetching data from Airtable table: {source_table}")
    
    schema = connector.get_table_schema(source_table, {})
    records_iter, next_offset = connector.read_table(
        table_name=source_table,
        start_offset={},
        table_options={}
    )
    
    records = list(records_iter)
    print(f"   ✅ Fetched {len(records)} records from {source_table}")
    
    return spark.createDataFrame(records, schema)


@dlt.table(
    name="creative_requests",
    comment="Creative Requests from Airtable",
    table_properties={
        "quality": "silver",
        "pipelines.autoOptimize.zOrderCols": "id"
    }
)
def creative_requests():
    """
    Ingest Creative Requests table from Airtable.
    """
    source_table = "Creative Requests"
    
    print(f"📊 Fetching data from Airtable table: {source_table}")
    
    schema = connector.get_table_schema(source_table, {})
    records_iter, next_offset = connector.read_table(
        table_name=source_table,
        start_offset={},
        table_options={}
    )
    
    records = list(records_iter)
    print(f"   ✅ Fetched {len(records)} records from {source_table}")
    
    return spark.createDataFrame(records, schema)


# =============================================================================
# ADD MORE TABLES HERE
# =============================================================================
# To add more tables, copy the pattern above:
#
# @dlt.table(
#     name="your_sanitized_table_name",
#     comment="Your Table from Airtable"
# )
# def your_function_name():
#     source_table = "Your Table Name"  # Exact name in Airtable
#     schema = connector.get_table_schema(source_table, {})
#     records_iter, _ = connector.read_table(source_table, {}, {})
#     records = list(records_iter)
#     return spark.createDataFrame(records, schema)
#
# =============================================================================

print()
print("=" * 80)
print("📋 DLT Tables Defined:")
print("   - packaging_tasks (main.default.packaging_tasks)")
print("   - campaigns (main.default.campaigns)")
print("   - creative_requests (main.default.creative_requests)")
print()
print("✅ Pipeline definition complete!")
print("   DLT will execute these tables when the pipeline runs.")
print("=" * 80)
