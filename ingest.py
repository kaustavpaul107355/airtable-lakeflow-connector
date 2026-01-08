"""
Airtable Lakeflow Connector - Workspace Deployment
===================================================

This implementation works in /Workspace/ without requiring /Repos/.

Key Features:
- ✅ NO serialization (connector runs on driver only)
- ✅ Gets credentials from UC connection automatically
- ✅ Works in /Workspace/ folders
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

2. Complete directory structure in Workspace:
   - sources/airtable/airtable.py
   - sources/interface/lakeflow_connect.py
   - libs/common/source_loader.py (not used but may be imported)
   - All __init__.py files in place
"""

import sys
import os

# =============================================================================
# PYTHON PATH SETUP - Critical for /Workspace/ deployment
# =============================================================================

print("=" * 80)
print("🚀 Airtable Lakeflow Connector - Workspace Deployment")
print("=" * 80)
print()

# Get the directory where this file is located
try:
    # Method 1: Use dbutils to get notebook path (works in DLT)
    notebook_path = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
    current_dir = os.path.dirname(notebook_path)
    print(f"✓ Detected notebook path: {notebook_path}")
    print(f"✓ Current directory: {current_dir}")
except:
    # Method 2: Fallback - assume we're in the right place
    current_dir = os.getcwd()
    print(f"⚠️  Could not detect notebook path, using CWD: {current_dir}")

# Add current directory to Python path
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
    print(f"✓ Added to sys.path: {current_dir}")

print()

# Now import our modules
import dlt
from sources.airtable.airtable import AirtableLakeflowConnector

print("✓ Imports successful")
print()

# =============================================================================
# GET CREDENTIALS FROM UC CONNECTION - Multiple fallback methods
# =============================================================================

bearer_token = None
base_id = None
base_url = None

# Method 1: Try system catalog query (newest Databricks versions)
print("🔍 Attempting to retrieve UC connection credentials...")
print()

try:
    print("   Method 1: Query system.information_schema.connections...")
    connection_df = spark.sql("""
        SELECT *
        FROM system.information_schema.connections
        WHERE connection_name = 'airtable'
    """)
    
    connection_row = connection_df.first()
    
    if connection_row:
        # Try to extract options - structure may vary
        if hasattr(connection_row, 'connection_options') and connection_row.connection_options:
            options = connection_row.connection_options
            bearer_token = options.get('bearer_token')
            base_id = options.get('base_id')
            base_url = options.get('base_url', 'https://api.airtable.com/v0')
        elif hasattr(connection_row, 'options') and connection_row.options:
            options = connection_row.options
            bearer_token = options.get('bearer_token')
            base_id = options.get('base_id')
            base_url = options.get('base_url', 'https://api.airtable.com/v0')
        
        if bearer_token and base_id:
            print("   ✅ Method 1 succeeded!")
except Exception as e:
    print(f"   ⚠️  Method 1 failed: {e}")

# Method 2: Try DESCRIBE CONNECTION (works in most versions)
if not bearer_token or not base_id:
    try:
        print("   Method 2: DESCRIBE CONNECTION airtable...")
        
        # DESCRIBE returns a different structure - parse it
        desc_df = spark.sql("DESCRIBE CONNECTION airtable")
        desc_rows = desc_df.collect()
        
        # Parse the description (format varies, but typically key-value pairs)
        options_dict = {}
        for row in desc_rows:
            # Try different column name patterns
            if hasattr(row, 'property_key') and hasattr(row, 'property_value'):
                options_dict[row.property_key] = row.property_value
            elif hasattr(row, 'key') and hasattr(row, 'value'):
                options_dict[row.key] = row.value
            elif hasattr(row, 'col_name') and hasattr(row, 'data_type'):
                options_dict[row.col_name] = row.data_type
        
        bearer_token = options_dict.get('bearer_token')
        base_id = options_dict.get('base_id')
        base_url = options_dict.get('base_url', 'https://api.airtable.com/v0')
        
        if bearer_token and base_id:
            print("   ✅ Method 2 succeeded!")
    except Exception as e:
        print(f"   ⚠️  Method 2 failed: {e}")

