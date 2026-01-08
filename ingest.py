"""
Airtable Lakeflow Connector - Simplified Pattern (No Serialization)
====================================================================

This implementation bypasses Python Data Source serialization by calling
the connector directly in @dlt.table functions.

Key Features:
- ✅ NO serialization (works in /Workspace/ or /Repos/)
- ✅ Gets credentials from UC connection automatically (via SQL query)
- ✅ NO explicit credential configuration (spark.conf.get)
- ✅ Simple @dlt.table decorators
- ✅ Connector runs on driver only

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

For local testing, use ingest_local.py instead.
"""

import dlt
from sources.airtable.airtable import AirtableLakeflowConnector
from libs.spec_parser import sanitize_table_name

# =============================================================================
# GET CREDENTIALS FROM UC CONNECTION (NO EXPLICIT ACCESS)
# =============================================================================
# Query UC connection metadata using SQL - credentials retrieved automatically
# No spark.conf.get(), no explicit keys, no Databricks secrets needed

print("=" * 80)
print("🚀 Airtable Lakeflow Connector - Simplified Pattern (No Serialization)")
print("=" * 80)
print()

try:
    # Query UC connection metadata using SQL
    # This retrieves credentials automatically without explicit access
    connection_info = spark.sql("""
        SELECT 
            options['bearer_token'] as bearer_token,
            options['base_id'] as base_id,
            options['base_url'] as base_url
        FROM system.information_schema.connections
        WHERE connection_name = 'airtable'
    """).first()
    
    if not connection_info:
        raise ValueError("UC connection 'airtable' not found")
    
    bearer_token = connection_info['bearer_token']
    base_id = connection_info['base_id']
    base_url = connection_info['base_url'] or "https://api.airtable.com/v0"
    
    print(f"✅ Base ID: {base_id[:10]}...")
    print(f"✅ Base URL: {base_url}")
    print(f"✅ Credentials retrieved from UC connection 'airtable' (via SQL query)")
    print()
    
except Exception as e:
    print()
    print("=" * 80)
    print("❌ ERROR: Cannot access UC connection 'airtable'")
    print("=" * 80)
    print(f"Error: {e}")
    print()
    print("🔧 TROUBLESHOOTING:")
    print()
    print("1. Verify connection exists:")
    print("   SHOW CONNECTIONS;")
    print()
    print("2. Check connection details:")
    print("   DESCRIBE CONNECTION airtable;")
    print()
    print("3. Ensure connection has required options:")
    print("   - bearer_token")
    print("   - base_id")
    print("   - base_url")
    print()
    print("4. Create connection if missing:")
    print("   See create_uc_connection.sql")
    print()
    print("=" * 80)
    raise RuntimeError("UC connection not accessible") from e

# =============================================================================
# CREATE CONNECTOR INSTANCE (runs on driver only, no serialization to workers)
# =============================================================================

connector = AirtableLakeflowConnector({
    "bearer_token": bearer_token,
    "base_id": base_id,
    "base_url": base_url,
    "batch_size": 100,
    "max_retries": 3,
    "timeout": 30
})

print("✓ Connector initialized on driver node")
print("✓ No serialization needed - connector stays on driver")
print()

# =============================================================================
# DEFINE TABLES (each table fetches data on driver, returns DataFrame)
# =============================================================================
# Data fetching happens on the driver, only simple records are distributed
# to workers. This avoids serialization of the connector and all its imports.
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
    """Ingest Packaging Tasks table from Airtable."""
    source_table = "Packaging Tasks"
    
    print(f"📊 Fetching data from Airtable table: {source_table}")
    
    # Fetch schema and data on driver (no serialization)
    schema = connector.get_table_schema(source_table, {})
    records_iter, next_offset = connector.read_table(
        table_name=source_table,
        start_offset={},
        table_options={}
    )
    
    # Materialize records on driver
    records = list(records_iter)
    print(f"   ✅ Fetched {len(records)} records from {source_table}")
    
    # Only simple data (list of dicts) gets distributed to workers
    # No connector code, no imports, no serialization issues
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
    """Ingest Campaigns table from Airtable."""
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
    """Ingest Creative Requests table from Airtable."""
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
# @dlt.table(name="your_sanitized_table_name", comment="Your Table")
# def your_function_name():
#     source_table = "Your Table Name"
#     schema = connector.get_table_schema(source_table, {})
#     records_iter, _ = connector.read_table(source_table, {}, {})
#     records = list(records_iter)
#     return spark.createDataFrame(records, schema)
#
# =============================================================================

print()
print("=" * 80)
print("📋 DLT Tables Defined:")
print("   - packaging_tasks")
print("   - campaigns")
print("   - creative_requests")
print()
print("✅ Pipeline definition complete!")
print("   DLT will execute these tables when the pipeline runs.")
print()
print("🎯 Benefits of this pattern:")
print("   ✅ No Python Data Source serialization")
print("   ✅ Works in /Workspace/ or /Repos/")
print("   ✅ Credentials from UC (no explicit access)")
print("   ✅ Simple and debuggable")
print("=" * 80)
