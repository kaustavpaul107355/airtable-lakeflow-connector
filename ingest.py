"""
Airtable Lakeflow Connector - Simplified Pattern (No Serialization)
====================================================================

This implementation bypasses Python Data Source serialization by calling
the connector directly in @dlt.table functions.

Key Features:
- ✅ NO serialization (connector runs on driver only)
- ✅ Gets credentials from UC connection (via SQL query)
- ✅ Works in /Workspace/ or /Repos/
- ✅ Simple @dlt.table decorators

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

import sys
import os

# =============================================================================
# PYTHON PATH SETUP (for /Workspace/ compatibility)
# =============================================================================
# Add current directory to Python path so imports work in both /Workspace/ and /Repos/

try:
    # Get current notebook/file directory
    current_dir = os.path.dirname(dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get())
    
    # Add to sys.path if not already there
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
        print(f"✓ Added to Python path: {current_dir}")
except:
    # Fallback: assume we're in the right directory
    print("⚠️  Could not detect notebook path, assuming imports will work")

# Now import our modules
import dlt
from sources.airtable.airtable import AirtableLakeflowConnector

# =============================================================================
# GET CREDENTIALS FROM UC CONNECTION
# =============================================================================

print("=" * 80)
print("🚀 Airtable Lakeflow Connector - Simplified Pattern (No Serialization)")
print("=" * 80)
print()

try:
    # Query UC connection using system catalog
    # Note: Syntax may vary by Databricks version
    connection_info = spark.sql("""
        SELECT 
            connection_type,
            connection_options
        FROM system.information_schema.connections
        WHERE connection_name = 'airtable'
    """).first()
    
    if not connection_info:
        raise ValueError("UC connection 'airtable' not found")
    
    # Extract options from the connection_options map
    options = connection_info['connection_options']
    bearer_token = options.get('bearer_token')
    base_id = options.get('base_id')
    base_url = options.get('base_url', 'https://api.airtable.com/v0')
    
    if not bearer_token or not base_id:
        raise ValueError("UC connection 'airtable' missing bearer_token or base_id")
    
    print(f"✅ Base ID: {base_id[:10] if base_id else 'N/A'}...")
    print(f"✅ Base URL: {base_url}")
    print(f"✅ Credentials retrieved from UC connection 'airtable'")
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
    print("3. Ensure connection type is GENERIC_LAKEFLOW_CONNECT")
    print()
    print("4. Verify connection has options: bearer_token, base_id, base_url")
    print()
    print("5. Check your permissions to read the connection")
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
# @dlt.table(name="your_table_name", comment="Your Table")
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
print("   ✅ Works in /Workspace/ (with sys.path setup)")
print("   ✅ Credentials from UC (SQL query)")
print("   ✅ Simple and debuggable")
print("=" * 80)
