#!/usr/bin/env python3
"""
Airtable Lakeflow Connector - Local Test
==========================================

Run this script locally to test your connector implementation
before deploying to Databricks.

Usage:
    1. Copy .credentials.example to .credentials
    2. Fill in your actual AIRTABLE_TOKEN and AIRTABLE_BASE_ID
    3. Update table names in pipeline_spec below
    4. Run: python ingest.py

Requirements:
    pip install -r requirements.txt
    pip install python-dotenv
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path for local imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

print("=" * 80)
print("🧪 AIRTABLE LAKEFLOW CONNECTOR - LOCAL TEST")
print("=" * 80)

# =============================================================================
# LOAD CREDENTIALS
# =============================================================================

try:
    from dotenv import load_dotenv
    load_dotenv('.credentials')
    print("✓ Loaded credentials from .credentials file")
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
    sys.exit(1)

AIRTABLE_TOKEN = os.getenv('AIRTABLE_TOKEN')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')

if not AIRTABLE_TOKEN or not AIRTABLE_BASE_ID:
    print("✗ Missing credentials!")
    print("  1. Copy .credentials.example to .credentials")
    print("  2. Edit .credentials with your actual token and base_id")
    sys.exit(1)

print(f"✓ Base ID: {AIRTABLE_BASE_ID[:10]}...")
print(f"✓ Token: {AIRTABLE_TOKEN[:10]}...")

# =============================================================================
# IMPORT FRAMEWORK COMPONENTS
# =============================================================================

print("\n" + "=" * 80)
print("📦 IMPORTING FRAMEWORK COMPONENTS")
print("=" * 80)

try:
    from pipeline.ingestion_pipeline import ingest
    print("✓ Imported ingestion_pipeline")
    
    from libs.common.source_loader import get_register_function  # Fixed: libs.common.source_loader
    print("✓ Imported source_loader")
    
    from sources.airtable.airtable import AirtableLakeflowConnector
    print("✓ Imported AirtableLakeflowConnector")
    
    # Fix: pipeline-spec has a hyphen, need to import differently
    import importlib.util
    spec_path = os.path.join(os.path.dirname(__file__), 'pipeline-spec', 'airtable_spec.py')
    spec_module = importlib.util.spec_from_file_location("airtable_spec", spec_path)
    airtable_spec = importlib.util.module_from_spec(spec_module)
    spec_module.loader.exec_module(airtable_spec)
    load_pipeline_spec_from_dict = airtable_spec.load_pipeline_spec_from_dict
    print("✓ Imported pipeline_spec")
    
except ImportError as e:
    print(f"✗ Import failed: {e}")
    print("\nMake sure all __init__.py files exist:")
    print("  - sources/__init__.py")
    print("  - sources/airtable/__init__.py")
    print("  - pipeline/__init__.py")
    print("  - libs/__init__.py")
    print("  - libs/common/__init__.py")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# =============================================================================
# PIPELINE SPECIFICATION
# =============================================================================
# As per expert guidance: Only use parameters under table_configuration
# Don't add extra parameters!

source_name = "airtable"

pipeline_spec = {
    "connection_name": "airtable_local",
    "base_id": AIRTABLE_BASE_ID,
    "default_catalog": "local_catalog",
    "default_schema": "airtable_test",
    
    # ==========================================================================
    # 📝 CONFIGURE YOUR TABLES HERE
    # ==========================================================================
    # Update these with your actual Airtable table names
    
    "objects": [
        {
            "table": {
                "source_table": "Packaging Tasks",        # ← Change to your table name
                "destination_table": "packaging_tasks",
                
                # Optional: Configure ingestion behavior
                # "scd_type": "2",          # For SCD Type 2 (history tracking)
                # "primary_keys": ["id"]    # Specify primary key(s)
            }
        },
        {
            "table": {
                "source_table": "Campaigns",              # ← Change to your table name
                "destination_table": "campaigns",
            }
        },
        {
            "table": {
                "source_table": "Creative Requests",      # ← Change to your table name
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
# MOCK SPARK SESSION FOR LOCAL TESTING
# =============================================================================

class MockSparkDataSource:
    """Mock Spark DataSource registry"""
    def register(self, source_class):
        print(f"    ✓ Would register: {source_class.__name__}")
        return source_class

class MockSpark:
    """Mock Spark session for local testing without actual Spark"""
    def __init__(self):
        self.dataSource = MockSparkDataSource()
        self._connection_options = {
            'bearer_token': AIRTABLE_TOKEN,
            'base_id': AIRTABLE_BASE_ID,
            'base_url': 'https://api.airtable.com/v0',
            'sourceName': 'airtable'
        }
    
    def conf(self):
        """Mock Spark config"""
        return self
    
    def get(self, key, default=None):
        """Mock config.get() for UC connection resolution"""
        return self._connection_options.get(key, default)

# =============================================================================
# TEST 1: REGISTER LAKEFLOW SOURCE
# =============================================================================

print("\n" + "=" * 80)
print("🔧 TEST 1: REGISTER LAKEFLOW SOURCE")
print("=" * 80)

try:
    spark = MockSpark()
    register_lakeflow_source = get_register_function(source_name)
    register_lakeflow_source(spark)
    print("✅ Source registration successful")
except Exception as e:
    print(f"✗ Registration failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# =============================================================================
# TEST 2: VALIDATE PIPELINE SPECIFICATION
# =============================================================================

print("\n" + "=" * 80)
print("🔧 TEST 2: VALIDATE PIPELINE SPECIFICATION")
print("=" * 80)

try:
    spec = load_pipeline_spec_from_dict(pipeline_spec)
    print(f"✓ Pipeline spec validated")
    print(f"    Connection: {spec.connection_name}")
    print(f"    Base ID: {spec.base_id}")
    print(f"    Catalog: {spec.default_catalog}")
    print(f"    Schema: {spec.default_schema}")
    print(f"    Tables: {len(spec.objects)}")
    print("\n  Configured tables:")
    for obj in spec.objects:
        src = obj.table.source_table
        dst = obj.table.destination_table
        print(f"    • {src} → {dst}")
    print("✅ Specification validation successful")
except Exception as e:
    print(f"✗ Spec validation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# =============================================================================
# TEST 3: TEST CONNECTOR DIRECTLY
# =============================================================================

print("\n" + "=" * 80)
print("🔧 TEST 3: TEST CONNECTOR IMPLEMENTATION")
print("=" * 80)

try:
    # Create connector with credentials
    options = {
        'bearer_token': AIRTABLE_TOKEN,
        'base_id': AIRTABLE_BASE_ID,
        'base_url': 'https://api.airtable.com/v0'
    }
    
    connector = AirtableLakeflowConnector(options)
    print("✓ Connector instantiated")
    
    # Test: List tables
    print("\n  📋 list_tables():")
    tables = connector.list_tables()
    print(f"    ✓ Found {len(tables)} tables:")
    for table in tables:
        print(f"      - {table}")
    
    if not tables:
        print("\n⚠️  No tables found in base. Check your base_id!")
        sys.exit(1)
    
    # Test: Get schema for first configured table
    test_table = spec.objects[0].table.source_table
    if test_table in tables:
        print(f"\n  📋 get_table_schema('{test_table}'):")
        schema = connector.get_table_schema(test_table, {})  # Pass empty dict for table_options
        print(f"    ✓ Schema has {len(schema.fields)} fields:")
        for field in schema.fields[:5]:
            print(f"      - {field.name}: {field.dataType}")
        if len(schema.fields) > 5:
            print(f"      ... and {len(schema.fields) - 5} more fields")
    else:
        print(f"\n⚠️  Table '{test_table}' not found in base!")
        print(f"    Available tables: {', '.join(tables)}")
        print("    Update table names in pipeline_spec!")
        sys.exit(1)
    
    # Test: Get table metadata
    print(f"\n  📋 read_table_metadata('{test_table}'):")
    metadata = connector.read_table_metadata(test_table, {})  # Pass empty dict for table_options
    print(f"    ✓ Metadata retrieved:")
    print(f"      - Primary keys: {metadata.get('primary_keys', [])}")
    print(f"      - Cursor field: {metadata.get('cursor_field', 'N/A')}")
    print(f"      - Ingestion type: {metadata.get('ingestion_type', 'N/A')}")
    
    # Test: Read table data
    print(f"\n  📋 read_table('{test_table}'):")
    records_iter, state = connector.read_table(
        table_name=test_table,
        start_offset={},  # Empty dict for initial load
        table_options={}  # Pass empty dict for table_options
    )
    
    # Fetch records
    records = list(records_iter)
    print(f"    ✓ Read {len(records)} records")
    
    if records:
        print(f"\n    Sample record (first one):")
        first_record = records[0]
        # Show first 5 fields
        for i, (key, value) in enumerate(first_record.items()):
            if i >= 5:
                print(f"      ... and {len(first_record) - 5} more fields")
                break
            # Truncate long values
            value_str = str(value)
            if len(value_str) > 50:
                value_str = value_str[:47] + "..."
            print(f"      - {key}: {value_str}")
        
        print(f"\n    State: {state}")
    else:
        print("    ⚠️  No records in table")
    
    print("\n✅ Connector implementation test successful")
    
except Exception as e:
    print(f"\n✗ Connector test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# =============================================================================
# TEST SUMMARY
# =============================================================================

print("\n" + "=" * 80)
print("✅ ALL LOCAL TESTS PASSED!")
print("=" * 80)
print(f"""
Your Airtable Lakeflow Connector is working correctly! 🎉

Test Results:
  ✓ Framework imports successful
  ✓ Source registration works
  ✓ Pipeline spec validates
  ✓ Connector instantiates
  ✓ list_tables() works
  ✓ get_table_schema() works
  ✓ read_table_metadata() works
  ✓ read_table() works
  ✓ Read {len(records)} records from '{test_table}'

Configuration:
  • Base ID: {AIRTABLE_BASE_ID}
  • Tables configured: {len(spec.objects)}
  • Tables in base: {len(tables)}

Next Steps:
  1. ✅ Your implementation is validated
  2. ✅ Ready for Databricks deployment
  3. 📞 Contact expert for deployment method
  
Share with expert:
  "Local testing passed! Connector successfully:
   - Lists {len(tables)} tables
   - Retrieves schemas correctly  
   - Reads data ({len(records)} records tested)
   - All validation passed
   Ready for deployment!"
""")

print("=" * 80)
print("🎯 Local testing complete!")
print("=" * 80)

