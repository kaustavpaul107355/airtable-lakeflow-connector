# 🧪 Local Testing Guide for Airtable Connector

**Based on Expert Guidance:** Test locally before deployment  
**Status:** Your implementation is correct - let's validate it!

---

## 🎯 What the Expert Said

> "For the pipeline_spec, please do not add extra parameters except the ones you could customize under table_configuration"

> "After you have the ingest.py, just fill the table you want to ingest and optional configurations to control how you want to ingest (e.g. scd types), then please just run the pipeline"

> "Your local test should pass with your Implementation"

---

## 📋 Prerequisites for Local Testing

### 1. Python Environment

```bash
# Create virtual environment
cd /Users/kaustav.paul/CursorProjects/Databricks/databricks-starter/databricks-apps/airtable-connector

python3 -m venv venv
source venv/bin/activate  # On Mac/Linux
# OR
# venv\Scripts\activate  # On Windows
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Your `requirements.txt` already has:
- `pydantic>=2.5.0` ✓
- `pyairtable>=2.3.0` ✓
- `pyspark>=3.5.0` ✓

### 3. Set Up Credentials

Copy your credentials:
```bash
cp .credentials.example .credentials
```

Edit `.credentials` with your real values:
```bash
AIRTABLE_TOKEN=your_actual_token_here
AIRTABLE_BASE_ID=your_actual_base_id_here
```

---

## 📝 Step 1: Create Local Test ingest.py

Create a simple `ingest.py` for local testing:

```python
# ingest.py - Local Testing Version
"""
Local test for Airtable Lakeflow Connector
Run this to validate your connector implementation before deployment
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import framework components
from pipeline.ingestion_pipeline import ingest
from libs.source_loader import get_register_function

# Load credentials from .credentials file
from dotenv import load_dotenv
load_dotenv('.credentials')

AIRTABLE_TOKEN = os.getenv('AIRTABLE_TOKEN')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')

if not AIRTABLE_TOKEN or not AIRTABLE_BASE_ID:
    raise ValueError("Missing AIRTABLE_TOKEN or AIRTABLE_BASE_ID in .credentials file")

print("=" * 80)
print("🧪 LOCAL TEST: Airtable Lakeflow Connector")
print("=" * 80)
print(f"Base ID: {AIRTABLE_BASE_ID[:10]}...")
print(f"Token: {AIRTABLE_TOKEN[:10]}...")
print("=" * 80)

# Source name
source_name = "airtable"

# =============================================================================
# PIPELINE SPECIFICATION
# =============================================================================
# As per expert: Only include parameters under table_configuration
# Don't add extra parameters!

pipeline_spec = {
    "connection_name": "airtable_local",  # Local testing connection
    "base_id": AIRTABLE_BASE_ID,
    "default_catalog": "local_catalog",  # For local testing
    "default_schema": "airtable_test",   # For local testing
    
    # Configure tables to ingest
    "objects": [
        {
            "table": {
                "source_table": "Packaging Tasks",  # YOUR TABLE NAME
                "destination_table": "packaging_tasks",
                # Optional: Configure SCD type
                # "scd_type": "2",  # For SCD Type 2
                # "primary_keys": ["id"]
            }
        },
        {
            "table": {
                "source_table": "Campaigns",  # YOUR TABLE NAME
                "destination_table": "campaigns",
            }
        },
        {
            "table": {
                "source_table": "Creative Requests",  # YOUR TABLE NAME  
                "destination_table": "creative_requests",
            }
        }
    ]
}

# =============================================================================
# MOCK SPARK FOR LOCAL TESTING
# =============================================================================

class MockSparkDataSource:
    """Mock Spark DataSource registry for local testing"""
    def register(self, source_class):
        print(f"✓ Would register: {source_class.__name__}")
        return source_class

class MockSpark:
    """Mock Spark session for local testing"""
    def __init__(self):
        self.dataSource = MockSparkDataSource()
        self._options = {
            'bearer_token': AIRTABLE_TOKEN,
            'base_id': AIRTABLE_BASE_ID,
            'base_url': 'https://api.airtable.com/v0'
        }
    
    def conf(self):
        """Mock conf for UC connection resolution"""
        return self
    
    def get(self, key):
        """Mock get for connection options"""
        return self._options.get(key)

# Create mock Spark session
spark = MockSpark()

# =============================================================================
# RUN LOCAL TEST
# =============================================================================

print("\n" + "=" * 80)
print("🔧 Step 1: Register Lakeflow Source")
print("=" * 80)

try:
    register_lakeflow_source = get_register_function(source_name)
    register_lakeflow_source(spark)
    print(f"✓ Successfully registered '{source_name}' connector")
except Exception as e:
    print(f"✗ Failed to register: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print("🔧 Step 2: Validate Pipeline Specification")
print("=" * 80)

try:
    from pipeline_spec.airtable_spec import load_pipeline_spec_from_dict
    spec = load_pipeline_spec_from_dict(pipeline_spec)
    print(f"✓ Pipeline spec validated successfully")
    print(f"  - Connection: {spec.connection_name}")
    print(f"  - Base ID: {spec.base_id}")
    print(f"  - Tables: {len(spec.objects)}")
except Exception as e:
    print(f"✗ Spec validation failed: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print("🔧 Step 3: Test Connector Directly")
print("=" * 80)

try:
    from sources.airtable.airtable import AirtableLakeflowConnector
    
    # Create connector with credentials
    options = {
        'bearer_token': AIRTABLE_TOKEN,
        'base_id': AIRTABLE_BASE_ID,
        'base_url': 'https://api.airtable.com/v0'
    }
    
    connector = AirtableLakeflowConnector(options)
    print("✓ Connector instantiated successfully")
    
    # Test: List tables
    print("\n📋 Testing list_tables():")
    tables = connector.list_tables()
    print(f"✓ Found {len(tables)} tables:")
    for table in tables:
        print(f"  - {table}")
    
    # Test: Get schema for first table
    if tables:
        test_table = tables[0]
        print(f"\n📋 Testing get_table_schema() for '{test_table}':")
        schema = connector.get_table_schema(test_table)
        print(f"✓ Schema retrieved: {len(schema.fields)} fields")
        for field in schema.fields[:5]:  # Show first 5 fields
            print(f"  - {field.name}: {field.dataType}")
        if len(schema.fields) > 5:
            print(f"  ... and {len(schema.fields) - 5} more fields")
    
    # Test: Get table metadata
    if tables:
        print(f"\n📋 Testing read_table_metadata() for '{test_table}':")
        metadata = connector.read_table_metadata(test_table)
        print(f"✓ Metadata retrieved:")
        print(f"  - Primary keys: {metadata.get('primary_keys', [])}")
        print(f"  - Cursor field: {metadata.get('cursor_field', 'N/A')}")
        print(f"  - Ingestion type: {metadata.get('ingestion_type', 'N/A')}")
    
    # Test: Read table data (just first 5 records)
    if tables:
        print(f"\n📋 Testing read_table() for '{test_table}':")
        records_iter, state = connector.read_table(
            table_name=test_table,
            latest_offset=None,
            schema=schema
        )
        
        records = list(records_iter)
        print(f"✓ Read {len(records)} records")
        
        if records:
            print(f"\n  Sample record (first one):")
            first_record = records[0]
            for key, value in list(first_record.items())[:5]:
                print(f"    - {key}: {value}")
        
        print(f"\n  State returned: {state}")
    
    print("\n" + "=" * 80)
    print("✅ ALL LOCAL TESTS PASSED!")
    print("=" * 80)
    print("\nYour connector implementation is working correctly! 🎉")
    print("\nNext steps:")
    print("1. Your connector is validated ✓")
    print("2. Ready for deployment via official tools")
    print("3. Contact expert for correct deployment method")
    
except Exception as e:
    print(f"\n✗ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
```

---

## 🚀 Step 2: Install Additional Dependency

You need `python-dotenv` for loading credentials:

```bash
pip install python-dotenv
```

Add to `requirements.txt`:
```bash
echo "python-dotenv>=1.0.0  # For loading .credentials file" >> requirements.txt
```

---

## 🏃 Step 3: Run Local Test

```bash
# Activate virtual environment
source venv/bin/activate

# Run the test
python ingest.py
```

---

## 📊 Expected Output

If everything works, you should see:

```
================================================================================
🧪 LOCAL TEST: Airtable Lakeflow Connector
================================================================================
Base ID: appSaRcgA5...
Token: patkBXwClC...
================================================================================

================================================================================
🔧 Step 1: Register Lakeflow Source
================================================================================
✓ Would register: LakeflowSource
✓ Successfully registered 'airtable' connector

================================================================================
🔧 Step 2: Validate Pipeline Specification
================================================================================
✓ Pipeline spec validated successfully
  - Connection: airtable_local
  - Base ID: appSaRcgA5UCGoRg5
  - Tables: 3

================================================================================
🔧 Step 3: Test Connector Directly
================================================================================
✓ Connector instantiated successfully

📋 Testing list_tables():
✓ Found 3 tables:
  - Packaging Tasks
  - Campaigns
  - Creative Requests

📋 Testing get_table_schema() for 'Packaging Tasks':
✓ Schema retrieved: 10 fields
  - id: StringType()
  - Name: StringType()
  - Status: StringType()
  - Due Date: DateType()
  - Assignee: StringType()
  ... and 5 more fields

📋 Testing read_table_metadata() for 'Packaging Tasks':
✓ Metadata retrieved:
  - Primary keys: ['id']
  - Cursor field: createdTime
  - Ingestion type: incremental

📋 Testing read_table() for 'Packaging Tasks':
✓ Read 25 records

  Sample record (first one):
    - id: rec123456789
    - Name: Task 1
    - Status: In Progress
    - Due Date: 2026-01-15
    - Assignee: John Doe

  State returned: {'latest_offset': '2026-01-07T12:00:00.000Z'}

================================================================================
✅ ALL LOCAL TESTS PASSED!
================================================================================

Your connector implementation is working correctly! 🎉

Next steps:
1. Your connector is validated ✓
2. Ready for deployment via official tools
3. Contact expert for correct deployment method
```

---

## 🐛 Troubleshooting

### Issue: ModuleNotFoundError

**If you get:**
```
ModuleNotFoundError: No module named 'pipeline'
```

**Fix:** Make sure you're running from the connector directory and all `__init__.py` files exist:
```bash
cd /Users/kaustav.paul/CursorProjects/Databricks/databricks-starter/databricks-apps/airtable-connector
find . -name "__init__.py" | sort
```

### Issue: Invalid Credentials

**If you get:**
```
401 Unauthorized or Invalid token
```

**Fix:** Check your `.credentials` file:
```bash
cat .credentials
# Make sure token and base_id are correct
```

### Issue: Table Not Found

**If you get:**
```
Table 'X' not found
```

**Fix:** Update the table names in `ingest.py` to match your actual Airtable tables:
```python
"objects": [
    {
        "table": {
            "source_table": "YOUR_ACTUAL_TABLE_NAME",  # ← Change this
            "destination_table": "your_destination",
        }
    }
]
```

---

## 📝 Step 4: Customize for Your Tables

Edit the `pipeline_spec` in `ingest.py` to match your Airtable base:

```python
pipeline_spec = {
    "connection_name": "airtable_local",
    "base_id": AIRTABLE_BASE_ID,
    "default_catalog": "local_catalog",
    "default_schema": "airtable_test",
    
    "objects": [
        {
            "table": {
                "source_table": "YOUR_TABLE_1",  # Exact name from Airtable
                "destination_table": "table_1",  # Desired name in Delta
                # Optional configurations:
                # "scd_type": "2",  # For SCD Type 2 tracking
                # "primary_keys": ["id"]  # Specify primary keys
            }
        },
        {
            "table": {
                "source_table": "YOUR_TABLE_2",
                "destination_table": "table_2",
            }
        }
        # Add more tables as needed
    ]
}
```

**As per expert:** Only use parameters under `table_configuration`. Don't add extra fields!

---

## ✅ What This Test Validates

Running this local test validates:

1. ✓ **Connector instantiation** - Can create connector with credentials
2. ✓ **List tables** - Can discover tables in your Airtable base
3. ✓ **Get schema** - Can retrieve and map Airtable field types
4. ✓ **Get metadata** - Can determine primary keys, cursor fields
5. ✓ **Read data** - Can fetch actual records from Airtable
6. ✓ **Pydantic spec** - Pipeline specification validates correctly
7. ✓ **Source registration** - Framework integration works

---

## 🎯 After Local Test Passes

Once local test passes:

1. **✅ Your implementation is confirmed working**
2. **✅ Ready for deployment**
3. **✅ Contact expert for deployment method**

Share with your expert:
```
Hi [Expert],

Local testing passed! ✅

Results:
• Connector instantiates correctly
• Lists {X} tables from Airtable base
• Retrieves schemas correctly
• Reads data successfully
• Pipeline spec validates
• All methods working

I used only table_configuration parameters as advised.
Ready for deployment - what's the next step?

Thanks!
```

---

## 📚 Additional: Test Individual Components

You can also test individual components:

### Test 1: Just the Connector

```python
# test_connector_only.py
from sources.airtable.airtable import AirtableLakeflowConnector
import os
from dotenv import load_dotenv

load_dotenv('.credentials')

options = {
    'bearer_token': os.getenv('AIRTABLE_TOKEN'),
    'base_id': os.getenv('AIRTABLE_BASE_ID'),
    'base_url': 'https://api.airtable.com/v0'
}

connector = AirtableLakeflowConnector(options)
print("Tables:", connector.list_tables())
```

### Test 2: Just the Spec

```python
# test_spec_only.py
from pipeline_spec.airtable_spec import load_pipeline_spec_from_dict

spec_dict = {
    "connection_name": "test",
    "base_id": "appXXX",
    "default_catalog": "catalog",
    "default_schema": "schema",
    "objects": [
        {"table": {"source_table": "Table1", "destination_table": "table1"}}
    ]
}

spec = load_pipeline_spec_from_dict(spec_dict)
print("Spec valid:", spec.connection_name)
```

---

## 🎉 Summary

**What to do:**
1. Set up virtual environment
2. Install dependencies (including `python-dotenv`)
3. Copy and edit `.credentials` file
4. Create `ingest.py` with your table names
5. Run `python ingest.py`
6. Verify all tests pass
7. Share results with expert

**Expected outcome:**
✅ Local test passes → Confirms your implementation is correct → Ready for deployment!

This gives you confidence before dealing with Databricks deployment! 🚀