# Validation
print()
if not bearer_token or not base_id:
    print("=" * 80)
    print("❌ ERROR: Could not retrieve credentials from UC connection")
    print("=" * 80)
    print()
    print("🔧 TROUBLESHOOTING STEPS:")
    print()
    print("1. Verify connection exists:")
    print("   Run in SQL: SHOW CONNECTIONS;")
    print()
    print("2. Check connection details:")
    print("   Run in SQL: DESCRIBE CONNECTION airtable;")
    print()
    print("3. Verify connection type:")
    print("   Should be: GENERIC_LAKEFLOW_CONNECT")
    print()
    print("4. Check connection options:")
    print("   Must have: bearer_token, base_id, base_url")
    print()
    print("5. Test connection access:")
    print("   Run this in a notebook:")
    print("   spark.sql('SELECT * FROM system.information_schema.connections WHERE connection_name = \\'airtable\\'').show()")
    print()
    print("6. Check your permissions:")
    print("   You need USE CONNECTION permission on 'airtable'")
    print()
    print("=" * 80)
    raise RuntimeError("Cannot retrieve UC connection credentials. See troubleshooting steps above.")

print(f"✅ Base ID: {base_id[:10] if len(base_id) > 10 else base_id}...")
print(f"✅ Base URL: {base_url}")
print(f"✅ Token: {bearer_token[:10] if len(bearer_token) > 10 else bearer_token}...")
print("✅ Credentials retrieved from UC connection 'airtable'")
print()

# =============================================================================
# CREATE CONNECTOR INSTANCE (runs on driver only)
# =============================================================================

print("🔧 Initializing Airtable connector...")

try:
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
    
except Exception as e:
    print(f"❌ Failed to initialize connector: {e}")
    raise

# =============================================================================
# DEFINE DLT TABLES
# =============================================================================

print("📋 Defining DLT tables...")
print()

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
    
    print(f"📊 Fetching data from Airtable: {source_table}")
    
    try:
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
        return spark.createDataFrame(records, schema)
        
    except Exception as e:
        print(f"   ❌ Error fetching {source_table}: {e}")
        raise


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
    
    print(f"📊 Fetching data from Airtable: {source_table}")
    
    try:
        schema = connector.get_table_schema(source_table, {})
        records_iter, next_offset = connector.read_table(
            table_name=source_table,
            start_offset={},
            table_options={}
        )
        
        records = list(records_iter)
        print(f"   ✅ Fetched {len(records)} records from {source_table}")
        
        return spark.createDataFrame(records, schema)
        
    except Exception as e:
        print(f"   ❌ Error fetching {source_table}: {e}")
        raise


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
    
    print(f"📊 Fetching data from Airtable: {source_table}")
    
    try:
        schema = connector.get_table_schema(source_table, {})
        records_iter, next_offset = connector.read_table(
            table_name=source_table,
            start_offset={},
            table_options={}
        )
        
        records = list(records_iter)
        print(f"   ✅ Fetched {len(records)} records from {source_table}")
        
        return spark.createDataFrame(records, schema)
        
    except Exception as e:
        print(f"   ❌ Error fetching {source_table}: {e}")
        raise


print("=" * 80)
print("✅ PIPELINE DEFINITION COMPLETE")
print("=" * 80)
print()
print("📋 Tables defined:")
print("   • packaging_tasks")
print("   • campaigns")
print("   • creative_requests")
print()
print("🎯 Deployment pattern:")
print("   ✅ No Python Data Source serialization")
print("   ✅ Works in /Workspace/ folders")
print("   ✅ Credentials from UC connection")
print("   ✅ Connector runs on driver only")
print("   ✅ Simple @dlt.table decorators")
print()
print("DLT will execute these tables when the pipeline runs.")
print("=" * 80)
